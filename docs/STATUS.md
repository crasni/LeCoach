# LeCoach implementation status

Last updated: 2026-10-07.

This file records verified implementation evidence. Task ownership and progress live in [TASKS.md](../TASKS.md); product scope lives in [GUIDE.md](../GUIDE.md).

## Verified

- GitHub repository: https://github.com/crasni/LeCoach. Canonical SSH remote supplied by the maintainer: `git@github.com:crasni/LeCoach.git`.
- Initial bootstrap commit: `5f3eb6b` on `main`, pushed to `origin/main` and verified against the remote commit.
- README, product guide, ignore rules, and three reference PDFs are present.
- At the start of coordination work, `git pull --ff-only` reported already up to date.

## Not implemented or verified

- Live camera/microphone capture, speech/vision inference, the sole engagement engine, production rehearsal UI, and the sole recorder/feedback generator are not integrated. The implemented shell displays authored synthetic examples only.
- No model availability, inference latency, local privacy behavior, or UGen300 runtime compatibility has been measured.
- Competition details in GUIDE.md are project context; the latest official requirements have not been rechecked during repository bootstrap or team coordination.
- Executable event contracts and lifecycle/transport behavior are validated below. Subsystem role handoffs remain requirements for the live MVP.

## Team assignments and access

FACT: On 2026-10-07 the maintainer supplied all five GitHub usernames and authorized assigning them to the five roles. The canonical named roster, task owners, branches, and reported invitation states are now in [TASKS.md](../TASKS.md). Assignment does not imply work has started.

IMPACT: Each onboarded agent can determine its lane from its collaborator's GitHub username. Some repository invitations are still pending according to the supplied roster, so those owners need to accept before pushing work. No collaborator has been messaged or newly invited by this agent.

PROPOSAL: Assigned owners follow the TASKS.md first-task and dependency instructions; the integration owner starts the scaffold. After accepting an invitation, update the access state in TASKS.md. GitHub API authentication is still unavailable here, so invitation acceptance cannot be checked automatically; SSH Git pull/push remains available.

## INT-01 planning — local, not published

FACT: On 2026-10-07, implementation planning started on `agent/integration` for the assigned integration owner, `crasni`. The branch was fast-forwarded locally to fetched `origin/main` at `d7d61c1` with no tree changes. The proposed [implementation plan](plans/INT-01.md) is kept separately from the shared task board at the user's request. At the end of planning the INT-01 claim was local and provisional, and no application code had been implemented; subsequent implementation evidence is below.

FACT: Inspection of `origin/agent/session-analysis` at `b8f5597` found PR #1 preparation with nine synthetic coaching cases. Reported utility-test results were inspected, not rerun. At that point those artifacts were not incorporated into this branch; PR review/merge state was not checked through the GitHub API. No live capture, inference, hardware measurements, pushes, or remote merges occurred during planning.

## INT-01 local scaffold validation

FACT: Implemented the shared Python 3.12.14 package, strict Pydantic v0 contracts, generated JSON Schema/TypeScript types, monotonic/fake clocks, FIFO subscriptions, isolated session lifecycle, and injected producer/consumer protocols. The loopback FastAPI API supports prepare/subscribe/start/stop, snapshots, authored/computed feedback distinction, and a volatile preview seam. The React/TypeScript shell plays synthetic cases and displays authored audience transitions and example coaching. Core setup, commands, and public handoff are in [README.md](../README.md#development) and [ARCHITECTURE.md](ARCHITECTURE.md#int-01-implementation-decisions-and-handoff).

FACT: Reviewed Lane 5's preparation and incorporated `checks/coaching/` unchanged from `dcc280f` (PR #1 branch head `b8f5597`) in local commit `b7a42cd`, preserving the contributor's authorship. Its nine cases / ten sessions pass both the original consistency utility and the executable event/session/feedback models. Positive reason codes remain pending Lane 4; authored reactions are not produced by an engagement algorithm. No remote PR was merged.

Validation host: Linux x86_64; CPython 3.12.14; Node 24.11.0; npm 11.6.1; uv 0.12.19. Resolved versions include FastAPI 0.142.2, Pydantic 2.13.5, React 19, Vite 7.3.7, and the versions pinned in the two lockfiles. No microphone, webcam, model, or accelerator was used.

| Check | Observed result |
| --- | --- |
| `uv run pytest -q` | 60 passed, including 18 unchanged coaching utility tests; 9 utility subtests passed. Tests cover invalid data, startup failure/timeout, pending work during stop, shared stop-before-drain ordering, drain timeout, idempotence, isolation, older observations, transcript revisions, consumer/feedback failures, and browser queue overflow without losing recorder events. |
| `uv run python scripts/validate_fixtures.py` | All 9 synthetic cases / 10 sessions validate; replay matches expected retention and is deterministic. |
| `uv run python scripts/export_schema.py --check` and frontend `types:check` | Python schema and generated TypeScript are current. |
| `uv run ruff check src scripts tests examples` | Pass. |
| frontend `npm run build` | TypeScript check and production Vite build pass. |
| frontend `npm run test:e2e` | 4 Chromium checks pass: authored deterioration/recovery and three example insights; stop/repeat and final transcript without foreign/duplicate content; empty session and 390-pixel layout; reconnection without another start request. The main replay made no off-device runtime requests and produced no browser errors. |
| Isolated setup under `/tmp/lecoach-clean-r845mzvq` | Created a fresh working-tree copy without `.venv`, node_modules, or build output. Frozen/offline uv installation, cached/offline npm ci, frontend build, all 60 Python tests, schema/type checks, and the subscription example pass. No downloads were needed after populating caches. |
| Wheel build | Core wheel builds offline; installed-artifact replay verifies packaged synthetic cases using the validated core environment dependencies. Standalone offline pip dependency resolution lacked cached wheels and was not used as installation evidence. Browser UI is launched from a checkout with the local frontend build; a distributable bundled UI is not part of this milestone. |

The browser checks used headless Chromium 153.0.8010.12 downloaded to `/tmp`; the Playwright installer timed out, so the same official browser archive was fetched directly and selected using `LECOACH_CHROMIUM_PATH`. The API tests needed unsandboxed local execution because sandbox cross-thread event-loop wakeups stalled TestClient startup. The suite emits one upstream Starlette/httpx deprecation warning; checks pass. These environment details do not establish inference performance.

IMPACT: All four subsystem owners have concrete module slots, consumable executable contracts, a shared context/clock, lifecycle protocols, and repeatable fixtures. Integration implements no competing live audience engine, recorder, or coaching selector. Default live API composition explicitly reports unavailable until producers/consumers are injected. An early-stopped replay does not invent an authored summary. Preview/device release behavior is checked only through fake adapters; real devices remain an INT-02 acceptance requirement.

PROPOSAL: Publish the reviewed role-branch commits only after explicit user push approval, obtain another collaborator's scaffold review, and hand off producer and consumer implementation. Keep INT-01 in progress until publication/review/acceptance; do not mark live P0 or UGen300 integration complete. The unrelated `openspec/config.yaml` that appeared during implementation was preserved and excluded from these commits.

## Evidence to add as work lands

For each completed task, record the commit/PR, exact runnable command, whether inputs are fixtures or live, observed result, and remaining limitation. For hardware measurements also record device, runtime/model version, and measurement method. Record discoveries as FACT / IMPACT / PROPOSAL as GUIDE.md requires.
