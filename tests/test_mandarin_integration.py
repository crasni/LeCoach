"""Synthetic Mandarin fallback conformance; no capture, ASR or localized browser."""

import asyncio
import json
from pathlib import Path

import pytest

from lecoach.coaching import InMemorySessionRecorder
from lecoach.contracts import Feedback, parse_event
from lecoach.contracts.interfaces import Components
from lecoach.engagement import RuleEngine
from lecoach.runtime.fixtures import FixtureCase, replay_case

ROOT = Path(__file__).resolve().parents[1] / "checks/integration/mandarin"
EXPECTED = {
    "mandarin_facing_recovery": ["NEUTRAL", "BORED", "INTERESTED", "ENGAGED"],
    "mandarin_mixed_content": ["NEUTRAL", "INTERESTED", "ENGAGED"],
    "mandarin_camera_missing": ["NEUTRAL"],
    "mandarin_long_pause": ["NEUTRAL", "BORED"],
    "mandarin_short": ["NEUTRAL"],
}


@pytest.mark.parametrize("name", EXPECTED)
def test_mandarin_unknown_metrics_do_not_invent_pace_or_fillers(name):
    fixture = json.loads((ROOT / f"{name}.json").read_text())
    events = [parse_event(e) for e in fixture["events"]]
    metrics = [e.payload for e in events if e.type == "speech.metrics"]
    assert metrics and all(
        p.wpm is None and p.filler_count is None and p.filler_rate_per_min is None
        for p in metrics
    )
    feedback = Feedback.model_validate(fixture["authored_feedback"])
    case = FixtureCase(
        name, "合成中文觀察；沒有啟用裝置或模型", events, {feedback.session_id: feedback}
    )
    recorders = []

    def factory(config):
        recorder = InMemorySessionRecorder()
        recorders.append(recorder)
        return Components(engagement=RuleEngine(), recorder=recorder)

    result = asyncio.run(replay_case(case, factory=factory))
    transitions = [e for e in result["delivery_trace"] if e["type"] == "engagement.state"]
    assert [e["payload"]["state"] for e in transitions] == EXPECTED[name]
    allowed = {"facing_away_sustained", "facing_audience", "silence_prolonged"}
    source_events = {e.event_id: e for e in events}
    for transition in transitions:
        for reason in transition["payload"]["reasons"]:
            assert reason["code"] in allowed
            for event_id in reason["source_event_ids"]:
                source = source_events[event_id]
                assert source.timestamp_s <= transition["timestamp_s"]
                if reason["code"] == "silence_prolonged":
                    assert source.payload.pause.state == "active"
                else:
                    assert source.source == "vision"
    completed = recorders[0].complete(fixture["duration_s"], [])
    assert completed.session_id == feedback.session_id
    finals = [e for e in completed.events if e.type == "speech.transcript" and e.payload.is_final]
    assert finals and any("\u4e00" <= char <= "\u9fff" for e in finals for char in e.payload.text)
    if name == "mandarin_mixed_content":
        text = "".join(e.payload.text for e in finals)
        assert "LeCoach" in text and "12" in text and "那個部門" in text and "就是這項功能" in text
    # Recorder-only composition must not install authored sample advice as computed coaching.
    assert result["feedback"] == []


def test_mandarin_repeated_replays_remain_isolated():
    fixture = json.loads((ROOT / "mandarin_facing_recovery.json").read_text())
    original = fixture["authored_feedback"]
    session_ids = [original["session_id"], original["session_id"] + "-second"]
    events = [
        parse_event({**e, "session_id": sid}) for sid in session_ids for e in fixture["events"]
    ]
    feedback = {
        sid: Feedback.model_validate({**original, "session_id": sid}) for sid in session_ids
    }
    recorders = []

    def factory(config):
        recorder = InMemorySessionRecorder()
        recorders.append(recorder)
        return Components(engagement=RuleEngine(), recorder=recorder)

    case = FixtureCase("mandarin_repeat", "兩次合成練習", events, feedback)
    asyncio.run(replay_case(case, factory))
    for sid, recorder in zip(session_ids, recorders, strict=True):
        completed = recorder.complete(fixture["duration_s"], [])
        assert {e.session_id for e in completed.events} == {sid}
