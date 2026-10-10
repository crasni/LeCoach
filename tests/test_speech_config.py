from unittest import TestCase

from pydantic import ValidationError

from lecoach.speech.config import SpeechConfig


class SpeechConfigTests(TestCase):
    def test_defaults_match_the_issue_6_decision(self):
        # English Stage I baseline accepted in https://github.com/crasni/LeCoach/issues/6
        config = SpeechConfig()
        self.assertEqual(
            (config.language, config.metrics_window_s, config.metrics_hop_s,
             config.min_observation_s, config.pause_min_s, config.coverage_wait_s,
             config.max_utterance_s),
            ("en", 10.0, 1.0, 5.0, 1.0, 3.0, 8.0),
        )
        self.assertTrue(config.analysis_supported)
        self.assertFalse(SpeechConfig(language="zh").analysis_supported)

    def test_model_dir_accepts_ordinary_paths(self):
        for path in ("models", "/home/presenter/" + "long-folder-name/" * 6 + "models",
                     "C:\\Users\\Presenter\\LeCoach\\models", "~/My Models"):
            with self.subTest(path=path):
                self.assertEqual(SpeechConfig(model_dir=path).model_dir, path)
        with self.assertRaises(ValidationError):
            SpeechConfig(model_dir="")

    def test_partials_can_be_disabled(self):
        self.assertEqual(SpeechConfig(partial_interval_s=0).partial_interval_s, 0.0)

    def test_rejects_invalid_values(self):
        for field in ("metrics_window_s", "metrics_hop_s", "min_observation_s", "pause_min_s",
                      "coverage_wait_s", "max_utterance_s"):
            for value in (0, -1, float("nan"), float("inf"), True, "1"):
                with self.subTest(field=field, value=value), self.assertRaises(ValidationError):
                    SpeechConfig(**{field: value})
        for bad in ({"metrics_hop_s": 11.0}, {"min_observation_s": 12.0}, {"language": "EN"},
                    {"sample_rate": 4_000}, {"model": "../weights x"}, {"unexpected": 1}):
            with self.subTest(bad=bad), self.assertRaises(ValidationError):
                SpeechConfig(**bad)
