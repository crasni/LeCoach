"""Check computed coaching against a separate, hand-derived synthetic-engine baseline.

Run: uv run python checks/coaching/feedback_replay.py [--case NAME] [--show-feedback]
No devices, files containing rehearsal output, models or network are used.
"""

import argparse
import asyncio
import json
from pathlib import Path

from lecoach.coaching.compose import replay_with_coaching
from lecoach.contracts import Feedback
from lecoach.contracts.events import validate_feedback
from lecoach.runtime.fixtures import FixtureRepository, replay_case


async def evaluate(name):
    case = FixtureRepository().load(name)
    components = []
    base = replay_with_coaching()

    def factory(config):
        current = base(config)
        components.append(current)
        return current

    result = await replay_case(case, factory=factory)
    assert len(result["feedback"]) == len(case.session_ids), "Missing computed feedback"
    feedback = [Feedback.model_validate(value) for value in result["feedback"]]
    completions = {
        e["session_id"]: e["payload"]
        for e in result["delivery_trace"]
        if e["type"] == "session.completed"
    }
    sessions = [
        component.recorder.complete(
            **{
                "duration_s": completions[report.session_id]["duration_s"],
                "incomplete_sources": completions[report.session_id]["incomplete_sources"],
            }
        )
        for component, report in zip(components, feedback, strict=True)
    ]
    for session, report in zip(sessions, feedback, strict=True):
        validate_feedback(report, session)
    return sessions, feedback, result


def check(name, sessions, feedback):
    baseline = json.loads(Path(__file__).with_name("engine_expectations.json").read_text())
    oracles = baseline[name]
    assert len(sessions) == len(oracles), "Session count differs"
    for session, report, expected in zip(sessions, feedback, oracles, strict=True):
        transitions = [
            [
                e.timestamp_s,
                e.payload.state,
                {r.code: r.source_event_ids for r in e.payload.reasons},
            ]
            for e in session.events
            if e.type == "engagement.state"
        ]
        assert transitions == expected["transitions"], f"{name}: engine evidence changed"
        moments = [[m.timestamp_s, m.kind, m.evidence_event_ids] for m in report.moments]
        assert moments == expected["moments"], f"{name}: coaching anchors changed"
        for phrase in expected["limitations_contain"]:
            assert any(phrase in text for text in report.limitations), f"Missing: {phrase}"


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    names = [d["name"] for d in FixtureRepository().describe()]
    parser.add_argument("--case", choices=names)
    parser.add_argument("--show-feedback", action="store_true")
    args = parser.parse_args()
    total = 0
    for name in [args.case] if args.case else names:
        sessions, feedback, _ = await evaluate(name)
        check(name, sessions, feedback)
        total += len(sessions)
        print(f"PASS {name}: computed audience, recorded timeline and coaching anchors")
        if args.show_feedback:
            print(json.dumps([report.model_dump() for report in feedback], indent=2))
    print(f"Verified {total} synthetic sessions; no live input or inference was exercised.")


if __name__ == "__main__":
    asyncio.run(main())
