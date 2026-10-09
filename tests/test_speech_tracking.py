from unittest import TestCase

from lecoach.speech.text import even_tokens
from lecoach.speech.tracking import UtteranceTracker


class UtteranceTrackerTests(TestCase):
    def setUp(self):
        self.tracker = UtteranceTracker()
        self.tracker.start(1, 5.9)

    def test_partial_is_corrected_and_frozen_by_its_final(self):
        first = self.tracker.partial(1, " There is no", 6.9)
        misheard = "There is no audience to tell you how it lens"
        corrected = self.tracker.partial(1, misheard, 8.9)
        self.assertEqual((first["revision"], corrected["revision"]), (0, 1))
        self.assertIsNone(self.tracker.partial(1, misheard, 9.0))
        self.tracker.end(1, 9.4)
        text = "There is no audience to tell you how it lands."
        payload, final = self.tracker.final(1, text, even_tokens(text, 5.9, 9.4), True)
        self.assertEqual(
            (payload["revision"], payload["is_final"], payload["text"], payload["end_s"]),
            (2, True, text, 9.4))
        self.assertEqual(len(final.tokens), 10)
        self.assertIsNone(self.tracker.partial(1, "late partial", 9.6))
        with self.assertRaisesRegex(ValueError, "already final"):
            self.tracker.final(1, text, [], True)

    def test_empty_final_retracts_a_hallucinated_partial(self):
        self.assertIsNotNone(self.tracker.partial(1, "Thank you.", 6.3))
        self.tracker.end(1, 6.3)
        payload, final = self.tracker.final(1, "  ", even_tokens("Thank you.", 5.9, 6.3), True)
        self.assertEqual((payload["text"], final.tokens), ("", ()))

    def test_partial_end_never_moves_backwards(self):
        self.tracker.partial(1, "one", 7.0)
        self.assertEqual(self.tracker.partial(1, "one two", 6.5)["end_s"], 7.0)

    def test_final_requires_an_ended_segment(self):
        with self.assertRaisesRegex(ValueError, "has not ended"):
            self.tracker.final(1, "text", [], True)

    def test_later_utterance_never_starts_before_the_previous_end(self):
        self.tracker.end(1, 9.4)
        self.tracker.start(2, 9.1)
        self.assertEqual(self.tracker.get(2).start_s, 9.4)
        with self.assertRaisesRegex(ValueError, "already started"):
            self.tracker.start(2, 10.0)
