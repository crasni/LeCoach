# leCoach implementation status

Last updated: 2026-10-07.

This file records verified implementation evidence. Task ownership and progress live in [TASKS.md](../TASKS.md); product scope lives in [GUIDE.md](../GUIDE.md).

## Verified

- GitHub repository: https://github.com/crasni/leCoach.
- Initial bootstrap commit: `5f3eb6b` on `main`, pushed to `origin/main` and verified against the remote commit.
- README, product guide, ignore rules, and three reference PDFs are present.
- At the start of coordination work, `git pull --ff-only` reported already up to date.

## Not implemented or verified

- No application scaffold, runnable product, camera/microphone capture, speech/vision inference, engagement engine, audience UI, or post-session feedback exists yet.
- No model availability, inference latency, local privacy behavior, or UGen300 runtime compatibility has been measured.
- Competition details in GUIDE.md are project context; the latest official requirements have not been rechecked during repository bootstrap or team coordination.
- Event contracts and five role handoffs describe the intended MVP, not implementation evidence.

## Team assignment blocker

FACT: SSH Git pull/push is authenticated as `crasni`. GitHub CLI has no API login; the collaborators API returned HTTP 401 on 2026-10-07.

IMPACT: Repository collaborators cannot be fetched or mapped to workstreams automatically. `crasni` is the verified repository maintainer; the other four accounts and their role preferences are unconfirmed.

PROPOSAL: Obtain the four GitHub usernames from the maintainer, or authenticate GitHub CLI with repository read access, then update the sole team roster in TASKS.md. Independent planning and lane preparation can proceed meanwhile.

## Evidence to add as work lands

For each completed task, record the commit/PR, exact runnable command, whether inputs are fixtures or live, observed result, and remaining limitation. For hardware measurements also record device, runtime/model version, and measurement method. Record discoveries as FACT / IMPACT / PROPOSAL as GUIDE.md requires.
