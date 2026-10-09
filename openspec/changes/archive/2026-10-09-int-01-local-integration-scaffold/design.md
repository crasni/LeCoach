# Design

## Context

Closure decision (2026-10-07): the implementation is merged via PR #4, and the maintainer explicitly accepted completion and instructed archiving. The remaining peer-review/downstream signoff gate is waived for this scaffold; the historical implementation and migration decisions below are unchanged.

See [proposal.md](proposal.md#why) for motivation. This is a migration of the existing INT-01 plan, not a proposal to replace the locally implemented scaffold. The implementation baseline is commits `b7a42cd` and `802042e`; [STATUS.md](../../../../docs/STATUS.md#int-01-local-scaffold-validation) records its checks and limitations. No main OpenSpec capability specs existed before migration, so the four delta specs establish initial acceptance descriptions.

[ARCHITECTURE.md](../../../../docs/ARCHITECTURE.md) remains the semantic contract reference. [GitHub Issues](https://github.com/crasni/LeCoach/issues?q=is%3Aissue+label%3Acoordination) control ownership, branch assignment, task state and acceptance. The OpenSpec checklist preserves historical execution evidence, not live task tracking, and does not reassign other lanes.

## Goals / Non-Goals

**Goals:** Preserve one composition point, shared time/identity, validated producer/consumer seams, bounded failure handling, and model-free replay. Keep generated frontend contracts reproducible. Capture observed decisions and remaining acceptance gates in the standard proposal → specs/design → tasks workflow.

**Non-Goals:** Implementing capture/models, an engagement algorithm, a recorder or moment selector, or production rehearsal UI during migration. These remain the assigned subsystem work. No new v0 fields, persistent store, raw-media recording, remote service, hardware claim, or P1 capability is introduced.

## Decisions

### One local process with injected components

Python 3.12.14 with uv runs FastAPI, the controller, and an in-process FIFO bus; Node 24.11.0/npm builds the React/TypeScript Vite shell. The pinned runtime files and lockfiles supply reproducible core setup. This keeps capture/model adapters close to their Python consumers and supports one local launch. A separate queue service or database would add deployment and lifecycle complexity without an INT-01 need.

`Components` is the composition seam. `SessionContext` shares identity, clock, `emit`, and configuration. The capture, vision-preview, engagement, recorder, and feedback protocols live in `src/lecoach/contracts/interfaces.py`. Capture/inference workers must marshal emissions onto the controller's event loop. Optional model dependencies are added through integration after producer owners verify compatibility; the core manifest currently contains no capture/model packages.

### One executable schema with generated frontend types

Strict Pydantic models implement ARCHITECTURE's v0 shapes. `scripts/export_schema.py` exports `contracts/schema.json`; the frontend generation script derives TypeScript. Both have parity checks. Maintaining independent handwritten frontend schemas would permit drift, so changes follow the shared-contract review and regeneration path.

The controller validates incoming events and stable-ID retries. Completed timelines and feedback are validated again at the consumer boundary, including session identity and evidence references. It keeps only deduplication hashes and latest display state; the actual recorder remains the sole full timeline owner.

### Shared clock and bounded lifecycle

Consumers attach before producers start. One monotonic clock defines capture time; fake time supports replay. Startup has a 5-second default bound per adapter. Failure of one adapter surfaces status without disabling a usable peer. Start/stop retries share controller work.

Stop freezes capture end, stops the engine, stops all acquisition, then drains producers under one default 2-second budget. Late pre-end observations can inform the recorder before completion but cannot revise displayed reactions. Timed-out sources are incomplete. Feedback generation has a default 5-second deadline. Independent unbounded drains or adapter-owned zero points would undermine consistent completion/time semantics.

### Loopback browser transport and bounded delivery

Use local HTTP for lifecycle/snapshot/feedback and WebSocket for snapshot/event wrappers. See ARCHITECTURE for the route inventory. Bind to `127.0.0.1`; Vite proxies local API/WebSocket traffic during development, and the backend serves `frontend/dist` for the checkout demo. Assets stay local and origins are restricted.

Browser delivery uses a default 128-event queue per client, independent of recorder delivery. Overflow closes that connection with code 1013; reconnect sends current state without another start. An unbounded queue would allow slow browsers to consume increasing memory. Preview uses the adapter's latest JPEG, capped by default at 512 kB and five frames/s; it is volatile and excluded from events. Browser camera capture would create a competing device stream.

### Authored replay and consumer replay share boundaries

Keep `checks/coaching/` unchanged from the reviewed Lane 5 preparation, preserving its authorship. Replay processes arrays in delivery order, including late events; the fake clock never moves backward and test-only delivery schedules do not change capture times. Sorting inputs first would erase the late-delivery cases.

The default shell is a synthetic inspection surface. It displays authored reactions/feedback and serves a summary only after authored completion. An injected engine suppresses authored reactions; an injected recorder/generator supplies validated computed outputs. Headless output is a delivery trace, not an additional production logger. The public subscription example exercises the same seam.

### Preserve planning links while moving execution artifacts

Store proposal, design, delta specs, and tasks in this change. Replace `docs/plans/INT-01.md` with a compatibility pointer; update existing board/architecture links. Keep the authoritative product, ownership, contract, and evidence documents in place. Duplicating the full old plan would leave two execution plans to reconcile.

## Risks / Trade-offs

- Authored fixture success can be mistaken for live or algorithm correctness → keep fixture/live and authored/computed labels, retain STATUS limitations, and leave INT-02 acceptance separate.
- Producer packages may conflict with the pinned core runtime → owners verify compatibility and coordinate manifest/contract changes through integration.
- Positive audience reason codes and recovery evidence remain incomplete → Lane 4 coordinates them with coaching before computed-feedback acceptance.
- Fake adapter cleanup does not establish real device release or inference latency → verify those during producer stabilization and INT-02.
- A built wheel includes core fixtures but does not bundle the browser UI → use the documented checkout build for this milestone; record the isolated-install evidence accurately.
- Local checks do not establish downstream agreement → leave publication, collaborator review, and acceptance tasks open.

## Migration Plan

1. Record the existing implementation and validation as checked tasks, with links to evidence; retain publication/review gates as unchecked.
2. Validate all four delta specs and the dependency-complete artifact set with the installed OpenSpec CLI.
3. Keep this change active until the reviewed handoff is accepted. Do not sync main specs or archive it during this planning migration.
4. Continue via the apply skill when explicitly requested. Any push still requires separate approval of the exact commits and role-branch destination under AGENTS.md; workflow commands do not grant it.
5. After accepted completion, use the archive workflow to incorporate delta specs into main OpenSpec specs. No application/data migration is required here. Reverting the documentation migration restores the previous plan; the existing implementation is unaffected.
