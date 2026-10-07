import asyncio
from unittest import IsolatedAsyncioTestCase

from lecoach.contracts import parse_event
from lecoach.contracts.interfaces import Components, SessionConfig
from lecoach.runtime.bus import EventBus
from lecoach.runtime.clock import FakeClock
from lecoach.runtime.fixtures import FixtureRepository, replay_case
from lecoach.runtime.session import SessionConflict, SessionController, SessionManager
from tests.helpers import Capture, Generator, Recorder, event


class RuntimeTests(IsolatedAsyncioTestCase):
    def controller(self, **components):
        clock = FakeClock()
        controller = SessionController(
            SessionConfig(mode="live", drain_timeout_s=0.02, startup_timeout_s=0.02),
            Components(**components),
            session_id="test-session",
            clock=clock,
        )
        return controller, clock

    async def test_start_stop_flush_and_retry(self):
        speech, vision, recorder = Capture(flush=True), Capture(), Recorder()
        controller, clock = self.controller(
            speech=speech, vision=vision, recorder=recorder, feedback=Generator()
        )
        await asyncio.gather(controller.start(), controller.start())
        self.assertEqual((speech.starts, vision.starts), (1, 1))
        clock.advance_to(10.0)
        await asyncio.gather(controller.stop(), controller.stop())
        self.assertEqual((speech.stops, vision.stops), (1, 1))
        self.assertEqual(controller.phase, "completed")
        self.assertEqual(controller.feedback_status, "ready")
        self.assertIn("drained-final", [e.event_id for e in recorder.completed.events])
        self.assertTrue(speech.released and vision.released)
        self.assertFalse(controller.emit(event(timestamp=10.0)))

    async def test_timeout_marks_incomplete_and_releases(self):
        speech, vision, recorder = Capture(pending=True), Capture(flush=True), Recorder()
        controller, clock = self.controller(speech=speech, vision=vision, recorder=recorder)
        await controller.start()
        clock.advance_to(2.0)
        await asyncio.wait_for(controller.stop(), 0.2)
        self.assertEqual(controller.incomplete_sources, ["speech"])
        self.assertTrue(speech.cancelled and speech.released and vision.released)
        self.assertEqual(recorder.completed.duration_s, 2.0)
        self.assertFalse(controller.emit(event(timestamp=1.0)))

    async def test_start_failure_leaves_other_adapter_usable(self):
        speech, vision = Capture(), Capture(fail=True)
        controller, clock = self.controller(speech=speech, vision=vision)
        await controller.start()
        self.assertEqual(controller.input_status["vision"]["reason"], "adapter_start_failed")
        self.assertTrue(vision.released)
        clock.advance_to(1.0)
        self.assertTrue(controller.emit(event()))
        await controller.stop()
        self.assertTrue(speech.released)

    async def test_start_timeout_and_stop_during_start(self):
        speech = Capture(delayed_start=True)
        controller, clock = self.controller(speech=speech)
        await controller.start()
        self.assertTrue(speech.released)
        self.assertEqual(controller.input_status["speech"]["reason"], "adapter_start_failed")
        await controller.stop()
        speech2 = Capture(delayed_start=True)
        controller2, _ = self.controller(speech=speech2)
        start = asyncio.create_task(controller2.start())
        await asyncio.sleep(0.001)
        await controller2.stop()
        await asyncio.gather(start, return_exceptions=True)
        self.assertTrue(speech2.released)
        self.assertEqual(controller2.phase, "completed")

    async def test_isolation_duplicates_stable_ids_and_capture_end(self):
        controller, clock = self.controller()
        emitted = []
        controller.bus.subscribe(emitted.append)
        await controller.start()
        clock.advance_to(3.0)
        self.assertFalse(controller.emit(event(session_id="foreign")))
        self.assertTrue(controller.emit(event()))
        self.assertFalse(controller.emit(event()))
        altered = event().model_dump()
        altered["payload"]["wpm"] = 200.0
        with self.assertRaisesRegex(ValueError, "stable event ID"):
            controller.emit(altered)
        await controller.stop()
        self.assertFalse(controller.emit(event(event_id="late", timestamp=2.0)))
        self.assertEqual(sum(e.event_id == "metric" for e in emitted), 1)
        with self.assertRaisesRegex(ValueError, "lifecycle"):
            controller.emit(
                parse_event(
                    {
                        "schema_version": 0,
                        "session_id": "test-session",
                        "event_id": "forged",
                        "source": "session",
                        "type": "session.started",
                        "timestamp_s": 0.0,
                        "payload": {},
                    }
                )
            )

    async def test_old_metric_does_not_overwrite_newer_display(self):
        controller, clock = self.controller()
        await controller.start()
        clock.advance_to(4.0)
        controller.emit(event(event_id="new", timestamp=4.0))
        controller.emit(event(event_id="old", timestamp=1.0))
        self.assertEqual(controller.latest["speech.metrics"].event_id, "new")
        await controller.stop()

    async def test_final_transcript_freezes_display(self):
        controller, clock = self.controller()
        await controller.start()
        case = FixtureRepository().load("late_final_and_duplicates")
        source_id = case.session_ids[0]
        finals = [
            e
            for e in case.events
            if e.type == "speech.transcript"
            and e.session_id == source_id
            and e.event_id != "after-completion"
        ]
        for original in finals:
            clock.advance_to(max(clock.now(), original.timestamp_s))
            controller.emit({**original.model_dump(), "session_id": controller.session_id})
        transcript = list(controller.transcript.values())
        self.assertEqual(len(transcript), 1)
        self.assertTrue(transcript[0].payload.is_final)
        self.assertEqual(transcript[0].payload.revision, 2)
        await controller.stop()

    async def test_consumer_failure_cleans_up(self):
        class BrokenRecorder(Recorder):
            def on_event(self, event):
                raise RuntimeError("test subscriber failure")

        controller, _ = self.controller(speech=Capture(), recorder=BrokenRecorder())
        with self.assertRaises(RuntimeError):
            await controller.start()
        await controller.stop()
        self.assertEqual(controller.phase, "completed")
        self.assertEqual(controller.feedback_status, "unavailable")

    async def test_manager_refuses_competing_session_and_resets(self):
        manager = SessionManager()
        first = manager.create(SessionConfig(), session_id="first")
        with self.assertRaises(SessionConflict):
            manager.create(SessionConfig())
        await first.stop()
        second = manager.create(SessionConfig(), session_id="second")
        self.assertNotEqual(first.context.session_id, second.context.session_id)
        self.assertEqual(second.clock.now(), 0)
        await manager.shutdown()

    async def test_fifo_reentrant_delivery(self):
        bus = EventBus()
        seen = []

        def emit_again(current):
            if current.event_id == "source":
                bus.publish(event(event_id="result"))

        bus.subscribe(emit_again)
        bus.subscribe(lambda e: seen.append(e.event_id))
        bus.publish(event(event_id="source"))
        self.assertEqual(seen, ["source", "result"])

    async def test_all_replays_deterministic_and_oracle_retention(self):
        repo = FixtureRepository()
        for description in repo.describe():
            case = repo.load(description["name"])
            first = await replay_case(case)
            self.assertEqual(first, await replay_case(case))
            self.assertEqual(len(first["feedback"]), len(case.session_ids))
            for session_id in case.session_ids:
                emitted = [e for e in first["delivery_trace"] if e["session_id"] == session_id]
                expected = repo._specs[case.name]["sessions"]
                oracle = next(s for s in expected if s["session_id"] == session_id)
                self.assertEqual(
                    [
                        e["event_id"]
                        for e in sorted(emitted, key=lambda e: (e["timestamp_s"], e["event_id"]))
                    ],
                    oracle["retained_event_ids"],
                )

    async def test_explicit_delivery_schedule_keeps_capture_time(self):
        case = FixtureRepository().load("late_final_and_duplicates")
        schedule = [max(12.0, e.timestamp_s) for e in case.events]
        result = await replay_case(case, delivery_schedule_s=schedule)
        final = next(e for e in result["delivery_trace"] if e["event_id"] == "final-2")
        original = next(
            e
            for e in case.events
            if e.event_id == "final-2" and e.session_id == case.session_ids[0]
        )
        self.assertEqual(final["timestamp_s"], original.timestamp_s)
        self.assertEqual(result["feedback"][0]["duration_s"], 10)

    async def test_fake_clock_rejects_backwards_or_nonfinite_time(self):
        clock = FakeClock()
        clock.advance_to(2.0)
        for invalid in (1.0, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                clock.advance_to(invalid)

    async def test_old_status_does_not_override_newer_metrics(self):
        controller, clock = self.controller()
        await controller.start()
        clock.advance_to(4.0)
        controller.emit(event(timestamp=4.0))
        controller.emit(
            {
                "schema_version": 0,
                "session_id": controller.session_id,
                "event_id": "late-status",
                "source": "speech",
                "type": "signal.status",
                "timestamp_s": 1.0,
                "payload": {"availability": "unavailable", "reason": "old_failure"},
            }
        )
        self.assertEqual(controller.input_status["speech"]["availability"], "available")
        await controller.stop()

    async def test_all_capture_stops_before_drain(self):
        speech, vision = Capture(), Capture()
        controller, _ = self.controller(speech=speech, vision=vision)
        original_drain = speech.drain

        async def verify_drain():
            self.assertTrue(vision.released)
            await original_drain()

        speech.drain = verify_drain
        await controller.start()
        await controller.stop()
        self.assertEqual(controller.incomplete_sources, [])

    async def test_wrong_recorder_identity_is_not_served_as_feedback(self):
        class WrongRecorder(Recorder):
            def complete(self, duration_s, incomplete_sources):
                completed = super().complete(duration_s, incomplete_sources).model_dump()
                completed["session_id"] = "wrong"
                for current in completed["events"]:
                    current["session_id"] = "wrong"
                return completed

        controller, _ = self.controller(recorder=WrongRecorder(), feedback=Generator())
        await controller.start()
        await controller.stop()
        self.assertIsNone(controller.feedback)
        self.assertEqual(controller.error, "feedback_unavailable")

    async def test_dangling_feedback_and_feedback_timeout(self):
        class BadGenerator(Generator):
            async def generate(self, session):
                value = (await super().generate(session)).model_dump()
                value["moments"] = [
                    {
                        "timestamp_s": 0.0,
                        "kind": "improvement",
                        "observation": "Synthetic faulty output",
                        "suggestion": "Do not accept this output",
                        "evidence_event_ids": ["does-not-exist"],
                    }
                ]
                return value

        controller, _ = self.controller(recorder=Recorder(), feedback=BadGenerator())
        await controller.start()
        await controller.stop()
        self.assertIsNone(controller.feedback)
        self.assertEqual(controller.feedback_status, "unavailable")

        class NeverGenerator(Generator):
            async def generate(self, session):
                await asyncio.Event().wait()

        manager = SessionManager(
            lambda config: Components(recorder=Recorder(), feedback=NeverGenerator())
        )
        second = manager.create(SessionConfig(feedback_timeout_s=0.02))
        await second.start()
        stop = asyncio.create_task(second.stop())
        await asyncio.sleep(0.001)
        self.assertEqual(second.feedback_status, "pending")
        with self.assertRaises(SessionConflict):
            manager.create(SessionConfig())
        await asyncio.wait_for(stop, 0.2)
        self.assertEqual(second.feedback_status, "unavailable")
