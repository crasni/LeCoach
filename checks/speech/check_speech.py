"""Check LeCoach speech event streams against the v0 speech contract.

Lane 2 (AUD-01) preparation utility. It checks the synthetic fixtures now and a
speech adapter's recorded event stream later. It is a test utility, not a
speech adapter, session controller, replay clock, logger, or engagement engine.
ARCHITECTURE.md remains the interface authority; README.md documents the
proposed v0 speech rules applied here.
"""

import argparse
import json
import math
from pathlib import Path

from speech_text import filler_count, word_count


ROOT = Path(__file__).resolve().parent
# Proposed v0 limits (README.md). Pass the agreed values when checking real output.
DEFAULTS = {"min_observation_s": 5.0, "pause_min_s": 1.0, "tolerance_s": 0.05}
AVAILABILITY = ("available", "unavailable", "error")
PAUSE_STATES = ("none", "active", "completed", "unknown")
LIFECYCLE = ("session.started", "session.stopping", "session.completed")
ORACLE_KEYS = ("capture_end_s", "final_transcript", "finalized_words", "finalized_fillers",
               "completed_pauses", "longest_active_pause_s", "speech_status",
               "null_wpm_metrics", "unavailable_metrics", "wpm_min", "wpm_max")


class CheckError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise CheckError(message)


def number(value):
    return type(value) in (int, float) and math.isfinite(value)


def close(left, right, tolerance=1e-6):
    return abs(left - right) <= tolerance


def overlaps(start, end, window_start, window_end):
    return start < window_end - 1e-9 and end > window_start + 1e-9


def _reject_constant(value):
    raise CheckError(f"Non-JSON numeric value: {value}")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), parse_constant=_reject_constant)


def read_stream(path):
    """Read a JSON array, or JSON Lines for a .jsonl file, in delivery order."""
    if Path(path).suffix != ".jsonl":
        return read_json(path)
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [json.loads(line, parse_constant=_reject_constant) for line in lines if line.strip()]


def check_pause(pause, window_end, tolerance):
    require(isinstance(pause, dict) and pause.get("state") in PAUSE_STATES,
            "Invalid pause state")
    require({"duration_s", "start_s", "end_s"} <= pause.keys(), "Incomplete pause")
    state, duration, start, end = (pause[key] for key in
                                   ("state", "duration_s", "start_s", "end_s"))
    if state == "none":
        require(duration == 0 and start is None and end is None,
                "Pause state none needs duration 0 and null start/end")
    elif state == "unknown":
        require(duration is None and start is None and end is None,
                "Unknown pause needs null duration/start/end, not zero")
    elif state == "active":
        require(number(start) and end is None and number(duration) and
                start <= window_end + tolerance and
                close(duration, window_end - start, tolerance),
                "Active pause needs a start, null end, and elapsed duration to window end")
    else:
        require(number(start) and number(end) and number(duration) and
                start < end <= window_end + tolerance and
                close(duration, end - start, tolerance),
                "Completed pause needs start < end <= window end and their difference")


def check_event(event, tolerance=DEFAULTS["tolerance_s"]):
    """Check one speech or lifecycle event's envelope and payload shape."""
    require(isinstance(event, dict), "Event must be an object")
    require({"schema_version", "session_id", "event_id", "source", "type", "timestamp_s",
             "payload"} <= event.keys(), "Incomplete event envelope")
    require(type(event["schema_version"]) is int and event["schema_version"] == 0,
            "Expected schema_version 0")
    require(all(isinstance(event[key], str) and event[key].strip()
                for key in ("session_id", "event_id")), "Missing session or event identity")
    try:
        kind, payload, at = event["type"], event["payload"], event["timestamp_s"]
        require(number(at) and at >= 0, "Invalid capture timestamp")
        require(isinstance(payload, dict), "Payload must be an object")
        if kind in LIFECYCLE:
            require(event["source"] == "session", "Lifecycle events use source session")
            if kind == "session.completed":
                require(number(payload.get("duration_s")) and
                        close(payload["duration_s"], at) and
                        isinstance(payload.get("incomplete_sources"), list),
                        "Completion needs duration_s at the capture end and "
                        "incomplete_sources")
            return
        require(event["source"] == "speech", "Speech events use source speech")
        if kind == "signal.status":
            require(payload.get("availability") in AVAILABILITY, "Invalid availability")
            require(isinstance(payload.get("reason"), str) and payload["reason"].strip(),
                    "Missing status reason")
        elif kind == "speech.transcript":
            require(isinstance(payload.get("utterance_id"), str) and
                    payload["utterance_id"].strip(), "Missing utterance identity")
            require(type(payload.get("revision")) is int and payload["revision"] >= 0,
                    "Invalid transcript revision")
            require(type(payload.get("is_final")) is bool and
                    isinstance(payload.get("text"), str), "Invalid transcript content")
            require(number(payload.get("start_s")) and number(payload.get("end_s")) and
                    0 <= payload["start_s"] <= payload["end_s"] and
                    close(payload["end_s"], at),
                    "Transcript needs capture start <= end, with timestamp_s at end_s")
        elif kind == "speech.metrics":
            start, end = payload.get("window_start_s"), payload.get("window_end_s")
            require(number(start) and number(end) and 0 <= start < end and close(end, at),
                    "Metrics need a capture window with timestamp_s at window_end_s")
            require(payload.get("availability") in AVAILABILITY, "Invalid availability")
            for field in ("wpm", "filler_count", "filler_rate_per_min", "pause"):
                require(field in payload, f"Missing {field}")
            wpm, count, rate = (payload[key] for key in
                                ("wpm", "filler_count", "filler_rate_per_min"))
            require(wpm is None or (number(wpm) and wpm >= 0), "Invalid wpm")
            require(count is None or (type(count) is int and count >= 0),
                    "Filler count must be a non-negative integer or null")
            require((count is None) == (rate is None),
                    "Filler count and rate must be null together")
            if count is not None:
                # The tolerance allows the published rate to be rounded to an integer.
                require(number(rate) and close(rate, count * 60 / (end - start), 0.5),
                        "Filler rate must equal filler_count per window minute")
            check_pause(payload["pause"], end, tolerance)
            if payload["availability"] != "available":
                require(wpm is None and count is None and
                        payload["pause"]["state"] == "unknown",
                        "Unavailable input must report null metrics and an unknown pause")
        else:
            raise CheckError(f"Unsupported speech event type {kind!r}")
    except CheckError as error:
        raise CheckError(f"{event['event_id']}: {error}") from None


def check_session(arrivals, config=None):
    """Check one session's speech and lifecycle events, given in delivery order.

    Returns the reconstruction a consumer should derive: the canonical final
    transcript, finalized word and filler totals, pauses, and metric availability.
    """
    config = {**DEFAULTS, **(config or {})}
    tolerance = config["tolerance_s"]
    for event in arrivals:
        check_event(event, tolerance)
    session_id = arrivals[0]["session_id"]

    # Deliveries: identical retries are allowed; nothing follows completion.
    first, completed = {}, False
    for position, event in enumerate(arrivals):
        require(event["session_id"] == session_id, "Mixed sessions in one session check")
        require(not completed, f"{event['event_id']}: delivered after session.completed")
        if event["event_id"] in first:
            require(first[event["event_id"]][1] == event,
                    f"{event['event_id']}: retry changed a stable event ID")
            continue
        first[event["event_id"]] = (position, event)
        completed = event["type"] == "session.completed"
    of_type = {}
    for position, event in sorted(first.values(), key=lambda item: item[0]):
        of_type.setdefault(event["type"], []).append((position, event))

    # Lifecycle.
    for kind in LIFECYCLE:
        require(len(of_type.get(kind, [])) <= 1, f"More than one {kind}")
    if "session.started" in of_type:
        require(of_type["session.started"][0][1]["timestamp_s"] == 0,
                "session.started must be at timestamp 0")
    capture_end = of_type["session.stopping"][0][1]["timestamp_s"] \
        if "session.stopping" in of_type else None
    incomplete = []
    if "session.completed" in of_type:
        completion = of_type["session.completed"][0][1]
        incomplete = completion["payload"]["incomplete_sources"]
        require(capture_end is not None and close(completion["timestamp_s"], capture_end),
                "session.completed must follow session.stopping at the capture end")
    if capture_end is not None:
        for _, event in first.values():
            require(event["source"] != "speech" or
                    event["timestamp_s"] <= capture_end + tolerance,
                    f"{event['event_id']}: capture time after the capture end")

    # Transcripts: revisions, finals, and reconciled utterances.
    revisions, finals, final_at = {}, {}, {}
    for position, event in of_type.get("speech.transcript", []):
        payload = event["payload"]
        utterance, revision = payload["utterance_id"], payload["revision"]
        known = revisions.setdefault(utterance, {})
        require(revision not in known,
                f"{utterance}: revision {revision} has two different event IDs")
        known[revision] = (position, payload)
        if payload["is_final"]:
            require(utterance not in finals,
                    f"{utterance}: finalized more than once with different event IDs")
            finals[utterance], final_at[utterance] = payload, position
    for utterance, known in revisions.items():
        if utterance in finals:
            require(max(known) == finals[utterance]["revision"],
                    f"{utterance}: revision after the final; a final freezes the utterance")
        partial_ends = [known[r][1]["end_s"] for r in sorted(known)
                        if not known[r][1]["is_final"]]
        require(partial_ends == sorted(partial_ends),
                f"{utterance}: partial end times must not move backwards")
        if "session.completed" in of_type and "speech" not in incomplete:
            require(utterance in finals,
                    f"{utterance}: never finalized before session.completed")
    spoken = sorted(finals.values(), key=lambda item: (item["start_s"], item["end_s"]))
    for before, after in zip(spoken, spoken[1:]):
        require(after["start_s"] >= before["end_s"] - tolerance,
                f"{before['utterance_id']} and {after['utterance_id']}: final utterances "
                "overlap; reconcile overlapping audio chunks inside the adapter")

    # Availability from speech signal.status, by capture time.
    statuses = sorted((event["timestamp_s"], event["payload"]["availability"],
                       event["payload"]["reason"])
                      for _, event in of_type.get("signal.status", []))
    outages, down = [], None
    for time, availability, _ in statuses:
        if availability != "available" and down is None:
            down = time
        elif availability == "available" and down is not None:
            outages.append((down, time))
            down = None
    if down is not None:
        outages.append((down, math.inf))
    for final in spoken:
        require(not any(final["end_s"] > down + tolerance and final["start_s"] < up
                        for down, up in outages),
                f"{final['utterance_id']}: speech captured during a reported input outage")

    # Metrics.
    completed_pauses, metrics = {}, []
    for position, event in of_type.get("speech.metrics", []):
        payload, event_id = event["payload"], event["event_id"]
        start, end = payload["window_start_s"], payload["window_end_s"]
        pause = payload["pause"]
        metrics.append(event)
        if payload["availability"] != "available":
            continue
        require(not any(overlaps(down, up, start, end) for down, up in outages),
                f"{event_id}: claims available input during a reported input outage")
        if pause["state"] in ("active", "completed"):
            pause_end = pause["end_s"] if pause["state"] == "completed" else end
            require(pause["duration_s"] >= config["pause_min_s"] - tolerance,
                    f"{event_id}: pause shorter than the minimum pause duration")
            require(not any(overlaps(final["start_s"], final["end_s"],
                                     pause["start_s"] + tolerance, pause_end - tolerance)
                            for final in spoken),
                    f"{event_id}: pause overlaps finalized speech")
            require(any(close(final["end_s"], pause["start_s"], tolerance) for final in spoken),
                    f"{event_id}: a pause must start where finalized speech ended "
                    "(leading silence is not a pause in the v0 rules)")
        if pause["state"] == "completed":
            require(any(close(final["start_s"], pause["end_s"], tolerance) for final in spoken),
                    f"{event_id}: a completed pause must end where speech resumed")
            key = (round(pause["start_s"], 3), round(pause["end_s"], 3))
            require(key not in completed_pauses,
                    f"{event_id}: completed pause already reported by {completed_pauses.get(key)}")
            completed_pauses[key] = event_id
        if pause["state"] == "none":
            ended = [final["end_s"] for final in spoken if final["end_s"] <= end + tolerance]
            speaking = any(final["start_s"] <= end + tolerance < final["end_s"]
                           for final in spoken)
            require(not ended or speaking or end - max(ended) < config["pause_min_s"] + tolerance,
                    f"{event_id}: {end - max(ended or [end]):.2f} s of silence after speech "
                    "must be reported as an active pause")
        if payload["wpm"] is None and payload["filler_count"] is None:
            continue
        require(end - start >= config["min_observation_s"] - tolerance,
                f"{event_id}: a window shorter than the minimum observation must report "
                "null, not zero")
        # Coverage: every utterance seen overlapping the window must be final already.
        for utterance, known in revisions.items():
            delivered = [payload for at, payload in known.values() if at < position]
            if delivered and overlaps(min(p["start_s"] for p in delivered),
                                      max(p["end_s"] for p in delivered), start, end):
                require(final_at.get(utterance, math.inf) < position,
                        f"{event_id}: counted the window before overlapping utterance "
                        f"{utterance} was finalized; report null for insufficient coverage")
        # Attribution-agnostic bounds from finals delivered before this event.
        touching = [final for utterance, final in finals.items()
                    if final_at[utterance] < position and
                    overlaps(final["start_s"], final["end_s"], start, end)]
        inside = [final for final in touching
                  if final["start_s"] >= start - tolerance and final["end_s"] <= end + tolerance]
        minutes = (end - start) / 60
        for value, measure, name, slack in (
                (payload["wpm"], word_count, "WPM", 0.5 * minutes + 1e-6),
                (payload["filler_count"], filler_count, "filler count", 0)):
            if value is None:
                continue
            low = sum(measure(final["text"]) for final in inside)
            high = sum(measure(final["text"]) for final in touching)
            amount = value * minutes if name == "WPM" else value
            require(low - slack <= amount <= high + slack,
                    f"{event_id}: {name} {value} is inconsistent with finalized text "
                    f"delivered before it ({low} to {high} in the window)")

    # Each silence between finalized utterances that reaches the pause minimum is
    # reported once as a completed pause (when the stream carries metrics at all).
    if metrics:
        for before, after in zip(spoken, spoken[1:]):
            gap = (before["end_s"], after["start_s"])
            if gap[1] - gap[0] < config["pause_min_s"] + tolerance or \
                    any(overlaps(down, up, *gap) for down, up in outages):
                continue
            require(any(close(start, gap[0], tolerance) and close(end, gap[1], tolerance)
                        for start, end in completed_pauses),
                    f"Silence {gap[0]}-{gap[1]} s between {before['utterance_id']} and "
                    f"{after['utterance_id']} was never reported as a completed pause")

    available = [event["payload"] for event in metrics
                 if event["payload"]["availability"] == "available"]
    wpm_values = [payload["wpm"] for payload in available if payload["wpm"] is not None]
    return {
        "session_id": session_id,
        "capture_end_s": capture_end,
        "final_transcript": [[final["utterance_id"], final["text"]] for final in spoken],
        "finalized_words": sum(word_count(final["text"]) for final in spoken),
        "finalized_fillers": sum(filler_count(final["text"]) for final in spoken),
        "completed_pauses": [list(key) for key in sorted(completed_pauses)],
        "longest_active_pause_s": max([payload["pause"]["duration_s"] for payload in available
                                       if payload["pause"]["state"] == "active"], default=0),
        "speech_status": [list(status) for status in statuses],
        "null_wpm_metrics": [event["event_id"] for event in metrics
                             if event["payload"]["availability"] == "available" and
                             event["payload"]["wpm"] is None],
        "unavailable_metrics": [event["event_id"] for event in metrics
                                if event["payload"]["availability"] != "available"],
        "wpm_min": min(wpm_values, default=None),
        "wpm_max": max(wpm_values, default=None),
    }


def check_stream(arrivals, config=None):
    """Check every session in a delivery-ordered stream; other sources are ignored."""
    require(isinstance(arrivals, list), "Stream must be an event array in delivery order")
    sessions = {}
    for event in arrivals:
        require(isinstance(event, dict), "Event must be an object")
        if event.get("source") in ("speech", "session"):
            sessions.setdefault(event.get("session_id"), []).append(event)
    require(sessions, "Stream contains no speech or session events")
    return [check_session(events, config) for events in sessions.values()]


def check_case(name, config=None):
    cases = read_json(ROOT / "expectations.json")
    require(name in cases, f"Unknown case: {name}")
    reports = check_stream(read_json(ROOT / "fixtures" / f"{name}.json"), config)
    oracles = cases[name]["sessions"]
    require(len(reports) == len(oracles), f"{name}: expected {len(oracles)} sessions")
    for report, oracle in zip(reports, oracles):
        require(report["session_id"] == oracle["session_id"],
                f"{name}: unexpected session {report['session_id']}")
        for key in ORACLE_KEYS:
            if key in oracle:
                require(report[key] == oracle[key],
                        f"{name}/{report['session_id']}: {key} differs from the case oracle: "
                        f"expected {oracle[key]!r}, got {report[key]!r}")
    return reports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", help="check one synthetic case")
    parser.add_argument("--stream", type=Path,
                        help="check a recorded speech event stream (JSON array or .jsonl, "
                             "in delivery order) instead of the synthetic cases")
    parser.add_argument("--summary", action="store_true",
                        help="print each session's reconstructed transcript and metrics")
    parser.add_argument("--min-observation-s", type=float,
                        default=DEFAULTS["min_observation_s"])
    parser.add_argument("--pause-min-s", type=float, default=DEFAULTS["pause_min_s"])
    args = parser.parse_args()
    if args.case and args.stream:
        parser.error("use --case or --stream, not both")
    config = {"min_observation_s": args.min_observation_s, "pause_min_s": args.pause_min_s}
    try:
        if args.stream:
            reports = check_stream(read_stream(args.stream), config)
            for report in reports:
                print(f"PASS {report['session_id']}: stream satisfies the v0 speech checks")
        else:
            names = [args.case] if args.case else list(read_json(ROOT / "expectations.json"))
            reports = []
            for name in names:
                reports += check_case(name, config)
                print(f"PASS {name}: synthetic fixture matches its oracle")
            print(f"Checked {len(names)} cases / {len(reports)} sessions. This does not verify "
                  "microphone capture, transcription accuracy, latency, or a live adapter.")
        if args.summary:
            print(json.dumps(reports, indent=2, ensure_ascii=False))
    except (CheckError, OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        parser.exit(1, f"FAIL: {error}\n")


if __name__ == "__main__":
    main()
