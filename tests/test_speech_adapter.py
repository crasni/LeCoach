"""SpeechAdapter lifecycle, degraded mode, and release through the session controller.

Scripted seams stand in for the microphone, voice activity detection, and the
model; worker threads, event-loop marshaling, and the controller are real.
"""

import asyncio
import subprocess
import sys
import threading
import time
from unittest import IsolatedAsyncioTestCase, TestCase

from lecoach.contracts import parse_event
from lecoach.contracts.interfaces import Components, SessionConfig, SessionContext
from lecoach.runtime.clock import FakeClock
from lecoach.runtime.session import SessionController, SessionManager
from lecoach.speech import (
    MicrophoneError,
    MicrophoneNotFound,
    MicrophonePermissionDenied,
    SpeechAdapter,
    SpeechConfig,
)
from tests.helpers import Recorder
from tests.speech_doubles import RATE, ScriptedSegmenter, ScriptedSource, ScriptedTranscriber
from tests.test_speech_pipeline import CHECKER

CONFIG = SpeechConfig()  # window 10 s, hop 1 s, minimum observation 5 s, pause 1 s, wait 3 s


async def until(predicate, timeout_s=3.0):
    deadline = time.monotonic() + timeout_s
    while not predicate():
        if time.monotonic() > deadline:
            raise AssertionError("condition not reached in time")
        await asyncio.sleep(0.005)


class RecordingController(SessionController):
    """Records which threads emitted and every emission the controller rejected."""

    def __init__(self, *args, **kwargs):
        self.rejected, self.threads = [], set()
        super().__init__(*args, **kwargs)

    def emit(self, value):
        self.threads.add(threading.current_thread().name)
        accepted = super().emit(value)
        if not accepted:
            self.rejected.append(value)
        return accepted


class SpeechAdapterSessionTests(IsolatedAsyncioTestCase):
    def session(self, intervals=(), finals=(), *, source=None, segmenter=None,
                transcriber=None, drain_timeout_s=1.0, **options):
        self.clock = FakeClock()
        self.source = source or ScriptedSource()
        self.segmenter = segmenter or ScriptedSegmenter(intervals)
        self.transcriber = transcriber or ScriptedTranscriber(finals)
        self.adapter = SpeechAdapter(CONFIG, self.source, self.segmenter, self.transcriber,
                                     idle_tick_s=0.01, **options)
        self.recorder = Recorder()
        self.controller = RecordingController(
            SessionConfig(mode="live", startup_timeout_s=1.0, drain_timeout_s=drain_timeout_s),
            Components(speech=self.adapter, recorder=self.recorder),
            session_id="speech-live",
            clock=self.clock,
        )
        return self.controller

    async def asyncTearDown(self):
        adapter = getattr(self, "adapter", None)
        for thread in adapter._threads if adapter else ():
            thread.join(5)

    async def run_to(self, seconds, step_s=2.0):
        """Advance the clock and deliver audio to it in steps, as a live device would,
        waiting for segmentation after each step (a single burst could overflow)."""
        while self.source.delivered < round(seconds * RATE):
            reached = min(seconds, self.source.delivered / RATE + step_s)
            self.clock.advance_to(max(reached, self.clock.now()))
            self.source.push(reached)
            await until(lambda: self.adapter.analyzed_s >= reached)

    def speech(self, kind=None):
        return [event for event in self.recorder.events
                if event.source == "speech" and kind in (None, event.type)]

    def finals(self):
        return {event.payload.utterance_id: (event.payload.start_s, event.payload.end_s,
                                             event.payload.text)
                for event in self.speech("speech.transcript") if event.payload.is_final}

    def windows(self):
        return {event.event_id: event.payload for event in self.speech("speech.metrics")}

    def statuses(self):
        return [(event.timestamp_s, event.payload.availability, event.payload.reason)
                for event in self.speech("signal.status")]

    def assert_consistent(self):
        """Capture-end bound, no rejected emissions, and the shared producer checks."""
        self.assertEqual(self.controller.phase, "completed")
        self.assertEqual(self.controller.threads, {threading.main_thread().name})
        self.assertEqual(self.controller.rejected, [])
        self.assertEqual(self.adapter.errors, [])
        end = self.controller.capture_end_s
        self.assertTrue(all(event.timestamp_s <= end for event in self.speech()))
        stream = [event.model_dump(mode="json") for event in self.recorder.events]
        CHECKER.check_stream(stream, {"min_observation_s": CONFIG.min_observation_s,
                                      "pause_min_s": CONFIG.pause_min_s})

    async def test_observations_carry_capture_times_from_sample_offsets(self):
        controller = self.session([(1.0, 2.5), (4.0, 6.2)],
                                  ["hello there everyone", "um so we begin"])
        began = time.perf_counter()
        await controller.start()
        self.assertLess(time.perf_counter() - began, controller.config.startup_timeout_s)
        self.assertEqual((self.source.opened, self.transcriber.calls), (1, 0))
        await self.run_to(7.0)
        await controller.stop()
        self.assertEqual(self.finals(), {"u1": (1.0, 2.5, "hello there everyone"),
                                         "u2": (4.0, 6.2, "um so we begin")})
        windows = self.windows()
        self.assertEqual(list(windows), ["pause-4", "metrics-7"])
        self.assertEqual(windows["pause-4"].pause.model_dump(),
                         {"state": "completed", "duration_s": 1.5, "start_s": 2.5, "end_s": 4.0})
        self.assertEqual((windows["metrics-7"].wpm, windows["metrics-7"].filler_count),
                         (51.4, 1))
        self.assertEqual(self.transcriber.thread_names, {"lecoach-speech-asr"})
        self.assertEqual((self.source.opened, self.source.closed), (1, 1))
        self.assert_consistent()

    async def test_long_speech_is_split_at_the_maximum_utterance_length(self):
        controller = self.session([(1.0, 20.0)], ["first part", "second part", "third part"])
        await controller.start()
        await self.run_to(21.0)
        await controller.stop()
        self.assertEqual(self.finals(), {"u1": (1.0, 9.0, "first part"),
                                         "u2": (9.0, 17.0, "second part"),
                                         "u3": (17.0, 20.0, "third part")})
        self.assertEqual(list(self.windows()), ["metrics-9", "metrics-17", "metrics-21"])
        self.assert_consistent()

    async def test_capture_time_starts_at_the_clock_and_ignores_inference_delay(self):
        clock, emitted = FakeClock(), []
        clock.advance_to(3.0)
        source, gate = ScriptedSource(), threading.Event()
        adapter = SpeechAdapter(CONFIG, source, ScriptedSegmenter([(1.0, 2.0)]),
                                ScriptedTranscriber(["late but placed"], gate=gate))
        self.adapter = adapter
        context = SessionContext("origin", clock, lambda event: emitted.append(
            parse_event(event)) or True, SessionConfig(mode="live"))
        await adapter.start(context)
        clock.advance_to(6.0)
        source.push(3.0)  # three seconds of audio after a start at 3.0 s
        await until(lambda: adapter.analyzed_s >= 6.0)
        clock.advance_to(8.0)  # transcription completes two seconds after speech ended
        gate.set()
        await adapter.stop_capture(8.0)
        await adapter.drain()
        final = next(event for event in emitted
                     if event.type == "speech.transcript" and event.payload.is_final)
        self.assertEqual((final.payload.start_s, final.payload.end_s, final.timestamp_s),
                         (4.0, 5.0, 5.0))
        self.assertTrue(all(event.timestamp_s <= 8.0 for event in emitted))

    async def test_speech_in_progress_is_cut_at_capture_end(self):
        controller = self.session([(1.0, 9.0)], ["we keep talking past the stop"])
        await controller.start()
        await self.run_to(6.0)
        self.clock.advance_to(6.0006)  # rounding to 6.001 would land after capture end
        await controller.stop()
        self.source.push(7.0)  # a late device buffer after stop is ignored
        self.assertEqual(self.finals(), {"u1": (1.0, 6.0, "we keep talking past the stop")})
        self.assertEqual(list(self.windows()), ["metrics-6"])
        self.assertIsNotNone(self.windows()["metrics-6"].wpm)
        self.assertEqual((self.source.opened, self.source.closed), (1, 1))
        self.assert_consistent()

    async def test_audio_ahead_of_the_clock_is_not_stamped_ahead_of_it(self):
        controller = self.session([(1.0, 6.3)], ["the audio clock runs fast"])
        await controller.start()
        await self.run_to(6.0)
        self.source.push(6.5)  # drift: the utterance ends at 6.3 s of audio, clock 6.0 s
        await until(lambda: "u1" in self.finals())
        await controller.stop()
        self.assertEqual(self.finals(), {"u1": (1.0, 6.0, "the audio clock runs fast")})
        self.assertEqual(list(self.windows()), ["metrics-6"])
        self.assert_consistent()

    async def test_model_not_ready_reports_error_and_null_windows(self):
        controller = self.session(transcriber=ScriptedTranscriber([], ready=False))
        await controller.start()
        self.clock.advance_to(6.0)
        await until(lambda: "metrics-6" in self.windows())  # emitted while running
        await controller.stop()
        self.assertEqual(self.statuses(), [(0.0, "error", "speech_model_unavailable")])
        self.assertEqual(self.source.opened, 0)
        self.assertEqual(list(self.windows()), ["metrics-5", "metrics-6"])
        for payload in self.windows().values():
            self.assertEqual((payload.availability, payload.wpm, payload.filler_count,
                              payload.pause.state), ("error", None, None, "unknown"))
        self.assert_consistent()

    async def test_microphone_failures_at_start_report_specific_reasons(self):
        cases = [
            (ScriptedSource(fail=MicrophonePermissionDenied()), "microphone_permission_denied"),
            (ScriptedSource(fail=MicrophoneNotFound()), "microphone_not_found"),
            (ScriptedSource(fail=MicrophoneError()), "microphone_unavailable"),
            (None, "microphone_not_found"),
        ]
        for source, reason in cases:
            with self.subTest(reason=reason, source=source):
                controller = self.session(source=source)
                self.adapter.source = source  # None: no input device configured
                await controller.start()
                self.clock.advance_to(5.0)
                await controller.stop()
                self.assertEqual(self.statuses(), [(0.0, "unavailable", reason)])
                self.assertEqual(self.windows()["metrics-5"].availability, "unavailable")
                self.assertIsNone(self.windows()["metrics-5"].wpm)
                if source is not None:  # released once, never reopened
                    self.assertEqual((source.opened, source.closed), (1, 1))
                self.assert_consistent()

    async def test_unexpected_start_error_is_left_to_the_controller(self):
        source = ScriptedSource(fail=RuntimeError("driver crashed"))
        controller = self.session(source=source)
        await controller.start()
        self.clock.advance_to(5.0)
        await controller.stop()
        self.assertEqual([event.payload.reason for event in self.speech()],
                         ["adapter_start_failed"])
        self.assertEqual((source.opened, source.closed), (1, 1))
        self.assert_consistent()

    async def test_segmenter_failure_closes_the_utterance_without_counting_it(self):
        class FailingSegmenter(ScriptedSegmenter):
            def process(self, samples, first_frame):
                if first_frame >= 3 * 16_000:
                    raise RuntimeError("voice activity model crashed")
                return super().process(samples, first_frame)

        controller = self.session(segmenter=FailingSegmenter([(1.0, 9.0)]),
                                  finals=["never transcribed"])
        await controller.start()
        self.clock.advance_to(4.0)
        self.source.push(4.0)
        await until(lambda: self.statuses())
        await controller.stop()
        self.assertEqual(self.statuses(), [(3.0, "error", "speech_segmentation_failed")])
        self.assertEqual(self.finals(), {"u1": (1.0, 3.0, "")})
        self.assertEqual(self.windows()["metrics-4"].availability, "error")
        self.assertEqual((self.source.opened, self.source.closed), (1, 1))
        self.assert_consistent()

    async def test_device_lost_mid_utterance_finalizes_and_degrades(self):
        controller = self.session([(1.0, 9.0)], ["cut off mid sentence"])
        await controller.start()
        await self.run_to(4.0)
        self.source.lose()
        await until(lambda: self.statuses())
        self.clock.advance_to(8.0)
        await until(lambda: "metrics-8" in self.windows())
        await controller.stop()
        self.assertEqual(self.statuses(), [(4.0, "error", "microphone_disconnected")])
        self.assertEqual(self.finals(), {"u1": (1.0, 4.0, "cut off mid sentence")})
        self.assertEqual(list(self.windows()), ["metrics-5", "metrics-6", "metrics-7", "metrics-8"])
        self.assertTrue(all(payload.availability == "error" and payload.wpm is None
                            for payload in self.windows().values()))
        self.assertEqual((self.source.opened, self.source.closed), (1, 1))
        self.assert_consistent()

    async def test_audio_queue_overflow_closes_the_utterance_and_degrades(self):
        gate = threading.Event()
        controller = self.session(segmenter=ScriptedSegmenter([(0.05, 3.0)], gate=gate),
                                  finals=["overflowing speech"], max_backlog_chunks=5)
        await controller.start()
        self.clock.advance_to(2.0)
        self.source.push(0.1)
        await until(lambda: self.segmenter.calls)  # segmentation is now blocked
        self.source.push(2.0)  # nineteen more chunks queue up behind it
        gate.set()
        await until(lambda: self.statuses())
        await controller.stop()
        self.assertEqual(self.statuses(), [(0.1, "error", "audio_queue_overflow")])
        self.assertEqual(self.finals(), {"u1": (0.05, 0.1, "overflowing speech")})
        self.assertEqual(self.windows()["metrics-2"].availability, "error")
        self.assertEqual((self.source.opened, self.source.closed), (1, 1))
        self.assert_consistent()

    async def test_transcription_failure_reports_error_without_counting_unknown_words(self):
        gate = threading.Event()
        controller = self.session(
            [(1.0, 2.0), (3.0, 4.0)],
            transcriber=ScriptedTranscriber(["first words", "second words"], fail_on=0,
                                            gate=gate))
        await controller.start()
        await self.run_to(5.0)
        gate.set()
        await until(lambda: "u2" in self.finals())
        self.clock.advance_to(5.5)
        self.source.push(5.5)  # segmentation stops at the next audio after the failure
        await until(lambda: self.statuses())
        self.clock.advance_to(7.0)
        await controller.stop()
        self.assertEqual(self.statuses(), [(5.0, "error", "transcription_failed")])
        self.assertEqual(self.finals(), {"u1": (1.0, 2.0, ""), "u2": (3.0, 4.0, "")})
        windows = self.windows()
        self.assertEqual(list(windows), ["pause-3", "metrics-5", "metrics-6", "metrics-7"])
        self.assertEqual((windows["metrics-5"].availability, windows["metrics-5"].wpm,
                          windows["metrics-5"].filler_count), ("available", None, None))
        self.assertEqual(windows["metrics-5"].pause.state, "active")
        self.assertTrue(all(windows[key].availability == "error"
                            for key in ("metrics-6", "metrics-7")))
        self.assert_consistent()

    async def test_slow_final_leaves_speech_incomplete_and_releases_once(self):
        gate = threading.Event()
        controller = self.session([(1.0, 9.0)], drain_timeout_s=0.1,
                                  transcriber=ScriptedTranscriber(["too slow"], gate=gate))
        await controller.start()
        await self.run_to(3.0)
        began = time.perf_counter()
        await asyncio.gather(controller.stop(), controller.stop())
        self.assertLess(time.perf_counter() - began, 1.0)
        self.assertEqual(controller.incomplete_sources, ["speech"])
        await self.adapter.stop_capture(3.0)  # repeated calls after completion are no-ops
        await self.adapter.drain()
        gate.set()  # the late transcription finishes after the session completed
        for thread in self.adapter._threads:
            thread.join(5)
        await asyncio.sleep(0.05)
        self.assertFalse(any(thread.is_alive() for thread in self.adapter._threads))
        self.assertEqual((self.source.opened, self.source.closed), (1, 1))
        self.assertEqual(self.finals(), {})
        self.assert_consistent()

    async def test_session_manager_composes_one_adapter_per_session(self):
        transcriber = ScriptedTranscriber(["composed end to end"])  # loaded once, shared
        sources = []

        def factory(config):
            sources.append(ScriptedSource())
            adapter = SpeechAdapter(CONFIG, sources[-1], ScriptedSegmenter([(0.5, 1.5)]),
                                    transcriber)
            return Components(speech=adapter, recorder=Recorder())

        manager, clock = SessionManager(factory), FakeClock()
        session = manager.create(SessionConfig(mode="live"), clock=clock)
        await session.start()
        clock.advance_to(6.0)
        sources[0].push(6.0)
        await until(lambda: session.components.speech.analyzed_s >= 6.0)
        await manager.shutdown()
        events = session.components.recorder.completed.events
        finals = [(event.payload.text, event.payload.end_s) for event in events
                  if event.type == "speech.transcript" and event.payload.is_final]
        self.assertEqual(finals, [("composed end to end", 1.5)])
        self.assertEqual([event.event_id for event in events if event.type == "speech.metrics"],
                         ["metrics-5", "metrics-6"])
        self.assertEqual((len(sources), sources[0].closed), (1, 1))


class SpeechImportTests(TestCase):
    def test_package_imports_without_optional_speech_dependencies(self):
        code = ("import sys, lecoach.speech; "
                "loaded = {'faster_whisper', 'sounddevice', 'numpy'} & set(sys.modules); "
                "assert not loaded, loaded")
        subprocess.run([sys.executable, "-c", code], check=True)
