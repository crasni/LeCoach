"""Inspect one canonical CompletedSession with the existing coaching generator.

This reads a local completed-session JSON, never captures or writes rehearsal
data, and never reconstructs audience decisions. JSON output is canonical Feedback;
the optional text timeline omits transcript text and all raw media.
"""

import argparse
import asyncio
import json
from pathlib import Path

from pydantic import ValidationError

from lecoach.coaching import TemplateFeedbackGenerator
from lecoach.contracts import CompletedSession, Feedback
from lecoach.engagement import DEFAULT_RULES, RuleConfig


async def generate(session: CompletedSession, rules: RuleConfig) -> Feedback:
    return await TemplateFeedbackGenerator(
        stale_after_s={"speech": rules.speech_stale_s, "vision": rules.vision_stale_s}
    ).generate(session)


def render(session: CompletedSession, feedback: Feedback, timeline: bool = False) -> str:
    lines = [f"Session {json.dumps(session.session_id)}; capture duration {session.duration_s:g} s"]
    for moment in feedback.moments:
        lines += [
            f"[{moment.timestamp_s:g} s] {moment.kind.upper()}: {moment.observation}",
            f"  Action: {moment.suggestion}",
            f"  Evidence: {json.dumps(moment.evidence_event_ids)}",
        ]
    lines += [f"Limitation: {message}" for message in feedback.limitations]
    if timeline:
        lines.append("Timeline (capture/decision times; transcript text omitted):")
        for event in session.events:
            line = f"  [{event.timestamp_s:g} s] {event.type} {json.dumps(event.event_id)}"
            if event.type == "engagement.state":
                reasons = {r.code: r.source_event_ids for r in event.payload.reasons}
                line += f" {event.payload.state}; reasons={json.dumps(reasons)}"
            lines.append(line)
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("session", type=Path, help="one canonical CompletedSession JSON file")
    parser.add_argument("--rules", type=Path, help="the session engine's RuleConfig JSON")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument(
        "--timeline", action="store_true", help="include the text-only event timeline"
    )
    args = parser.parse_args(argv)
    if args.timeline and args.format == "json":
        parser.error("--timeline is for text output; JSON output is canonical Feedback only")
    try:
        session = CompletedSession.model_validate_json(args.session.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValidationError):
        parser.error("cannot read a valid canonical CompletedSession; input contents are not shown")
    try:
        rules = (
            RuleConfig.model_validate_json(args.rules.read_text(encoding="utf-8"))
            if args.rules
            else DEFAULT_RULES
        )
    except (OSError, UnicodeError, ValidationError):
        parser.error("cannot read a valid RuleConfig; input contents are not shown")
    feedback = asyncio.run(generate(session, rules))
    print(
        feedback.model_dump_json(indent=2)
        if args.format == "json"
        else render(session, feedback, args.timeline)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
