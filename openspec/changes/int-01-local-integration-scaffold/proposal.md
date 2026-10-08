# Proposal

## Why

The four subsystem owners need one runnable local scaffold and compatible contracts before implementing the live rehearsal pipeline. This change migrates the existing INT-01 plan into OpenSpec, recording the scaffold already implemented locally and the remaining publication/review gates without starting another implementation.

## What Changes

- Establish executable v0 event, completed-session, feedback, and adapter contracts with generated frontend types.
- Provide isolated session lifecycle, a shared capture clock, FIFO routing, bounded startup/drain, and failure handling.
- Expose a loopback API, reconnectable event stream, volatile preview seam, and browser inspection shell.
- Reuse the reviewed coaching preparation cases for deterministic synthetic replay with explicit authored-output provenance.
- Provide locked setup, reproducible checks, and downstream consumption examples.
- Replace the full plan at `docs/plans/INT-01.md` with a compatibility link to these artifacts; keep ownership/progress in [TASKS.md](../../../TASKS.md).

The implementation in `b7a42cd` and `802042e` is merged through PR #4; checked tasks record existing evidence, rather than new work performed during migration. On 2026-10-07 the maintainer accepted completion and instructed archiving, waiving the remaining peer-review/downstream signoff gate. Live inference, audience smoothing, production coaching, hardware validation, and P1 features are outside INT-01.

## Capabilities

### New Capabilities

These are initial OpenSpec descriptions of the existing scaffold; the repository previously had no capability specs.

- `event-contracts`: Validated shared events and consumer outputs, with generated cross-language types.
- `session-lifecycle`: Session identity, shared time, routing, bounded shutdown, and injected subsystem boundaries.
- `local-rehearsal-transport`: Local lifecycle API, bounded event delivery, snapshots, preview, and browser controls.
- `synthetic-replay`: Deterministic fixture replay, honest provenance, and model-free handoff examples.

### Modified Capabilities

None.

## Impact

The scaffold spans `src/lecoach/contracts/`, `runtime/`, `api/`, `cli.py`, `frontend/`, generated `contracts/schema.json`, checks, examples, and locked Python/npm configuration. Audio, vision, engagement, and coaching directories are implementation slots for their assigned owners.

[ARCHITECTURE.md](../../../docs/ARCHITECTURE.md) remains authoritative for schemas, units, clocks, and subsystem boundaries; these delta specs capture behavioral acceptance gates. [GUIDE.md](../../../GUIDE.md) controls product scope, and [STATUS.md](../../../docs/STATUS.md#int-01-local-scaffold-validation) records actual validation and limitations. This migration changes planning documents only and does not revise the v0 contract or claim live/hardware completion.
