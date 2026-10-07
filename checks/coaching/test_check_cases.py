"""Negative checks for evidence integrity and future recorder/feedback output."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from check_cases import (CheckError, ROOT, check_completed, check_event,
                         check_feedback, load_case, read_json)


class CoachingCaseChecks(unittest.TestCase):
    def setUp(self):
        self.spec, sessions = load_case("weak_to_improved")
        self.session = sessions[0]
        self.expected = self.spec["sessions"][0]["feedback"]
        self.feedback = copy.deepcopy(self.expected)

    def test_all_authored_scenarios_are_consistent(self):
        for name in read_json(ROOT / "expectations.json"):
            with self.subTest(case=name):
                load_case(name)

    def test_observation_and_action_can_be_rephrased(self):
        self.feedback["moments"][0]["observation"] = "These windows were about 205 and 200 WPM."
        self.feedback["moments"][0]["suggestion"] = "Rehearse the passage more slowly."
        check_feedback(self.feedback, self.expected, self.session)

    def test_dangling_evidence_fails(self):
        self.feedback["moments"][0]["evidence_event_ids"].append("missing-event")
        with self.assertRaisesRegex(CheckError, "Dangling"):
            check_feedback(self.feedback, self.expected, self.session)

    def test_duplicate_evidence_fails(self):
        ids = self.feedback["moments"][0]["evidence_event_ids"]
        ids.append(ids[0])
        with self.assertRaisesRegex(CheckError, "duplicate evidence"):
            check_feedback(self.feedback, self.expected, self.session)

    def test_input_failure_cannot_be_a_delivery_observation(self):
        spec, sessions = load_case("camera_unavailable")
        expected = spec["sessions"][0]["feedback"]
        actual = copy.deepcopy(expected)
        actual["moments"][0]["evidence_event_ids"].append("camera-denied")
        with self.assertRaisesRegex(CheckError, "limitation used as coaching"):
            check_feedback(actual, expected, sessions[0])

    def test_no_strength_is_invented_for_empty_session(self):
        spec, sessions = load_case("empty_session")
        expected = spec["sessions"][0]["feedback"]
        actual = copy.deepcopy(expected)
        actual["moments"] = [self.feedback["moments"][-1]]
        with self.assertRaisesRegex(CheckError, "Moment count"):
            check_feedback(actual, expected, sessions[0])

    def test_adjacent_incident_is_not_counted_twice(self):
        spec, sessions = load_case("adjacent_incidents")
        expected = spec["sessions"][0]["feedback"]
        actual = copy.deepcopy(expected)
        actual["moments"].append(copy.deepcopy(actual["moments"][0]))
        with self.assertRaisesRegex(CheckError, "Moment count"):
            check_feedback(actual, expected, sessions[0])

    def test_capture_timestamp_is_not_replaced_by_decision_time(self):
        self.feedback["moments"][0]["timestamp_s"] = 20.5
        with self.assertRaisesRegex(CheckError, "incorrectly timed"):
            check_feedback(self.feedback, self.expected, self.session)

    def test_missing_limitations_fail(self):
        spec, sessions = load_case("no_usable_signals")
        expected = spec["sessions"][0]["feedback"]
        actual = copy.deepcopy(expected)
        actual["limitations"] = []
        with self.assertRaisesRegex(CheckError, "limitation"):
            check_feedback(actual, expected, sessions[0])

    def test_feedback_cannot_add_an_engagement_score(self):
        self.feedback["engagement_score"] = 90
        with self.assertRaisesRegex(CheckError, "Feedback fields"):
            check_feedback(self.feedback, self.expected, self.session)

    def test_final_arriving_during_drain_must_be_retained(self):
        _, sessions = load_case("late_final_and_duplicates")
        actual = copy.deepcopy(sessions[0])
        actual["events"] = [event for event in actual["events"] if event["event_id"] != "final-2"]
        with self.assertRaisesRegex(CheckError, "timeline differs"):
            check_completed(actual, sessions[0])

    def test_duplicate_final_must_not_be_retained_twice(self):
        _, sessions = load_case("late_final_and_duplicates")
        actual = copy.deepcopy(sessions[0])
        final = next(event for event in actual["events"] if event["event_id"] == "final-2")
        actual["events"].append(copy.deepcopy(final))
        with self.assertRaisesRegex(CheckError, "timeline differs"):
            check_completed(actual, sessions[0])

    def test_events_after_completion_are_not_retained(self):
        _, sessions = load_case("drain_timeout")
        actual = copy.deepcopy(sessions[0])
        arrivals = read_json(ROOT / "fixtures" / "drain_timeout.json")
        actual["events"].append(arrivals[-1])
        with self.assertRaisesRegex(CheckError, "timeline differs"):
            check_completed(actual, sessions[0])

    def test_repeat_sessions_cannot_share_a_timeline(self):
        _, sessions = load_case("repeated_sessions")
        actual = copy.deepcopy(sessions[1])
        actual["events"] = copy.deepcopy(sessions[0]["events"])
        with self.assertRaisesRegex(CheckError, "timeline differs"):
            check_completed(actual, sessions[1])

    def test_unknown_is_not_zero_in_a_startup_window(self):
        _, sessions = load_case("insufficient_window")
        actual = copy.deepcopy(sessions[0])
        next(event for event in actual["events"] if event["type"] == "speech.metrics") \
            ["payload"]["wpm"] = 0
        with self.assertRaisesRegex(CheckError, "timeline differs"):
            check_completed(actual, sessions[0])

    def test_nonfinite_timestamps_are_rejected(self):
        event = copy.deepcopy(self.session["events"][0])
        event["timestamp_s"] = float("nan")
        with self.assertRaisesRegex(CheckError, "timestamp"):
            check_event(event)

    def test_cli_accepts_canonical_output_batches(self):
        with tempfile.TemporaryDirectory() as folder:
            completed = Path(folder) / "completed.json"
            feedback = Path(folder) / "feedback.json"
            completed.write_text(json.dumps([self.session]))
            feedback.write_text(json.dumps([self.feedback]))
            result = subprocess.run(
                [sys.executable, str(ROOT / "check_cases.py"), "--case", "weak_to_improved",
                 "--completed", str(completed), "--feedback", str(feedback)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_cli_rejects_non_json_numbers_without_a_traceback(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "feedback.json"
            path.write_text('[{"duration_s": NaN}]')
            result = subprocess.run(
                [sys.executable, str(ROOT / "check_cases.py"), "--case", "empty_session",
                 "--feedback", str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertIn("Non-JSON numeric value", result.stderr)
            self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
