import asyncio
import json
from unittest import IsolatedAsyncioTestCase

from lecoach.coaching import InMemorySessionRecorder
from lecoach.contracts import CompletedSession, parse_event
from lecoach.contracts.interfaces import Components, SessionConfig, SessionContext
from lecoach.runtime.clock import FakeClock
from lecoach.runtime.fixtures import FixtureRepository, fixture_root, replay_case
from lecoach.runtime.session import SessionController
from tests.helpers import Capture, event


def lifecycle(kind, at=0.0, session_id="unit", incomplete_sources=None):
    return parse_event(
        {
            "schema_version": 0,
            "session_id": session_id,
            "event_id": f"session:{kind}",
            "source": "session",
            "type": f"session.{kind}",
            "timestamp_s": at,
            "payload": {"duration_s": at, "incomplete_sources": incomplete_sources or []}
            if kind == "completed"
            else {},
        }
    )


class RecorderTests(IsolatedAsyncioTestCase):
    def setUp(self):
        self.recorder = InMemorySessionRecorder()
        self.context = SessionContext("unit", FakeClock(), lambda event: False, SessionConfig())
        self.recorder.start(self.context)

    def start_log(self):
        self.recorder.on_event(lifecycle("started"))

    def end_log(self, at=3.0, incomplete_sources=None):
        self.recorder.on_event(lifecycle("stopping", at))
        self.recorder.on_event(lifecycle("completed", at, incomplete_sources=incomplete_sources))
        return self.recorder.complete(at, incomplete_sources or [])

    async def test_all_existing_cases_match_the_actual_recorder(self):
        repo = FixtureRepository()
        specs = json.loads((fixture_root() / "expectations.json").read_text())
        for description in repo.describe():
            with self.subTest(case=description["name"]):
                case = repo.load(description["name"])
                recorders = []

                def factory(config):
                    recorder = InMemorySessionRecorder()
                    recorders.append(recorder)
                    return Components(recorder=recorder)

                result = await replay_case(case, factory=factory)
                self.assertEqual(result["feedback"], [])
                index = {(e.session_id, e.event_id): e for e in case.events}
                oracles = specs[case.name]["sessions"]
                self.assertEqual(len(recorders), len(oracles))
                for recorder, oracle in zip(recorders, oracles):
                    actual = recorder.complete(oracle["duration_s"], oracle["incomplete_sources"])
                    expected = CompletedSession(
                        session_id=oracle["session_id"],
                        duration_s=oracle["duration_s"],
                        incomplete_sources=oracle["incomplete_sources"],
                        events=[
                            index[(oracle["session_id"], event_id)]
                            for event_id in oracle["retained_event_ids"]
                        ],
                    )
                    self.assertEqual(actual, expected)

    async def test_controller_drain_and_retry_with_real_recorder(self):
        clock = FakeClock()
        speech, vision = Capture(flush=True), Capture()
        controller = SessionController(
            SessionConfig(mode="live"),
            Components(speech=speech, vision=vision, recorder=InMemorySessionRecorder()),
            session_id="unit",
            clock=clock,
        )
        await controller.start()
        clock.advance_to(10.0)
        await asyncio.gather(controller.stop(), controller.stop())
        actual = controller.components.recorder.complete(10.0, [])
        self.assertIsNone(controller.error)
        self.assertEqual(controller.feedback_status, "unavailable")
        self.assertIn("drained-final", [e.event_id for e in actual.events])
        self.assertEqual(sum(e.type == "session.completed" for e in actual.events), 1)
        self.assertTrue(speech.released and vision.released)
        self.assertFalse(controller.emit(event("unit", "closed-callback", 9.0)))

    async def test_controller_timeout_preserves_incomplete_source(self):
        clock = FakeClock()
        speech = Capture(pending=True)
        recorder = InMemorySessionRecorder()
        controller = SessionController(
            SessionConfig(mode="live", drain_timeout_s=0.02),
            Components(speech=speech, vision=Capture(), recorder=recorder),
            session_id="unit",
            clock=clock,
        )
        await controller.start()
        clock.advance_to(2.0)
        await asyncio.wait_for(controller.stop(), 1.0)
        actual = recorder.complete(2.0, ["speech"])
        self.assertIsNone(controller.error)
        self.assertEqual(actual.incomplete_sources, ["speech"])
        self.assertTrue(speech.cancelled and speech.released)

    async def test_controller_can_stop_an_empty_session(self):
        recorder = InMemorySessionRecorder()
        controller = SessionController(SessionConfig(), Components(recorder=recorder))
        await controller.stop()
        actual = recorder.complete(0.0, [])
        self.assertEqual(actual.duration_s, 0.0)
        self.assertEqual(len(actual.events), 3)
        self.assertIsNone(controller.error)

    def test_order_and_null_values_are_preserved(self):
        self.start_log()
        latest = event("unit", "later", 2.0).model_dump()
        latest["payload"]["wpm"] = None
        self.recorder.on_event(parse_event(latest))
        self.recorder.on_event(event("unit", "b", 1.0))
        self.recorder.on_event(event("unit", "a", 1.0))
        actual = self.end_log()
        observations = [e for e in actual.events if e.source == "speech"]
        self.assertEqual([e.event_id for e in observations], ["a", "b", "later"])
        self.assertIsNone(observations[-1].payload.wpm)

    def test_identical_retry_is_stored_once(self):
        self.start_log()
        observation = event("unit")
        self.recorder.on_event(observation)
        self.recorder.on_event(observation)
        actual = self.end_log()
        self.assertEqual(sum(e.event_id == "metric" for e in actual.events), 1)

    def test_conflicting_retry_is_rejected_without_changing_evidence(self):
        self.start_log()
        observation = event("unit")
        self.recorder.on_event(observation)
        changed = observation.model_dump()
        changed["payload"]["wpm"] = 205.0
        with self.assertRaisesRegex(ValueError, "stable event ID"):
            self.recorder.on_event(parse_event(changed))
        actual = self.end_log()
        self.assertEqual(next(e for e in actual.events if e.event_id == "metric"), observation)

    def test_foreign_and_post_stop_events_are_excluded_but_drain_is_kept(self):
        self.start_log()
        self.recorder.on_event(event("foreign", "foreign", 1.0))
        self.recorder.on_event(lifecycle("stopping", 2.0))
        self.recorder.on_event(event("unit", "after-capture", 3.0))
        neutral = FixtureRepository().load("weak_to_improved").events[1].model_dump()
        neutral.update(session_id="unit", event_id="after-engine-stop", timestamp_s=1.0)
        self.recorder.on_event(parse_event(neutral))
        self.recorder.on_event(event("unit", "during-drain", 1.0))
        self.recorder.on_event(lifecycle("completed", 2.0))
        self.recorder.on_event(event("unit", "after-completion", 1.0))
        actual = self.recorder.complete(2.0, [])
        self.assertEqual(
            {e.event_id for e in actual.events},
            {"session:started", "session:stopping", "session:completed", "during-drain"},
        )

    def test_complete_is_idempotent_and_snapshots_are_independent(self):
        self.start_log()
        neutral = FixtureRepository().load("weak_to_improved").events[1].model_dump()
        neutral.update(session_id="unit")
        incoming = parse_event(neutral)
        self.recorder.on_event(incoming)
        incoming.payload.usable_sources.append("speech")
        actual = self.end_log(incomplete_sources=["speech"])
        retained = next(e for e in actual.events if e.type == "engagement.state")
        self.assertEqual(retained.payload.usable_sources, [])
        retained.payload.usable_sources.append("vision")
        actual.events.clear()
        actual.incomplete_sources.clear()
        again = self.recorder.complete(3.0, ["speech"])
        self.assertEqual(len(again.events), 4)
        self.assertEqual(again.incomplete_sources, ["speech"])
        self.assertEqual(
            next(e for e in again.events if e.type == "engagement.state").payload.usable_sources,
            [],
        )

    def test_completion_metadata_cannot_be_changed(self):
        self.start_log()
        self.end_log()
        with self.assertRaisesRegex(ValueError, "metadata"):
            self.recorder.complete(3.0, ["vision"])
        with self.assertRaisesRegex(ValueError, "metadata"):
            self.recorder.complete(4.0, [])

    def test_reusing_a_recorder_does_not_mix_sessions_or_mutate_old_output(self):
        self.start_log()
        self.recorder.on_event(event("unit"))
        first = self.end_log()
        next_context = SessionContext("next", FakeClock(), lambda e: False, SessionConfig())
        self.recorder.start(next_context)
        self.recorder.on_event(lifecycle("started", session_id="next"))
        self.recorder.on_event(event("unit", "old-callback", 1.0))
        self.recorder.on_event(lifecycle("stopping", session_id="next"))
        self.recorder.on_event(lifecycle("completed", session_id="next"))
        second = self.recorder.complete(0.0, [])
        self.assertEqual(len(second.events), 3)
        self.assertTrue(all(e.session_id == "next" for e in second.events))
        self.assertEqual(len(first.events), 4)
        self.assertTrue(all(e.session_id == "unit" for e in first.events))

    def test_active_recording_cannot_be_replaced(self):
        with self.assertRaisesRegex(RuntimeError, "current recording"):
            self.recorder.start(self.context)
        self.start_log()
        self.recorder.on_event(lifecycle("stopping", 3.0))
        self.recorder.on_event(lifecycle("completed", 3.0))
        with self.assertRaisesRegex(RuntimeError, "current recording"):
            self.recorder.start(self.context)

    def test_completion_requires_the_recorded_lifecycle(self):
        with self.assertRaisesRegex(RuntimeError, "session.completed"):
            self.recorder.complete(3.0, [])
        with self.assertRaisesRegex(ValueError, "precede"):
            self.recorder.on_event(event("unit"))
        self.start_log()
        with self.assertRaisesRegex(ValueError, "completion must follow stop"):
            self.recorder.on_event(lifecycle("completed", 3.0))
        self.recorder.on_event(lifecycle("stopping", 3.0))
        with self.assertRaisesRegex(ValueError, "same capture end"):
            self.recorder.on_event(lifecycle("completed", 4.0))
        self.recorder.on_event(lifecycle("completed", 3.0))
        self.assertEqual(self.recorder.complete(3.0, []).duration_s, 3.0)
