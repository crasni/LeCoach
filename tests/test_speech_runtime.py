"""Real speech runtime: Silero streaming, PortAudio handling, and Whisper on audio.

Skipped unless the optional `speech` group is installed. Model tests also need
prepared weights (`python -m lecoach.speech.model --download`, or a directory in
`LECOACH_SPEECH_MODEL_DIR`); the end-to-end test also needs `espeak-ng`, which
synthesizes the English speech. No microphone is used: these are synthetic
signals, not microphone or recognition-quality evidence.
"""

import asyncio
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import time
import types
import wave
from array import array
from pathlib import Path
from unittest import IsolatedAsyncioTestCase, TestCase, mock, skipUnless

from lecoach.contracts.interfaces import Components, SessionConfig
from lecoach.runtime.clock import FakeClock
from lecoach.runtime.session import SessionController
from lecoach.speech import MicrophoneLost, MicrophoneNoSignal, MicrophoneNotFound, SpeechConfig
from lecoach.speech.adapter import SpeechAdapter
from tests.helpers import Recorder

RUNTIME = all(importlib.util.find_spec(name) for name in ("numpy", "faster_whisper"))
MODEL_DIR = os.environ.get("LECOACH_SPEECH_MODEL_DIR", "models")
MODEL = Path(MODEL_DIR) / "faster-whisper-base.en" / "model.bin"
ESPEAK = shutil.which("espeak-ng")


def config(**changes):
    return SpeechConfig(model_dir=MODEL_DIR, **changes)


@skipUnless(RUNTIME, "speech dependency group not installed")
class ResamplerTests(TestCase):
    def test_streaming_resampling_matches_a_direct_signal(self):
        import numpy as np

        from lecoach.speech.sources import LinearResampler

        t48 = np.arange(48_000) / 48_000
        source = np.sin(2 * np.pi * 220 * t48).astype(np.float32)
        resampler = LinearResampler(48_000, 16_000)
        pieces = [resampler(source[index:index + 1411]) for index in range(0, len(source), 1411)]
        out = np.concatenate(pieces)
        expected = np.sin(2 * np.pi * 220 * np.arange(len(out)) / 16_000)
        self.assertEqual(len(out), 16_000)
        self.assertLess(float(np.max(np.abs(out - expected))), 0.01)


class FakeStream:
    def __init__(self, **options):
        self.options, self.started, self.aborted, self.closed = options, 0, 0, 0

    def start(self):
        self.started += 1

    def abort(self, ignore_errors=True):
        self.aborted += 1

    def close(self, ignore_errors=True):
        self.closed += 1

    def deliver(self, block):
        status = types.SimpleNamespace(input_overflow=False)
        self.options["callback"](block.reshape(-1, 1), len(block), None, status)


def fake_sounddevice(supports_16k=True, query_error=None):
    module = types.ModuleType("sounddevice")
    module.streams = []

    def query_devices(device=None, kind=None):
        if query_error:
            raise RuntimeError(query_error)
        return {"name": "Fake Mic", "default_samplerate": 48_000.0}

    def check_input_settings(device=None, channels=None, dtype=None, samplerate=None):
        if samplerate == 16_000 and not supports_16k:
            raise RuntimeError("Invalid sample rate [PaErrorCode -9997]")

    def input_stream(**options):
        stream = FakeStream(**options)
        module.streams.append(stream)
        return stream

    module.query_devices, module.check_input_settings = query_devices, check_input_settings
    module.InputStream = input_stream
    return module


@skipUnless(RUNTIME, "speech dependency group not installed")
class PortAudioSourceTests(TestCase):
    def open_source(self, module, **options):
        from lecoach.speech.sources import PortAudioSource

        received, errors = [], []
        source = PortAudioSource(**options)
        with mock.patch.dict(sys.modules, {"sounddevice": module}):
            source.open(received.append, errors.append)
        self.addCleanup(source.close)
        return source, received, errors

    def test_opens_a_mono_16k_stream_and_hands_over_float_arrays(self):
        import numpy as np

        module = fake_sounddevice()
        source, received, errors = self.open_source(module)
        stream = module.streams[0]
        self.assertEqual((stream.options["samplerate"], stream.options["channels"],
                          stream.options["blocksize"], stream.started), (16_000, 1, 512, 1))
        stream.deliver(np.full(512, 0.25, dtype=np.float32))
        self.assertEqual((type(received[0]), received[0].typecode, len(received[0])),
                         (array, "f", 512))
        self.assertEqual((received[0][0], errors), (0.25, []))
        source.close()
        source.close()
        self.assertEqual((stream.aborted, stream.closed), (1, 1))

    def test_resamples_when_the_device_cannot_capture_at_16k(self):
        import numpy as np

        module = fake_sounddevice(supports_16k=False)
        source, received, _ = self.open_source(module)
        stream = module.streams[0]
        self.assertEqual((stream.options["samplerate"], source.device_rate), (48_000, 48_000))
        stream.deliver(np.full(1536, 0.5, dtype=np.float32))
        self.assertEqual(len(received[0]), 512)

    def test_device_problems_become_microphone_errors(self):
        with self.assertRaises(MicrophoneNotFound):
            self.open_source(fake_sounddevice(query_error="Error querying device -1"))

    def test_a_stream_that_stops_on_its_own_is_lost(self):
        module = fake_sounddevice()
        _, _, errors = self.open_source(module)
        module.streams[0].options["finished_callback"]()
        self.assertEqual([type(error) for error in errors], [MicrophoneLost])

    def test_digital_silence_and_stalls_are_reported_once(self):
        import numpy as np

        module = fake_sounddevice()
        _, _, errors = self.open_source(module, no_signal_s=0.1, stall_s=0.3)
        for _ in range(5):
            module.streams[0].deliver(np.zeros(512, dtype=np.float32))
        time.sleep(0.8)  # the watchdog would also report the stall; only one report is sent
        self.assertEqual([type(error) for error in errors], [MicrophoneNoSignal])


@skipUnless(RUNTIME, "speech dependency group not installed")
class SileroSegmenterTests(TestCase):
    def test_streaming_matches_batch_probabilities_and_silence_has_no_speech(self):
        import numpy as np

        from lecoach.speech.vad import FRAME, SileroSegmenter, shared_silero_model

        rng = np.random.default_rng(0)
        audio = (0.05 * rng.standard_normal(FRAME * 60)).astype(np.float32)
        batch = shared_silero_model()(audio)
        segmenter = SileroSegmenter(config())
        streamed = []
        segmenter.gate.feed = lambda start, probability: streamed.append(probability) or []
        position = 0
        for size in (100, 900, 3000, 512, 26208):
            chunk = audio[position:position + size]
            segmenter.process(array("f", chunk.tobytes()), position)
            position += size
        self.assertEqual(len(streamed), 60)
        self.assertLess(float(np.max(np.abs(np.array(streamed) - batch))), 1e-5)
        silent = SileroSegmenter(config())
        self.assertEqual(silent.process(array("f", bytes(4 * 16_000)), 0), [])
        self.assertEqual(silent.flush(16_000), [])


def synthesize(text: str, directory: str) -> Path:
    path = Path(directory) / "speech.wav"
    subprocess.run([ESPEAK, "-v", "en-us", "-s", "150", "-w", str(path), text], check=True)
    return path


def load_audio(path: Path):
    import numpy as np

    from lecoach.speech.sources import LinearResampler

    with wave.open(str(path), "rb") as file:
        rate = file.getframerate()
        pcm = np.frombuffer(file.readframes(file.getnframes()), dtype="<i2")
    return LinearResampler(rate, 16_000)((pcm / 32768).astype(np.float32))


@skipUnless(RUNTIME and MODEL.is_file(), "speech runtime or prepared model missing")
class WhisperRuntimeTests(TestCase):
    def test_generated_silence_gives_an_empty_final(self):
        from lecoach.speech.whisper import load_transcriber

        result = load_transcriber(config()).transcribe(array("f", bytes(4 * 32_000)), 16_000, True)
        self.assertEqual((result.text, result.words), ("", ()))

    @skipUnless(ESPEAK, "espeak-ng not installed")
    def test_synthesized_english_is_transcribed_with_word_times(self):
        from lecoach.speech.whisper import load_transcriber

        with tempfile.TemporaryDirectory() as directory:
            audio = load_audio(synthesize("Hello everyone. Today I want to show you our project.",
                                          directory))
        result = load_transcriber(config()).transcribe(array("f", audio.tobytes()), 16_000, True)
        self.assertIn("hello everyone", result.text.lower())
        self.assertIn("project", result.text.lower())
        self.assertTrue(result.words)
        self.assertLessEqual(result.words[-1].end_s, len(audio) / 16_000 + 0.5)


class ArraySource:
    """Hands over prepared audio when the test pushes it, like a device would."""

    sample_rate = 16_000

    def __init__(self, audio):
        self.audio, self.position, self.closed = audio, 0, 0

    def open(self, on_audio, on_error):
        self.on_audio = on_audio

    def close(self):
        self.closed += 1

    def push(self, until_s: float):
        target = min(len(self.audio), round(until_s * 16_000))
        while self.position < target:
            block = self.audio[self.position:min(self.position + 512, target)]
            self.on_audio(array("f", block.tobytes()))
            self.position += len(block)


@skipUnless(RUNTIME and MODEL.is_file() and ESPEAK, "speech runtime, model or espeak-ng missing")
class EndToEndTests(IsolatedAsyncioTestCase):
    async def test_synthesized_talk_produces_checked_speech_events(self):
        import faster_whisper.transcribe
        import faster_whisper.utils
        import numpy as np

        from lecoach.speech.vad import SileroSegmenter
        from lecoach.speech.whisper import load_transcriber
        from tests.test_speech_pipeline import CHECKER

        with tempfile.TemporaryDirectory() as directory:
            first = load_audio(synthesize("Hello everyone. Um, today I want to show you how our "
                                          "team built a faster way to practice talks.", directory))
            second = load_audio(synthesize("Thank you for listening.", directory))
        silence = np.zeros(16_000, dtype=np.float32)
        audio = np.concatenate([silence, first, silence, silence, second, silence, silence])
        source = ArraySource(audio)
        # Audio is pushed faster than real time, so windows wait for real finals
        # instead of timing out on the default 3 s coverage wait.
        settings = config(coverage_wait_s=30.0)
        adapter = SpeechAdapter(settings, source, SileroSegmenter(settings),
                                load_transcriber(settings), idle_tick_s=0.01)
        recorder, clock = Recorder(), FakeClock()
        controller = SessionController(
            SessionConfig(mode="live", drain_timeout_s=30.0), Components(speech=adapter,
                                                                       recorder=recorder),
            session_id="speech-e2e", clock=clock)
        no_download = AssertionError("start and capture must not download")
        with mock.patch.object(faster_whisper.utils, "download_model", side_effect=no_download), \
                mock.patch.object(faster_whisper.transcribe, "download_model",
                                  side_effect=no_download):
            await controller.start()
            end_s = len(audio) / 16_000
            step = 0.0
            while step < end_s:
                step = min(end_s, step + 0.5)
                clock.advance_to(step)
                source.push(step)
                deadline = time.monotonic() + 30
                while adapter.analyzed_s < step - 0.04 and time.monotonic() < deadline:
                    await asyncio.sleep(0.005)
            await controller.stop()
        self.assertEqual(controller.incomplete_sources, [])
        finals = [event.payload for event in recorder.events
                  if event.type == "speech.transcript" and event.payload.is_final]
        texts = " ".join(payload.text.lower() for payload in finals)
        self.assertIn("hello everyone", texts)
        self.assertIn("thank you for listening", texts)
        windows = [event.payload for event in recorder.events if event.type == "speech.metrics"]
        self.assertTrue(any(payload.wpm for payload in windows))
        self.assertTrue(any(payload.pause.state == "completed" for payload in windows))
        self.assertEqual((adapter.errors, source.closed), ([], 1))
        stream = [event.model_dump(mode="json") for event in recorder.events]
        CHECKER.check_stream(stream, {"min_observation_s": settings.min_observation_s,
                                      "pause_min_s": settings.pause_min_s})
