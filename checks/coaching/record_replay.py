"""Exercise the production recorder against hand-authored, synthetic cases.

Run from the root: uv run python checks/coaching/record_replay.py
No inference or computed feedback is involved. Nothing is saved to disk.
"""

import asyncio

from check_cases import check_completed, load_case

from lecoach.coaching import InMemorySessionRecorder
from lecoach.contracts.interfaces import Components
from lecoach.runtime.fixtures import FixtureRepository, replay_case


async def main() -> None:
    repository = FixtureRepository()
    total = 0
    for description in repository.describe():
        name = description["name"]
        spec, expected_sessions = load_case(name)
        recorders: list[InMemorySessionRecorder] = []

        def factory(config):
            recorder = InMemorySessionRecorder()
            recorders.append(recorder)
            return Components(recorder=recorder)

        result = await replay_case(repository.load(name), factory=factory)
        assert not result["feedback"], "Recorder-only replay must not invent feedback"
        assert len(recorders) == len(expected_sessions)
        for recorder, oracle, expected in zip(recorders, spec["sessions"], expected_sessions):
            actual = recorder.complete(oracle["duration_s"], oracle["incomplete_sources"])
            check_completed(actual.model_dump(), expected)
            total += 1
        print(f"PASS {name}: production recorder matches synthetic retained-event oracle")
    print(f"Recorded {total} synthetic sessions; no live devices or computed coaching verified.")


if __name__ == "__main__":
    asyncio.run(main())
