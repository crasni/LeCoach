# leCoach — team work and ownership

This is the single task board for the five engineering lanes. Read [GUIDE.md](GUIDE.md) for product scope and priorities, [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for shared contracts, and [docs/STATUS.md](docs/STATUS.md) for verified integration results. Do not maintain a competing task board or copy the product specification here.

Read [docs/STATUS.md](docs/STATUS.md) for the current implementation baseline and validation evidence. Synthetic fixtures and replay do not establish live processing or accelerator compatibility.

## Five lanes

Each collaborator takes one lane; a lane can use an AI coding agent under that collaborator's responsibility. These are persistent product responsibilities, not claims about concurrently running agents. `crasni` is the known repository maintainer. All lane assignments await verified collaborator names or an explicit claim.

| Lane | Owner | Lane branch | Owns | First task |
| --- | --- | --- | --- | --- |
| 1 — Integration / competition | Unassigned | `agent/integration` | Shared contracts, app composition, setup, project documentation, integration and submission checklist | INT-01 |
| 2 — Audio / speech | Unassigned | `agent/audio-streaming` | Microphone capture, local transcription, speech metrics, speech adapter | AUD-01 |
| 3 — Vision / body language | Unassigned | `agent/vision-pose` | Camera capture, pose/facing approximation, motion metrics, vision adapter | VIS-01 |
| 4 — Realtime experience / engagement | Unassigned | `agent/avatar-ui` | Deterministic engagement engine, smoothing, session controls and live audience UI | LIVE-01 |
| 5 — Coaching / analytics / demo | Unassigned | `agent/session-analysis` | Session event store, moment selection, feedback, demo scenarios and evidence | COACH-01 |

Module boundaries follow the agreed architecture. Lane 1 establishes actual directories during INT-01; other lanes keep edits inside their subsystem and its checks/examples. Shared contracts, app entry point, dependency manifests/lockfiles and shared documentation require an integration handoff. Do not independently select incompatible frameworks or edit another lane's internals.

## Claim and session protocol

1. Start each work session with `git status` and fetch/pull current work safely. Do not overwrite local changes; update the branch from current `main` before coding.
2. Read GUIDE, AGENTS, this board, architecture, current status and relevant open PRs/issues. Inspect existing code and changed contracts.
3. Pick the highest-priority unclaimed task in your lane whose dependencies are satisfied. Record a **GitHub username**, task status, exact branch and date below. A role label or a runtime agent name is not an owner.
4. Publish the claim before implementation so other collaborators can see it. Use a small documentation PR through the integrator, or the repository's existing authorized claim workflow. Until visible on the shared board, the claim is provisional. Resolve conflicting claims before duplicating work.
5. Work on the recorded feature branch. Keep changes scoped. Proposed contract changes go to Lane 1 first; the integrator owns approval and merge of shared contract changes and coordinates affected consumers.
6. Open a PR with the task ID, concrete behavior, reproduction/check commands and results, dependencies, mock/live mode, limitations and interface changes. Link the PR in the board and move the task to `review`.
7. Lane 1 verifies the handoff against the shared contracts, resolves integration and merges in dependency order. Mark `done` only after merge and acceptance evidence. Update verified integration status when behavior changes.

Statuses: `todo` (unclaimed), `claimed`, `in_progress`, `blocked`, `review`, `done`. A blocked task includes the blocker, required decision/person and next action. `done` requires runnable behavior, basic failure handling, a consumable documented interface, relevant validation and downstream handoff. No task is currently implemented or claimed.

| Task | Owner | Status | Branch | PR / evidence / blocker | Updated |
| --- | --- | --- | --- | --- | --- |
| INT-01 | — | todo | — | Establish runnable skeleton and contract handoff | — |
| INT-02 | — | todo | — | Depends on subsystem PRs | — |
| INT-03 | — | todo | — | Hardware access and official submission verification needed | — |
| AUD-01 | — | todo | — | Confirm INT-01 contracts before integration | — |
| AUD-02 | — | todo | — | Depends on AUD-01 | — |
| VIS-01 | — | todo | — | Confirm INT-01 contracts before integration | — |
| VIS-02 | — | todo | — | Depends on VIS-01 | — |
| LIVE-01 | — | todo | — | Confirm INT-01 contracts before integration | — |
| LIVE-02 | — | todo | — | Depends on LIVE-01 and live adapter handoffs | — |
| COACH-01 | — | todo | — | Confirm INT-01 contracts before integration | — |
| COACH-02 | — | todo | — | Depends on COACH-01 and integrated live session | — |

## Lane 1 — Integration / competition

**INT-01 — P0: runnable skeleton and shared contracts.** Define one reproducible local launch path, module boundaries and shared session/event contracts in ARCHITECTURE. Publish representative fixtures so independent lanes can develop immediately. Establish session start/stop and routing interfaces without implementing other lanes' inference logic. Acceptance: clean-checkout setup instructions work; producers and consumers agree on timestamp units, session identity, event meanings, unavailable/stale inputs and mock/live provenance; fixtures can travel through the skeleton. Downstream handoff: all four lanes can consume the contract and run their examples without importing each other's implementation internals.

**INT-02 — P0: integrate and verify the live rehearsal.** Compose speech, vision, engagement, UI and session coaching. Acceptance: start a local microphone/camera session, change delivery, see stable audience reactions, stop, then inspect timestamped feedback; device permission/availability failures are understandable; stale or absent input is represented honestly; repeat sessions do not mix events. Record host, commands, checks and remaining limitations in STATUS. Dependencies: AUD-01/02, VIS-01/02, LIVE-01/02 and COACH-01.

**INT-03 — P0: hardware and submission evidence.** Verify latest official competition requirements and source provenance before final submission. Check the intended UGen300 adapter/model path against official documents and actual available hardware; record what runs, where it runs and measured performance. Acceptance: reproducible setup, clear architecture and documented hardware status support an English proposal and approximately three-minute demo; official deadline/page/video requirements are verified. CPU fallback and untested accelerator plans remain explicitly labeled. Hardware access is an external dependency; do not block the local baseline on it or imply validation without measurement. Final external submission/publication requires the team's applicable authorization.

## Lane 2 — Audio / speech

**AUD-01 — P0.1: live local speech producer.** Capture the microphone, run local streaming or chunked transcription, and publish timestamped partial/final transcript, approximate WPM, fillers and pauses under the shared contract. Keep capture/model code behind the speech adapter; avoid UI imports. Acceptance: an actual microphone rehearsal produces consumable events; silence and empty transcripts are handled; transcript revisions do not double-count words/fillers; device/model failures are surfaced; speech processing does not require a remote API. Include a small replay fixture/example for downstream development, explicitly labeled synthetic or recorded. Dependencies: INT-01 contract. Handoff: Lane 4 gets live speech metrics and Lane 5 gets timestamped transcripts/events plus confidence/limitations.

**AUD-02 — P0.1: stabilize and measure.** Check normal pace, rapid speech, repeated fillers and prolonged silence on the intended host. Acceptance: record model/configuration, approximate event latency and observed limitations; start/stop releases capture; the integrated UI remains responsive; timestamps align with the shared session clock. Give Lane 1 exact run/config instructions and evidence; hardware acceleration is claimed only when tested. Dependency: AUD-01.

## Lane 3 — Vision / body language

**VIS-01 — P0.2: live local vision producer.** Capture camera frames and publish person/body pose, approximate facing direction and gesture/activity signals under the shared contract. Keep pose inference separate from UI and use an adapter boundary for hardware changes. Acceptance: an actual camera session distinguishes audience-facing versus sustained looking away and low versus active movement; missing person, low confidence and camera errors become unavailable data, not negative behavior; timestamps follow the session clock. No precise gaze/emotion recognition is required. Include a small labeled fixture/example. Dependencies: INT-01 contract. Handoff: Lane 4 consumes visual metrics; Lane 5 consumes timestamped evidence with confidence/limitations.

**VIS-02 — P0.2: stabilize and measure.** Check facing/looking-away, useful gestures, low movement and no-person conditions on the intended host. Acceptance: record model/configuration, throughput/event latency and limitations; cap processing load so the audience UI stays responsive; stopping a session releases the camera. Give Lane 1 exact run/config instructions and hardware evidence where available. Dependency: VIS-01.

## Lane 4 — Realtime experience / engagement

**LIVE-01 — P0.3/P0.4: deterministic engagement and visible audience.** Combine speech/vision events into the agreed audience states with smoothing/hysteresis. Expose evidence/reasons for transitions to coaching. Build a simple audience using SVG/CSS/2D assets, plus session controls and useful camera/transcript views. Acceptance: labeled replay fixtures show weak delivery lowering audience attention and improved delivery restoring it; rapid metric jitter does not flicker avatars; missing/stale signals do not become negative coaching evidence; states and reasons remain timestamped; no LLM sits in the control loop. Dependency: INT-01 contract. Handoff: Lane 5 receives audience transition events and their evidence; Lane 1 receives launch/integration instructions. Fixture success is not a live pipeline completion claim.

**LIVE-02 — P0.3/P0.4: connect the live rehearsal.** Wire the real speech/vision adapters through Lane 1's composition boundary. Acceptance: start/stop and repeat sessions work; real delivery changes visibly drive stable reactions; device errors and unavailable inputs are understandable; mock/replay mode is visibly distinguished when used. Check the core experience with INT-02 and COACH-01. Dependencies: LIVE-01, AUD-01 and VIS-01.

## Lane 5 — Coaching / analytics / demo

**COACH-01 — P0.5: session timeline and evidence-based feedback.** Store synchronized speech, vision and audience events locally and select important moments using deterministic rules. Acceptance: completed sessions show a timeline, one supported strong moment and two or three supported improvement moments when enough evidence exists; every insight names a timestamp, observed reason and practical action; short/empty or missing-input sessions report insufficient evidence instead of inventing moments; repeated sessions remain separate. Retain only the data needed for the MVP, with raw audio/video recording off by default. Dependency: INT-01 contract and LIVE-01 transition interface; labeled fixtures permit development before live integration. Handoff: Lane 4 gets the summary/timeline interface, and Lane 1 gets replay/check instructions.

**COACH-02 — P0: credible demo and evaluation.** Write demo instructions with weak delivery, improved delivery, session feedback and the local-AI story. Acceptance: an integrated live run yields timestamped audience changes and useful coaching; record repeatable scenarios and actual results, including missing-device/input cases; an English script fits approximately three minutes and distinguishes measured hardware behavior from plans. Coordinate proposal/demo evidence with INT-03; claims must match STATUS. Dependencies: COACH-01 and INT-02. Do not publish a video or submit externally without applicable team authorization.

## Integration order and priority gate

1. INT-01 contracts/skeleton land first. Audio, vision, audience and coaching can then proceed independently against shared fixtures.
2. Merge small producer/consumer PRs with documented handoffs. Lane 1 composes them; owners fix failures in their own modules.
3. Run a live microphone + camera session through audience reactions and post-session feedback. Complete stability checks and record the difference between fixture, live CPU and verified accelerator runs.
4. Finish hardware/submission evidence and the repeatable demo. Latest official requirements override stale planning dates in the guide.

P1 audience questions, local LLM feedback and TTS remain unclaimed until the integrated P0 path is working and repeatable. Do not add precise gaze tracking, emotion recognition, 3D avatars, slide understanding or model training to this delivery plan.
