import copy

import pytest
from pydantic import ValidationError

from lecoach.contracts import Feedback, parse_event
from lecoach.runtime.fixtures import FixtureRepository
from tests.helpers import event


def test_all_reviewed_fixtures_validate():
    repo = FixtureRepository()
    assert len(repo.describe()) == 9
    assert sum(len(repo.load(case["name"]).session_ids) for case in repo.describe()) == 10


@pytest.mark.parametrize(
    "change",
    [
        {"schema_version": False},
        {"timestamp_s": True},
        {"timestamp_s": float("nan")},
        {"timestamp_s": float("inf")},
        {"source": "vision"},
        {"schema_version": "0"},
        {"timestamp_s": -1},
        {"event_id": "   "},
        {"unknown_field": 1},
    ],
)
def test_invalid_envelope_rejected(change):
    value = event().model_dump()
    value.update(change)
    with pytest.raises(ValidationError):
        parse_event(value)


@pytest.mark.parametrize(
    "key,value",
    [
        ("window_start_s", 2.0),
        ("window_end_s", 5.0),
        ("wpm", float("nan")),
        ("filler_count", 1.5),
        ("filler_count", True),
        ("wpm", "144"),
    ],
)
def test_invalid_metric_rejected(key, value):
    data = event().model_dump()
    data["payload"][key] = value
    with pytest.raises(ValidationError):
        parse_event(data)


def test_unknown_values_are_preserved():
    data = event().model_dump()
    data["payload"].update(
        wpm=None,
        filler_count=None,
        filler_rate_per_min=None,
        pause={"state": "unknown", "duration_s": None, "start_s": None, "end_s": None},
    )
    assert parse_event(data).payload.wpm is None


def test_no_person_cannot_supply_facing_score():
    data = FixtureRepository().load("weak_to_improved").events[3].model_dump()
    data["payload"]["person_present"] = False
    with pytest.raises(ValidationError):
        parse_event(data)


def test_invalid_pause_and_feedback_quota_rejected():
    data = event().model_dump()
    data["payload"]["pause"] = {
        "state": "completed",
        "start_s": 0.0,
        "end_s": 1.0,
        "duration_s": 5.0,
    }
    with pytest.raises(ValidationError):
        parse_event(data)
    feedback = next(iter(FixtureRepository().load("weak_to_improved").authored_feedback.values()))
    value = feedback.model_dump()
    value["moments"].append(copy.deepcopy(value["moments"][-1]))
    with pytest.raises(ValidationError):
        Feedback.model_validate(value)
