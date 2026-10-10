"""Production speech seams without the optional runtime: decisions, errors, fakes.

These run in the core environment. `tests/test_speech_runtime.py` exercises the
real Silero, faster-whisper, and PortAudio code when the `speech` group exists.
"""

import asyncio
import os
import sys
import tempfile
import types
from pathlib import Path
from unittest import IsolatedAsyncioTestCase, TestCase, mock

from lecoach.contracts.interfaces import Components, SessionConfig
from lecoach.runtime.clock import FakeClock
from lecoach.runtime.session import SessionController
from lecoach.speech import (
    MicrophoneError,
    MicrophoneNotFound,
    MicrophonePermissionDenied,
    SpeechConfig,
    whisper,
)
from lecoach.speech import model as model_cli
from lecoach.speech.local import DEVICE_VARIABLE, build_local_adapter
from lecoach.speech.probe import describe, summarize
from lecoach.speech.seams import Boundary
from lecoach.speech.sources import PortAudioSource, classify
from lecoach.speech.vad import FRAME, SpeechGate
from tests.helpers import Recorder

RATE = 16_000


def gate(**options):
    return SpeechGate(SpeechConfig(), **options)


def feed(speech_gate, probabilities, first=0):
    boundaries = []
    for index, probability in enumerate(probabilities):
        boundaries += speech_gate.feed(first + index * FRAME, probability)
    return boundaries


class SpeechGateTests(TestCase):
    def test_start_is_padded_and_end_follows_the_minimum_silence(self):
        speech_gate = gate(min_silence_s=0.1, pad_s=0.05)  # 3 silent frames end a segment
        boundaries = feed(speech_gate, [0.1] * 10 + [0.9] * 20 + [0.1] * 5)
        pad = round(0.05 * RATE)
        self.assertEqual(boundaries, [Boundary("start", 10 * FRAME - pad),
                                      Boundary("end", 30 * FRAME + pad)])

    def test_hysteresis_keeps_speech_between_the_thresholds(self):
        speech_gate = gate(min_silence_s=0.1, pad_s=0.0)
        boundaries = feed(speech_gate, [0.9] * 5 + [0.4] * 20 + [0.9] * 5)
        self.assertEqual(boundaries, [Boundary("start", 0)])  # 0.4 is above 0.35
        self.assertEqual(speech_gate.flush(40 * FRAME), [Boundary("end", 40 * FRAME)])
        self.assertEqual(speech_gate.flush(41 * FRAME), [])

    def test_short_dips_do_not_end_speech(self):
        speech_gate = gate(min_silence_s=0.5, pad_s=0.0)  # 16 frames
        boundaries = feed(speech_gate, [0.9] * 5 + [0.1] * 10 + [0.9] * 5 + [0.1] * 16)
        self.assertEqual(boundaries, [Boundary("start", 0), Boundary("end", 20 * FRAME)])

    def test_a_new_start_never_precedes_the_previous_end(self):
        speech_gate = gate(min_silence_s=0.1, pad_s=0.2)
        boundaries = feed(speech_gate, [0.9] * 5 + [0.1] * 3 + [0.9] * 3)
        end = boundaries[1].frame
        self.assertEqual(boundaries[2], Boundary("start", end))

    def test_long_speech_splits_at_the_quietest_recent_frame(self):
        speech_gate = gate(pad_s=0.0)
        probabilities = [0.9] * 250
        probabilities[200] = 0.36  # quietest frame inside the last 2 s before 8 s
        boundaries = feed(speech_gate, probabilities)
        cut = 200 * FRAME + FRAME // 2
        self.assertEqual(boundaries, [Boundary("start", 0), Boundary("end", cut),
                                      Boundary("start", cut)])
        self.assertLess(cut, 8 * RATE)  # before the adapter's own backstop


class ErrorMappingTests(TestCase):
    def test_portaudio_messages_map_to_specific_reasons(self):
        cases = {
            "Error querying device -1": MicrophoneNotFound,
            "Error querying device 99": MicrophoneNotFound,
            "No input device matching 'USB'": MicrophoneNotFound,
            "Not an input device: 'Speakers (Realtek(R) Audio)'": MicrophoneNotFound,
            "Multiple input devices found for 'usb':\n[1] USB, MME\n[7] USB, Windows WASAPI":
                MicrophoneError,
            "Invalid device [PaErrorCode -9996]": MicrophoneNotFound,
            "Error opening InputStream: Permission denied": MicrophonePermissionDenied,
            "Error opening InputStream: Device unavailable [PaErrorCode -9985]": MicrophoneError,
        }
        for message, expected in cases.items():
            with self.subTest(message=message):
                self.assertIs(type(classify(RuntimeError(message))), expected)

    def test_missing_audio_backend_is_reported_not_raised_raw(self):
        with mock.patch.dict(sys.modules, {"sounddevice": None}):
            with self.assertRaises(MicrophoneError) as raised:
                PortAudioSource().open(lambda samples: None, lambda error: None)
        self.assertEqual(raised.exception.reason, "microphone_unavailable")


def segment(text, no_speech=0.1, words=()):
    return types.SimpleNamespace(text=text, no_speech_prob=no_speech, words=list(words))


def word(text, start, end):
    return types.SimpleNamespace(word=text, start=start, end=end)


class TranscriptionMappingTests(TestCase):
    def test_finals_keep_word_times_and_drop_non_speech_segments(self):
        result = whisper.to_transcription(
            [segment(" Hello everyone,", words=[word(" Hello", 0.0, 0.2),
                                                 word(" everyone,", 0.2, 0.7)]),
             segment(" You", no_speech=0.81, words=[word(" You", 1.0, 1.2)]),
             segment(" um, today.", words=[word(" um,", 1.3, 1.6), word(" today.", 1.9, 2.1)])],
            "en", words=True)
        self.assertEqual(result.text, "Hello everyone, um, today.")
        self.assertEqual([(w.text, w.end_s) for w in result.words],
                         [(" Hello", 0.2), (" everyone,", 0.7), (" um,", 1.6), (" today.", 2.1)])
        self.assertEqual(result.language, "en")

    def test_partials_carry_text_only_and_silence_gives_an_empty_final(self):
        partial = whisper.to_transcription([segment(" Hello", words=[word(" Hello", 0, 1)])],
                                           "en", words=False)
        self.assertEqual((partial.text, partial.words), ("Hello", ()))
        silent = whisper.to_transcription([segment(" You", no_speech=0.81)], "en", words=True)
        self.assertEqual((silent.text, silent.words), ("", ()))


class ModelProviderTests(TestCase):
    def setUp(self):
        self.addCleanup(whisper._TRANSCRIBERS.clear)
        self.directory = Path(tempfile.mkdtemp())

    def test_a_missing_model_is_unavailable_and_never_downloaded(self):
        config = SpeechConfig(model_dir=str(self.directory))
        with self.assertRaises(whisper.ModelUnavailable) as raised:
            whisper.load_transcriber(config)
        self.assertIn("--download", str(raised.exception))
        self.assertIsNone(whisper.get_transcriber(config))

    def test_the_model_loads_once_from_local_files_only(self):
        config = SpeechConfig(model_dir=str(self.directory))
        path = whisper.model_path(config)
        path.mkdir(parents=True)
        (path / "model.bin").write_bytes(b"")
        calls = []
        fake = types.ModuleType("faster_whisper")
        fake.WhisperModel = lambda *args, **kwargs: calls.append((args, kwargs)) or object()
        with mock.patch.dict(sys.modules, {"faster_whisper": fake}):
            first = whisper.load_transcriber(config)
            second = whisper.load_transcriber(config)
        self.assertIs(first, second)
        self.assertEqual(calls, [((str(path),), {"device": "cpu", "compute_type": "int8",
                                                 "local_files_only": True})])

    def test_download_command_targets_the_ignored_models_directory(self):
        calls = []
        utils = types.ModuleType("faster_whisper.utils")
        utils.download_model = lambda name, output_dir: calls.append((name, output_dir)) or "ok"
        with mock.patch.dict(sys.modules, {"faster_whisper": types.ModuleType("faster_whisper"),
                                           "faster_whisper.utils": utils}):
            code = model_cli.main(["--download", "--model-dir", str(self.directory)])
        self.assertEqual(code, 0)
        self.assertEqual(calls, [("base.en", str(self.directory / "faster-whisper-base.en"))])

    def test_the_command_requires_an_action(self):
        with self.assertRaises(SystemExit):
            model_cli.main([])


class LocalCompositionTests(IsolatedAsyncioTestCase):
    async def test_missing_runtime_degrades_with_a_status_instead_of_failing(self):
        config = SpeechConfig(model_dir=tempfile.mkdtemp())
        # Block every optional package: a real first import inside patch.dict would be
        # removed again on exit, and numpy cannot be initialized twice in one process.
        missing = dict.fromkeys(("faster_whisper", "sounddevice", "numpy", "onnxruntime"))
        with mock.patch.dict(sys.modules, missing):
            adapter = build_local_adapter(config)
        recorder = Recorder()
        controller = SessionController(SessionConfig(mode="live"),
                                       Components(speech=adapter, recorder=recorder),
                                       clock=FakeClock())
        await controller.start()
        await controller.stop()
        statuses = [(event.payload.availability, event.payload.reason)
                    for event in recorder.events
                    if event.source == "speech" and event.type == "signal.status"]
        self.assertEqual(statuses, [("error", "speech_model_unavailable")])
        await asyncio.sleep(0)


class DeviceSelectionTests(TestCase):
    def device(self, value, **options):
        with mock.patch.dict(os.environ), \
                mock.patch("lecoach.speech.local.SileroSegmenter", return_value=None):
            os.environ.pop(DEVICE_VARIABLE, None)
            if value is not None:
                os.environ[DEVICE_VARIABLE] = value
            return build_local_adapter(SpeechConfig(), transcriber=None, **options).source.device

    def test_the_variable_names_the_microphone_by_index_or_name(self):
        self.assertIsNone(self.device(None))
        self.assertIsNone(self.device("  "))
        self.assertEqual(self.device("3"), 3)
        self.assertEqual(self.device(" USB MME "), "USB MME")

    def test_an_explicit_device_overrides_the_variable(self):
        self.assertEqual(self.device("3", device=5), 5)
        self.assertEqual(self.device("3", device="Headset"), "Headset")


class ProbeHelperTests(TestCase):
    def test_latency_summary(self):
        self.assertIsNone(summarize([]))
        self.assertEqual(summarize([0.5, 1.5, 1.0]),
                         {"count": 3, "median_s": 1.0, "p95_s": 1.5, "max_s": 1.5})

    def test_descriptions_ignore_partials(self):
        partial = types.SimpleNamespace(type="speech.transcript", payload=types.SimpleNamespace(
            is_final=False))
        self.assertIsNone(describe(partial))
