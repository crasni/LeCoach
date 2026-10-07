# LeCoach agent handoffs

These five roles divide engineering ownership; they do not add five coaching modes to the MVP. Collaborator assignments live only in [TASKS.md](../TASKS.md). Copy one numbered prompt into the assigned collaborator's agent session. Each collaborator operates one role; do not start additional agents independently. GUIDE.md owns product scope, TASKS.md owns task status and collaborator assignments, ARCHITECTURE.md owns shared contracts, and STATUS.md records implementation evidence. Coordinate shared-document changes through the integration owner. Integration merges the scaffold and shared contracts first; other roles may prepare fixtures and checks in parallel.

All five roles must follow the [push approval rule in AGENTS.md](../AGENTS.md#required-user-approval-before-every-push). Local commits are allowed; before each push, present the changes, validation, commits, and destination, then wait for explicit user approval. A role assignment or instruction to publish a claim/PR does not waive this rule.

All development, documentation, and task-claim commits belong on the role branch named in your prompt, including the integration owner's work. Follow the [required branch workflow](../AGENTS.md#required-branch-workflow--never-push-to-main). Never push directly to `main`; publish only the approved role branch and propose a reviewed PR into `main`.

## 1. Project, integration, and competition

You own LeCoach integration. Work on `agent/integration`.

Start with a clean checkout, pull the latest `main`, and read [AGENTS.md](../AGENTS.md), [GUIDE.md](../GUIDE.md), [TASKS.md](../TASKS.md), [docs/ARCHITECTURE.md](ARCHITECTURE.md), and README.md. Inspect existing code, assignments, and open PRs before editing. Follow the owner-claim protocol in AGENTS.md: start your next assigned task in TASKS.md with one Owner set to your actual GitHub username and your role branch before implementing it; add the PR URL when available. Confirm the task is assigned to your username and is not already active in another session; coordinate any conflicting ownership or unresolved claim rather than duplicate work. Report current state, role, next task, and blockers briefly.

Own shared contracts, repository scaffolding, application composition, integration checks, canonical documentation, competition evidence, and final submission coordination. Subsystem implementation belongs to its assigned role. Establish the canonical contracts in ARCHITECTURE.md before downstream implementation; review proposed changes and coordinate affected owners. Do not let multiple copies of schemas or ownership tables become authorities. Do not independently spawn agents or silently change shared interfaces.

First deliverable: a minimal runnable application skeleton with agreed event interfaces, a shared session clock, and a synthetic fixture connecting speech and vision events through audience reactions to session feedback. Record setup and integration checks. Resolve the stack and folder layout centrally so other roles can proceed in parallel.

Completion checks: all four subsystem PRs integrate; a fresh checkout can run the documented setup; unavailable devices/models produce clear user-facing states; live and fixture modes are distinguishable; local processing claims reflect demonstrated behavior; hardware claims have cited evidence. Verify current contest requirements against official sources. Maintain an approximately three-minute proposed demo plan in docs/DEMO.md, clearly marked as a team planning target until official limits are verified. Record unresolved issues and submission work in TASKS.md.

## 2. Audio and speech

You own LeCoach audio and speech. Work on `agent/audio-streaming`.

Start with a clean checkout, pull the latest `main`, and read [AGENTS.md](../AGENTS.md), [GUIDE.md](../GUIDE.md), [TASKS.md](../TASKS.md), [docs/ARCHITECTURE.md](ARCHITECTURE.md), and README.md. Inspect existing code, assignments, and open PRs before editing. Follow the owner-claim protocol in AGENTS.md: start your next assigned audio task in TASKS.md with one Owner set to your actual GitHub username and your role branch before implementing it; add the PR URL when available. Confirm the task is assigned to your username and is not already active in another session; coordinate any conflicting ownership or unresolved claim rather than duplicate work. Report current state, role, next task, and blockers briefly.

Own microphone capture, local streaming/chunked transcription, transcript timestamps, approximate WPM, fillers, and pause signals, plus audio-specific examples and checks. Emit events using the canonical contract and shared session clock in ARCHITECTURE.md. Engagement rules, UI, session analysis, and shared scaffolding belong to other roles. Do not independently spawn agents or change shared interfaces; propose necessary changes to the integration owner first.

After the integration scaffold and contracts merge, first deliverable: a local audio adapter producing timestamped transcript and delivery events from microphone input, with a recorded or synthetic fixture for repeatable integration. Choose a practical local speech implementation within the approved architecture; expose its operating limitations instead of claiming unsupported hardware acceleration.

Completion checks: start/stop releases the microphone; absent permissions/devices/models yield clear errors; timestamps align with the session clock; fixtures demonstrate pace, fillers, and silence behavior; latency is measured on the actual development device; the engagement/UI owner can consume the events without importing model internals. Document audio setup and limitations, update the claimed task, and open a scoped PR.

## 3. Vision and body language

You own LeCoach vision. Work on `agent/vision-pose`.

Start with a clean checkout, pull the latest `main`, and read [AGENTS.md](../AGENTS.md), [GUIDE.md](../GUIDE.md), [TASKS.md](../TASKS.md), [docs/ARCHITECTURE.md](ARCHITECTURE.md), and README.md. Inspect existing code, assignments, and open PRs before editing. Follow the owner-claim protocol in AGENTS.md: start your next assigned vision task in TASKS.md with one Owner set to your actual GitHub username and your role branch before implementing it; add the PR URL when available. Confirm the task is assigned to your username and is not already active in another session; coordinate any conflicting ownership or unresolved claim rather than duplicate work. Report current state, role, next task, and blockers briefly.

Own webcam/frame capture, person/body pose, approximate head/facing direction, gesture/activity signals, and vision-specific examples and checks. Emit events using the canonical contract and shared session clock in ARCHITECTURE.md. Expose preview frames through the agreed interface; the UI owner renders the preview. Engagement rules, feedback, and shared scaffolding belong to other roles. Do not independently spawn agents or change shared interfaces; propose necessary changes to the integration owner first.

After the integration scaffold and contracts merge, first deliverable: a local vision adapter emitting timestamped facing and movement signals, with a repeatable fixture for facing-camera, looking-away, and gesture scenarios. Keep head direction approximate; precise eye tracking and emotion recognition are outside P0.

Completion checks: start/stop releases the webcam; camera denial, missing models, and no-person frames have explicit states; missing observations are not treated as poor presentation behavior; timestamps align with the session clock; processing rate/latency is measured on the actual device; consumers use the public interface without importing model internals. Document vision setup and limitations, update the claimed task, and open a scoped PR.

## 4. Real-time experience, engagement, and audience

You own LeCoach real-time experience. Work on `agent/avatar-ui`.

Start with a clean checkout, pull the latest `main`, and read [AGENTS.md](../AGENTS.md), [GUIDE.md](../GUIDE.md), [TASKS.md](../TASKS.md), [docs/ARCHITECTURE.md](ARCHITECTURE.md), and README.md. Inspect existing code, assignments, and open PRs before editing. Follow the owner-claim protocol in AGENTS.md: start your next assigned engagement/UI task in TASKS.md with one Owner set to your actual GitHub username and your role branch before implementing it; add the PR URL when available. Confirm the task is assigned to your username and is not already active in another session; coordinate any conflicting ownership or unresolved claim rather than duplicate work. Report current state, role, next task, and blockers briefly.

Own the deterministic engagement engine, smoothing/hysteresis, audience-state transitions, session controls, camera preview rendering, live transcript, and simple animated audience UI. Consume canonical speech/vision events and emit canonical engagement events; ARCHITECTURE.md owns the schemas. Audio/vision model code, session logging, coaching selection, and shared scaffolding belong to other roles. Do not independently spawn agents or change shared interfaces; propose necessary changes to the integration owner first.

After the integration scaffold and contracts merge, first deliverable: a complete rehearsal screen driven by synthetic events, showing gradual audience disengagement during weak delivery and recovery as delivery improves. Keep the engine independent of rendering and avoid an LLM in the live control loop. Integrate the coaching owner's summary through the agreed interface instead of creating a second feedback implementation.

Completion checks: repeatable fixtures verify deterioration and recovery, smoothing prevents rapid state flicker, stale/missing signals do not become negative evidence, and session restart clears prior state. Camera/transcript/device states are understandable; avatars react visibly without overwhelming the speaker; live adapters can replace fixtures through the same contracts. Document the rules and relevant checks, update the claimed task, and open a scoped PR.

## 5. Coaching, session analysis, and demo evidence

You own LeCoach coaching and session analysis. Work on `agent/session-analysis`.

Start with a clean checkout, pull the latest `main`, and read [AGENTS.md](../AGENTS.md), [GUIDE.md](../GUIDE.md), [TASKS.md](../TASKS.md), [docs/ARCHITECTURE.md](ARCHITECTURE.md), and README.md. Inspect existing code, assignments, and open PRs before editing. Follow the owner-claim protocol in AGENTS.md: start your next assigned session-analysis task in TASKS.md with one Owner set to your actual GitHub username and your role branch before implementing it; add the PR URL when available. Confirm the task is assigned to your username and is not already active in another session; coordinate any conflicting ownership or unresolved claim rather than duplicate work. Report current state, role, next task, and blockers briefly.

Own session logging, synchronized timeline construction, important-moment selection, concise post-session coaching, analysis fixtures, and reproducible demo/evaluation scenarios. Consume canonical events and return the canonical summary contract in ARCHITECTURE.md; the UI owner renders it. Engagement rules, audio/vision inference, and shared scaffolding belong to other roles. Do not independently spawn agents or change shared interfaces; propose necessary changes to the integration owner first. Coordinate demo evidence with the integration owner, who owns DEMO.md and contest claims.

After the integration scaffold and contracts merge, first deliverable: a local session recorder and deterministic feedback generator that turns a weak-to-improved rehearsal fixture into one strong moment and two to three improvement moments, when the evidence supports them. Every insight must include a timestamp, observed reason, and concrete action. Return fewer insights for short or insufficient sessions rather than inventing evidence.

Completion checks: audio, vision, and audience events share one timeline; session end produces usable feedback; empty/partial sessions and missing modalities are handled; consecutive sessions remain isolated; every insight traces to observed events; a repeatable scenario demonstrates weak delivery, recovery, and a useful summary. Document storage behavior and demo evidence, update the claimed task, and open a scoped PR. Optional LLM summaries, audience questions, and TTS wait until P0 works end to end.
