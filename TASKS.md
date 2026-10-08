# LeCoach tasks — moved to GitHub Issues

[GitHub Issues](https://github.com/crasni/LeCoach/issues?q=is%3Aissue+label%3Acoordination) are the sole live task records: assignments, branches, status, dependencies, remaining work and acceptance criteria. Read full bodies/comments and native **Blocked by** relationships, not just titles.

```sh
gh issue list --repo crasni/LeCoach --assignee <username> --state open --label coordination
gh issue view <number> --repo crasni/LeCoach --comments
gh api repos/crasni/LeCoach/issues/<number>/dependencies/blocked_by
```

Follow [AGENTS.md](AGENTS.md) for session/branch/publication rules. [AGENT_ROLES.md](docs/AGENT_ROLES.md) describes stable lane boundaries; [GUIDE.md](GUIDE.md) defines product scope; [ARCHITECTURE.md](docs/ARCHITECTURE.md) defines shared interfaces. Existing assignments and implementation history were preserved; this migration does not restart work or accept unfinished live tasks.

This file is retained for old links only. Do not add a roster, status table, claim checklist, dependency graph or acceptance criteria here. The old board remains in Git history; [STATUS.md](docs/STATUS.md) preserves dated implementation evidence.
