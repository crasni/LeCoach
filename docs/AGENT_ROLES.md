# Stable engineering lane boundaries

Start with [AGENTS.md](../AGENTS.md). GitHub Issues—not this file—determine the assigned collaborator, branch, next useful work, blockers and task acceptance. Read existing implementation/PRs and continue the assigned work; a lane description is not a new claim or blank implementation prompt.

## Lane 1 — Integration / competition

Own shared contracts, app composition, setup, dependency manifests/lockfiles, canonical documentation, cross-lane review/integration and competition/hardware provenance. Agree interface/configuration changes with affected owners using [OpenSpec](WORKFLOW.md); integrate consumable public seams rather than rewriting subsystems. Separate local artifact validation from live/model/target measurements and external submission receipts.

## Lane 2 — Audio / speech

Own microphone capture, local transcription, transcript timing/revisions, WPM/fillers/pauses, speech metrics and the speech producer lifecycle in `src/lecoach/speech/`, plus focused tests. Reuse the shared SessionContext/clock and public adapter seams. Report measurement/configuration decisions through the Issue; central dependency changes go through integration. Measure real latency/filler limitations rather than claiming synthetic tests prove model quality.

## Lane 3 — Vision / body language

Own camera capture, local pose, approximate head/body-facing and activity, normalized visual events and preview in `src/lecoach/vision/`, plus focused tests. Use shared units/timing/lifecycle. Distinguish facing approximation from eye contact/emotion and explicitly handle missing camera/person. Coordinate selected runtime/dependencies with integration before changing shared files.

## Lane 4 — Realtime experience / engagement

Own the **sole** deterministic engine/rules in `src/lecoach/engagement/` and the rehearsal UI in `frontend/`: smoothed states, evidence-backed reasons, avatar reactions, metrics/transcript/input notices and camera preview. Agree reason/evidence semantics with coaching and integration. Use public producers/composition, not another capture stack. Thresholds remain demo heuristics until measured.

## Lane 5 — Coaching / analytics / demo

Own the **sole** session recorder, deterministic moment selector and template feedback in `src/lecoach/coaching/`, synthetic coaching checks and English demo scenario/evaluation handoff. Consume actual engine transitions/source evidence without building another engine or inventing authored moments. Preserve null/unavailable and session/drain/revision semantics. Coordinate final script/evidence with integration; external recording/upload is not implicit task authorization.

## Shared guardrails

Keep changes within the assigned Issue and subsystem, tests/examples and approved handoffs. Product scope stays in [GUIDE](../GUIDE.md), shared semantics in [ARCHITECTURE](ARCHITECTURE.md), behavior changes in linked OpenSpec, and current state/acceptance in the Issue. Do not copy these sources into role prompts, rebuild merged components, modify another lane's internals or start additional agents without team/user authorization.
