# INT-01 implementation plan

Status: implementation prepared locally; validation evidence is recorded in [STATUS.md](../STATUS.md). Publication and team review are pending.

## Execution sequence

Planning started locally on 2026-10-07 at the user's request, followed by the user's instruction to implement it. This document retains the execution order, acceptance gates, and original implementation proposals. [ARCHITECTURE.md](../ARCHITECTURE.md) now records the executable handoff and remains authoritative for shared contracts. [STATUS.md](../STATUS.md) distinguishes verified scaffold behavior from pending live implementation.

The first milestone is a reproducible local skeleton that lets each subsystem owner implement against the same interfaces. Replay will demonstrate wiring with explicitly authored audience and feedback outputs until the assigned owners supply their implementations. Their work replaces those fixture outputs through the same seams.

| Step | Deliverable | Acceptance before proceeding |
| --- | --- | --- |
| 1. Confirm the integration handoff | Review existing v0 contracts and Lane 5's preparation PR; record executable seams, fixture/live provenance, language baseline, and module placement in ARCHITECTURE. | Preserve compatible fixture shapes. Resolve any producer/consumer change with affected owners before they implement against it. Record review findings without merging or publishing remotely. |
| 2. Scaffold and executable contracts | Python package, minimal frontend shell, dependency lockfiles, validated event/session/feedback types, generated frontend types, and one shared configuration entry point. | A clean environment installs only core dependencies and validates all agreed fixtures without downloading models or opening devices. Generated types match the Python schema; invalid values and mismatched event source/type are rejected. |
| 3. Session lifecycle and event routing | Shared monotonic/fake clocks, adapter and consumer protocols, controller, and in-process subscriptions. | Subscribers attach before capture; session IDs isolate runs; retries deduplicate; partial startup failures release started adapters. Stop is idempotent, drains bounded pending work, lists timed-out sources, and rejects post-completion callbacks. |
| 4. Local API and transport | Start/stop/snapshot/feedback endpoints, event stream, and preview seam proposed below, to be recorded in ARCHITECTURE after coordination. | A client subscribes before starting; unavailable adapters produce clear status. A slow/disconnected browser cannot block inference or recording. Reconnection reports current session state and never starts a second capture. |
| 5. Deterministic replay and handoff examples | Headless replay command, small transport inspection screen, and adapters that supply synthetic events without model dependencies. Reuse Lane 5 preparation cases after review. | Preserve fixture delivery order and capture timestamps, including late events; fake time never moves backward. Repeated replay is identical. The shell visibly says synthetic replay; authored audience/feedback outputs are never presented as computed results. |
| 6. Reproducibility and publication preparation | Clean-checkout setup, runnable examples, relevant integration checks, lane-specific handoff notes, updated TASKS/STATUS, and scoped local commits. | Core checks and frontend build pass; documented commands work in an isolated checkout; evidence names the host, fixture/live mode, and limitations. Present exact commits and destination for explicit push approval only when publication is ready. |

Implementation remains in Lane 1. The frontend shell in step 5 is a transport and lifecycle inspection surface; the production rehearsal UI and sole engagement engine belong to LIVE-01. Controller subscriptions hand events to Lane 5's recorder; Lane 1 does not build a second session logger or feedback selector. Model choice, capture, and inference remain with audio and vision owners.

Headless checks will cover weak-to-improved replay, missing camera with valid speech, no usable signals, empty sessions, startup null metrics, duplicate/late transcript revisions, stop with pending work, timeout, partial startup failure, and consecutive sessions. Transport checks will cover subscribe-before-start, reconnection, and a slow client. Actual audience smoothing and evidence-based coaching are acceptance gates for LIVE-01 and COACH-01 once their implementations are available.

After INT-01's reviewed handoff lands, AUD-01, VIS-01, LIVE-01, and COACH-01 can implement independently in the agreed directories. INT-02 integrates those implementations and proves the real microphone/camera → audience → feedback path, including repeated sessions and missing devices. INT-03 verifies hardware and official submission requirements against sources and measurements. Hardware access does not block the local scaffold; P1 remains gated by a repeatable integrated P0 rehearsal.

**Existing preparation to preserve:** `origin/agent/session-analysis` at `b8f5597` contains [PR #1](https://github.com/crasni/LeCoach/pull/1), nine synthetic coaching cases, and its own pending claim/status updates. Its case consistency checks are preparation, not implemented coaching. Positive audience reason codes still need Lane 4's handoff. Review and reuse these artifacts; do not independently recreate them or treat their proposed task updates as already merged into `main`.

## Proposed INT-01 stack and layout

Original implementation proposal dated 2026-10-07. The execution sequence above defines delivery order and acceptance gates. [TASKS.md](../../TASKS.md) remains authoritative for ownership and task progress. See ARCHITECTURE for the current executable handoff rather than treating this proposal as a second contract reference.

Use a local **Python backend with FastAPI**, and **React + TypeScript with Vite** for the browser interface. Python keeps the capture/model adapters, engagement engine, and coaching consumers in one runtime; the frontend renders normalized outputs. One backend process and an in-process event bus are sufficient for P0. Run blocking capture/inference outside the API event loop, marshaling emissions back through the shared controller. No queue service or external database is needed for the scaffold.

Proposed runtime baseline: CPython 3.12, managed through `uv`, and Node.js 24 LTS with npm. Lock core dependencies and the exact tested Python patch during scaffolding. The current host has Python 3.14.4, a managed Python 3.13.15, Node 24.11.0, npm 11.6.1, and uv; Python 3.12 still needs provisioning. This baseline is a planning choice, not a claim that future audio/vision packages or accelerator runtimes are compatible. Owners must verify their selected packages on the agreed baseline and report conflicts before changing it.

Use Pydantic models to implement [ARCHITECTURE.md's](../ARCHITECTURE.md) event, completed-session, and feedback shapes. Export JSON Schema and generate frontend TypeScript types from that schema; generated types are not edited separately. Schema/fixture checks prevent drift from this document. Keep speech and vision dependencies in optional groups so core replay and consumer development need no model installation. Keep downloaded weights and rehearsal exports in the existing ignored locations.

Proposed directory boundaries:

| Location | Purpose and boundary |
| --- | --- |
| `src/lecoach/contracts/` | Executable types, schema export, shared adapter/consumer protocols. Changes go through integration. |
| `src/lecoach/runtime/` | Session controller, clocks, event routing, replay scheduler, shared configuration. |
| `src/lecoach/api/` | Local API, event transport, and application composition. |
| `src/lecoach/speech/` | Speech producer implementation and optional dependencies. |
| `src/lecoach/vision/` | Vision producer implementation, latest preview frame, and optional dependencies. |
| `src/lecoach/engagement/` | Sole deterministic audience engine and its rule configuration. |
| `src/lecoach/coaching/` | Sole recorder, completed timeline, moment selection, and feedback generator. |
| `frontend/src/` | Browser transport client, rehearsal controls, audience, preview, transcript, and summary rendering. |
| `frontend/src/generated/` | Types generated from the Python contract schema. |
| `checks/` | Reproducible synthetic cases and subsystem acceptance utilities; preserve existing `checks/coaching/` preparation when reviewed. |
| `tests/` and `scripts/` | Runtime/API checks, schema generation, local launch, and handoff examples. |

See TASKS for the authoritative owners and branches; this table sets module boundaries without reassigning work. Shared Python/npm manifests and lockfiles remain integration-owned. Subsystem owners request their dependency additions through integration.

### Proposed executable seams

Translate the lifecycle functions in [ARCHITECTURE.md](../ARCHITECTURE.md#session-lifecycle) into Python protocols for `SpeechAdapter`, `VisionAdapter`, `EngagementEngine`, `SessionRecorder`, and `FeedbackGenerator`. All receive the same session context and communicate through canonical events. The recorder subscribes to lifecycle, speech, vision, and engagement events; the engine subscribes to speech/vision/status and emits audience events. Provide injected fixture implementations for wiring checks; model implementations need not be imported in fixture mode.

The session context includes session identity, the shared clock, `emit(event)`, and centrally supplied configuration. Require `mode: "fixture" | "live"` in session configuration and the API session descriptor. Keep provenance outside the existing v0 event envelope so reviewed fixtures with `session.started.payload: {}` remain valid. Record the actual adapter/model/processing device in session metadata when live adapters arrive; a configured accelerator target alone is not verified acceleration.

The controller owns session phase, input status, and transport subscriptions. It does not retain a second complete timeline; completed events and coaching come from the injected recorder/generator. Any bounded transport buffer is temporary delivery state, not a substitute for the recorder. Fixture outputs are explicitly authored examples; they must not run alongside the actual engine or be confused with generated feedback.

Proposed P0 retention: the sole recorder keeps the active/completed rehearsal in memory, clears it when a new session starts or the application exits, and writes no automatic exports. Explicit development exports go under ignored `sessions/`. Raw audio/video recording remains off. Hand this policy to Lane 5 before it implements the recorder; any later persistence needs a documented retention/deletion policy.

Configuration will separate lifecycle/drain and transport settings from modality settings and engagement thresholds, with one composition entry point. Engagement defaults remain in the sole engine's configuration under Lane 4's review. Select a documented analysis language before tuning pace/filler rules; do not embed fixture numbers as universal thresholds.

### Proposed local transport and capture

Bind the backend and development UI to loopback. Use local HTTP for lifecycle/snapshot/summary requests and WebSocket for canonical events. Serve the built frontend from the backend for the eventual single-process demo; use Vite's local API/WebSocket proxy during development. Restrict accepted origins to the local UI. Bundle UI assets locally and keep raw media, transcript, and inference off remote services.

Proposed routes, to implement and validate during INT-01:

| Route | Behavior |
| --- | --- |
| `GET /api/health` | Backend readiness; fixture mode does not require devices/models. |
| `POST /api/sessions` | Allocate a prepared session and return its ID, phase, and explicit mode; no capture yet. |
| `WS /api/sessions/{id}/events` | Attach event subscription before starting; on reconnect, send a transport snapshot before new canonical events. |
| `POST /api/sessions/{id}/start` | Start the prepared session after subscriptions are ready. Refuse competing active sessions; retries must not start capture twice. |
| `POST /api/sessions/{id}/stop` | Idempotently stop acquisition and begin bounded draining; expose completion/incomplete sources. |
| `GET /api/sessions/{id}` | Current phase, input availability, mode, and latest display state. |
| `GET /api/sessions/{id}/feedback` | Canonical feedback when ready, explicit pending/unavailable state otherwise. |
| `GET /api/sessions/{id}/preview` | Local, volatile MJPEG preview from the vision adapter's most recent frame; clear unavailable state without a frame. |

Snapshots and HTTP status objects are transport wrappers, not new canonical event types. Reconnect never starts capture or inference again; the completed recorder output supplies the final full timeline. A bounded per-client queue isolates slow browsers; on overflow disconnect with an explicit resynchronization condition instead of silently losing events or blocking producers/recording. Stop/disconnect cleanup and stale-session rejection need integration checks.

The speech and vision adapters own host microphone/camera acquisition. The browser renders the adapter's preview, so it does not open a second camera stream. The preview stores only the latest frame in memory, uses a configured rate/size cap, and never joins the event log. Device permissions and platform setup are verified with the producer owners when their live adapters arrive.

### Proposed replay handoff

Review Lane 5's preparation at `origin/agent/session-analysis` / PR #1 before incorporating it. Those fixtures are arrays in **delivery order**, which can differ from capture order. Preserve original timestamps and IDs in acceptance replay; do not sort inputs before dispatch. A fake clock advances monotonically according to a test-only delivery schedule, allowing stale observations, late finals, and drain deadlines to be exercised without wall-clock delays. A browser demonstration can pace the same schedule without changing event capture times.

Separate replay of authored complete streams from replay of producer inputs through actual consumers. Complete-stream replay displays authored audience transitions and feedback only as synthetic examples. Once Lane 4/5 implementations are integrated, feed speech/vision fixtures into the real engine and recorder/generator and validate their emitted outputs. Positive reason codes and supported recovery evidence still require Lane 4 coordination. Real device release and measured inference latency require live checks beyond these fixtures.

Technical references used to assess this proposal: [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/), [Pydantic JSON Schema generation](https://docs.pydantic.dev/latest/concepts/json_schema/), [uv Python version selection](https://docs.astral.sh/uv/concepts/python-versions/), and [Vite setup requirements](https://vite.dev/guide/). Package resolution and reproducible launch commands will be recorded after implementation checks; these references do not establish model or hardware compatibility.
