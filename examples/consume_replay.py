"""A downstream consumer uses only public contracts and the replay seam.

This is a synthetic event subscription example, not a session recorder.
Run from the repository root: uv run python examples/consume_replay.py
"""

import asyncio
from collections import Counter

from lecoach.contracts import Event
from lecoach.runtime.fixtures import FixtureRepository, replay_case


async def main():
    counts = Counter()

    def on_event(event: Event):
        counts[event.type] += 1

    result = await replay_case(FixtureRepository().load("weak_to_improved"), on_event=on_event)
    print(f"Synthetic subscription received {dict(counts)}")
    print(
        f"Replay delivered {len(result['delivery_trace'])} normalized events; feedback is authored."
    )


if __name__ == "__main__":
    asyncio.run(main())
