"""Production audio sources: the PortAudio microphone and a real-time WAV replay.

Both deliver mono float32 blocks at the analysis rate on their own thread; the
adapter only queues them. `sounddevice` and `numpy` come from the optional
`speech` dependency group and are imported when a source opens, so importing this
module needs neither. Device problems surface as `MicrophoneError` subclasses,
raised from `open` or reported through `on_error` while running.
"""

import threading
import time
import wave
from array import array
from collections.abc import Callable, Sequence
from pathlib import Path

from .seams import (
    MicrophoneError,
    MicrophoneLost,
    MicrophoneNoSignal,
    MicrophoneNotFound,
    MicrophonePermissionDenied,
)

BLOCK_S = 0.032  # one 512-sample voice-activity frame per block at 16 kHz

_PERMISSION_HINTS = ("permission", "not permitted", "access denied", "unauthorized")
_MISSING_HINTS = ("error querying device", "no default input", "no input device", "invalid device",
                  "not an input device", "device not found", "no such device")


def classify(error: BaseException) -> MicrophoneError:
    """Map a PortAudio or sounddevice failure to the status the adapter reports."""
    if isinstance(error, MicrophoneError):
        return error
    text = str(error).lower()
    if any(hint in text for hint in _PERMISSION_HINTS):
        return MicrophonePermissionDenied(str(error))
    if any(hint in text for hint in _MISSING_HINTS):
        return MicrophoneNotFound(str(error))
    return MicrophoneError(str(error))


def _to_block(samples) -> array:
    """A fresh float32 `array` from a numpy block, the adapter's fast path."""
    block = array("f")
    block.frombytes(samples.astype("float32", copy=False).tobytes())
    return block


class LinearResampler:
    """Streaming linear interpolation from a device rate to the analysis rate."""

    def __init__(self, source_rate: int, target_rate: int) -> None:
        self.step = source_rate / target_rate
        self._next = 0.0  # next output position; -1 is the previous block's last sample
        self._tail = 0.0

    def __call__(self, block):
        import numpy as np

        if not len(block):
            return block.astype(np.float32)
        last = len(block) - 1
        count = int((last - self._next) // self.step) + 1 if self._next <= last else 0
        positions = self._next + self.step * np.arange(count)
        extended = np.concatenate(([self._tail], block)).astype(np.float32)
        out = np.interp(positions + 1, np.arange(len(extended)), extended).astype(np.float32)
        self._next = (positions[-1] + self.step if count else self._next) - len(block)
        self._tail = float(block[-1])
        return out


class PortAudioSource:
    """The microphone through PortAudio (`sounddevice`), as mono float32.

    Captures at `sample_rate` when the device supports it, otherwise at the
    device's default rate with streaming resampling. A stream that stops on its
    own or stalls for `stall_s` is reported as lost; input that stays exact
    digital silence for `no_signal_s` after opening (macOS delivers that when
    microphone access is denied) is reported as `MicrophoneNoSignal`.
    """

    def __init__(self, sample_rate: int = 16_000, device: int | str | None = None, *,
                 stall_s: float = 2.0, no_signal_s: float = 2.0) -> None:
        self.sample_rate = sample_rate
        self.device = device
        self.stall_s, self.no_signal_s = stall_s, no_signal_s
        self.device_name: str | None = None
        self.device_rate: int | None = None
        self.overflows = 0  # blocks PortAudio reported as overflowed (dropped input)
        self._stream = None
        self._on_error: Callable[[MicrophoneError], None] | None = None
        self._closing = threading.Event()
        self._report_lock = threading.Lock()
        self._reported = False
        self._last_audio = 0.0
        self._signal_seen = False
        self._silent_samples = 0

    def open(self, on_audio: Callable[[Sequence[float]], None],
             on_error: Callable[[MicrophoneError], None]) -> None:
        try:
            import sounddevice as sd
        except (ImportError, OSError) as error:  # speech group or PortAudio library missing
            raise MicrophoneError(f"audio backend unavailable: {error}") from error
        self._on_error = on_error
        try:
            info = sd.query_devices(self.device, kind="input")
            self.device_name = str(info["name"])
            rate = self.sample_rate
            try:
                sd.check_input_settings(device=self.device, channels=1, dtype="float32",
                                        samplerate=rate)
            except Exception:  # the device cannot capture at the analysis rate itself
                rate = int(info["default_samplerate"])
                sd.check_input_settings(device=self.device, channels=1, dtype="float32",
                                        samplerate=rate)
            self.device_rate = rate
            resample = LinearResampler(rate, self.sample_rate) if rate != self.sample_rate else None

            def callback(indata, frames, time_info, status) -> None:
                if status.input_overflow:
                    self.overflows += 1
                mono = indata[:, 0]
                if resample is not None:
                    mono = resample(mono)
                self._check_signal(mono)
                on_audio(_to_block(mono))

            self._stream = sd.InputStream(
                samplerate=rate, channels=1, dtype="float32", device=self.device,
                blocksize=round(BLOCK_S * rate), callback=callback,
                finished_callback=lambda: self._report(MicrophoneLost("input stream stopped")))
            self._last_audio = time.monotonic()
            self._stream.start()
        except Exception as error:
            self.close()
            raise classify(error) from error
        threading.Thread(target=self._watch_stall, name="lecoach-speech-mic-watchdog",
                         daemon=True).start()

    def close(self) -> None:
        self._closing.set()
        stream, self._stream = self._stream, None
        if stream is not None:
            try:
                stream.abort(ignore_errors=True)
            finally:
                stream.close(ignore_errors=True)

    def _check_signal(self, mono) -> None:
        self._last_audio = time.monotonic()
        if self._signal_seen:
            return
        if mono.any():
            self._signal_seen = True
            return
        self._silent_samples += len(mono)
        if self._silent_samples >= self.no_signal_s * self.sample_rate:
            self._report(MicrophoneNoSignal(
                "input is digital silence: microphone access denied or the device is muted"))

    def _watch_stall(self) -> None:
        while not self._closing.wait(0.25):
            if time.monotonic() - self._last_audio > self.stall_s:
                self._report(MicrophoneLost(f"no audio for {self.stall_s} s"))
                return

    def _report(self, error: MicrophoneError) -> None:
        with self._report_lock:
            if self._reported or self._closing.is_set() or self._on_error is None:
                return
            self._reported = True
        self._on_error(error)


class WavFileSource:
    """Replay a WAV file in real time, as if it were the microphone.

    For reproducible checks of the same take across configurations or models.
    Accepts 16-bit PCM, mono or stereo, at any rate. End of file is not an error:
    the source simply stops delivering audio.
    """

    def __init__(self, path: str | Path, sample_rate: int = 16_000, *, speed: float = 1.0) -> None:
        self.path, self.sample_rate, self.speed = Path(path), sample_rate, speed
        self.device_name, self.device_rate = str(self.path), None
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def load(self):
        import numpy as np

        try:
            with wave.open(str(self.path), "rb") as file:
                if file.getsampwidth() != 2:
                    raise MicrophoneError(f"{self.path}: only 16-bit PCM WAV is supported")
                self.device_rate = file.getframerate()
                pcm = np.frombuffer(file.readframes(file.getnframes()), dtype="<i2")
                pcm = pcm.reshape(-1, file.getnchannels()).mean(axis=1)
        except (OSError, wave.Error, EOFError) as error:
            raise MicrophoneNotFound(f"{self.path}: {error}") from error
        audio = (pcm / 32768).astype(np.float32)
        if self.device_rate != self.sample_rate:
            audio = LinearResampler(self.device_rate, self.sample_rate)(audio)
        return audio

    def open(self, on_audio: Callable[[Sequence[float]], None],
             on_error: Callable[[MicrophoneError], None]) -> None:
        try:
            audio = self.load()
        except ImportError as error:
            raise MicrophoneError(f"audio backend unavailable: {error}") from error
        block = round(BLOCK_S * self.sample_rate)

        def play() -> None:
            started = time.monotonic()
            for index in range(0, len(audio), block):
                due = started + index / self.sample_rate / self.speed
                if self._stop.wait(max(0.0, due - time.monotonic())):
                    return
                on_audio(_to_block(audio[index:index + block]))

        self._thread = threading.Thread(target=play, name="lecoach-speech-wav", daemon=True)
        self._thread.start()

    def close(self) -> None:
        self._stop.set()
