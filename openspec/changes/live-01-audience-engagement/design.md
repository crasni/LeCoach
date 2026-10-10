# Design

## Context

See [proposal.md](proposal.md#why). The base implementation is on `main` (PR #7, merge `6326825`). This design records the decisions behind it and the refinements this change proposes. The requirements are in the `audience-engagement` and `rehearsal-screen` delta specs.

Other documents keep their roles:

- [ARCHITECTURE.md](../../../docs/ARCHITECTURE.md#engagement-contract--role-4) owns event semantics.
- `src/lecoach/engagement/config.py` owns every rule default and unit.
- `src/lecoach/engagement/README.md` explains the rules.
- Issues #18 and #19 own state and acceptance. [STATUS.md](../../../docs/STATUS.md#live-01-local-engine-and-rehearsal-screen) holds the 2026-10-08 evidence.

The engine plugs into INT-01's `EngagementEngine` seam: `start(context)`, `on_event(event)`, `stop()`. The controller forwards speech/vision events, including `signal.status`, through its FIFO bus and rejects engagement emissions once stopping begins. In fixture mode, the replay seam advances a fake clock to each delivery time before dispatch and skips authored engagement events whenever an engine is injected.

## Goals / Non-Goals

**Goals:**

- Make the engine's decision a pure function of the delivered stream, delivery times and configuration, so fixtures are repeatable acceptance tests.
- Give every audience transition evidence that Lane 5 can cite without recomputing a state.
- Keep rendering independent of the rules.

**Non-Goals:**

- Weighting or scoring delivery.
- Using activity/gesture signals; more movement is not automatically better.
- Inferring intent from pauses.
- Changing v0 events, or adding a second engine or recorder.
- Persisting rehearsal data.
- Composing live adapters (issue #19).

## Decisions

### Latched rules instead of a score

Each negative behavior is one named rule. A rule latches on sustained evidence and releases at a separate clear threshold. The newest latched rule picks `CONFUSED` or `BORED`, and every latched rule is cited.

*Alternative:* a weighted engagement score with smoothing. Rejected because it produces reasons that are hard to explain and creates a second score that ARCHITECTURE forbids in feedback. Named rules map directly to Lane 5's moments and to UI copy.

### Measure sustain over capture windows, not over calls

A rule's sustain is the capture span of consecutive triggering windows, from the first window's start to the last window's end. Gaps are at most `max_window_gap_s`, and a run stops at the source's latest outage. Sustain is not the number of events or the wall time between evaluations.

This keeps fixture cadence (5 s hops) and live cadence (1 s hops, the speech default recorded in issue #6) on the same thresholds. Silence uses the producer's active-pause duration directly. The per-source history is bounded by `history_limit` (64 observations), so a sustain must fit within that many consecutive windows.

*Alternative:* counting N consecutive events. Rejected because it ties thresholds to hop length.

### Unknown is never negative

Usability is decided per source before any rule runs. A stale, unavailable or outage-affected source, or vision without a person or pose, simply drops out, and its rules release. Only an observation captured after an outage restores the source. An `available` status alone does not revive older evidence, because that would let pre-outage windows re-latch a rule. Null values neither trigger nor clear. Zero WPM is excluded from the pace rules because it means silence. With no usable source, the audience resets to `NEUTRAL` immediately; the UI shows input loss separately.

This follows ARCHITECTURE's rule that signal absence is not evidence of poor delivery. Lane 5's limitation cases rely on it.

### Pauses hold pace and filler rules (proposed refinement)

Speech metrics are 10 s trailing windows. When the speaker stops, each later window contains more silence, so WPM falls through the comfortable band while the producer already reports an active pause.

Lane 2 ran its adapter against the merged engine (issue #6, PR #26 evidence). Fast speech followed by silence went CONFUSED → INTERESTED (`pace_steady` citing mostly silent windows) → BORED. While an active pause of at least `pause_hold_s` is reported, pace and filler rules therefore neither latch nor release, and that window gives speech no verdict, like null WPM. Another in-band source, typically facing, can still keep the evaluation positive and advance `ENGAGED`. The default of 1 s equals the producer's pause minimum, so every reported active pause holds. A completed pause does not hold.

*Alternative:* make a holding pause count as out of band. Rejected: every ordinary pause of 1 s or more would then restart the `ENGAGED` timer and start drifting toward `NEUTRAL`, although looking at the audience while pausing is good delivery.

*Alternatives:*

- Treat only long pauses (2 s) as holding. Rejected: within 1.5 s of silence after 200 WPM speech, a 10 s window already reads about 170 WPM, the clear edge.
- Discount WPM by the pause duration. Rejected: the engine would re-derive a speech measurement, which belongs to Lane 2.

### Recovery path and smoothing

Positive evidence requires every usable source with known values to be in its positive band:

- pace between the two clear thresholds and fillers at or below their clear rate;
- facing at or above the facing-toward threshold.

Null or zero WPM and a holding pause give speech no verdict. Each source in band contributes its own reason.

Positive evidence yields `INTERESTED`. `ENGAGED` requires every evaluation for `engaged_after_s` to be positive; any other evaluation restarts that timer. Mixed evidence drifts to `NEUTRAL` only after `neutral_after_s`. Every transition except the no-input reset also respects `min_state_dwell_s`.

The merged code timed `ENGAGED` from entry into `INTERESTED` and checked only the current evaluation, so alternating windows could reach it. That contradicted ARCHITECTURE's "`ENGAGED` for sustained positive observations" and coaching's use of `ENGAGED` as a sustained strength. This change proposes the fix.

*Alternative:* only per-rule hysteresis. Rejected because positive and neutral transitions could still flicker near band edges.

### Ordering, time and citations

Observations are kept per source in window-end order. Older or equal window ends are ignored, as are observations already stale on arrival. A late observation therefore cannot overwrite a newer one or rewrite a reaction already shown. Decisions are stamped with the shared clock.

A negative reason cites the run that latched it, plus later triggering windows, up to `max_evidence_ids`. Values in the hysteresis band are not cited, because they do not meet the trigger.

Without input events, staleness would only be noticed on the next observation. Live mode therefore also re-evaluates on a loop timer (`tick_interval_s`). Fixture mode does not tick, which keeps replay deterministic under fake time.

### Rendering stays a consumer

The browser shows the latest `engagement.state` and keeps a deduplicated, uncapped transition list. The engine's reactions are discrete; the UI adds visual smoothing only, never state:

- seats adopt a new state in a staggered ripple;
- one in four seats stays neutral during negative states;
- reduced motion disables animation.

The UI's state handling:

- **Input status** is derived from the latest status and metrics events in the snapshot. A status event wins a capture-time tie, and a later unavailable metrics window keeps the status's specific reason. The backend snapshot's coarser `input_status` is only a fallback before any event.
- **Metrics** are shown only when captured after the source's latest status event. Neither an outage nor a later recovery status brings back a pre-outage value.
- **The waiting message** follows current input, not the last transition.
- **Transcripts** are kept in capture order.
- **The preview** is requested only while the camera's status is available. It stays hidden until a frame arrives, retries every 2 s, and is removed when the camera fails, so a frozen stream is never shown.

Plain-language wording for each state, reason code and input-status reason lives in `frontend/src/copy.ts`; the engine sends only codes. Composite messages, such as the waiting notice, and mode labels are written in `main.tsx`.

### Composition for synthetic replay

`replay_with_engine()` returns a factory that supplies only the engine. For live mode it raises the existing `live_not_integrated` conflict, and it marks itself `live_integrated = False` so health stays honest.

The served app and `lecoach replay` now default to this factory. `--audience authored` keeps authored transitions. `examples/consume_replay.py` passes no factory, so it still reports authored transitions. Coaching remains authored because no recorder or generator is injected.

*Alternative:* leaving authored audiences as the default. Rejected because LIVE-01's deliverable is a rehearsal screen driven by the real engine.

## Risks / Trade-offs

- **[Coarse provenance]** With the engine injected, the snapshot reports `output_provenance: computed` and headless replay reports `computed_consumers`, although feedback is still authored. → The UI labels coaching as authored. Lane 1 owns the field and may want separate audience and feedback provenance.
- **[INT-01 spec interactions]** Two unarchived INT-01 deltas describe the authored default this change altered:
  - `synthetic-replay`: "Default complete-stream replay SHALL identify audience transitions … as authored". `replay_case()` without a factory still does that; only the app and CLI defaults changed.
  - `local-rehearsal-transport`: the "Synthetic rehearsal" scenario expects the default shell to present reactions as authored examples. The served shell now labels the audience as computed and only coaching as authored.

  → The integration owner reconciles both wordings before either change is archived.
- **[Lane 5 oracle drift]** `checks/coaching/expectations.json` cites authored transition IDs and times (20.5 s, 30.5 s, 42 s), but the engine computes 20 s, 30 s, 35 s and 40 s. → Lane 5's open PR #24 marks that oracle as historical. On `main`, checks/coaching/README.md still describes it as awaiting Lane 4 output.

  On 2026-10-09, PR #24's branch (`9850ae0`) ran in an isolated worktree without merging:
  - its coaching, feedback and engine tests pass (51);
  - with this change's `src/lecoach/engagement` and `tests/test_engagement.py` overlaid, they pass (with this change's engine tests replacing PR #7's);
  - every coaching case yields the same moments both ways, for example two improvements and one strength for `weak_to_improved`.
- **[Held-rule citations can age]** A rule held inside its hysteresis band keeps citing the windows that latched it. These can be older than the stale age when another transition re-cites the rule; a re-cited window can also simply age before the next transition. → This is intended. The coaching selector (PR #24) rejects a reason when its newest cited window, or the source's newest observation, is staler than that source's limit, and records an omission. Stale evidence therefore never becomes advice. The transition that latched the rule carries fresh evidence.
- **[Behavior change after merge]** The pause hold, uninterrupted `ENGAGED`, and outage boundaries change when `INTERESTED`, `ENGAGED` and pace/filler rules fire relative to PR #7. Codes and event shapes are unchanged. → Before merge, the follow-up PR asks integration and coaching (@crasni, @WolflordR) to review on issue #18, and Lane 2 (@firstsnow1226) is notified on issue #6.
  - `weak_to_improved` transitions are unchanged.
  - Lane 2's `prolonged_silence` fixture now returns to `NEUTRAL` at 30 s, where it showed `INTERESTED` before, because that window reports a new 1 s active pause.
- **[Public configuration coupling]** Coaching composition reads `speech_stale_s` and `vision_stale_s` from the engine's configuration. → Renaming or redefining them is an interface change that needs this review path and coaching sign-off.
- **[Sparse fixture vision]** Fixture vision arrives every 5–10 s, so with a 6 s vision stale age vision is briefly unusable between samples (for example, `usable_sources` is `["speech"]` at 20 s in `weak_to_improved`). → This is accurate for that input. VIS-01's live adapter emits 1 s windows, about 70 ms after their end on the measured Mac.
- **[Heuristic thresholds]** Bands assume English pace, the demo analysis language recorded in issue #6. → Issue #19 retunes thresholds from recorded rehearsals. Defaults stay documented as demo heuristics.
- **[Browser-only outage coverage]** None of the fixtures the replay UI serves has a mid-session outage or a live preview. → `frontend/e2e/ui-states.spec.ts` scripts both through a mocked local backend: an outage, a late pre-outage window, a recovery status, and a failing then recovering preview. A mutation check confirmed the outage check fails when blanking is disabled. Engine-side, `checks/speech/fixtures/microphone_lost.json` replays one through the engine.
- **[Missed transitions on reconnect]** A reconnection snapshot carries only the latest audience state, so transitions emitted while disconnected are missing from the browser timeline. → The recorder (COACH-01) owns the complete timeline.

## Migration Plan

The base is merged. The refinements land through a follow-up PR on `agent/avatar-ui` after review. Rollback is `lecoach replay --audience authored`, or reverting the composition lines in `api/app.py` and `cli.py`. The engine and screen have no persisted state or schema migration.

## Open Questions

- Should snapshot and replay provenance distinguish audience output from feedback output? This is Lane 1's decision and does not change these specs.
