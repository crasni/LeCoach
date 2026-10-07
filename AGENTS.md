# leCoach agent entry point

The product is **leCoach**. Work toward the frozen P0 scope in [GUIDE.md](GUIDE.md). This file is the common entry point for every collaborator and coding agent.

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

- Exactly one owner per task. Claim the task in `TASKS.md` with your GitHub username and lane branch before implementing it. Land or coordinate that claim through the integration owner before assuming ownership; a conflicting claim must be resolved first.
- Use your assigned role branch. Never commit directly to `main` during feature development.
- Keep changes within your lane. Coordinate shared contracts, scaffold, dependencies, and root configuration through the integration owner; agree on a contract revision before changing producers or consumers.
- Submit a scoped PR referencing task IDs, behavior changed, validation evidence, limitations, and downstream handoff. A PR author does not merge their own feature until the integration owner has reviewed it.
- Merge compatible PRs through the integration owner, then pull and inspect changes before continuing. Do not merge incomplete adapters into a supposedly live demo.
- Never overwrite uncommitted work, force-push shared branches, fabricate completion evidence, or create a second engagement engine/logger.
- These five roles represent the whole team. Additional agent delegation requires an explicit request by the user or coordination with the team; avoid assigning another agent to an already-owned task.

## Completion standard

A task is done when it runs, handles basic failures, respects the shared contracts, has an appropriate reproducible example or meaningful check, and downstream consumers can use it. Update `TASKS.md` and `docs/STATUS.md` with the evidence in the same PR.

Distinguish synthetic fixtures, real camera/microphone input, local inference, and measured UGen300 inference. Do not present a planned accelerator adapter as working hardware integration. Do not claim eye tracking or emotion detection from approximate head direction.

Keep voice, video, transcripts, sessions, credentials, and downloaded model weights out of Git. P1 work begins only after the integrated P0 demo passes.
