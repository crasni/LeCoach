# leCoach agent entry point

You are joining a coordinated five-person engineering team building **leCoach**. Read this file when you first open the repository and at the start of every new agent session. Understand the existing plan and your assignment before editing code.

## Understand the project

leCoach is **Your Private AI Audience**: a local presentation rehearsal tool that listens through the microphone, watches through the webcam, and makes virtual audience avatars react to delivery in real time. After the rehearsal it highlights specific strong and improvement moments with practical suggestions. Live audience response is the central product value.

The agreed direction is Workplace AI / Battlefield Lightning in the ASUS UGen AI League Hackathon 2026, targeting ASUS UGen300. Prioritize a simple, reliable Stage I prototype and demo. Treat competition details and hardware capabilities as requiring official verification before claiming them.

The frozen MVP is local speech analysis + approximate body/head-facing analysis → one deterministic engagement engine with smoothing → simple reactive avatars → synchronized timeline and concise feedback. Optional LLM feedback, audience questions, and TTS wait until P0 works end to end. Keep rehearsal data local.

This is an orientation summary. [GUIDE.md](GUIDE.md) controls product scope; [docs/STATUS.md](docs/STATUS.md) records what actually works. Do not assume the planned system has been implemented, invent launch commands, or rebuild components without inspecting the repository.

## First-session onboarding

1. Follow the read-before-work sequence below, then inspect the repository, recent commits, and relevant open PRs when accessible.
2. Identify the collaborator's GitHub username and match it to the Owner column in [TASKS.md](TASKS.md). A matching row is the assigned lane: use its branch, first task, and role prompt without asking the user to assign a lane again. Do not invent a username or infer identity from someone else's Git commit author. Check the row's access state; pending invitations must be accepted before pushing work.
3. If your user explicitly assigned a lane, use it and coordinate its claim on the shared board. Otherwise, if the roster does not identify your lane, ask the user which lane to take while continuing read-only inspection. Do not silently take another collaborator's work.
4. Read that lane's prompt in [docs/AGENT_ROLES.md](docs/AGENT_ROLES.md). TASKS.md provides its exact branch, first task, dependencies, and acceptance criteria. Remain in that lane for the session unless the team explicitly reassigns you.
5. Pick the highest-priority available task whose dependencies are met. Claim it using the protocol below. If no integration owner is assigned yet, coordinate the initial claim with the repository maintainer identified in TASKS.md.
6. Start with a concise update using this format, then execute the authorized task:

   ```text
   CURRENT STATE: What exists, what changed, and what is verified.
   MY ROLE: Lane and collaborator username; flag any unconfirmed assignment.
   NEXT TASK: Task ID, branch, and concrete first deliverable.
   DEPENDENCIES / BLOCKERS: Required interfaces, pending handoffs, and missing access.
   ```

If integration scaffolding or a required contract has not landed, coordinate with Lane 1. Prepare compatible fixtures, implementation research, or checks inside your lane while waiting; do not independently create a competing application stack or shared interface. Missing GitHub API access is a reported limitation, not evidence that there are no collaborators or open PRs.

## Human handoff to a new agent

Open this repository in your coding agent and give it:

```text
Read AGENTS.md and follow its onboarding instructions before making changes.
My GitHub username is <username>. Find my assigned lane in TASKS.md.
Read the shared documents, inspect current code and claims, then report your
current state, role, next task, and blockers. Claim and implement the highest-
priority available task in my lane, validate it, and update the shared task
board and implementation status. Coordinate interfaces with the integrator.
```

Replace `<username>` with the actual collaborator's GitHub username. The shared board remains authoritative for ownership; a handoff does not override an existing claim.

## Read before work

1. Check `git status` and preserve existing local changes. Pull with `git pull --ff-only` when safe; never reset someone else's work.
2. Read [GUIDE.md](GUIDE.md) for product scope and priorities.
3. Read [TASKS.md](TASKS.md) for the five workstreams, owners, dependencies, and current task state.
4. Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the shared event contracts.
5. Read [docs/STATUS.md](docs/STATUS.md) for what has actually been verified, and the relevant prompt in [docs/AGENT_ROLES.md](docs/AGENT_ROLES.md).
6. Inspect current implementation and open PRs before adding code. GitHub collaborator access alone does not assign a workstream.

## One source for each fact

| Fact | Authoritative location |
| --- | --- |
| Product scope, priorities, competition source hierarchy | `GUIDE.md` |
| Team membership mapping, task ownership, branches, task progress | `TASKS.md` |
| Event schemas, units, clocks, subsystem boundaries | `docs/ARCHITECTURE.md` |
| Tested behavior, limitations, blockers and hardware evidence | `docs/STATUS.md` |
| Instructions for starting each role | `docs/AGENT_ROLES.md` |

Link to these documents instead of copying their facts into another spec. Latest official competition rules and official hardware documentation take precedence over repository assumptions, as GUIDE.md requires. Record a conflict before changing the plan.

## Claim and collaborate

- Exactly one owner per task. Named assignments already in `TASKS.md` determine ownership; activate your assigned task by updating its status and date with your GitHub username and lane branch before implementing it. Land or coordinate that claim through the integration owner before assuming ownership; a conflicting claim must be resolved first.
- Use your assigned role branch. Never commit directly to `main` during feature development.
- Keep changes within your lane. Coordinate shared contracts, scaffold, dependencies, and root configuration through the integration owner; agree on a contract revision before changing producers or consumers.
- Submit a scoped PR referencing task IDs, behavior changed, validation evidence, limitations, and downstream handoff. Subsystem PRs require integration-owner review before merge; integration-owner changes should receive another collaborator's review. Coordinate the initial documentation/scaffold handoff with the maintainer if the integration role is still unassigned.
- Merge compatible PRs through the integration owner, then pull and inspect changes before continuing. Do not merge incomplete adapters into a supposedly live demo.
- Never overwrite uncommitted work, force-push shared branches, fabricate completion evidence, or create a second engagement engine/logger.
- These five roles represent the whole team. Additional agent delegation requires an explicit request by the user or coordination with the team; avoid assigning another agent to an already-owned task.

## Completion standard

A task is done when it runs, handles basic failures, respects the shared contracts, has an appropriate reproducible example or meaningful check, and downstream consumers can use it. Update `TASKS.md` and `docs/STATUS.md` with the evidence in the same PR.

Distinguish synthetic fixtures, real camera/microphone input, local inference, and measured UGen300 inference. Do not present a planned accelerator adapter as working hardware integration. Do not claim eye tracking or emotion detection from approximate head direction.

Keep voice, video, transcripts, sessions, credentials, and downloaded model weights out of Git. P1 work begins only after the integrated P0 demo passes.
