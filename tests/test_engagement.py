"""LIVE-01 checks for the sole engagement engine, using synthetic inputs only."""

import asyncio
import json
from pathlib import Path
from unittest import IsolatedAsyncioTestCase, TestCase

from pydantic import ValidationError

from lecoach.contracts import parse_event
from lecoach.contracts.interfaces import Components, SessionConfig, SessionContext
from lecoach.engagement import RuleConfig, RuleEngine
from lecoach.engagement.compose import replay_with_engine
from lecoach.runtime.clock import FakeClock
from lecoach.runtime.fixtures import FixtureRepository, replay_case
from lecoach.runtime.session import SessionController

SPEECH_FIXTURES = Path(__file__).resolve().parents[1] / "checks" / "speech" / "fixtures"
NEGATIVE = {"CONFUSED", "BORED"}


def speech(event_id, end, wpm=144.0, filler_rate=0.0, pause=None, window=5.0, session="s"):
    return parse_event(
        {
            "schema_version": 0,
            "session_id": session,
            "event_id": event_id,
            "source": "speech",
            "type": "speech.metrics",
            "timestamp_s": end,
            "payload": {
                "window_start_s": max(0.0, end - window),
                "window_end_s": end,
                "availability": "available",
                "wpm": wpm,
                "filler_count": None if filler_rate is None else 0,
                "filler_rate_per_min": filler_rate,
                "pause": pause
                or {"state": "none", "duration_s": 0.0, "start_s": None, "end_s": None},
            },
        }
    )


def vision(event_id, end, facing=0.8, present=True, window=1.0, session="s"):
    known = present is True
    return parse_event(
        {
            "schema_version": 0,
            "session_id": session,
            "event_id": event_id,
            "source": "vision",
            "type": "vision.metrics",
            "timestamp_s": end,
            "payload": {
                "window_start_s": max(0.0, end - window),
                "window_end_s": end,
                "availability": "available",
                "person_present": present,
                "pose_available": present,
                "facing_score": facing if known else None,
                "activity_score": 0.3 if known else None,
            },
        }
    )


def status(event_id, source, at, availability="unavailable", session="s"):
    return parse_event(
        {
            "schema_version": 0,
            "session_id": session,
            "event_id": event_id,
            "source": source,
            "type": "signal.status",
            "timestamp_s": at,
            "payload": {"availability": availability, "reason": "camera_disconnected"},
        }
    )


class Harness:
    """Drives the engine directly with a fake clock and validates every emission."""

    def __init__(self, rules=None, mode="fixture", session="s"):
        self.clock = FakeClock()
        self.events = []
        self.engine = RuleEngine(rules)
        self.context = SessionContext(session, self.clock, self._emit, SessionConfig(mode=mode))
        self.engine.start(self.context)

    def _emit(self, value):
        self.events.append(parse_event(value))
        return True

    def feed(self, *events):
        for event in events:
            self.clock.advance_to(max(self.clock.now(), event.timestamp_s))
            self.engine.on_event(event)

    def at(self, t):
        self.clock.advance_to(t)
        self.engine.evaluate()

    @property
    def states(self):
        return [e.payload.state for e in self.events]


def transitions(trace):
    return [e for e in trace if e["type"] == "engagement.state"]


class FixtureReplayTests(IsolatedAsyncioTestCase):
    async def test_weak_delivery_lowers_and_improved_delivery_restores(self):
        case = FixtureRepository().load("weak_to_improved")
        result = await replay_case(case, replay_with_engine())
        states = [e["payload"]["state"] for e in transitions(result["delivery_trace"])]
        self.assertEqual(states, ["NEUTRAL", "CONFUSED", "BORED", "INTERESTED", "ENGAGED"])
        trace = {e["event_id"]: e for e in result["delivery_trace"]}
        codes = []
        for event in transitions(result["delivery_trace"]):
            self.assertNotIn(event["event_id"], {"audience-pace", "audience-recovery"})
            for reason in event["payload"]["reasons"]:
                codes.append(reason["code"])
                for cited in reason["source_event_ids"]:
                    # Evidence exists, arrived first, and keeps its capture time.
                    self.assertIn(cited, trace)
                    self.assertLessEqual(trace[cited]["timestamp_s"], event["timestamp_s"])
        self.assertTrue({"pace_high", "facing_away_sustained", "pace_steady"} <= set(codes))

    async def test_replay_is_deterministic(self):
        case = FixtureRepository().load("weak_to_improved")
        first = await replay_case(case, replay_with_engine())
        second = await replay_case(case, replay_with_engine())
        self.assertEqual(
            transitions(first["delivery_trace"]), transitions(second["delivery_trace"])
        )

    async def test_missing_inputs_never_produce_negative_states(self):
        repository = FixtureRepository()
        for name in ("no_usable_signals", "empty_session", "insufficient_window", "drain_timeout"):
            with self.subTest(case=name):
                result = await replay_case(repository.load(name), replay_with_engine())
                states = {e["payload"]["state"] for e in transitions(result["delivery_trace"])}
                self.assertFalse(states & NEGATIVE)

    async def test_camera_unavailable_uses_speech_only(self):
        result = await replay_case(
            FixtureRepository().load("camera_unavailable"), replay_with_engine()
        )
        for event in transitions(result["delivery_trace"]):
            self.assertNotIn("vision", event["payload"]["usable_sources"])
            codes = {r["code"] for r in event["payload"]["reasons"]}
            self.assertNotIn("facing_away_sustained", codes)

    async def test_repeated_sessions_start_fresh(self):
        result = await replay_case(
            FixtureRepository().load("repeated_sessions"), replay_with_engine()
        )
        by_session = {}
        for event in transitions(result["delivery_trace"]):
            by_session.setdefault(event["session_id"], []).append(event)
        self.assertEqual(len(by_session), 2)
        for events in by_session.values():
            self.assertEqual(events[0]["event_id"], "engagement-0")
            self.assertEqual(events[0]["payload"]["state"], "NEUTRAL")

    async def test_all_cases_emit_valid_engagement_events(self):
        repository = FixtureRepository()
        for spec in repository.describe():
            with self.subTest(case=spec["name"]):
                result = await replay_case(repository.load(spec["name"]), replay_with_engine())
                for event in transitions(result["delivery_trace"]):
                    parse_event(event)

    async def test_speech_fixtures_drive_expected_rules(self):
        expected = {
            "rapid_speech.json": ("CONFUSED", "pace_high"),
            "filler_heavy.json": ("CONFUSED", "fillers_frequent"),
            "prolonged_silence.json": ("BORED", "silence_prolonged"),
        }
        for name in sorted(p.name for p in SPEECH_FIXTURES.glob("*.json")):
            with self.subTest(case=name):
                events = [
                    parse_event(e)
                    for e in json.loads((SPEECH_FIXTURES / name).read_text(encoding="utf-8"))
                ]
                emitted = await self.play(events)
                negative = [e for e in emitted if e.payload.state in NEGATIVE]
                if name in expected:
                    state, code = expected[name]
                    self.assertTrue(negative, "weak delivery should lower attention")
                    self.assertEqual(negative[0].payload.state, state)
                    self.assertIn(code, [r.code for r in negative[0].payload.reasons])
                elif name != "steady_pace.json":
                    # Outages, silence-only, unsupported language and delayed output
                    # are input limitations, never negative evidence.
                    self.assertEqual(negative, [])

    async def play(self, events):
        emitted, controller = [], None
        for event in events:
            if event.type == "session.started":
                controller = SessionController(
                    SessionConfig(),
                    Components(engagement=RuleEngine()),
                    session_id=event.session_id,
                )
                controller.bus.subscribe(
                    lambda e: emitted.append(e) if e.type == "engagement.state" else None
                )
                await controller.start(event)
                continue
            if controller is None or event.session_id != controller.session_id:
                continue
            if controller.phase == "completed":
                continue
            controller.clock.advance_to(max(controller.clock.now(), event.timestamp_s))
            if event.source != "engagement":
                controller.accept_authored(event)
        return emitted


class EngineRuleTests(TestCase):
    def test_starts_neutral_without_usable_sources(self):
        h = Harness()
        self.assertEqual(h.states, ["NEUTRAL"])
        self.assertEqual(h.events[0].payload.usable_sources, [])
        self.assertEqual(h.events[0].timestamp_s, 0.0)

    def test_metric_jitter_does_not_flicker(self):
        h = Harness()
        for second in range(1, 61):
            wpm = 200.0 if second % 2 else 150.0
            facing = 0.3 if second % 2 else 0.7
            h.feed(
                speech(f"sp-{second}", float(second), wpm=wpm, window=1.0),
                vision(f"vi-{second}", float(second), facing=facing),
            )
        self.assertFalse(set(h.states) & NEGATIVE)
        times = [e.timestamp_s for e in h.events]
        gaps = [b - a for a, b in zip(times, times[1:])]
        self.assertTrue(all(gap >= h.engine.config.min_state_dwell_s for gap in gaps))
        self.assertLessEqual(len(h.events), 3)

    def test_hysteresis_band_holds_a_negative_state(self):
        h = Harness()
        for t in (5.0, 10.0, 15.0, 20.0):
            h.feed(speech(f"fast-{t}", t, wpm=200.0))
        self.assertEqual(h.states[-1], "CONFUSED")
        for t in (25.0, 30.0, 35.0):
            h.feed(speech(f"band-{t}", t, wpm=175.0))  # Between clear and trigger edges.
        self.assertEqual(h.states[-1], "CONFUSED")
        h.feed(speech("calm", 40.0, wpm=150.0))
        self.assertEqual(h.states[-1], "INTERESTED")

    def test_stale_speech_is_dropped_not_held_against_the_speaker(self):
        h = Harness()
        for t in (5.0, 10.0, 15.0):
            h.feed(speech(f"fast-{t}", t, wpm=200.0))
        self.assertEqual(h.states[-1], "CONFUSED")
        # Speech stops arriving; vision keeps reporting a speaker facing the audience.
        for t in range(16, 40):
            h.feed(vision(f"v-{t}", float(t), facing=0.8))
        self.assertEqual(h.states[-2:], ["INTERESTED", "ENGAGED"])
        last = h.events[-1]
        self.assertEqual(last.payload.usable_sources, ["vision"])
        self.assertNotIn("pace_high", [r.code for r in last.payload.reasons])

    def test_losing_every_input_returns_to_neutral_without_reasons(self):
        h = Harness()
        for t in (5.0, 10.0, 15.0):
            h.feed(speech(f"fast-{t}", t, wpm=200.0))
        self.assertEqual(h.states[-1], "CONFUSED")
        h.at(40.0)
        self.assertEqual(h.states[-1], "NEUTRAL")
        self.assertEqual(h.events[-1].payload.reasons, [])
        self.assertEqual(h.events[-1].payload.usable_sources, [])

    def test_absent_person_and_camera_errors_are_not_facing_away(self):
        h = Harness()
        for t in range(1, 21):
            h.feed(vision(f"gone-{t}", float(t), present=False))
        self.assertEqual(h.states, ["NEUTRAL"])
        h2 = Harness()
        for t in range(1, 5):
            h2.feed(vision(f"away-{t}", float(t), facing=0.1))
        h2.feed(status("cam-lost", "vision", 4.5))
        for t in range(5, 20):
            h2.at(float(t))
        self.assertFalse(set(h2.states) & NEGATIVE)

    def test_sustained_facing_away_needs_duration(self):
        h = Harness()
        for t in range(1, 6):
            h.feed(vision(f"away-{t}", float(t), facing=0.1))
        self.assertEqual(h.states, ["NEUTRAL"])
        for t in range(6, 9):
            h.feed(vision(f"away-{t}", float(t), facing=0.1))
        self.assertEqual(h.states[-1], "BORED")
        reason = h.events[-1].payload.reasons[0]
        self.assertEqual(reason.code, "facing_away_sustained")
        self.assertLessEqual(len(reason.source_event_ids), h.engine.config.max_evidence_ids)

    def test_older_observation_cannot_overwrite_newer(self):
        h = Harness()
        for t in (5.0, 10.0, 15.0):
            h.feed(speech(f"fast-{t}", t, wpm=200.0))
        self.assertEqual(h.states[-1], "CONFUSED")
        h.clock.advance_to(20.0)
        h.engine.on_event(speech("late-calm", 12.0, wpm=140.0))
        self.assertEqual(h.states[-1], "CONFUSED")

    def test_prolonged_silence_after_speech(self):
        h = Harness()
        h.feed(speech("talk", 5.0))
        active = {"state": "active", "duration_s": 7.0, "start_s": 6.0, "end_s": None}
        h.feed(speech("quiet", 13.0, wpm=0.0, pause=active))
        self.assertEqual(h.states[-1], "BORED")
        self.assertEqual(h.events[-1].payload.reasons[0].code, "silence_prolonged")

    def test_restart_and_stop(self):
        h = Harness()
        for t in (5.0, 10.0, 15.0):
            h.feed(speech(f"fast-{t}", t, wpm=200.0))
        h.engine.stop()
        count = len(h.events)
        h.feed(speech("after-stop", 20.0, wpm=200.0))
        self.assertEqual(len(h.events), count)
        clock, emitted = FakeClock(), []
        h.engine.start(
            SessionContext(
                "next", clock, lambda v: emitted.append(parse_event(v)) or True, SessionConfig()
            )
        )
        self.assertEqual([e.event_id for e in emitted], ["engagement-0"])
        self.assertEqual(h.engine.state, "NEUTRAL")
        self.assertFalse(any(rule.active for rule in h.engine.rules))
        h.engine.on_event(speech("foreign", 1.0, wpm=200.0, session="s"))
        self.assertEqual(len(emitted), 1)

    def test_rule_configuration_is_validated(self):
        with self.assertRaises(ValidationError):
            RuleConfig(pace_high_wpm=150.0)
        with self.assertRaises(ValidationError):
            RuleConfig(facing_away_below=0.7)


class LiveTickTests(IsolatedAsyncioTestCase):
    async def test_live_tick_notices_stale_inputs_without_new_events(self):
        rules = RuleConfig(tick_interval_s=0.01)
        h = Harness(rules, mode="live")
        for t in (5.0, 10.0, 15.0):
            h.feed(speech(f"fast-{t}", t, wpm=200.0))
        self.assertEqual(h.states[-1], "CONFUSED")
        h.clock.advance_to(60.0)
        await asyncio.sleep(0.05)
        self.assertEqual(h.states[-1], "NEUTRAL")
        h.engine.stop()
        count = len(h.events)
        await asyncio.sleep(0.03)
        self.assertEqual(len(h.events), count)


class CompositionTests(TestCase):
    def test_default_app_computes_audience_but_keeps_live_unavailable(self):
        from fastapi.testclient import TestClient

        from lecoach.api.app import create_app

        with TestClient(create_app(replay_with_engine())) as client:
            assert client.get("/api/health").json()["live_integrated"] is False
            assert client.post("/api/sessions", json={"mode": "live"}).status_code == 503
            snapshot = client.post("/api/sessions", json={}).json()
            assert snapshot["output_provenance"] == "computed"
