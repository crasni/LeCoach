# Engagement engine (Lane 4, LIVE-01)

`RuleEngine` is the sole engagement engine. It implements the `EngagementEngine`
protocol from `lecoach.contracts.interfaces`, consumes canonical `speech.*`,
`vision.*` and `signal.status` events, and emits canonical `engagement.state`
events. Event shapes and reason-code meanings live in
[ARCHITECTURE.md](../../../docs/ARCHITECTURE.md#engagement-contract--role-4); every rule
default and unit lives in [config.py](config.py). No model or LLM is in this loop, and
the engine never imports capture, UI or coaching code.

## Decision rules

1. **Usable sources.** A source is usable when its newest observation is fresh
   (`speech_stale_s`, `vision_stale_s` measured from the capture window end),
   reports `available`, was captured after the source's latest `unavailable`/`error`
   `signal.status`, and, for vision, has a detected person and pose. An `available`
   status alone does not revive pre-outage observations. Older observations never
   replace a newer one; observations already stale on arrival are ignored. The two
   stale ages are a public interface: downstream consumers such as coaching
   composition (Lane 5, PR #24) read them from `RuleConfig` instead of defining
   their own.
2. **Negative rules** latch only with sustained evidence: consecutive windows (gaps
   up to `max_window_gap_s`, never spanning an outage, within the last
   `history_limit` observations) covering at least the rule's sustain duration. They
   clear only after their newest observation crosses the separate clear threshold
   (hysteresis), becomes unknown (null, or zero WPM for `pace_low`), or when their
   source stops being usable. While speech reports an active pause of at least
   `pause_hold_s`, the trailing window is filling with silence, so pace and filler
   rules neither latch nor clear.

   | Code | Source | Trigger → clear | Audience |
   | --- | --- | --- | --- |
   | `pace_high` | speech | WPM ≥ 180 for 15 s → ≤ 170 | CONFUSED |
   | `fillers_frequent` | speech | ≥ 12 fillers/min for 15 s → ≤ 8 | CONFUSED |
   | `pace_low` | speech | 0 < WPM ≤ 90 for 15 s → ≥ 105 | BORED |
   | `silence_prolonged` | speech | active pause ≥ 6 s → speech resumes | BORED |
   | `facing_away_sustained` | vision | facing < 0.4 for 6 s → ≥ 0.6 | BORED |

   Zero WPM means silence and is left to the pause rule. Null values, an `unknown`
   pause, a missing person and low movement never trigger anything. Activity is not
   used: more movement is not automatically better.
3. **State.** With no usable source the audience returns to `NEUTRAL` with no reasons
   immediately. Otherwise, if any negative rule is active, the most recently latched
   rule chooses `CONFUSED` or `BORED` and every active rule is cited. If none is
   active and every usable source with a verdict looks good (`pace_steady`: 105–170
   WPM and at most 8 fillers/min; `facing_audience`: facing ≥ 0.6), the audience
   becomes `INTERESTED`, citing one reason per source in its positive band. Speech
   gives no verdict, neither good nor bad, for null or zero WPM or while an active
   pause of at least `pause_hold_s` is reported; another source can then carry the
   positive evaluation. It becomes `ENGAGED` only after every
   evaluation for `engaged_after_s` was positive; any non-positive evaluation restarts
   that timer. Mixed or unknown observations drift back to `NEUTRAL` after
   `neutral_after_s`.
4. **Smoothing.** Apart from the no-input reset, a state is held for at least
   `min_state_dwell_s` before another transition. The browser additionally ripples a
   change across seats, so faces do not all flip at once.
5. **Timing and evidence.** Each emitted event carries the shared clock time of the
   decision; reasons cite at most `max_evidence_ids` supporting event IDs with their
   original capture times, all no later than the decision. A negative reason cites the
   run that latched it plus later windows that still meet the trigger, so a rule held
   inside its hysteresis band can cite windows older than the stale age. In live mode the engine re-evaluates every `tick_interval_s`, so
   stale inputs are dropped without waiting for a new event. After `stop()` nothing
   is emitted; `start()` resets all state for a new session.

## Checks

```sh
uv run pytest -q tests/test_engagement.py
uv run lecoach replay --case weak_to_improved            # computed audience (default)
uv run lecoach replay --case weak_to_improved --audience authored
```

`weak_to_improved` yields `NEUTRAL → CONFUSED (20 s, pace_high) → BORED (30 s,
facing_away_sustained) → INTERESTED (35 s) → ENGAGED (40 s)`. Lane 2's synthetic
speech fixtures trigger `pace_high`, `fillers_frequent` and `silence_prolonged`; outage,
silence-only, unsupported-language and delayed-delivery cases produce no negative
state. After fast speech stops, the audience stays `CONFUSED` and then becomes
`BORED` (`silence_prolonged`) instead of briefly showing `INTERESTED` from
silence-filled windows (issue #6). These are synthetic replays, not live pipeline
evidence. Thresholds are demo
heuristics to retune with recorded rehearsals in LIVE-02.
