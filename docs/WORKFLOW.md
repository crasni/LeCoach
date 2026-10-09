# Behavior specification and task workflow

[AGENTS.md](../AGENTS.md) is the session/publication entry point. [GitHub Issues](https://github.com/crasni/LeCoach/issues?q=is%3Aissue+label%3Acoordination) exclusively own assignments, branches, live status, blockers, remaining work and task acceptance. `TASKS.md` is a compatibility pointer, not a second board.

## OpenSpec's role

Use existing `openspec/` proposal/design/capability specs to agree behavior and interface deltas **before** changing producers/consumers. Architecture and executable contracts remain the canonical shared semantics. Routine implementation or test work against an agreed contract does not require a fresh proposal. Link the change from the Issue and PR; don't duplicate owner/status/blocker/acceptance fields in OpenSpec.

Existing implementation checklists are historical evidence/work breakdown, not a competing live tracker. Resolve conflicts against the Issue and actual commits/checks; do not infer acceptance from an artifact's completion count. Preserve earlier contributor implementation and acceptance exceptions. Archive only after agreed acceptance; publication still follows AGENTS scope.

## Existing CLI / agent workflow

From the repository root, use the installed OpenSpec workflow rather than reinitializing the project:

```sh
openspec list --json
openspec status --change <change-name> --json
openspec validate <change-name> --strict
openspec doctor --json
```

Agent commands already used in this repository:

```text
$openspec-apply-change <change-name>
$openspec-archive-change <change-name>
```

The apply workflow reads the existing artifacts and implements the assigned Issue scope. The archive workflow preserves agreed capability specs and evidence after acceptance. If an agent/CLI version exposes different commands, inspect its help/installed skills before use; do not invent flags or silently restart scaffolding.

## Working order

Read the assigned Issue/comments/native dependencies, inspect its existing branch and relevant spec/contracts, update the Issue, implement/check useful unblocked work, publish a scoped assigned-branch PR, record exact checks and handoffs, and request integration review. Agree shared behavior changes through the relevant Issue/OpenSpec first. A component PR uses `Refs #N` unless it actually satisfies every task acceptance gate.
