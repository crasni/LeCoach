"""Replays the reviewed synthetic speech scenarios through the production pipeline."""

import importlib.util
import json
import sys
from pathlib import Path
from unittest import TestCase

from lecoach.contracts import parse_event
from lecoach.speech.config import SpeechConfig
from lecoach.speech.pipeline import SpeechPipeline
from lecoach.speech.seams import Transcription

CHECKS = Path(__file__).resolve().parents[1] / "checks" / "speech"


def load(name):
    """Load a standalone checks/speech module (they import siblings by bare name)."""
    sys.path.insert(0, str(CHECKS))
    try:
        spec = importlib.util.spec_from_file_location(f"speech_checks_{name}",
                                                      CHECKS / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(CHECKS))


GENERATOR, CHECKER = load("make_fixtures"), load("check_speech")


def fixture_config(spec):
    rules = GENERATOR.RULES
    return SpeechConfig(
        language=spec.get("language", "en"),
        metrics_window_s=rules["window_s"],
        metrics_hop_s=rules["hop_s"],
        min_observation_s=rules["min_observation_s"],
        pause_min_s=rules["pause_min_s"],
        coverage_wait_s=rules["max_wait_s"],
    )


def replay(spec):
    """Feed one scenario's capture-time inputs in arrival order; return emitted events."""
    pipeline = SpeechPipeline(spec["session_id"], fixture_config(spec))
    end, latency = spec["capture_end"], GENERATOR.LATENCY
    utterances = sorted(spec.get("utterances", []), key=lambda item: item["start"])
    inputs = []
    for seq, item in enumerate(utterances, 1):
        partials = (GENERATOR.auto_partials(item) if item["partials"] is None
                    else item["partials"])
        final_at = item["final_at"] or item["end"] + (
            latency["drain_final"] if item["end"] >= end else latency["final"])
        inputs.append((item["start"], 0, pipeline.speech_started, (seq, item["start"])))
        for partial in partials:
            inputs.append((partial[0] + latency["partial"], 2, pipeline.partial,
                           (seq, partial[1], partial[0])))
        inputs.append((item["end"], 1, pipeline.speech_ended, (seq, item["end"])))
        inputs.append((final_at, 3, pipeline.finalized, (seq, Transcription(item["text"]))))
    for time, availability, reason in spec.get("status", []):
        inputs.append((time, 1, pipeline.unavailable, (time, availability, reason)))
    inputs.sort(key=lambda item: item[:2])
    events, cursor = [], 0
    for step in range(int(end / 0.05 + 1e-9) + 1):
        now = round(step * 0.05, 3)
        while cursor < len(inputs) and inputs[cursor][0] <= now + 1e-9:
            _, _, method, args = inputs[cursor]
            events += method(*args)
            cursor += 1
        events += pipeline.advance(now)
    for _, _, method, args in inputs[cursor:]:
        events += method(*args)
    return events + pipeline.finish(end)


def committed(case, session_id):
    events = json.loads((CHECKS / "fixtures" / f"{case}.json").read_text(encoding="utf-8"))
    return {event["event_id"]: event for event in events if event["session_id"] == session_id}


class SpeechPipelineParityTests(TestCase):
    def sessions(self):
        for case, specs in GENERATOR.SCENARIOS.items():
            for spec in specs:
                yield case, spec

    def test_metrics_match_the_committed_fixtures(self):
        for case, spec in self.sessions():
            with self.subTest(case=case, session=spec["session_id"]):
                expected = {event_id: event["payload"]
                            for event_id, event in committed(case, spec["session_id"]).items()
                            if event["type"] == "speech.metrics"}
                produced = {event["event_id"]: event["payload"] for event in replay(spec)
                            if event["type"] == "speech.metrics"}
                self.assertTrue(expected)
                self.assertEqual(produced, expected)

    def test_transcripts_and_statuses_match_the_committed_fixtures(self):
        for case, spec in self.sessions():
            with self.subTest(case=case, session=spec["session_id"]):
                expected = {event_id: event["payload"]
                            for event_id, event in committed(case, spec["session_id"]).items()
                            if event["type"] in ("speech.transcript", "signal.status")}
                produced = {event["event_id"]: event["payload"] for event in replay(spec)
                            if event["type"] in ("speech.transcript", "signal.status")}
                self.assertEqual(produced, expected)

    def test_emitted_streams_validate_and_pass_the_producer_checks(self):
        for case, spec in self.sessions():
            with self.subTest(case=case, session=spec["session_id"]):
                events = replay(spec)
                for event in events:
                    parse_event(event)
                end = spec["capture_end"]
                envelope = {"schema_version": 0, "session_id": spec["session_id"],
                            "source": "session"}
                stream = (
                    [{**envelope, "event_id": "00-start", "type": "session.started",
                      "timestamp_s": 0, "payload": {}}]
                    + events
                    + [{**envelope, "event_id": "90-stop", "type": "session.stopping",
                        "timestamp_s": end, "payload": {}},
                       {**envelope, "event_id": "99-completed", "type": "session.completed",
                        "timestamp_s": end,
                        "payload": {"duration_s": end, "incomplete_sources": []}}])
                CHECKER.check_stream(stream, {"min_observation_s": 5.0, "pause_min_s": 1.0})

    def test_late_finals_beyond_the_coverage_wait_report_null(self):
        pipeline = SpeechPipeline("late", SpeechConfig(metrics_hop_s=5.0))
        pipeline.speech_started(1, 1.0)
        pipeline.speech_ended(1, 4.0)
        self.assertEqual(pipeline.advance(7.9), [])
        late = pipeline.advance(8.0)
        self.assertEqual([event["event_id"] for event in late], ["metrics-5"])
        self.assertIsNone(late[0]["payload"]["wpm"])
        final = pipeline.finalized(1, Transcription("finally transcribed words"))
        self.assertEqual([event["type"] for event in final], ["speech.transcript"])
