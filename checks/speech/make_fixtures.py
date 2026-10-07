"""Generate the synthetic AUD-01 speech fixtures from the scenario scripts below.

Every utterance, timing, latency, and delivery effect here is hand-written
synthetic data. No microphone, audio file, or model was used. The generator
applies the proposed v0 speech rules documented in README.md so the committed
fixtures stay internally consistent; check_speech.py validates them
independently with attribution-agnostic bounds. Run with --check to confirm
the committed fixtures still match these scripts.
"""

import argparse
import json
import math
from pathlib import Path

from speech_text import spoken_tokens


ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"

# Proposed v0 speech-metric defaults (README.md). Lane 1 owns the central
# configuration once INT-01 lands; these values only shape the fixtures.
RULES = {
    "window_s": 10.0,          # trailing metrics window
    "hop_s": 5.0,              # periodic metrics spacing (live may use 1-2 s)
    "min_observation_s": 5.0,  # shorter windows report null WPM/fillers
    "pause_min_s": 1.0,        # silence between speech this long is a pause
    "max_wait_s": 3.0,         # wait for overlapping finals, then report null
}
# Synthetic delivery delays after capture, in seconds.
LATENCY = {"partial": 0.3, "final": 0.8, "drain_final": 0.6, "metrics": 0.2,
           "vad_onset": 0.3, "status": 0.1, "ready": 0.05, "complete": 0.2}


def num(value):
    value = round(value, 3)
    return int(value) if value == int(value) else value


def label(value):
    return str(num(value))


def utterance(uid, start, end, text, partials=None, final_at=None):
    """partials: None for automatic 1 s prefixes, or [(end_s, text[, deliver_at])]."""
    return {"id": uid, "start": start, "end": end, "text": text,
            "partials": partials, "final_at": final_at}


def auto_partials(item):
    words = item["text"].split()
    duration = item["end"] - item["start"]
    result, previous, step = [], "", 1
    while item["start"] + step < item["end"] - 0.2:
        end = item["start"] + step
        text = " ".join(words[:math.floor(len(words) * step / duration)])
        if text and text != previous:
            result.append((end, text))
            previous = text
        step += 1
    return result


def token_times(item):
    """Spread spoken tokens evenly; each token is attributed to its end time."""
    tokens = spoken_tokens(item["text"])
    step = (item["end"] - item["start"]) / max(len(tokens), 1)
    return [(item["end"] if index == len(tokens) - 1 else item["start"] + (index + 1) * step,
             counts_as_word, ends_filler)
            for index, (_, counts_as_word, ends_filler) in enumerate(tokens)]


def build_session(spec):
    session_id, end = spec["session_id"], spec["capture_end"]
    utterances = sorted(spec.get("utterances", []), key=lambda item: item["start"])
    statuses = spec.get("status", [])
    lost = next((time for time, availability, _ in statuses if availability != "available"),
                None)
    outgoing = []

    def emit(event_id, kind, source, timestamp, payload, deliver_at):
        deliver_at = spec.get("delays", {}).get(event_id, deliver_at)
        event = {"schema_version": 0, "session_id": session_id, "event_id": event_id,
                 "source": source, "type": kind, "timestamp_s": num(timestamp),
                 "payload": payload}
        outgoing.append((round(deliver_at, 3), len(outgoing), event))
        for retry_at in spec.get("retries", {}).get(event_id, []):
            outgoing.append((round(retry_at, 3), len(outgoing), event))

    emit("00-start", "session.started", "session", 0, {}, 0)
    for index, (time, availability, reason) in enumerate(statuses, 1):
        emit(f"speech-status-{index}", "signal.status", "speech", time,
             {"availability": availability, "reason": reason}, time + LATENCY["status"])

    final_delivery = {}
    for item in utterances:
        partials = auto_partials(item) if item["partials"] is None else item["partials"]
        for revision, partial in enumerate(partials):
            partial_end, text = partial[0], partial[1]
            deliver_at = partial[2] if len(partial) > 2 else partial_end + LATENCY["partial"]
            emit(f"{item['id']}-r{revision}", "speech.transcript", "speech", partial_end,
                 {"utterance_id": item["id"], "revision": revision, "is_final": False,
                  "start_s": num(item["start"]), "end_s": num(partial_end), "text": text},
                 deliver_at)
        latency = LATENCY["drain_final"] if item["end"] >= end else LATENCY["final"]
        deliver_at = item["final_at"] or item["end"] + latency
        final_delivery[item["id"]] = deliver_at
        emit(f"{item['id']}-r{len(partials)}", "speech.transcript", "speech", item["end"],
             {"utterance_id": item["id"], "revision": len(partials), "is_final": True,
              "start_s": num(item["start"]), "end_s": num(item["end"]),
              "text": item["text"]}, deliver_at)

    timed_tokens = [token for item in utterances for token in token_times(item)]
    gaps = [(before["end"], after["start"]) for before, after in zip(utterances, utterances[1:])
            if after["start"] - before["end"] >= RULES["pause_min_s"]]

    def pause_at(time, completed=None):
        if completed is not None:
            return {"state": "completed", "duration_s": num(time - completed),
                    "start_s": num(completed), "end_s": num(time)}
        ended = [item["end"] for item in utterances if item["end"] <= time]
        speaking = any(item["start"] <= time < item["end"] for item in utterances)
        if ended and not speaking and time - max(ended) >= RULES["pause_min_s"]:
            return {"state": "active", "duration_s": num(time - max(ended)),
                    "start_s": num(max(ended)), "end_s": None}
        return {"state": "none", "duration_s": 0, "start_s": None, "end_s": None}

    def metrics(event_id, time, due, completed=None):
        """Emit window [time - window_s, time]; due is the nominal emission time."""
        start = max(0.0, time - RULES["window_s"])
        minutes = (time - start) / 60
        payload = {"window_start_s": num(start), "window_end_s": num(time)}
        if lost is not None and time > lost:
            availability = next(a for t, a, _ in statuses if t == lost)
            payload.update({"availability": availability, "wpm": None, "filler_count": None,
                            "filler_rate_per_min": None,
                            "pause": {"state": "unknown", "duration_s": None,
                                      "start_s": None, "end_s": None}})
            emit(event_id, "speech.metrics", "speech", time, payload, due)
            return
        # Wait (bounded) for finals of every utterance overlapping the window.
        pending = [final_delivery[item["id"]] + LATENCY["ready"] for item in utterances
                   if item["start"] < time and item["end"] > start]
        deliver_at = max([due] + pending)
        covered = deliver_at <= due + RULES["max_wait_s"]
        deliver_at = min(deliver_at, due + RULES["max_wait_s"])
        known = (covered and spec.get("language", "en") == "en" and
                 time - start >= RULES["min_observation_s"])
        words = sum(1 for at, is_word, _ in timed_tokens if start < at <= time and is_word)
        fillers = sum(1 for at, _, is_filler in timed_tokens if start < at <= time and is_filler)
        payload.update({
            "availability": "available",
            "wpm": num(round(words / minutes, 1)) if known else None,
            "filler_count": fillers if known else None,
            "filler_rate_per_min": num(round(fillers / minutes, 1)) if known else None,
            "pause": pause_at(time, completed),
        })
        emit(event_id, "speech.metrics", "speech", time, payload, deliver_at)

    # Candidates in capture order: (nominal time, kind, pause start). A periodic
    # window ends where an utterance still being spoken began, so it never waits
    # for unfinished speech. Periodic windows that would not advance, or that
    # are shorter than the minimum observation time, are skipped; the final
    # capture-end window is always reported.
    hop = RULES["hop_s"]
    candidates = [(hop * step, "metrics", None)
                  for step in range(1, int(end / hop + 1e-9) + 1)]
    candidates += [(pause_end, "pause", pause_start) for pause_start, pause_end in gaps
                   if pause_end <= end and (lost is None or pause_end <= lost)]
    candidates.append((end, "metrics", None))
    last_window_end = 0.0
    for due, kind, pause_start in sorted(candidates,
                                         key=lambda item: (item[0], item[1] != "pause")):
        if kind == "pause":
            window_end = due
            metrics(f"pause-{label(due)}", due, due + LATENCY["vad_onset"], pause_start)
        else:
            window_end = next((item["start"] for item in utterances
                               if item["start"] < due < item["end"]), due)
            too_short = window_end < RULES["min_observation_s"] and due < end
            if window_end <= last_window_end + 1e-9 or too_short:
                continue
            metrics(f"metrics-{label(window_end)}", window_end, due + LATENCY["metrics"])
        last_window_end = window_end

    emit("90-stop", "session.stopping", "session", end, {}, end)
    completed_at = max(deliver for deliver, _, _ in outgoing) + LATENCY["complete"]
    emit("99-completed", "session.completed", "session", end,
         {"duration_s": num(end), "incomplete_sources": []}, completed_at)
    return [event for _, _, event in sorted(outgoing, key=lambda item: item[:2])]


SCENARIOS = {
    "steady_pace": [{
        "session_id": "synthetic-speech-steady-pace",
        "capture_end": 31.0,
        "utterances": [
            utterance("u1", 0.8, 4.6, "Practicing a presentation alone has one fundamental "
                      "problem for every speaker."),
            utterance("u2", 5.9, 9.4, "There is no audience to tell you how it lands.",
                      [(6.9, "There is no"), (7.9, "There is no audience to tell"),
                       (8.9, "There is no audience to tell you how it lens")]),
            utterance("u3", 9.9, 14.1, "LeCoach gives you a private audience that reacts "
                      "while you speak."),
            utterance("u4", 15.8, 19.6, "Everything runs locally, so your rehearsal never "
                      "leaves the device."),
            utterance("u5", 20.3, 24.7, "Um, the avatars lean in when your pace is steady "
                      "and clear."),
            utterance("u6", 26.2, 29.4, "Afterwards, it shows the few moments that "
                      "mattered most."),
        ],
    }],
    "rapid_speech": [{
        "session_id": "synthetic-speech-rapid",
        "capture_end": 30.0,
        "utterances": [
            utterance("u1", 0.6, 4.4, "Today I want to show you how LeCoach works."),
            utterance("u2", 5.0, 9.0, "We capture your voice and camera, and the audience "
                      "reacts right away."),
            utterance("u3", 9.4, 13.0, "The speech pipeline transcribes locally, measures "
                      "your pace, counts fillers, and tracks pauses."),
            utterance("u4", 13.3, 17.0, "The vision pipeline estimates facing direction and "
                      "movement, then the engagement engine combines everything."),
            utterance("u5", 17.3, 21.0, "When you rush through the key result, the audience "
                      "gets confused and starts drifting away."),
            utterance("u6", 21.3, 25.0, "Then you see exactly where it happened, why it "
                      "happened, and what to try next time."),
            utterance("u7", 25.4, 28.6, "All of it runs on your own machine with no cloud "
                      "service involved."),
        ],
    }],
    "filler_heavy": [{
        "session_id": "synthetic-speech-fillers",
        "capture_end": 25.0,
        "utterances": [
            utterance("u1", 0.9, 5.4, "Um, so, uh, today I want to, um, talk about our "
                      "results."),
            utterance("u2", 6.2, 11.0, "The model, you know, it basically, uh, listens to "
                      "the microphone."),
            utterance("u3", 11.7, 16.9, "And then, like, the audience, um, reacts, I mean, "
                      "it changes faces."),
            utterance("u4", 18.3, 23.0, "Uh, so, um, that is basically how it, uh, works."),
        ],
    }],
    "prolonged_silence": [{
        "session_id": "synthetic-speech-long-pause",
        "capture_end": 32.0,
        "utterances": [
            utterance("u1", 0.7, 4.9, "Let me walk you through the three steps of a "
                      "rehearsal."),
            utterance("u2", 5.5, 9.8, "First, you start a session and the audience appears."),
            utterance("u3", 20.6, 24.4, "Sorry, I lost my place for a moment there."),
            utterance("u4", 25.1, 29.0, "Second, you speak while the avatars react in real "
                      "time."),
        ],
    }],
    "delivery_effects": [{
        "session_id": "synthetic-speech-delivery",
        "capture_end": 20.0,
        "utterances": [
            # Model warm-up delays the first partial and final.
            utterance("u1", 1.2, 4.6, "Our results are ready.",
                      [(3.0, "Our results", 6.1)], final_at=8.9),
            # The last partial is delivered after its final.
            utterance("u2", 6.0, 9.6, "This is the part that matters most.",
                      [(7.0, "This is"), (8.0, "This is the part"),
                       (9.0, "This is the part that matter", 10.5)]),
            # A cough triggers voice activity; the hallucinated partial is
            # retracted by an empty final.
            utterance("u3", 11.0, 11.4, "", [(11.4, "Thank you.")], final_at=12.2),
            utterance("u4", 12.5, 16.2, "We slow down and pause before the key number."),
            # Speech continues at stop; the final is drained after session.stopping.
            utterance("u5", 17.0, 20.0, "And that is why we",
                      [(18.0, "And that"), (19.0, "And that is why")]),
        ],
        "delays": {"pause-11": 12.9},
        "retries": {"u2-r3": [10.7]},
    }],
    "microphone_denied": [{
        "session_id": "synthetic-speech-mic-denied",
        "capture_end": 10.0,
        "status": [(0.0, "unavailable", "microphone_permission_denied")],
    }],
    "microphone_lost": [{
        "session_id": "synthetic-speech-mic-lost",
        "capture_end": 20.0,
        "utterances": [
            utterance("u1", 0.8, 4.9, "We are about to see the audience react."),
            utterance("u2", 5.5, 9.7, "Watch what happens when I speed up a little."),
            utterance("u3", 10.2, 12.4, "Here is the", [(11.2, "Here")], final_at=13.0),
        ],
        "status": [(12.4, "error", "microphone_disconnected")],
    }],
    "silence_only": [{
        "session_id": "synthetic-speech-silence",
        "capture_end": 15.0,
    }],
    "unsupported_language": [{
        "session_id": "synthetic-speech-mandarin",
        "capture_end": 15.5,
        "language": "zh",
        "utterances": [
            utterance("u1", 0.8, 4.6, "大家好，今天我想介紹 LeCoach。",
                      [(2.0, "大家好"), (3.5, "大家好，今天我想")]),
            utterance("u2", 5.9, 10.2, "它會在你練習的時候即時給你反應。",
                      [(7.0, "它會在你"), (9.0, "它會在你練習的時候即時")]),
            utterance("u3", 10.8, 14.0, "所有資料都留在你的電腦上。",
                      [(12.0, "所有資料"), (13.5, "所有資料都留在你的")]),
        ],
    }],
    "repeated_sessions": [
        {
            "session_id": "synthetic-speech-repeat-a",
            "capture_end": 8.0,
            "utterances": [utterance("u1", 0.8, 4.0, "This is my first attempt.",
                                     [(2.0, "This is")])],
        },
        {
            "session_id": "synthetic-speech-repeat-b",
            "capture_end": 8.0,
            "utterances": [utterance("u1", 0.6, 4.4, "Second attempt, a little slower.",
                                     [(2.0, "Second attempt")])],
        },
    ],
}


def render(events):
    lines = [json.dumps(event, ensure_ascii=False) for event in events]
    return "[\n" + ",\n".join(lines) + "\n]\n"


def generate():
    return {name: render([event for spec in sessions for event in build_session(spec)])
            for name, sessions in SCENARIOS.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="fail if committed fixtures differ from the scenario scripts")
    args = parser.parse_args()
    stale = []
    for name, content in generate().items():
        path = FIXTURES / f"{name}.json"
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(path.name)
        else:
            FIXTURES.mkdir(exist_ok=True)
            path.write_text(content, encoding="utf-8")
    if stale:
        parser.exit(1, f"FAIL: regenerate fixtures: {', '.join(stale)}\n")
    print("Fixtures match the scenario scripts." if args.check else
          f"Wrote {len(SCENARIOS)} synthetic fixtures to {FIXTURES}")


if __name__ == "__main__":
    main()
