# LeCoach agent entry point

LeCoach is **Your Private AI Audience**: local speech and approximate body/head-facing signals drive one deterministic audience engine, followed by evidence-based coaching. Keep the frozen P0 scope in [GUIDE.md](GUIDE.md); optional LLM, questions and TTS wait for an accepted end-to-end P0.

## One source for each fact

| Fact | Source |
| --- | --- |
| Owner, assigned branch, live status, blockers, remaining work and task acceptance | [GitHub Issues](https://github.com/crasni/LeCoach/issues?q=is%3Aissue+label%3Acoordination) |
| Behavior/interface proposal, agreed delta and rationale | Linked `openspec/` proposal/design/specs; [OpenSpec workflow](docs/WORKFLOW.md) |
| Canonical event schemas, units, clocks and subsystem boundaries | [ARCHITECTURE.md](docs/ARCHITECTURE.md) and `src/lecoach/contracts/` |
| Product scope and official-source hierarchy | [GUIDE.md](GUIDE.md) |
| Reproducible checks, dated observations and limitations | Issue/PR evidence; [STATUS.md](docs/STATUS.md) is historical evidence, not a live board |
| Stable lane responsibilities | [AGENT_ROLES.md](docs/AGENT_ROLES.md) |

[TASKS.md](TASKS.md) is a compatibility pointer only. Do not copy live Issue fields or acceptance into a second file/board. OpenSpec implementation checklists may provide historical evidence/work breakdown, but never override the Issue's current state or acceptance.

## Start or resume a session

1. Check `git status` and the current branch. Preserve uncommitted work; fetch safely. Never reset, stash away, delete or overwrite another session's work. Use an isolated checkout/worktree when another session shares the clone.
2. Confirm the collaborator's actual GitHub username from the user or authenticated account, never from a commit author or runtime agent name. Read assigned Issues, full bodies/comments, native **Blocked by** relationships, relevant PRs and existing remote/local code:

   ```sh
   gh issue list --repo crasni/LeCoach --assignee <username> --state open --label coordination
   gh issue view <number> --repo crasni/LeCoach --comments
   gh api repos/crasni/LeCoach/issues/<number>/dependencies/blocked_by
   gh pr list --repo crasni/LeCoach --state open
   git fetch --prune origin
   ```

3. Use the Issue's owner and **Implementation branch**. Existing assignments persist; do not ask to choose a lane again, reassign someone else, create duplicate tasks or restart merged/partially implemented work. Track the existing remote role branch. If identity/assignment/access is unresolved, ask while continuing read-only inspection.
4. Read the relevant contract/spec and stable role boundary before editing. Select useful work within the Issue: distinguish completed work, independent work and the exact gated handoff. A dependency on final acceptance need not prevent independent tests, fixtures or design.
5. Update the assigned Issue body/status label and add a concise start/resume comment. Report `CURRENT STATE`, `MY ROLE`, `NEXT TASK` (Issue + branch + deliverable), and `DEPENDENCIES / BLOCKERS`. No documentation claim PR is needed.

## Issue coordination

- Exactly one responsible GitHub assignee and one `status:*` label: `todo`, `in_progress`, `blocked`, or `review`; accepted completion is a closed Issue. Keep the body status consistent with its label; don't treat a task's initial audit timestamp as current evidence.
- Maintain owner, branch, already done, remaining work, exact required handoff, acceptance and links to relevant specs/PRs. Add/remove native **Blocked by** relationships as dependencies are actually accepted. Explain external access/hardware/team decisions in the body when they are not Issues.
- Identify the blocker, needed decision/interface, responsible owner and useful independent work. Tag affected owners in the Issue. Never invent a shared contract or interpret silence as approval.
- Shared event/configuration/behavior changes need a linked OpenSpec proposal/delta, integration agreement and affected-owner review before producers/consumers change. Routine implementation/tests against an agreed interface do not need a new spec.
- Root composition, dependency manifests/lockfiles and canonical shared documentation are integration-owned. Other lanes propose those changes through the relevant Issue/PR; don't import another lane's private internals, create a second engine/recorder or merge an incomplete adapter to bypass a blocker.
- Missing GitHub access is a limitation, not proof that work/owners/PRs do not exist. Keep local notes explicitly provisional and reconcile the Issue when access returns.

## Scoped autonomous branch publication

The maintainer explicitly replaced per-push approval with this scoped policy during the coordination migration. Agents may independently implement, test, commit and push routine work **within their assigned Issue/lane to its assigned role branch**, and open/update scoped PRs. No separate approval is required for each such push; record commit/PR/check evidence in the Issue.

Before publishing, verify the exact branch, staged diff, remote and scope. The canonical remote is `git@github.com:crasni/LeCoach.git`. Push an explicit single destination, for example:

```sh
git push origin HEAD:refs/heads/<assigned-role-branch>
```

**Never push directly to `main`**, including refspec/API bypasses. No force push, history rewrite, multi-branch/tag push, branch deletion, ownership reassignment, unrelated changes or publication of private data is covered. Conflicting remote updates stop publication; inspect and reconcile without discarding work. Broader/destructive actions, other people's branches and merges require specific maintainer/team authorization. Competition upload/submission and real rehearsal recording/publication require their own authorization.

## PR review and completion

Open a scoped PR targeting `main`, linked to the Issue and relevant OpenSpec, with behavior, reproducible commands/results, fixture versus live mode, limitations, changed interfaces and downstream handoff. Move the Issue to `review` only when the submitted scope is reviewable. Integration coordinates review and dependency-order merge; integration-owned changes should receive another collaborator's review unless the maintainer explicitly waives it.

A merged preparation/component PR does **not** complete a larger live task. Close the Issue only after all its acceptance is verified: runnable behavior, basic failures, documented consumable interface, appropriate tests and downstream acceptance. Partial PRs use `Refs #N`, not automatic closing keywords. Record any acceptance exception and who authorized it. Add dated implementation evidence to STATUS only when useful, not a second progress/blocker board.

Distinguish synthetic fixtures, actual microphone/camera, local model inference and measured UGen300 inference. Do not claim validated latency, target compatibility, eye tracking or emotion detection without evidence. Keep voice/video/transcripts/sessions/credentials/downloaded model weights out of Git. Additional agent delegation needs an explicit user request or team coordination; don't duplicate an owned task.

## Handoff to an existing or new agent

```text
Read AGENTS.md. My GitHub username is <username>.
Read my assigned GitHub Issues, comments, dependencies and existing branch/PR work.
Continue the existing assignment rather than restarting it. Report current state,
next useful deliverable and exact blockers, then implement/check/publish within
its authorized scope. Update the Issue; coordinate shared interfaces before changes.
```
