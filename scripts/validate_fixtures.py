"""Validate all reviewed synthetic inputs using executable v0 contracts."""

from lecoach.runtime.fixtures import FixtureRepository

repository = FixtureRepository()
sessions = 0
for description in repository.describe():
    case = repository.load(description["name"])
    sessions += len(case.session_ids)
    print(f"PASS {case.name}: {len(case.events)} authored input events")
print(f"Validated {len(repository.describe())} synthetic cases / {sessions} sessions.")
