# Proposal

## Why

Live audience response is LeCoach's central product value, so producers, coaching and the UI need one deterministic engine with traceable reasons plus a screen that shows its reactions. LIVE-01 ([issue #18](https://github.com/crasni/LeCoach/issues/18)) merged through [PR #7](https://github.com/crasni/LeCoach/pull/7) without integration review or an OpenSpec change, and issue #18's acceptance asks integration and coaching to confirm the reason/evidence interface, so this change records that behavior and proposes the fixes review found.

## What Changes

- **Record (merged in PR #7):**
  - the sole engagement engine in `src/lecoach/engagement/`, which turns canonical speech, vision and `signal.status` events into evidence-cited `engagement.state` transitions;
  - sustained-evidence negative rules with separate clear thresholds and a minimum state dwell;
  - unusable input (missing, stale, unknown or outage) never counted as poor delivery;
  - one validated rule configuration, and the reason codes in [ARCHITECTURE.md](../../../docs/ARCHITECTURE.md#engagement-contract--role-4);
  - the rehearsal screen: rippling 2D audience, plain-language reasons, timeline, input status, metrics, transcript, live preview slot and provenance labels;
  - composition in Lane 1 files, merged before integration review: the served app and `lecoach replay` compute audiences with the engine during synthetic replay (`--audience authored` restores authored ones); live mode stays unavailable.
- **Proposed engine refinements (behavior delta for review):**
  - `ENGAGED` requires positive evidence at every evaluation for the engaged duration, as ARCHITECTURE's "sustained positive observations" requires. The merged code let interrupted evidence through.
  - While speech reports an active pause, pace and filler rules hold, and that window gives no pace verdict. This answers Lane 2's issue #6 observation that silence-filled trailing windows produced `pace_steady`.
  - Only an observation captured after an outage restores a source, and sustained runs never span an outage.
  - The observation history bound moves into the configuration. Consumers can read the stale ages there.
- **Proposed screen fixes:**
  - metric values show only when captured after the source's latest status;
  - a status wins capture-time ties and keeps its specific reason through later unavailable windows;
  - the waiting message follows current input;
  - the transcript stays in capture order and the timeline keeps every transition;
  - the camera preview appears only once a frame arrives, retries while the camera opens, and is removed when the camera fails;
  - adapter status reasons get plain-language text.
- **Out of scope:**
  - live adapter wiring and composition (issue #19, AUD-01, VIS-01, INT-02);
  - recording and feedback selection (COACH-01);
  - threshold tuning on real rehearsals, P1 features, and any v0 event-shape change.

## Capabilities

### New Capabilities

- `audience-engagement`: Deterministic simulated audience reactions from speech and vision observations. Covers input usability, outages and staleness, sustained-evidence rules, pause holding, hysteresis and dwell, evidence-cited transitions, session isolation, and the consumer-readable rule configuration.
- `rehearsal-screen`: The browser rehearsal experience that renders engine output. Covers audience visualization, reaction explanations, timeline, input status and metrics, transcript, camera preview, mode and provenance labels, and narrow-screen layout.

### Modified Capabilities

None. No capability is in `openspec/specs/` yet. INT-01's unarchived `synthetic-replay` and `local-rehearsal-transport` deltas describe the default replay shell this change altered; design.md records both interactions for the integration owner to reconcile before archiving.

## Impact

- **Code:**
  - `src/lecoach/engagement/` (engine, configuration, composition helper, rules README);
  - `frontend/src/` (`main.tsx`, `Audience.tsx`, `copy.ts`, `style.css`);
  - `tests/test_engagement.py`;
  - `frontend/e2e/replay.spec.ts` and `frontend/e2e/ui-states.spec.ts`.
- **Shared files (Lane 1):** `src/lecoach/api/app.py` and `src/lecoach/cli.py` compose the engine. `frontend/playwright.config.ts` resolves the backend executable on Windows. ARCHITECTURE carries the reason codes.
- **Interfaces:** No event schema, generated type or dependency change.
  - The reason vocabulary, citation semantics and `RuleConfig` stale ages are consumed by Lane 5's open PR #24.
  - The refinements change when `INTERESTED`, `ENGAGED` and pace rules fire, but not event shapes or codes.
- **Coordination:**
  - Lane 2 ran the issue #6 speech defaults (English, 10 s window, 1 s hop) against this engine, and that run produced the pause observation the refinement addresses.
  - Lane 5's PR #24 marks the authored `weak_to_improved` oracle as historical; on `main` that README still awaits Lane 4 output.
  - Issue #17 holds the disposition of the unmerged `revert-7-agent/avatar-ui` branch.
  - Live state, blockers and acceptance stay in issues #18 and #19. [STATUS.md](../../../docs/STATUS.md#live-01-local-engine-and-rehearsal-screen) holds the 2026-10-08 PR #7 evidence; checks for this change belong on issue #18 and the follow-up PR.
