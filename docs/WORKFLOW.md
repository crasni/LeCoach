# Internal development workflow

This document is for collaborators and coding agents. Start with
[AGENTS.md](../AGENTS.md) for branch, ownership, and approval requirements.

## OpenSpec workflow

OpenSpec is initialized here with the `spec-driven` schema. The active
[INT-01 proposal](../openspec/changes/int-01-local-integration-scaffold/proposal.md)
contains the migrated plan, design, capability specs, and execution checklist.
Completed local implementation is checked off; publication/review remains pending.
The shared task board continues to own assignments and overall progress.

Verify repository setup and the change from the root:

```sh
openspec --version
openspec list
openspec status --change int-01-local-integration-scaffold
openspec validate int-01-local-integration-scaffold --strict
```

In Codex, use `$openspec-propose` for a new change,
`$openspec-update-change` to revise planning artifacts, and
`$openspec-apply-change int-01-local-integration-scaffold` to continue this change.
After completed tasks and accepted review, use `$openspec-archive-change`.
These are agent skill commands entered in chat; terminal verification uses the
CLI commands above. Pushes still require the explicit approval in [AGENTS.md](../AGENTS.md#required-user-approval-before-every-push).

