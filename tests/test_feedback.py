from unittest import IsolatedAsyncioTestCase

from fastapi.testclient import TestClient

from checks.coaching.feedback_replay import check, evaluate
from lecoach.api.app import create_app
from lecoach.coaching import TemplateFeedbackGenerator
from lecoach.coaching.compose import replay_with_coaching
from lecoach.contracts import CompletedSession, parse_event
from lecoach.engagement import DEFAULT_RULES, RuleConfig
from lecoach.runtime.fixtures import FixtureRepository
from tests.helpers import event
from tests.test_coaching import lifecycle


def speech(at=10.0, event_id="speech", **metrics):
    value = event("unit", event_id, at).model_dump()
    value["payload"].update({"window_start_s": max(0.0, at - 10.0), "wpm": 200.0, **metrics})
    if value["payload"]["availability"] != "available":
        value["payload"].update(
            wpm=None,
            filler_count=None,
            filler_rate_per_min=None,
            pause={"state": "unknown", "duration_s": None, "start_s": None, "end_s": None},
        )
    return parse_event(value)


def vision(at=10.0, event_id="vision", **metrics):
    value = next(
        e for e in FixtureRepository().load("weak_to_improved").events if e.type == "vision.metrics"
    ).model_dump()
    value.update(session_id="unit", event_id=event_id, timestamp_s=at)
    value["payload"].update(
        {
            "window_start_s": max(0.0, at - 5.0),
            "window_end_s": at,
            "facing_score": 0.2,
            **metrics,
        }
    )
    if not value["payload"]["person_present"] or not value["payload"]["pose_available"]:
        value["payload"].update(facing_score=None, activity_score=None)
    return parse_event(value)


def transition(code="pace_high", refs=("speech",), at=10.0, state="CONFUSED", **changes):
    payload = {
        "state": state,
        "previous_state": "NEUTRAL",
        "reasons": [{"code": code, "source_event_ids": list(refs)}],
        "usable_sources": ["speech", "vision"],
    }
    payload.update(changes.pop("payload", {}))
    return parse_event(
        {
            "schema_version": 0,
            "session_id": "unit",
            "event_id": f"audience-{at}",
            "source": "engagement",
            "type": "engagement.state",
            "timestamp_s": at,
            "payload": payload,
            **changes,
        }
    )


def completed(*events, duration=50.0, incomplete=()):
    timeline = [
        lifecycle("started"),
        *events,
        lifecycle("stopping", duration),
        lifecycle("completed", duration, incomplete_sources=list(incomplete)),
    ]
    return CompletedSession(
        session_id="unit",
        duration_s=duration,
        incomplete_sources=list(incomplete),
        events=sorted(timeline, key=lambda e: (e.timestamp_s, e.event_id)),
    )


def generator(rules=DEFAULT_RULES):
    return TemplateFeedbackGenerator(
        stale_after_s={
            "speech": rules.speech_stale_s,
            "vision": rules.vision_stale_s,
        }
    )


class FeedbackTests(IsolatedAsyncioTestCase):
    async def test_engine_recorder_generator_against_all_synthetic_baselines(self):
        for description in FixtureRepository().describe():
            with self.subTest(case=description["name"]):
                sessions, reports, result = await evaluate(description["name"])
                check(description["name"], sessions, reports)
                self.assertEqual(result["output_provenance"], "computed_consumers")
                again = await evaluate(description["name"])
                self.assertEqual((sessions, reports), again[:2])

    async def test_actual_strength_uses_only_engine_cited_vision_not_same_time_frame(self):
        _, reports, _ = await evaluate("weak_to_improved")
        strength = next(m for m in reports[0].moments if m.kind == "strength")
        self.assertIn("vision-35", strength.evidence_event_ids)
        self.assertNotIn("vision-40", strength.evidence_event_ids)
        self.assertEqual(strength.timestamp_s, 40.0)

    async def test_templates_use_measured_values_and_practical_actions(self):
        observations = [
            ("pace_high", speech(), "200", "pausing"),
            ("pace_low", speech(wpm=70.0), "70", "phrases"),
            ("fillers_frequent", speech(filler_count=4, filler_rate_per_min=24.0), "24", "breath"),
            (
                "silence_prolonged",
                speech(
                    pause={
                        "state": "active",
                        "duration_s": 7.0,
                        "start_s": 3.0,
                        "end_s": None,
                    }
                ),
                "7 seconds",
                "transition",
            ),
            ("facing_away_sustained", vision(), "appeared", "camera"),
        ]
        for code, metric, observed, action in observations:
            with self.subTest(code=code):
                report = await generator().generate(
                    completed(metric, transition(code, [metric.event_id]))
                )
                self.assertEqual(len(report.moments), 1)
                moment = report.moments[0]
                self.assertIn(observed, moment.observation)
                self.assertIn(action, moment.suggestion)
                self.assertEqual(moment.timestamp_s, metric.timestamp_s)
                self.assertIn(metric.event_id, moment.evidence_event_ids)
                self.assertIn("audience-10.0", moment.evidence_event_ids)
                for jargon in ("cited", "windows", "out of 1", "ENGAGED", "head/body"):
                    self.assertNotIn(jargon, moment.observation)
                if code == "silence_prolonged":
                    self.assertIn("at least", moment.observation)
                    self.assertIn("cannot tell", moment.observation)
                if code == "fillers_frequent":
                    self.assertIn("transcript", moment.observation.lower())

    async def test_active_pause_advice_does_not_invent_its_end_or_intent(self):
        metrics = [
            speech(
                at,
                f"pause-{at}",
                pause={
                    "state": "active",
                    "duration_s": at - 3.0,
                    "start_s": 3.0,
                    "end_s": None,
                },
            )
            for at in (10.0, 11.0)
        ]
        report = await generator().generate(
            completed(
                *metrics,
                transition(
                    "silence_prolonged", [m.event_id for m in metrics], at=11.0, state="BORED"
                ),
            )
        )
        moment = report.moments[0]
        self.assertIn("at least 8 seconds", moment.observation)
        self.assertIn("cannot tell whether it was planned", moment.observation)
        self.assertEqual(moment.timestamp_s, 10.0)
        self.assertTrue(all(m.event_id in moment.evidence_event_ids for m in metrics))

    async def test_invalid_unknown_future_wrong_source_and_lifecycle_evidence_omitted(self):
        cases = [
            transition("unpublished_reason"),
            transition(refs=["missing"]),
            transition(refs=["session:started"]),
            transition("facing_away_sustained", refs=["speech"]),
            transition(at=9.0),
            transition(payload={"usable_sources": ["vision"]}),
            transition(payload={"reasons": []}),
        ]
        for reaction in cases:
            with self.subTest(reaction=reaction):
                report = await generator().generate(completed(speech(), reaction))
                self.assertEqual(report.moments, [])
                self.assertTrue(any("left out" in text for text in report.limitations))

    async def test_unknown_null_unavailable_and_zero_pace_never_negative_advice(self):
        for metric in [speech(wpm=None), speech(wpm=0.0), speech(availability="unavailable")]:
            with self.subTest(metric=metric):
                report = await generator().generate(completed(metric, transition()))
                self.assertEqual(report.moments, [])

    async def test_missing_person_pose_or_facing_never_negative_advice(self):
        for changes in [
            {"person_present": False},
            {"pose_available": False},
            {"facing_score": None},
        ]:
            with self.subTest(changes=changes):
                report = await generator().generate(
                    completed(vision(**changes), transition("facing_away_sustained", ["vision"]))
                )
                self.assertEqual(report.moments, [])
                self.assertTrue(any("camera" in text.lower() for text in report.limitations))

    async def test_stale_citations_and_stale_sources_do_not_become_advice(self):
        for observations in [(speech(),), (speech(), speech(30.0, "new"))]:
            with self.subTest(observations=observations):
                report = await generator().generate(completed(*observations, transition(at=30.0)))
                self.assertEqual(report.moments, [])

    async def test_historical_sustain_windows_allowed_when_latest_citation_fresh(self):
        report = await generator().generate(
            completed(
                speech(1.0, "old"),
                speech(20.0, "new"),
                transition(refs=["old", "new"], at=20.0),
            )
        )
        self.assertEqual(report.moments[0].timestamp_s, 1.0)
        self.assertIn("old", report.moments[0].evidence_event_ids)

    async def test_superseding_outage_blocks_evidence_until_new_observation(self):
        status = parse_event(
            {
                "schema_version": 0,
                "session_id": "unit",
                "event_id": "outage",
                "source": "speech",
                "type": "signal.status",
                "timestamp_s": 11.0,
                "payload": {"availability": "unavailable", "reason": "synthetic"},
            }
        )
        report = await generator().generate(completed(speech(), status, transition(at=12.0)))
        self.assertEqual(report.moments, [])
        recovered = await generator().generate(
            completed(
                speech(),
                status,
                speech(12.0, "recovered"),
                transition(refs=["recovered"], at=12.0),
            )
        )
        self.assertEqual(len(recovered.moments), 1)
        self.assertTrue(any("part" in text for text in recovered.limitations))

    async def test_freshness_is_supplied_by_shared_config(self):
        session = completed(speech(), transition(at=12.0))
        self.assertEqual(len((await generator().generate(session)).moments), 1)
        custom = RuleConfig(speech_stale_s=1.0)
        self.assertEqual((await generator(custom).generate(session)).moments, [])

    async def test_available_status_cannot_revive_pre_outage_citations(self):
        for source, code, metric in [
            ("speech", "pace_high", speech()),
            ("vision", "facing_away_sustained", vision()),
        ]:
            for availability in ["unavailable", "error"]:
                with self.subTest(source=source, availability=availability):
                    outage = parse_event(
                        {
                            "schema_version": 0,
                            "session_id": "unit",
                            "event_id": "outage",
                            "source": source,
                            "type": "signal.status",
                            "timestamp_s": 11.0,
                            "payload": {"availability": availability, "reason": "synthetic"},
                        }
                    )
                    ready = parse_event(
                        {
                            **outage.model_dump(),
                            "event_id": "ready",
                            "timestamp_s": 12.0,
                            "payload": {"availability": "available", "reason": "synthetic"},
                        }
                    )
                    report = await generator().generate(
                        completed(
                            metric,
                            outage,
                            ready,
                            transition(code, [metric.event_id], at=13.0),
                        )
                    )
                    self.assertEqual(report.moments, [])
                    self.assertTrue(any("left out" in text for text in report.limitations))

    async def test_post_outage_window_cannot_validate_old_citations_or_capture_time_ties(self):
        outage = parse_event(
            {
                "schema_version": 0,
                "session_id": "unit",
                "event_id": "outage",
                "source": "speech",
                "type": "signal.status",
                "timestamp_s": 11.0,
                "payload": {"availability": "error", "reason": "synthetic"},
            }
        )
        for captured_at in [10.0, 11.0]:
            with self.subTest(captured_at=captured_at):
                report = await generator().generate(
                    completed(
                        speech(captured_at, "old"),
                        outage,
                        speech(12.0, "new"),
                        transition(refs=["old", "new"], at=12.0),
                    )
                )
                self.assertEqual(report.moments, [])
        recovered = await generator().generate(
            completed(
                speech(),
                outage,
                speech(12.0, "new"),
                transition(refs=["new"], at=12.0),
            )
        )
        self.assertEqual(len(recovered.moments), 1)
        self.assertNotIn("speech", recovered.moments[0].evidence_event_ids)

    async def test_interested_or_uncited_engaged_not_a_supported_strength(self):
        for reaction in [
            transition("pace_steady", state="INTERESTED"),
            transition(state="ENGAGED", payload={"reasons": []}),
            transition("pace_high", state="ENGAGED"),
        ]:
            with self.subTest(reaction=reaction):
                report = await generator().generate(completed(speech(wpm=144.0), reaction))
                self.assertEqual(report.moments, [])

    async def test_strongest_multisource_candidate_wins_and_positive_sources_can_stand_alone(self):
        single = transition("pace_steady", state="ENGAGED")
        combined = transition(
            at=20.0,
            state="ENGAGED",
            payload={
                "reasons": [
                    {"code": "pace_steady", "source_event_ids": ["later"]},
                    {"code": "facing_audience", "source_event_ids": ["vision"]},
                ]
            },
        )
        report = await generator().generate(
            completed(
                speech(wpm=144.0),
                single,
                speech(20.0, "later", wpm=145.0),
                vision(20.0, facing_score=0.8),
                combined,
            )
        )
        self.assertEqual(len(report.moments), 1)
        self.assertEqual(report.moments[0].timestamp_s, 20.0)
        self.assertIn("camera", report.moments[0].observation)
        self.assertIn("145", report.moments[0].observation)
        for code, metric in [
            ("pace_steady", speech(wpm=144.0)),
            ("facing_audience", vision(facing_score=0.8)),
        ]:
            with self.subTest(code=code):
                report = await generator().generate(
                    completed(metric, transition(code, [metric.event_id], state="ENGAGED"))
                )
                self.assertEqual(len(report.moments), 1)
                moment = report.moments[0]
                self.assertIn(metric.event_id, moment.evidence_event_ids)
                if code == "pace_steady":
                    self.assertIn("144", moment.observation)
                    self.assertNotIn("camera", moment.observation + moment.suggestion)
                else:
                    self.assertIn("appeared", moment.observation)
                    self.assertNotIn("pace", moment.observation + moment.suggestion)
                    self.assertNotIn("words per minute", moment.observation)

    async def test_repeated_causes_merge_and_reused_evidence_cannot_fill_quotas(self):
        report = await generator().generate(
            completed(
                speech(),
                transition(),
                transition(at=11.0, state="BORED"),
                transition(at=12.0, state="NEUTRAL", payload={"reasons": []}),
                transition(at=13.0),
            )
        )
        self.assertEqual(len(report.moments), 1)
        self.assertIn("audience-11.0", report.moments[0].evidence_event_ids)

    async def test_maximum_three_improvements_with_distinct_supported_incidents(self):
        events = []
        for at in [10.0, 20.0, 30.0, 40.0]:
            name = f"speech-{at}"
            events.extend(
                [
                    speech(at, name),
                    transition(refs=[name], at=at),
                    transition(at=at + 1, state="NEUTRAL", payload={"reasons": []}),
                ]
            )
        report = await generator().generate(completed(*events))
        self.assertEqual([m.timestamp_s for m in report.moments], [10.0, 20.0, 30.0])

    async def test_generator_does_not_mutate_inputs_or_retain_session_state(self):
        instance = generator()
        session = completed(speech(), transition())
        before = session.model_dump()
        first = await instance.generate(session)
        self.assertEqual(session.model_dump(), before)
        first.moments[0].evidence_event_ids.clear()
        self.assertTrue((await instance.generate(session)).moments[0].evidence_event_ids)
        empty = completed().model_dump()
        empty["session_id"] = "next"
        for item in empty["events"]:
            item["session_id"] = "next"
        report = await instance.generate(CompletedSession.model_validate(empty))
        self.assertEqual(report.session_id, "next")
        self.assertEqual(report.moments, [])

    async def test_incomplete_source_reported_without_discarding_supported_evidence(self):
        report = await generator().generate(
            completed(speech(), transition(), incomplete=["speech"])
        )
        self.assertEqual(len(report.moments), 1)
        self.assertTrue(any("did not finish" in text for text in report.limitations))

    async def test_invalid_freshness_limits_fail_explicitly(self):
        for limits in [{}, {"speech": float("nan"), "vision": 1.0}, {"speech": 1.0, "vision": 0.0}]:
            with self.subTest(limits=limits), self.assertRaises(ValueError):
                await TemplateFeedbackGenerator(stale_after_s=limits).generate(completed())


def test_injected_composition_serves_computed_feedback_through_existing_api():
    with TestClient(create_app(replay_with_coaching())) as client:
        assert client.get("/api/health").json()["live_integrated"] is False
        assert client.post("/api/sessions", json={"mode": "live"}).status_code == 503
        session_id = client.post(
            "/api/sessions",
            json={
                "fixture_case": "weak_to_improved",
                "replay_speed": 100.0,
            },
        ).json()["session_id"]
        with client.websocket_connect(f"/api/sessions/{session_id}/events") as websocket:
            websocket.receive_json()
            assert client.post(f"/api/sessions/{session_id}/start").status_code == 200
            for _ in range(150):
                message = websocket.receive_json()
                if (
                    message["kind"] == "snapshot"
                    and message["snapshot"]["feedback_status"] == "ready"
                ):
                    break
            else:
                raise AssertionError("computed feedback did not become ready")
        response = client.get(f"/api/sessions/{session_id}/feedback")
        assert response.status_code == 200
        report = response.json()
        assert report["session_id"] == session_id
        assert [(m["timestamp_s"], m["kind"]) for m in report["moments"]] == [
            (10.0, "improvement"),
            (25.0, "improvement"),
            (40.0, "strength"),
        ]
