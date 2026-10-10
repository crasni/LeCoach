"""Streaming voice activity detection.

`SpeechGate` turns per-frame speech probabilities into segment boundaries in
plain Python. `SileroSegmenter` computes those probabilities with the Silero
model bundled in faster-whisper. It carries the model state and frame context
across chunks, so streaming matches whole-file processing exactly.
"""

import threading
from array import array
from collections import deque

from .config import SpeechConfig
from .seams import Boundary

FRAME = 512  # Silero frame at 16 kHz (32 ms)
_CONTEXT = 64  # samples of the previous frame the model sees with each frame


class SpeechGate:
    """Hysteresis over frame probabilities, with padding and bounded segment length.

    Speech starts at a frame scoring at least `threshold`, padded back by `pad_s`
    but never before the previous segment's end. It ends `pad_s` after the first
    of `min_silence_s` of frames scoring below the lower threshold. A segment
    about to reach `max_utterance_s` is split at its quietest frame in the last
    `split_window_s`, before the adapter's own length backstop.
    """

    def __init__(self, config: SpeechConfig, *, frame: int = FRAME, threshold: float = 0.5,
                 neg_threshold: float | None = None, min_silence_s: float = 0.5,
                 pad_s: float = 0.1, split_window_s: float = 2.0) -> None:
        rate = config.sample_rate
        self.frame = frame
        self.threshold = threshold
        self.neg_threshold = (max(threshold - 0.15, 0.01) if neg_threshold is None
                              else neg_threshold)
        self.min_silence = max(1, round(min_silence_s * rate / frame))
        self.pad = round(pad_s * rate)
        self.max_length = round(config.max_utterance_s * rate) - frame
        self.split_window = round(split_window_s * rate)
        self._open = False
        self._start = self._last_end = 0
        self._silence_run = self._silence_start = 0
        self._recent: deque[tuple[int, float]] = deque()

    def feed(self, frame_start: int, probability: float) -> list[Boundary]:
        boundaries: list[Boundary] = []
        if not self._open:
            if probability < self.threshold:
                return boundaries
            self._open, self._silence_run = True, 0
            self._start = max(frame_start - self.pad, self._last_end, 0)
            self._recent.clear()
            boundaries.append(Boundary("start", self._start))
        frame_end = frame_start + self.frame
        if probability < self.neg_threshold:
            if not self._silence_run:
                self._silence_start = frame_start
            self._silence_run += 1
            if self._silence_run >= self.min_silence:
                return boundaries + self._close(min(self._silence_start + self.pad, frame_end))
        else:
            self._silence_run = 0
        self._recent.append((frame_start, probability))
        while self._recent[0][0] < frame_end - self.split_window:
            self._recent.popleft()
        if frame_end - self._start >= self.max_length:
            boundaries += self._split(frame_end)
        return boundaries

    def flush(self, end_frame: int) -> list[Boundary]:
        return self._close(end_frame) if self._open else []

    def _close(self, end: int) -> list[Boundary]:
        end = max(end, self._start)
        self._open, self._silence_run, self._last_end = False, 0, end
        return [Boundary("end", end)]

    def _split(self, frame_end: int) -> list[Boundary]:
        candidates = [(probability, start) for start, probability in self._recent
                      if start > self._start]
        cut = min(candidates)[1] + self.frame // 2 if candidates else frame_end
        cut = min(max(cut, self._start + 1), frame_end)
        self._start = cut
        self._recent = deque(item for item in self._recent if item[0] >= cut)
        return [Boundary("end", cut), Boundary("start", cut)]


_SHARED_MODEL = None
_SHARED_LOCK = threading.Lock()


def shared_silero_model():
    """faster-whisper's bundled Silero model, loaded once per process."""
    global _SHARED_MODEL
    with _SHARED_LOCK:
        if _SHARED_MODEL is None:
            from faster_whisper.vad import get_vad_model

            _SHARED_MODEL = get_vad_model()
        return _SHARED_MODEL


class SileroSegmenter:
    """The `Segmenter` seam on Silero probabilities; one instance per session."""

    def __init__(self, config: SpeechConfig, *, model=None, **gate_options) -> None:
        if config.sample_rate != 16_000:
            raise ValueError("Silero voice activity detection here expects 16 kHz audio")
        import numpy as np

        self._np = np
        self.gate = SpeechGate(config, **gate_options)
        self._session = (model or shared_silero_model()).session
        self._pending = np.zeros(0, dtype=np.float32)
        self._pending_start: int | None = None
        self._h = np.zeros((1, 1, 128), dtype=np.float32)
        self._c = np.zeros((1, 1, 128), dtype=np.float32)
        self._context = np.zeros(_CONTEXT, dtype=np.float32)

    def process(self, samples, first_frame: int) -> list[Boundary]:
        np = self._np
        if isinstance(samples, array):
            chunk = np.frombuffer(samples, dtype=np.float32)
        else:
            chunk = np.asarray(samples, dtype=np.float32)
        if self._pending_start is None or first_frame != self._pending_start + len(self._pending):
            self._pending, self._pending_start = chunk.copy(), first_frame  # not contiguous
        else:
            self._pending = np.concatenate((self._pending, chunk))
        count = len(self._pending) // FRAME
        if not count:
            return []
        frames = self._pending[:count * FRAME].reshape(count, FRAME)
        boundaries: list[Boundary] = []
        for index, probability in enumerate(self._probabilities(frames)):
            boundaries += self.gate.feed(self._pending_start + index * FRAME, float(probability))
        self._pending = self._pending[count * FRAME:]
        self._pending_start += count * FRAME
        return boundaries

    def flush(self, end_frame: int) -> list[Boundary]:
        return self.gate.flush(end_frame)

    def _probabilities(self, frames):
        np = self._np
        contexts = np.concatenate((self._context[None, :], frames[:-1, -_CONTEXT:]), axis=0)
        batch = np.concatenate((contexts, frames), axis=1)
        probabilities, self._h, self._c = self._session.run(
            None, {"input": batch, "h": self._h, "c": self._c})
        self._context = frames[-1, -_CONTEXT:].copy()
        return probabilities
