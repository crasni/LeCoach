"""Speech analysis configuration.

Defaults are the English Stage I baseline accepted in issue #6
(https://github.com/crasni/LeCoach/issues/6). They remain demo heuristics until
AUD-02 recordings tune them. Pace bands, filler thresholds, and
prolonged-silence durations belong to the engagement rules.
"""

from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from lecoach.contracts.events import Model

# WPM and filler rules exist only for these analysis languages; other
# languages still produce transcripts and pauses, with null WPM and fillers.
SUPPORTED_ANALYSIS_LANGUAGES = frozenset({"en"})


def _seconds(default: float, upper: float, lower_inclusive: bool = False):
    bound = {"ge": 0} if lower_inclusive else {"gt": 0}
    return Field(default=default, strict=True, le=upper, allow_inf_nan=False, **bound)


Name = Annotated[str, Field(strict=True, min_length=1, max_length=64, pattern=r"^[\w.\-/]+$")]


class SpeechConfig(Model):
    language: str = Field(default="en", strict=True, pattern=r"^[a-z]{2,3}(-[A-Za-z0-9]+)?$")
    metrics_window_s: float = _seconds(10.0, 120)
    metrics_hop_s: float = _seconds(1.0, 60)
    min_observation_s: float = _seconds(5.0, 120)
    pause_min_s: float = _seconds(1.0, 60)
    coverage_wait_s: float = _seconds(3.0, 60)
    max_utterance_s: float = _seconds(8.0, 30)
    # Re-transcribe a growing utterance this often for live partials; 0 disables.
    partial_interval_s: float = _seconds(1.0, 30, lower_inclusive=True)
    sample_rate: int = Field(default=16_000, strict=True, ge=8_000, le=48_000)
    model: Name = "base.en"
    device: Literal["cpu", "cuda", "auto"] = "cpu"
    compute_type: Name = "int8"
    # A filesystem path, relative to the working directory or absolute.
    model_dir: str = Field(default="models", strict=True, min_length=1, max_length=4096)

    @model_validator(mode="after")
    def consistent_windows(self) -> Self:
        if self.metrics_hop_s > self.metrics_window_s:
            raise ValueError("metrics hop must not exceed the metrics window")
        if self.min_observation_s > self.metrics_window_s:
            raise ValueError("minimum observation must fit inside the metrics window")
        return self

    @property
    def analysis_supported(self) -> bool:
        return self.language in SUPPORTED_ANALYSIS_LANGUAGES
