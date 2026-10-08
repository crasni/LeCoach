import importlib.util
import json
from pathlib import Path
from unittest import TestCase

from lecoach.speech import text

CHECKS = Path(__file__).resolve().parents[1] / "checks" / "speech"
SENTENCES = [
    "Um, so, uh, today I want to, um, talk about our results.",
    "The model, you know, it basically, uh, listens to the microphone.",
    "And then, like, the audience, um, reacts, I mean, it changes faces.",
    "I like it. Do you know the answer? I mean it.",
    "It's 3.5 times faster, e.g. on UGen300 — don't you think?",
    "[BLANK_AUDIO] (applause) Thank you.",
    "Ummm... hmm, mhm, ahh, err, eh, mm",
    "like um",
    "大家好，今天我想介紹 LeCoach。",
    "",
]


def standalone_rules():
    spec = importlib.util.spec_from_file_location("standalone_speech_text",
                                                  CHECKS / "speech_text.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SpeechTextTests(TestCase):
    def test_package_rules_match_the_standalone_checker(self):
        standalone = standalone_rules()
        corpus = list(SENTENCES)
        for path in sorted((CHECKS / "fixtures").glob("*.json")):
            corpus += [event["payload"]["text"]
                       for event in json.loads(path.read_text(encoding="utf-8"))
                       if event["type"] == "speech.transcript"]
        self.assertGreater(len(corpus), 100)
        for sentence in corpus:
            with self.subTest(sentence=sentence):
                self.assertEqual(text.spoken_tokens(sentence),
                                 standalone.spoken_tokens(sentence))

    def test_model_word_times_attribute_tokens(self):
        words = [(" Um,", 1.2), (" it", 1.5), (" was,", 1.8), (" like,", 2.1), (" fast.", 2.6)]
        tokens = text.timed_tokens(words, 1.0, 2.6)
        self.assertEqual([token.at_s for token in tokens], [1.2, 1.5, 1.8, 2.1, 2.6])
        self.assertEqual([token.counts_as_word for token in tokens],
                         [False, True, True, True, True])
        self.assertEqual([token.ends_filler for token in tokens],
                         [True, False, False, True, False])

    def test_misaligned_words_fall_back_to_an_even_spread(self):
        tokens = text.timed_tokens([(" [BLANK", 1.0), ("_AUDIO] hello", 2.0)], 0.0, 2.0)
        self.assertEqual(tokens, text.even_tokens(" [BLANK_AUDIO] hello", 0.0, 2.0))
        self.assertEqual(tokens[-1].at_s, 2.0)

    def test_word_times_are_clamped_to_the_utterance(self):
        tokens = text.timed_tokens([(" early", 0.5), (" late", 9.0)], 1.0, 3.0)
        self.assertEqual([token.at_s for token in tokens], [1.0, 3.0])
