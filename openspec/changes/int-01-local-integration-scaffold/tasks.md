# Tasks

Migrated from `docs/plans/INT-01.md` on 2026-10-07. Checked tasks reflect existing local implementation in `b7a42cd` and `802042e`, supported by [STATUS.md](../../../docs/STATUS.md#int-01-local-scaffold-validation); migration does not rerun or claim new application validation. [TASKS.md](../../../TASKS.md) remains authoritative for ownership and task progress. On 2026-10-07 the maintainer explicitly instructed completion and archiving, accepting the merged scaffold and waiving the remaining peer-review/downstream signoff gate.

## 1. Confirm the integration handoff

- [x] 1.1 Inspect Lane 5 preparation at `b8f5597` / PR #1 and reuse `checks/coaching/` unchanged from `dcc280f`; verify original fixture checks and authorship in local commit `b7a42cd`.
- [x] 1.2 Record executable seams, provenance, clocks, module boundaries, and runtime baseline in ARCHITECTURE; verify the documented handoff matches the implemented public contracts.

## 2. Scaffold and executable contracts

- [x] 2.1 Establish the Python package, frontend shell, pinned runtime files, and lockfiles; verify frozen core setup succeeds without capture/model packages.
- [x] 2.2 Implement strict event, completed-session, and feedback validation with contract checks; verify `uv run pytest -q tests/test_contracts.py` passes and all reviewed fixture cases validate.
- [x] 2.3 Export JSON Schema and generate frontend types; verify `uv run python scripts/export_schema.py --check` and `npm --prefix frontend run types:check` pass, and document regeneration in README/ARCHITECTURE.

## 3. Session lifecycle and event routing

- [x] 3.1 Implement shared monotonic/fake clocks, injected subsystem protocols, and FIFO routing; verify startup ordering, reentrant routing, and delivery-time checks in `tests/test_runtime.py`.
- [x] 3.2 Implement isolated lifecycle, event deduplication, bounded startup/stop/drain, consumer failure cleanup, and validated feedback; verify runtime checks cover partial startup failure, timeout, late finals, repeated calls, and consecutive sessions.
- [x] 3.3 Document lifecycle bounds, adapter cleanup obligations, and sole engine/recorder boundaries in ARCHITECTURE; verify a consumer can use the shared context without importing another subsystem implementation.

## 4. Local API and transport

- [x] 4.1 Expose prepare/subscribe/start/stop, snapshots, feedback, fixture discovery, and preview; verify `tests/test_api.py` covers subscribed startup, origins, unavailable inputs, and authored-summary behavior, and record routes in ARCHITECTURE.
- [x] 4.2 Bound browser queues and implement snapshot reconnection; verify overflow closes with code 1013 without dropping recorder delivery and reconnection does not restart capture.
- [x] 4.3 Build the synthetic inspection shell and volatile preview seam; verify the frontend build and browser checks cover controls, mode labels, empty feedback, repeat sessions, mobile layout, and reconnect.

## 5. Deterministic replay and handoff examples

- [x] 5.1 Preserve delivery order, capture timestamps, IDs, and monotonic fake time; verify all nine cases / ten sessions with `uv run python scripts/validate_fixtures.py` and runtime determinism checks.
- [x] 5.2 Separate authored complete-stream replay from injected consumer outputs and keep early-stop feedback unavailable; verify replay/transport checks and document authored-output limitations in README/STATUS.
- [x] 5.3 Provide the headless command and public subscription example; verify `uv run lecoach replay --case empty_session` and `uv run python examples/consume_replay.py` run without devices or models.

## 6. Integration verification and publication preparation

- [x] 6.1 Verify the combined scaffold with 60 Python tests, fixture checks, lint, schema/type parity, production build, and four Chromium checks; record observed results and environment limitations in STATUS.
- [x] 6.2 Verify setup in an isolated fresh working-tree copy and core wheel fixture packaging; record passing setup commands and the standalone offline-wheel dependency-resolution limitation accurately in STATUS.
- [x] 6.3 Prepare scoped local commits and update board/status/handoff links; verify the role branch contains implementation commits `b7a42cd` and `802042e`, with publication still pending.
- [x] 6.4 Prepare the final reviewable commit set, including this migration, and request explicit push approval naming exact commits and `git@github.com:crasni/LeCoach.git` / `agent/integration`; verify the user's approval matches that commit set and destination before publishing.
- [x] 6.5 After approval, publish only the approved role-branch commits and open a scoped INT-01 PR with evidence/limitations; verify remote refs and the PR point to the approved commits, then link the PR and set the shared board to review.
- [x] 6.6 Record the maintainer's explicit acceptance of the merged scaffold and instruction to mark INT-01 complete and archive; record that the original collaborator-review/downstream signoff gate was waived, without claiming those reviews occurred.

## Workflow follow-up

Publication evidence (2026-10-07): the user explicitly approved publication of `b7a42cd`, `802042e`, `8ecacd4`, and `a7a91ef` to the role branch. SSH verified head `a7a91ef`; [PR #4](https://github.com/crasni/LeCoach/pull/4) subsequently merged as main `c0f6c68`. Its public reviews and comments were empty when checked. The maintainer subsequently instructed completion and archiving, replacing the original task 6.6 review gate with explicit maintainer acceptance. See [STATUS](../../../docs/STATUS.md#int-01-maintainer-acceptance).

- All 20 tasks are closed through implemented evidence, publication and the maintainer-authorized acceptance exception. This does not establish live P0 integration or accelerator inference.
- Archive with `$openspec-archive-change int-01-local-integration-scaffold`; verify the resulting main capability specs and archive record. The archive instruction does not grant push approval.
- Start separate proposals for later assigned tasks when dependencies allow; INT-02 live acceptance and INT-03 hardware/submission evidence remain separate work.
