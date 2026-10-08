# Proposal

## Why

LeCoach has a validated synthetic scaffold and initial competition/hardware research, but lacks a finished English proposal and a reviewable submission package tied to demonstrated behavior. INT-03 must turn that preparation into credible deliverables while exposing the live-demo and target-device dependencies that remain with INT-02 and the subsystem owners.

## What Changes

- Reconcile the integration branch with merged preparation PRs #1 and #3, preserving existing local work and contributor evidence; update the authoritative task/status records during implementation.
- Refresh official requirements and source provenance in the existing reference documents, resolving or explicitly recording cutoff, registration, submission-form, and originality/licensing questions.
- Produce an editable English proposal, a PDF export, and a local readiness record that maps important claims to verified evidence or clearly identified plans.
- Coordinate the existing demo plan with Lane 5's scenario/script, checking the final recording against its demonstrated input and inference mode.
- Provide a reproducible hardware-readiness and measurement record: distinguish synthetic replay, live CPU operation, vendor documentation, and actual UGen300 runs; document unavailable hardware without inventing measurements.
- Keep local preparation, live validation, and external publication/submission as separate completion gates under the existing approval workflow.

This change specifies submission deliverables and evidence acceptance. It does not implement microphone/camera adapters, engagement rules, coaching, or an accelerator adapter; change shared event contracts; take Lane 5's script/scenario ownership; or expand P0. INT-01 archive work remains separate.

## Capabilities

### New Capabilities

- `submission-package`: A reviewable English proposal/demo package with requirement checks, evidence-linked claims, unresolved gates, and recorded publication/submission state.
- `hardware-evidence`: Reproducible environment, compatibility, and performance evidence with explicit input/inference provenance and an honest unavailable-device outcome.

These describe acceptance of the delivered artifacts and evidence workflow, not new rehearsal runtime features. No main capability specs currently exist; the active INT-01 deltas cover different runtime behaviors.

### Modified Capabilities

None.

## Impact

Implementation belongs to Lane 1 on `agent/integration`. Expected changes are the existing [requirements](../../../docs/CONTEST.md), [sources](../../../docs/SOURCES.md), [demo plan](../../../docs/DEMO.md), [GitHub task Issue](https://github.com/crasni/LeCoach/issues/12), and [status](../../../docs/STATUS.md), plus `docs/submission/` deliverables and a hardware evidence guide. [GUIDE.md](../../../GUIDE.md) retains scope, and [ARCHITECTURE.md](../../../docs/ARCHITECTURE.md) retains contracts.

No application dependency or API change is planned. Live evidence requires INT-02 and owner handoffs; accelerator measurements additionally require a compatible device/runtime/model setup. Missing target hardware does not prevent local Stage I preparation. Private media, transcripts, session exports, credentials, and weights stay out of Git. Scoped role-branch publication follows AGENTS; final recording, external publication/submission and broader actions require separate applicable authorization.
