# Tasks

This checklist is a historical work breakdown, not a tracker. [Issue #18](https://github.com/crasni/LeCoach/issues/18) owns LIVE-01's state, blockers, remaining handoffs and acceptance; [issue #19](https://github.com/crasni/LeCoach/issues/19) owns LIVE-02. Unmarked tasks record work merged through [PR #7](https://github.com/crasni/LeCoach/pull/7) (`fc96ec8`, `6f276eb`; merge `6326825`). Tasks marked *(post-migration)* were done on `agent/avatar-ui` on 2026-10-09 for the follow-up PR.

## 1. Engine rules, configuration and engine docs

- [x] 1.1 Declare every rule default and unit in `src/lecoach/engagement/config.py`, rejecting inverted pace, filler and facing thresholds. Verify with `test_rule_configuration_is_validated` in `uv run pytest -q tests/test_engagement.py`.
- [x] 1.2 Implement the source-usability, ordering and staleness checks: newest-window ordering, stale-on-arrival rejection, `signal.status` outages, and vision person/pose. Verify the stale, older-observation, absent-person and camera-outage tests in `tests/test_engagement.py`. *(post-migration)* `test_stale_on_arrival_observation_is_not_used_or_cited` now places the late window within the run gap, so it fails if the stale-on-arrival check is removed (mutation-checked).
- [x] 1.3 Implement the sustained-evidence latches, hysteresis release, negative state mapping, positive recovery, neutral drift and minimum dwell. Verify with the hysteresis, jitter, sustained-facing, prolonged-silence and `weak_to_improved` deterioration/recovery tests. *(post-migration)* Add `test_mixed_evidence_drifts_back_to_neutral`.
- [x] 1.4 Emit evidence-cited transitions with shared-clock timestamps, starting `NEUTRAL`, with restart isolation, a live-mode tick and no emission after stop. Verify with the restart/stop, live-tick and evidence-ordering tests, and run every coaching fixture through `parse_event`.
- [x] 1.5 Document the rules in `src/lecoach/engagement/README.md` and propose reason codes in ARCHITECTURE. Verify that the README's `weak_to_improved` sequence matches `uv run lecoach replay --case weak_to_improved`.
- [x] 1.6 *(post-migration)* Specify the citation semantics coaching relies on. Verify with `test_held_rule_cites_only_triggering_observations`.
- [x] 1.7 *(post-migration)* Require uninterrupted positive evidence for `ENGAGED`. Verify with `test_engaged_needs_uninterrupted_positive_evidence` (ENGAGED 5 s after positive evidence began, not earlier), `test_mixed_evidence_restarts_the_engaged_timer`, and the tightened jitter test (never `ENGAGED`).
- [x] 1.8 *(post-migration)* Hold pace and filler rules during an active pause of at least `pause_hold_s`, and give such windows no pace verdict (issue #6 observation). Verify with:
  - `test_trailing_silence_does_not_count_as_a_steady_pace`;
  - `test_active_pause_holds_pace_rules`;
  - `test_active_pause_is_not_positive_pace`, with no rule latched;
  - `test_pausing_speech_gives_no_verdict_so_facing_can_carry_engagement`;
  - `test_completed_pause_does_not_hide_a_steady_pace`, where the completed-pause window alone produces the transition.
- [x] 1.9 *(post-migration)* Restore a source only with an observation captured after its outage, stop sustained runs at outages, and move the history bound into `RuleConfig.history_limit`. Verify with:
  - `test_recovery_status_alone_does_not_revive_pre_outage_evidence`, which fails if a recovery status revives the source or a run crosses the outage;
  - `test_history_limit_bounds_how_long_a_run_can_be_measured`;
  - the extended configuration test (filler inversion, pause hold, history bound).
- [x] 1.10 *(post-migration)* Update the engine README for 1.6–1.9. Verify that the full engine suite passes: `uv run pytest -q tests/test_engagement.py` (32 tests).

## 2. Synthetic replay composition

- [x] 2.1 Add `replay_with_engine()`, which supplies only the engine, rejects live mode and keeps health `live_integrated` false. Verify with `test_default_app_computes_audience_but_keeps_live_unavailable`.
- [x] 2.2 Default the served app and `lecoach replay` to engine-computed audiences, with `--audience authored` as the escape hatch, and update README. Verify that `uv run lecoach replay --case weak_to_improved` emits `NEUTRAL → CONFUSED (20 s) → BORED (30 s) → INTERESTED (35 s) → ENGAGED (40 s)` and `--audience authored` the authored ones. `examples/consume_replay.py` passes no factory, so it still runs and reports the five authored transitions.
- [x] 2.3 Replay Lane 2's speech fixtures through the engine. Verify that `test_speech_fixtures_drive_expected_rules` triggers `pace_high`, `fillers_frequent` and `silence_prolonged`, and finds no negative state for outages, silence-only, unsupported language or delayed delivery.
- [x] 2.4 *(post-migration)* Check the coaching consumer without merging its branch. In an isolated worktree of `agent/session-analysis` at `9850ae0` (PR #24), run `pytest tests/test_coaching.py tests/test_feedback.py tests/test_engagement.py`. Verify 51 passed as-is, and 63 with this change's `src/lecoach/engagement` and `tests/test_engagement.py` overlaid, with identical moments for every coaching case.

## 3. Rehearsal screen

- [x] 3.1 Replace the inspection shell with the rehearsal screen: rippling SVG audience, reason copy, timeline, input chips, metrics, transcript partials, live preview slot and provenance labels. Verify with `npm --prefix frontend run build`.
- [x] 3.2 Update the browser checks for computed transitions with reasons and the not-connected live option. Verify that `npm --prefix frontend run test:e2e` passes the replay, stop/repeat, empty/narrow and reconnection checks.
- [x] 3.3 Let `frontend/playwright.config.ts` resolve the backend executable on Windows and POSIX. Verify that the e2e web server starts on the Windows host.
- [x] 3.4 *(post-migration)* Fix the screen's state handling:
  - show metrics only when captured after the source's latest status;
  - derive input status so a status wins capture-time ties and keeps its specific reason through later unavailable windows;
  - drive the waiting message from current input;
  - keep transcripts in capture order;
  - keep every transition;
  - show the live preview only after a frame arrives, retry it while the camera opens, and remove it when the camera fails;
  - add plain-language text for every status reason in the speech and vision adapter READMEs.

  Verify with `frontend/e2e/ui-states.spec.ts`, which uses a mocked local backend:
  - the outage check scripts a mid-session outage, a late pre-outage window, a recovery status, a missing pose runtime and out-of-order utterances;
  - the live check scripts a failed then retried preview and a camera failure.

  All 7 Chromium checks pass, stable across three runs. With the blanking disabled, the outage check fails.
- [x] 3.5 *(post-migration)* Add a camera-unavailable replay check. Verify that it confirms plain status text and an unaffected speech pace; it does not exercise mid-session blanking, which 3.4 covers.

## 4. Evidence

- [x] 4.1 Record the validation host, commands, results and limitations in STATUS for PR #7. Verify that pytest, ruff, the schema check, fixture validation and the e2e results are recorded with the pre-existing Windows `types:check` CRLF failure.
- [x] 4.2 *(post-migration)* Validate this change. Verify that `openspec validate live-01-audience-engagement --strict` passes.

## Workflow follow-up

- Archive this change after issue #18's acceptance is recorded. Confirm that `audience-engagement` and `rehearsal-screen` appear under `openspec/specs/`. Coordinate archive order with INT-01's change, whose `synthetic-replay` and `local-rehearsal-transport` wording this change affects.
- LIVE-02 (issue #19: live adapter wiring, real-device checks, threshold retuning) gets its own change if live composition needs new agreed behavior.
