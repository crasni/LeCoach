"""Negative checks for the speech rules, fixtures, and future adapter output."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from check_speech import CheckError, ROOT, check_case, check_event, check_stream, read_json
from speech_text import filler_count, word_count


def fixture(name):
    return read_json(ROOT / "fixtures" / f"{name}.json")


def find(events, event_id, session_id=None):
    return next(event for event in events if event["event_id"] == event_id and
                (session_id is None or event["session_id"] == session_id))


def position(events, event_id):
    return next(index for index, event in enumerate(events) if event["event_id"] == event_id)


class SpeechTextRules(unittest.TestCase):
    def test_hesitations_are_fillers_but_not_words(self):
        text = "Um, so, uh, today I want to, um, talk about our results."
        self.assertEqual((word_count(text), filler_count(text)), (9, 3))
        self.assertEqual((word_count("Ummm, hmm, mhm."), filler_count("Ummm, hmm, mhm.")),
                         (0, 3))

    def test_discourse_markers_count_only_when_set_off(self):
        for text, fillers in (("It was, like, really fast.", 1), ("I like it.", 0),
                              ("You know, it works.", 1), ("Do you know the answer?", 0),
                              ("I mean, it works.", 1), ("I mean it.", 0)):
            with self.subTest(text=text):
                self.assertEqual(filler_count(text), fillers)

    def test_annotations_numbers_and_contractions(self):
        self.assertEqual(word_count("[BLANK_AUDIO] (applause) Thank you."), 2)
        self.assertEqual(word_count("It's 3.5 times faster, don't you think?"), 7)


class FixtureCases(unittest.TestCase):
    def test_all_cases_match_their_oracles(self):
        for name in read_json(ROOT / "expectations.json"):
            with self.subTest(case=name):
                check_case(name)

    def test_fixtures_match_the_scenario_scripts(self):
        result = subprocess.run([sys.executable, str(ROOT / "make_fixtures.py"), "--check"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_other_sources_are_ignored(self):
        events = fixture("steady_pace")
        vision = {"schema_version": 0, "session_id": events[0]["session_id"],
                  "event_id": "vision-5", "source": "vision", "type": "vision.metrics",
                  "timestamp_s": 5, "payload": {}}
        check_stream(events[:2] + [vision] + events[2:])


class TranscriptChecks(unittest.TestCase):
    def setUp(self):
        self.events = fixture("delivery_effects")

    def test_retry_must_repeat_the_same_event(self):
        retry = [index for index, event in enumerate(self.events)
                 if event["event_id"] == "u2-r3"][-1]
        self.events[retry] = copy.deepcopy(self.events[retry])
        self.events[retry]["payload"]["text"] = "This is the part that matters."
        with self.assertRaisesRegex(CheckError, "retry changed a stable event ID"):
            check_stream(self.events)

    def test_final_freezes_the_utterance(self):
        late = copy.deepcopy(find(self.events, "u2-r2"))
        late.update(event_id="u2-r4", timestamp_s=9.6)
        late["payload"].update(revision=4, end_s=9.6)
        self.events.insert(position(self.events, "90-stop"), late)
        with self.assertRaisesRegex(CheckError, "revision after the final"):
            check_stream(self.events)

    def test_second_final_needs_the_original_event_id(self):
        duplicate = copy.deepcopy(find(self.events, "u2-r3"))
        duplicate["event_id"] = "u2-final-again"
        self.events.insert(position(self.events, "90-stop"), duplicate)
        with self.assertRaisesRegex(CheckError, "two different event IDs"):
            check_stream(self.events)

    def test_pending_partial_must_be_finalized_before_completion(self):
        self.events = [event for event in self.events if event["event_id"] != "u5-r2"]
        with self.assertRaisesRegex(CheckError, "never finalized"):
            check_stream(self.events)

    def test_partial_end_cannot_move_backwards(self):
        find(self.events, "u4-r1")["payload"]["end_s"] = 13.0
        find(self.events, "u4-r1")["timestamp_s"] = 13.0
        with self.assertRaisesRegex(CheckError, "must not move backwards"):
            check_stream(self.events)

    def test_overlapping_chunks_must_be_reconciled(self):
        events = fixture("steady_pace")
        find(events, "u3-r3")["payload"]["start_s"] = 9.0
        with self.assertRaisesRegex(CheckError, "overlap"):
            check_stream(events)


class MetricChecks(unittest.TestCase):
    def test_partial_or_duplicate_text_cannot_inflate_wpm(self):
        events = fixture("delivery_effects")
        # 11 finalized words; double-counting the retried final would give 18.
        find(events, "metrics-10")["payload"]["wpm"] = 108
        with self.assertRaisesRegex(CheckError, "WPM 108 is inconsistent"):
            check_stream(events)

    def test_fillers_come_from_finalized_text_in_the_window(self):
        events = fixture("filler_heavy")
        payload = find(events, "metrics-25")["payload"]
        payload.update(filler_count=11, filler_rate_per_min=66)
        with self.assertRaisesRegex(CheckError, "filler count 11 is inconsistent"):
            check_stream(events)

    def test_filler_rate_must_match_count(self):
        events = fixture("filler_heavy")
        find(events, "metrics-25")["payload"]["filler_rate_per_min"] = 4
        with self.assertRaisesRegex(CheckError, "Filler rate"):
            check_stream(events)

    def test_window_waits_for_overlapping_finals(self):
        events = fixture("delivery_effects")
        find(events, "metrics-5")["payload"].update(wpm=0, filler_count=0,
                                                    filler_rate_per_min=0)
        with self.assertRaisesRegex(CheckError, "before overlapping utterance u1"):
            check_stream(events)

    def test_short_window_is_null_not_zero(self):
        events = fixture("silence_only")
        payload = find(events, "metrics-5")["payload"]
        payload["window_start_s"] = 2
        with self.assertRaisesRegex(CheckError, "null, not zero"):
            check_stream(events)

    def test_unavailable_input_is_null_not_zero(self):
        events = fixture("microphone_denied")
        find(events, "metrics-5")["payload"]["wpm"] = 0
        with self.assertRaisesRegex(CheckError, "Unavailable input must report null"):
            check_stream(events)

    def test_outage_cannot_report_available_metrics(self):
        events = fixture("microphone_lost")
        find(events, "metrics-15")["payload"].update(
            availability="available", wpm=0, filler_count=0, filler_rate_per_min=0,
            pause={"state": "none", "duration_s": 0, "start_s": None, "end_s": None})
        with self.assertRaisesRegex(CheckError, "reported input outage"):
            check_stream(events)

    def test_metric_timestamp_is_window_end(self):
        events = fixture("steady_pace")
        find(events, "metrics-15")["timestamp_s"] = 15.2
        with self.assertRaisesRegex(CheckError, "timestamp_s at window_end_s"):
            check_stream(events)

    def test_capture_cannot_follow_capture_end(self):
        events = fixture("steady_pace")
        late = copy.deepcopy(find(events, "metrics-31"))
        late["event_id"] = "metrics-33"
        late["timestamp_s"] = 33
        late["payload"].update(window_start_s=23, window_end_s=33)
        late["payload"]["pause"].update(duration_s=3.6)
        events.insert(position(events, "99-completed"), late)
        with self.assertRaisesRegex(CheckError, "after the capture end"):
            check_stream(events)

    def test_nonfinite_values_are_rejected(self):
        event = copy.deepcopy(find(fixture("steady_pace"), "metrics-15"))
        event["payload"]["wpm"] = float("nan")
        with self.assertRaisesRegex(CheckError, "Invalid wpm"):
            check_event(event)


class PauseChecks(unittest.TestCase):
    def test_completed_pause_is_reported_once(self):
        events = fixture("steady_pace")
        again = copy.deepcopy(find(events, "pause-5.9"))
        again["event_id"] = "pause-5.9-retry"
        events.insert(position(events, "pause-5.9") + 1, again)
        with self.assertRaisesRegex(CheckError, "already reported by pause-5.9"):
            check_stream(events)

    def test_pause_cannot_overlap_speech(self):
        events = fixture("steady_pace")
        find(events, "pause-5.9")["payload"]["pause"].update(start_s=4.0, duration_s=1.9)
        with self.assertRaisesRegex(CheckError, "overlaps finalized speech"):
            check_stream(events)

    def test_leading_silence_is_not_a_pause(self):
        events = fixture("silence_only")
        find(events, "metrics-10")["payload"]["pause"] = {
            "state": "active", "duration_s": 10, "start_s": 0, "end_s": None}
        with self.assertRaisesRegex(CheckError, "leading silence is not a pause"):
            check_stream(events)

    def test_long_silence_after_speech_is_an_active_pause(self):
        events = fixture("prolonged_silence")
        find(events, "metrics-15")["payload"]["pause"] = {
            "state": "none", "duration_s": 0, "start_s": None, "end_s": None}
        with self.assertRaisesRegex(CheckError, "must be reported as an active pause"):
            check_stream(events)

    def test_every_completed_pause_is_reported(self):
        events = [event for event in fixture("steady_pace") if event["event_id"] != "pause-15.8"]
        with self.assertRaisesRegex(CheckError, "never reported as a completed pause"):
            check_stream(events)

    def test_short_gap_is_not_a_pause(self):
        events = fixture("steady_pace")
        find(events, "metrics-9.9")["payload"]["pause"] = {
            "state": "active", "duration_s": 0.5, "start_s": 9.4, "end_s": None}
        with self.assertRaisesRegex(CheckError, "shorter than the minimum pause"):
            check_stream(events)

    def test_pause_shapes(self):
        event = copy.deepcopy(find(fixture("prolonged_silence"), "metrics-20"))
        for pause, message in (
                ({"state": "active", "duration_s": 10.2, "start_s": 9.8, "end_s": 20},
                 "Active pause"),
                ({"state": "none", "duration_s": 2, "start_s": None, "end_s": None},
                 "Pause state none"),
                ({"state": "unknown", "duration_s": 0, "start_s": None, "end_s": None},
                 "not zero")):
            with self.subTest(state=pause["state"]):
                event["payload"]["pause"] = pause
                with self.assertRaisesRegex(CheckError, message):
                    check_event(event)


class LifecycleAndSessions(unittest.TestCase):
    def test_lifecycle_requires_start(self):
        events = [event for event in fixture("silence_only")
                  if event["type"] != "session.started"]
        with self.assertRaisesRegex(CheckError, "requires session.started"):
            check_stream(events)

    def test_start_must_be_first_delivery(self):
        events = fixture("silence_only")
        start = events.pop(0)
        events.insert(len(events) - 1, start)
        with self.assertRaisesRegex(CheckError, "first delivery"):
            check_stream(events)

    def test_completion_needs_stop(self):
        events = [event for event in fixture("silence_only")
                  if event["type"] != "session.stopping"]
        with self.assertRaisesRegex(CheckError, "must follow session.stopping"):
            check_stream(events)

    def test_lifecycle_payloads_match_canonical_contract(self):
        for kind, update in (
                ("session.started", {"unexpected": True}),
                ("session.stopping", {"unexpected": True}),
                ("session.completed", {"incomplete_sources": ["camera"]}),
                ("session.completed", {"incomplete_sources": ["speech", "speech"]}),
                ("session.completed", {"unexpected": True})):
            with self.subTest(kind=kind, update=update):
                events = fixture("silence_only")
                next(event for event in events if event["type"] == kind)["payload"].update(update)
                with self.assertRaises(CheckError):
                    check_stream(events)

    def test_nothing_is_delivered_after_completion(self):
        events = fixture("steady_pace")
        events.append(copy.deepcopy(find(events, "u6-r2")))
        with self.assertRaisesRegex(CheckError, "delivered after session.completed"):
            check_stream(events)

    def test_reused_ids_are_scoped_by_session(self):
        events = fixture("repeated_sessions")
        reports = check_stream(events)
        self.assertEqual([report["final_transcript"][0][1] for report in reports],
                         ["This is my first attempt.", "Second attempt, a little slower."])
        # A consumer that ignored session_id would treat session B's u1-r0 as a
        # changed retry of session A's event.
        merged = [copy.deepcopy(event) for event in events if event["source"] == "speech"]
        for event in merged:
            event["session_id"] = "synthetic-speech-repeat-a"
        with self.assertRaisesRegex(CheckError, "u1-r0: retry changed a stable event ID"):
            check_stream(merged)


class CommandLine(unittest.TestCase):
    def run_cli(self, *arguments):
        return subprocess.run([sys.executable, str(ROOT / "check_speech.py"), *arguments],
                              capture_output=True, text=True)

    def test_recorded_stream_can_be_checked_as_json_or_jsonl(self):
        events = fixture("delivery_effects")
        with tempfile.TemporaryDirectory() as folder:
            array, lines = Path(folder) / "speech.json", Path(folder) / "speech.jsonl"
            array.write_text(json.dumps(events), encoding="utf-8")
            lines.write_text("\n".join(json.dumps(event) for event in events),
                             encoding="utf-8")
            for path in (array, lines):
                with self.subTest(path=path.name):
                    result = self.run_cli("--stream", str(path), "--summary")
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("PASS synthetic-speech-delivery", result.stdout)

    def test_failures_exit_without_a_traceback(self):
        with tempfile.TemporaryDirectory() as folder:
            for content, message in (('[{"timestamp_s": NaN}]', "Non-JSON numeric value"),
                                     ('[{"source": "speech"}]', "Incomplete event envelope")):
                path = Path(folder) / "speech.json"
                path.write_text(content, encoding="utf-8")
                with self.subTest(message=message):
                    result = self.run_cli("--stream", str(path))
                    self.assertEqual(result.returncode, 1)
                    self.assertIn(message, result.stderr)
                    self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
