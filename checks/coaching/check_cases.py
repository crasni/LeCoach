"""Check synthetic COACH-01 cases and, later, real consumer output.

This is a test utility, not a recorder, replay clock, engagement engine, or
feedback generator. ARCHITECTURE.md remains the interface authority.
"""

import argparse
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EVENT_SOURCES = {
    "session.started": "session",
    "session.stopping": "session",
    "session.completed": "session",
    "speech.transcript": "speech",
    "speech.metrics": "speech",
    "vision.metrics": "vision",
    "engagement.state": "engagement",
}


class CheckError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise CheckError(message)


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def read_json(path):
    def reject_constant(value):
        raise CheckError(f"Non-JSON numeric value: {value}")

    return json.loads(Path(path).read_text(encoding="utf-8"),
                      parse_constant=reject_constant)


def check_event(event):
    require(isinstance(event, dict), "Event must be an object")
    require({"schema_version", "session_id", "event_id", "source", "type",
             "timestamp_s", "payload"} <= event.keys(), "Incomplete event envelope")
    require(type(event["schema_version"]) is int and event["schema_version"] == 0,
            "Expected schema_version 0")
    require(text(event["session_id"]) and text(event["event_id"]), "Missing event identity")
    require(number(event["timestamp_s"]) and event["timestamp_s"] >= 0,
            "Invalid capture/decision timestamp")
    kind, payload = event["type"], event["payload"]
    require(isinstance(payload, dict), "Payload must be an object")
    if kind == "signal.status":
        require(event["source"] in ("speech", "vision"), "Invalid status source")
        require(payload.get("availability") in ("available", "unavailable", "error"),
                "Invalid availability")
        require(text(payload.get("reason")), "Missing status reason")
    else:
        require(kind in EVENT_SOURCES and event["source"] == EVENT_SOURCES[kind],
                "Unsupported fixture event type/source")
    if kind in ("speech.metrics", "vision.metrics"):
        start, end = payload.get("window_start_s"), payload.get("window_end_s")
        require(number(start) and number(end) and 0 <= start <= end,
                "Invalid observation window")
        require(end == event["timestamp_s"], "Metric timestamp must be window end")
        require(payload.get("availability") in ("available", "unavailable", "error"),
                "Missing metric availability")
        fields = ("wpm", "filler_count", "filler_rate_per_min") if kind == "speech.metrics" \
            else ("facing_score", "activity_score")
        for field in fields:
            require(field in payload, f"Missing {field}")
            value = payload[field]
            require(value is None or (number(value) and value >= 0), f"Invalid {field}")
            if kind == "vision.metrics":
                require(value is None or value <= 1, f"Invalid {field} range")
        if kind == "vision.metrics":
            for field in ("person_present", "pose_available"):
                require(field in payload and
                        (payload[field] is None or type(payload[field]) is bool),
                        f"Invalid {field}")
            if payload["person_present"] is False or payload["pose_available"] is False:
                require(payload["facing_score"] is None and payload["activity_score"] is None,
                        "Missing pose/person cannot supply derived scores")
        else:
            require(payload["filler_count"] is None or type(payload["filler_count"]) is int,
                    "Filler count must be an integer")
            pause = payload.get("pause", {})
            require(pause.get("state") in ("none", "active", "completed", "unknown"),
                    "Invalid pause state")
            require({"duration_s", "start_s", "end_s"} <= pause.keys(), "Incomplete pause")
            if pause["state"] == "unknown":
                require(pause["duration_s"] is None, "Unknown pause must have null duration")
    if kind == "speech.transcript":
        require(text(payload.get("utterance_id")), "Missing utterance identity")
        require(type(payload.get("revision")) is int and payload["revision"] >= 0,
                "Invalid transcript revision")
        require(type(payload.get("is_final")) is bool and isinstance(payload.get("text"), str),
                "Invalid transcript content")
        require(number(payload.get("start_s")) and number(payload.get("end_s")) and
                0 <= payload["start_s"] <= payload["end_s"] == event["timestamp_s"],
                "Invalid transcript capture interval")
    if kind == "engagement.state":
        states = {"ENGAGED", "NEUTRAL", "CONFUSED", "BORED", "INTERESTED"}
        require(payload.get("state") in states and payload.get("previous_state") in states,
                "Invalid audience state")
        require(isinstance(payload.get("reasons"), list), "Missing transition reasons")
        sources = payload.get("usable_sources")
        require(isinstance(sources, list) and len(sources) == len(set(sources)) and
                set(sources) <= {"speech", "vision"}, "Invalid usable sources")
        for reason in payload["reasons"]:
            require(text(reason.get("code")) and isinstance(reason.get("source_event_ids"), list)
                    and reason["source_event_ids"], "Missing transition evidence")


def check_completed(actual, expected):
    require(isinstance(actual, dict), "Completed session must be an object")
    for key in ("session_id", "duration_s", "incomplete_sources"):
        require(actual.get(key) == expected[key], f"Completed session has wrong {key}")
    require(number(actual["duration_s"]), "Invalid completed duration")
    require(actual.get("events") == expected["events"],
            "Completed timeline differs from retained events (order, duplicates, drain, or isolation)")


def check_feedback(actual, expected, session):
    require(isinstance(actual, dict) and set(actual) ==
            {"session_id", "duration_s", "moments", "limitations"}, "Invalid Feedback fields")
    require(actual["session_id"] == session["session_id"] and
            number(actual["duration_s"]) and actual["duration_s"] == session["duration_s"],
            "Feedback identity/duration differs from its completed session")
    require(isinstance(actual["limitations"], list) and all(text(x) for x in actual["limitations"]),
            "Limitations must be plain-language strings")
    if expected["limitations"]:
        require(actual["limitations"], "Missing input/insufficient-evidence limitation")
    require(isinstance(actual["moments"], list) and
            len(actual["moments"]) == len(expected["moments"]),
            "Moment count differs from the scenario's evidence-supported expectation")
    events = {event["event_id"]: event for event in session["events"]}
    remaining = {(moment["kind"], moment["timestamp_s"]): moment
                 for moment in expected["moments"]}
    for moment in actual["moments"]:
        require(isinstance(moment, dict) and set(moment) ==
                {"timestamp_s", "kind", "observation", "suggestion", "evidence_event_ids"},
                "Invalid Moment fields")
        require(number(moment["timestamp_s"]) and
                0 <= moment["timestamp_s"] <= session["duration_s"], "Invalid moment timestamp")
        require(text(moment["observation"]) and text(moment["suggestion"]),
                "Every moment needs an observation and action")
        target = remaining.pop((moment["kind"], moment["timestamp_s"]), None)
        require(target is not None, "Unplanned, duplicate, or incorrectly timed moment")
        ids = moment["evidence_event_ids"]
        require(isinstance(ids, list) and ids and all(text(x) for x in ids) and
                len(ids) == len(set(ids)), "Missing/duplicate evidence IDs")
        require(set(target["evidence_event_ids"]) <= set(ids), "Missing expected supporting evidence")
        require(all(event_id in events for event_id in ids), "Dangling or cross-session evidence")
        require(any(events[x]["type"] == "engagement.state" for x in ids),
                "Moment must refer to the recorded audience output")
        measurements = [events[x] for x in ids if events[x]["type"] in
                        ("speech.metrics", "vision.metrics")]
        require(measurements, "Moment has no supporting measurements")
        for event in measurements:
            payload = event["payload"]
            fields = ("wpm", "filler_rate_per_min") if event["source"] == "speech" \
                else ("facing_score", "activity_score")
            require(payload["availability"] == "available" and
                    any(payload.get(field) is not None for field in fields),
                    "Unavailable/unknown observation used as delivery evidence")
        require(all(events[x]["type"] not in
                    ("signal.status", "session.started", "session.stopping", "session.completed")
                    for x in ids), "Input/lifecycle limitation used as coaching evidence")


def load_case(name):
    cases = read_json(ROOT / "expectations.json")
    require(name in cases, f"Unknown case: {name}")
    spec = cases[name]
    arrivals = read_json(ROOT / "fixtures" / f"{name}.json")
    require(isinstance(arrivals, list), "Fixture must be an event array in delivery order")
    index = {}
    for event in arrivals:
        check_event(event)
        key = (event["session_id"], event["event_id"])
        require(key not in index or index[key] == event, "Retry changed a stable event ID")
        index[key] = event
    sessions = []
    for oracle in spec["sessions"]:
        ids = oracle["retained_event_ids"]
        require(len(ids) == len(set(ids)), "Oracle includes a duplicate event")
        events = [index[(oracle["session_id"], event_id)] for event_id in ids]
        require(events == sorted(events, key=lambda x: (x["timestamp_s"], x["event_id"])),
                "Oracle timeline is not ordered by capture time and event ID")
        require(all(event["timestamp_s"] <= oracle["duration_s"] for event in events),
                "Oracle retained capture after session end")
        completed = [event for event in events if event["type"] == "session.completed"]
        require(len(completed) == 1 and completed[0]["timestamp_s"] == oracle["duration_s"]
                and completed[0]["payload"] == {
                    "duration_s": oracle["duration_s"],
                    "incomplete_sources": oracle["incomplete_sources"]},
                "Oracle and lifecycle completion disagree")
        retained = {event["event_id"]: event for event in events}
        for event in events:
            if event["type"] != "engagement.state":
                continue
            for reason in event["payload"]["reasons"]:
                for event_id in reason["source_event_ids"]:
                    require(event_id in retained, "Transition has dangling evidence")
                    source = retained[event_id]
                    require(source["type"] in ("speech.metrics", "vision.metrics") and
                            source["source"] in event["payload"]["usable_sources"] and
                            source["timestamp_s"] <= event["timestamp_s"] and
                            source["payload"]["availability"] == "available",
                            "Transition uses unavailable or future evidence")
        session = {"session_id": oracle["session_id"], "duration_s": oracle["duration_s"],
                   "events": events, "incomplete_sources": oracle["incomplete_sources"]}
        check_feedback(oracle["feedback"], oracle["feedback"], session)
        sessions.append(session)
    return spec, sessions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", help="Check one named synthetic case")
    parser.add_argument("--completed", type=Path, help="JSON array of real CompletedSession outputs")
    parser.add_argument("--feedback", type=Path, help="JSON array of real Feedback outputs")
    args = parser.parse_args()
    if (args.completed or args.feedback) and not args.case:
        parser.error("--completed/--feedback requires --case")
    try:
        names = [args.case] if args.case else list(read_json(ROOT / "expectations.json"))
        total = 0
        for name in names:
            spec, sessions = load_case(name)
            for path, check, expectations in (
                (args.completed, check_completed, sessions),
                (args.feedback, check_feedback, [x["feedback"] for x in spec["sessions"]]),
            ):
                if path is None:
                    continue
                outputs = read_json(path)
                require(isinstance(outputs, list) and len(outputs) == len(sessions),
                        "Output batch has wrong session count")
                for actual, expected, session in zip(outputs, expectations, sessions):
                    if check is check_feedback:
                        check(actual, expected, session)
                    else:
                        check(actual, expected)
            total += len(sessions)
            print(f"PASS {name}: synthetic fixture and hand-authored expectations")
        print(f"Checked {len(names)} cases / {total} expected sessions. "
              "This does not verify a live pipeline or a production feedback generator.")
    except (CheckError, OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        parser.exit(1, f"FAIL: {error}\n")


if __name__ == "__main__":
    main()
