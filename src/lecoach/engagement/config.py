"""Every audience-rule default and unit, in one place.

These numbers are demo heuristics tuned against the synthetic fixtures. They are
not scientifically validated measures of delivery quality.
"""

from typing import Self

from pydantic import Field, model_validator

from lecoach.contracts.events import Model


class RuleConfig(Model):
    # Pace (finalized words per minute from speech.metrics). A pace rule latches when
    # consecutive windows cover at least `pace_sustain_s`; it clears only once pace
    # returns inside the comfortable band, so values between the two edges hold.
    pace_high_wpm: float = Field(default=180.0, gt=0)
    pace_high_clear_wpm: float = Field(default=170.0, gt=0)
    pace_low_wpm: float = Field(default=90.0, gt=0)
    pace_low_clear_wpm: float = Field(default=105.0, gt=0)
    pace_sustain_s: float = Field(default=15.0, gt=0)

    # Fillers per minute of finalized text in the same window.
    filler_rate_high_per_min: float = Field(default=12.0, gt=0)
    filler_rate_clear_per_min: float = Field(default=8.0, ge=0)
    filler_sustain_s: float = Field(default=15.0, gt=0)

    # An active pause at least this long, after speech has started, while capture works.
    silence_prolonged_s: float = Field(default=6.0, gt=0)

    # Approximate head/body facing in [0, 1]. Not eye contact.
    facing_away_below: float = Field(default=0.4, ge=0, le=1)
    facing_toward_at_least: float = Field(default=0.6, ge=0, le=1)
    facing_away_sustain_s: float = Field(default=6.0, gt=0)

    # Observations whose capture window ended longer ago than this are ignored.
    # Speech covers a 10 s window, a 5 s hop and up to 3 s of finalization wait.
    speech_stale_s: float = Field(default=15.0, gt=0)
    vision_stale_s: float = Field(default=6.0, gt=0)
    # Consecutive windows further apart than this do not form one sustained run.
    max_window_gap_s: float = Field(default=5.0, ge=0)

    # Smoothing / hysteresis on the audience itself.
    min_state_dwell_s: float = Field(default=3.0, ge=0)
    engaged_after_s: float = Field(default=5.0, ge=0)
    neutral_after_s: float = Field(default=5.0, ge=0)

    # Live-mode re-evaluation interval so stale inputs are noticed without new events.
    tick_interval_s: float = Field(default=0.5, gt=0)

    # Most recent supporting event IDs cited per reason.
    max_evidence_ids: int = Field(default=4, ge=1)

    @model_validator(mode="after")
    def ordered_bands(self) -> Self:
        if not (
            self.pace_low_wpm
            < self.pace_low_clear_wpm
            < self.pace_high_clear_wpm
            < self.pace_high_wpm
        ):
            raise ValueError("pace bands must be low < low_clear < high_clear < high")
        if self.filler_rate_clear_per_min >= self.filler_rate_high_per_min:
            raise ValueError("filler clear rate must be below the trigger rate")
        if self.facing_away_below >= self.facing_toward_at_least:
            raise ValueError("facing-away threshold must be below the facing-toward threshold")
        return self


DEFAULT_RULES = RuleConfig()
