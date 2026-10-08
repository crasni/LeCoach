import argparse
import asyncio
import json
from pathlib import Path

from lecoach.engagement.compose import replay_with_engine
from lecoach.runtime.fixtures import FixtureRepository, replay_case


def main() -> None:
    parser = argparse.ArgumentParser(description="LeCoach local integration scaffold")
    sub = parser.add_subparsers(dest="command", required=True)
    replay = sub.add_parser("replay", help="Replay hand-authored synthetic fixtures headlessly")
    replay.add_argument("--case", default="weak_to_improved")
    replay.add_argument("--output", type=Path, help="Explicitly save a synthetic delivery trace")
    replay.add_argument(
        "--audience",
        choices=("engine", "authored"),
        default="engine",
        help="Compute audience states with the engagement engine, or keep authored ones",
    )
    sub.add_parser("serve", help="Serve the loopback API and built frontend")
    args = parser.parse_args()
    if args.command == "serve":
        import uvicorn

        uvicorn.run("lecoach.api.app:app", host="127.0.0.1", port=8000)
    else:
        try:
            result = asyncio.run(
                replay_case(
                    FixtureRepository().load(args.case),
                    replay_with_engine() if args.audience == "engine" else None,
                )
            )
        except (OSError, ValueError) as error:
            parser.exit(1, f"Replay failed: {error}\n")
        serialized = json.dumps(result, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(serialized)
            print(f"Saved synthetic delivery trace to {args.output}")
        else:
            print(serialized, end="")
