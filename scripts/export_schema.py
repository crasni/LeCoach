"""Generate one language-neutral schema from the executable Python contracts."""

import argparse
import json
from pathlib import Path

from lecoach.contracts import CompletedSession, Event, Feedback
from lecoach.contracts.events import Model
from lecoach.contracts.interfaces import SessionConfig, SessionSnapshot


class ContractSchema(Model):
    event: Event
    config: SessionConfig
    snapshot: SessionSnapshot
    completed_session: CompletedSession
    feedback: Feedback


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    target = Path(__file__).resolve().parents[1] / "contracts" / "schema.json"
    content = json.dumps(ContractSchema.model_json_schema(), indent=2) + "\n"
    if args.check:
        if not target.exists() or target.read_text() != content:
            parser.exit(1, "Contract schema is stale; run scripts/export_schema.py.\n")
    else:
        target.parent.mkdir(exist_ok=True)
        target.write_text(content)


if __name__ == "__main__":
    main()
