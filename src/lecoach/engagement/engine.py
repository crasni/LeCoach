"""The sole deterministic engagement engine.

Speech and vision observations latch explicit rules; the audience state follows the
rules with dwell and hysteresis. Missing, stale or unknown observations never count
against the speaker: they only shrink the set of usable sources. No model or LLM
participates in this control loop.
"""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field

from lecoach.contracts import Event
from lecoach.contracts.events import SpeechMetricsPayload, VisionMetricsPayload
from lecoach.contracts.interfaces import SessionContext

from .config import DEFAULT_RULES, RuleConfig

SOURCES = ("speech", "vision")


@dataclass(frozen=True)
class Observation:
    event_id: str
    start_s: float
    end_s: float
    payload: SpeechMetricsPayload | VisionMetricsPayload


# A predicate answers True, False, or None when the observation cannot tell.
Predicate = Callable[[SpeechMetricsPayload | VisionMetricsPayload], bool | None]


@dataclass
class Rule:
    code: str
    source: str
    state: str
    trigger: Predicate
    clear: Predicate
    sustain_s: float
    active: bool = False
    onset_s: float = 0.0
    evidence: list[str] = field(default_factory=list)


def _known(value, test) -> bool | None:
    return None if value is None else test(value)


class RuleEngine:
    """Implements the EngagementEngine protocol: start(context), on_event(event), stop()."""

    def __init__(self, rules: RuleConfig | None = None) -> None:
        self.config = rules or DEFAULT_RULES
        self.context: SessionContext | None = None
        self.running = False
        self._timer: asyncio.TimerHandle | None = None
        self._reset()

    # Protocol -----------------------------------------------------------------

    def start(self, context: SessionContext) -> None:
        self.stop()
        self._reset()
        self.context = context
        self.running = True
        self._emit("NEUTRAL", [], [])
        if context.config.mode == "live":
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = None
            if loop is not None:
                self._timer = loop.call_later(self.config.tick_interval_s, self._tick)

    def on_event(self, event: Event) -> None:
        if not self.running or event.session_id != self.context.session_id:
            return
        if event.source not in SOURCES:
            return
        if event.type == "signal.status":
            # Only an observation captured after an outage restores the source; an
            # "available" status alone never revives pre-outage evidence.
            if event.payload.availability != "available":
                self._down_since[event.source] = max(
                    event.timestamp_s, self._down_since.get(event.source, -1.0)
                )
            self.evaluate()
        elif event.type in ("speech.metrics", "vision.metrics"):
            self._observe(event)
            self.evaluate()

    def stop(self) -> None:
        self.running = False
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    # State --------------------------------------------------------------------

    def _reset(self) -> None:
        c = self.config
        self.state = "NEUTRAL"
        self.entered_s = 0.0
        self._sequence = 0
        self._neutral_since: float | None = None
        self._positive_since: float | None = None
        self._history: dict[str, list[Observation]] = {s: [] for s in SOURCES}
        self._down_since: dict[str, float] = {}
        self.rules = [
            Rule(
                "pace_high",
                "speech",
                "CONFUSED",
                *self._speaking(
                    lambda p: _known(p.wpm, lambda w: w >= c.pace_high_wpm),
                    lambda p: _known(p.wpm, lambda w: w <= c.pace_high_clear_wpm),
                ),
                c.pace_sustain_s,
            ),
            Rule(
                "fillers_frequent",
                "speech",
                "CONFUSED",
                *self._speaking(
                    lambda p: _known(
                        p.filler_rate_per_min, lambda r: r >= c.filler_rate_high_per_min
                    ),
                    lambda p: _known(
                        p.filler_rate_per_min, lambda r: r <= c.filler_rate_clear_per_min
                    ),
                ),
                c.filler_sustain_s,
            ),
            Rule(
                # Zero WPM is silence, handled by the pause rule, not slow speech.
                "pace_low",
                "speech",
                "BORED",
                *self._speaking(
                    lambda p: _known(p.wpm or None, lambda w: w <= c.pace_low_wpm),
                    lambda p: _known(p.wpm or None, lambda w: w >= c.pace_low_clear_wpm),
                ),
                c.pace_sustain_s,
            ),
            Rule(
                "silence_prolonged",
                "speech",
                "BORED",
                self._silence_trigger,
                lambda p: None if p.pause.state == "unknown" else p.pause.state != "active",
                0.0,
            ),
            Rule(
                "facing_away_sustained",
                "vision",
                "BORED",
                lambda p: _known(p.facing_score, lambda f: f < c.facing_away_below),
                lambda p: _known(p.facing_score, lambda f: f >= c.facing_toward_at_least),
                c.facing_away_sustain_s,
            ),
        ]

    def _pausing(self, p: SpeechMetricsPayload) -> bool:
        """A long active pause fills the trailing window with silence."""
        return p.pause.state == "active" and (
            p.pause.duration_s is None or p.pause.duration_s >= self.config.pause_hold_s
        )

    def _speaking(self, trigger: Predicate, clear: Predicate) -> tuple[Predicate, Predicate]:
        """While the speaker is pausing, pace and filler rules hold rather than decide."""
        return (
            lambda p: None if self._pausing(p) else trigger(p),
            lambda p: False if self._pausing(p) else clear(p),
        )

    def _silence_trigger(self, p: SpeechMetricsPayload) -> bool | None:
        if p.pause.state == "unknown":
            return None
        return (
            p.pause.state == "active"
            and p.pause.duration_s is not None
            and p.pause.duration_s >= self.config.silence_prolonged_s
        )

    def _stale_s(self, source: str) -> float:
        return self.config.speech_stale_s if source == "speech" else self.config.vision_stale_s

    def _observe(self, event: Event) -> None:
        payload = event.payload
        history = self._history[event.source]
        now = self.context.clock.now()
        if now - payload.window_end_s > self._stale_s(event.source):
            return  # Too old to influence a live reaction.
        if history and payload.window_end_s <= history[-1].end_s:
            return  # Never let an older observation overwrite a newer one.
        history.append(
            Observation(event.event_id, payload.window_start_s, payload.window_end_s, payload)
        )
        del history[: -self.config.history_limit]

    def usable(self, source: str, now: float) -> bool:
        history = self._history[source]
        if not history:
            return False
        latest = history[-1]
        if now - latest.end_s > self._stale_s(source):
            return False
        down = self._down_since.get(source)
        if down is not None and latest.end_s <= down:
            return False
        p = latest.payload
        if p.availability != "available":
            return False
        if source == "vision":
            return p.person_present is True and p.pose_available is True
        return True

    def _run(self, source: str, test: Predicate) -> list[Observation]:
        """Consecutive most-recent observations that satisfy `test`, oldest first."""
        run: list[Observation] = []
        down = self._down_since.get(source, -1.0)
        for obs in reversed(self._history[source]):
            if obs.end_s <= down or test(obs.payload) is not True:
                break  # A run never spans an outage.
            if run and run[-1].start_s - obs.end_s > self.config.max_window_gap_s:
                break
            run.append(obs)
        return run[::-1]

    def _cite(self, run: list[Observation]) -> list[str]:
        return [obs.event_id for obs in run[-self.config.max_evidence_ids :]]

    def _update_rules(self, usable: list[str], now: float) -> None:
        for rule in self.rules:
            if rule.source not in usable:
                rule.active = False  # Unknown is not negative evidence.
                continue
            latest = self._history[rule.source][-1]
            triggered = rule.trigger(latest.payload)
            cleared = rule.clear(latest.payload)
            if rule.active:
                if cleared is True or (triggered is None and cleared is None):
                    rule.active = False
                elif triggered and latest.event_id not in rule.evidence:
                    rule.evidence = (rule.evidence + [latest.event_id])[
                        -self.config.max_evidence_ids :
                    ]
                continue
            if triggered:
                run = self._run(rule.source, rule.trigger)
                if run and run[-1].end_s - run[0].start_s >= rule.sustain_s:
                    rule.active, rule.onset_s, rule.evidence = True, now, self._cite(run)

    def _good(self, source: str):
        c = self.config
        if source == "speech":

            def test(p: SpeechMetricsPayload) -> bool | None:
                if not p.wpm or self._pausing(p):
                    return None  # Silence or unknown coverage says nothing positive.
                return c.pace_low_clear_wpm <= p.wpm <= c.pace_high_clear_wpm and (
                    p.filler_rate_per_min is None
                    or p.filler_rate_per_min <= c.filler_rate_clear_per_min
                )

            return "pace_steady", test
        return "facing_audience", lambda p: _known(
            p.facing_score, lambda f: f >= c.facing_toward_at_least
        )

    def _positive(self, usable: list[str]) -> list[dict] | None:
        reasons = []
        for source in usable:
            code, test = self._good(source)
            verdict = test(self._history[source][-1].payload)
            if verdict is False:
                return None
            if verdict:
                reasons.append(
                    {"code": code, "source_event_ids": self._cite(self._run(source, test))}
                )
        return reasons or None

    # Decision -----------------------------------------------------------------

    def _tick(self) -> None:
        self._timer = None
        if not self.running:
            return
        self.evaluate()
        self._timer = asyncio.get_running_loop().call_later(self.config.tick_interval_s, self._tick)

    def evaluate(self) -> None:
        if not self.running:
            return
        now = self.context.clock.now()
        usable = [s for s in SOURCES if self.usable(s, now)]
        self._update_rules(usable, now)
        active = [r for r in self.rules if r.active]
        order = {rule.code: index for index, rule in enumerate(self.rules)}

        if not usable:
            self._neutral_since = self._positive_since = None
            if self.state != "NEUTRAL":
                self._emit("NEUTRAL", [], [])  # Input loss is shown separately; not a reaction.
            return

        positive = None if active else self._positive(usable)
        if active:
            self._neutral_since = self._positive_since = None
            active.sort(key=lambda r: (r.onset_s, order[r.code]))
            newest = max(active, key=lambda r: (r.onset_s, -order[r.code]))
            target = newest.state
            reasons = [{"code": r.code, "source_event_ids": list(r.evidence)} for r in active]
        elif positive:
            self._neutral_since = None
            if self._positive_since is None:
                self._positive_since = now
            reasons = positive
            # ENGAGED needs positive evidence at every evaluation for engaged_after_s.
            if self.state == "ENGAGED" or (
                self.state == "INTERESTED"
                and now - self._positive_since >= self.config.engaged_after_s
            ):
                target = "ENGAGED"
            else:
                target = "INTERESTED"
        else:
            reasons = []
            self._positive_since = None
            if self._neutral_since is None:
                self._neutral_since = now
            target = (
                "NEUTRAL"
                if now - self._neutral_since >= self.config.neutral_after_s
                else self.state
            )

        if target == self.state:
            return
        if now - self.entered_s < self.config.min_state_dwell_s:
            return  # Hold the current reaction long enough to avoid flicker.
        self._emit(target, reasons, usable)

    def _emit(self, state: str, reasons: list[dict], usable: list[str]) -> None:
        now = self.context.clock.now()
        previous = self.state
        self.state, self.entered_s = state, now
        event_id = f"engagement-{self._sequence}"
        self._sequence += 1
        self.context.emit(
            {
                "schema_version": 0,
                "session_id": self.context.session_id,
                "event_id": event_id,
                "source": "engagement",
                "type": "engagement.state",
                "timestamp_s": now,
                "payload": {
                    "state": state,
                    "previous_state": previous,
                    "reasons": reasons,
                    "usable_sources": usable,
                },
            }
        )
