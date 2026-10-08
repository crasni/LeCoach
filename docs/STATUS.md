# LeCoach implementation status

Last updated: 2026-10-08 (Asia/Taipei).

This file records verified implementation evidence. Task ownership and progress live in [TASKS.md](../TASKS.md); product scope lives in [GUIDE.md](../GUIDE.md).

## Verified

- GitHub repository: https://github.com/crasni/LeCoach. Canonical SSH remote supplied by the maintainer: `git@github.com:crasni/LeCoach.git`.
- Initial bootstrap commit: `5f3eb6b` on `main`, pushed to `origin/main` and verified against the remote commit.
- README, product guide, ignore rules, and three reference PDFs are present.
- At the start of coordination work, `git pull --ff-only` reported already up to date.

## Not implemented or verified

- Live camera/microphone capture, speech/vision inference and generated coaching are not integrated. The synthetic rehearsal screen now uses the sole deterministic engagement engine; the in-memory recorder is available through injection but is not enabled in default API composition. Example feedback remains authored.
- No model availability, inference latency, local privacy behavior, or UGen300 runtime compatibility has been measured.
- Current competition requirement verification is recorded under INT-03 below; final submission, cutoff details and target-device inference remain unverified.
- Executable event contracts and lifecycle/transport behavior are validated below. Subsystem role handoffs remain requirements for the live MVP.

## INT-03 refreshed package and browser validation

FACT: Continued INT-03 on 2026-10-08, documentation branch baseline `4cd7887`; application code is unchanged from merged source `8345c98`. Refreshed the 12-slide editable proposal/PDF and claim map for the computed engine, rehearsal UI, injected recorder and 130-test / 69-subtest evidence. The synthetic audience now has the computed 0/20/30/35/40-second times; coaching remains explicitly authored. The recorder is tested through injection and is not enabled in default browser composition. Live capture, inference, feedback generation and UGen300 claims remain pending.

FACT: With Node 24.11.0 / npm 11.6.1, generated frontend types and production build pass. Playwright Chromium 153.0.8010.12, downloaded into temporary storage, passes all **four existing browser checks** in 24.5 s:

- Computed audience deterioration/recovery and reason labels; authored coaching after completion; no browser errors or non-loopback requests during this replay.
- Early stop, repeat-session isolation and delayed/revised transcript handling.
- Empty-session completion and a 390×844 narrow layout without horizontal overflow.
- WebSocket interruption/reconnection without a duplicate start or playback restart.

Commands from the repository root, with the documented Node 24 runtime on PATH:

```sh
npm --prefix frontend run types:check
npm --prefix frontend run build
PLAYWRIGHT_BROWSERS_PATH=/tmp/lecoach-browser npm --prefix frontend run test:e2e
```

The first browser run used system Node 22 and also passed; because the project requires Node 24, build/types/browser checks were repeated using the already-installed Node 24 runtime above. The backend's earlier 130 tests / 69 subtests, recorder checks and fixture checks are retained under the main-reconciliation record; no application changes justified another backend run. Headless replay also confirms camera-unavailable speech still reaches CONFUSED, while unavailable inputs, empty sessions, delayed transcript and drain-timeout examples stay NEUTRAL. These are synthetic checks, not actual microphone/camera or inference measurements.

FACT: Re-exported with LibreOffice 26.2.6.3 and isolated profile `/tmp/lecoach-int03-refresh-lo`, inspected all 12 rendered pages, and checked paragraph/page parity and six reference annotations. The refreshed hashes and per-page evidence are recorded in [readiness](submission/readiness.md). Re-fetched the public official rules at approximately 11:18 UTC: their normalized content hash is unchanged, as SOURCES records. The rendered public announcements page showed no announcements at inspection; form/registration details and the pre-delivery recheck remain pending. No organizer/team message or authenticated action occurred.

IMPACT: The refreshed local proposal passes task 6.1 with conditional/live/external scenarios explicitly pending; the CLI confirms 16/23 tasks complete. [README's test guide](../README.md#try-the-current-prototype) now explains what users can run and what to expect. Lane 5's script and advice reconciliation, INT-02 live evidence, final footage and external delivery still prevent full INT-03 completion.

PROPOSAL: Review the refreshed proposal and exact local commit range for role-branch publication. Obtain the required team/form details and owner demo/live handoffs; do not treat authored example coaching as generated feedback or a local PDF as a submission receipt.

## Latest main reconciliation — 2026-10-08

FACT: At the user's request, fetched and fast-forwarded local main to `c88386a`, then pulled it into `agent/integration` in local merge `8345c98`. Main includes [PR #7](https://github.com/crasni/LeCoach/pull/7) (engagement engine/rehearsal screen) and [PR #5](https://github.com/crasni/LeCoach/pull/5) (in-memory recorder). Resolved the COACH-01 task-board conflict by retaining owner evidence and recording the merged recorder plus unfinished selection/template feedback. Existing INT-01 acceptance and INT-03 deliverables are retained. A public read-only open-PR listing returned no open PRs at inspection; no remote review, merge or push was performed here.

FACT: On Linux x86_64 / Python 3.12.14, merged application source `8345c98` passes **130 tests and 69 subtests** in 1.01 s, with one upstream Starlette/httpx deprecation warning. The recorder matches nine synthetic cases / ten sessions; fixture validation, core lint and schema parity pass. Frontend generated-type check and production build pass. Commands:

```sh
uv run --frozen pytest -q
uv run --frozen --offline python checks/coaching/record_replay.py
uv run --frozen --offline python scripts/validate_fixtures.py
uv run --frozen --offline ruff check src scripts tests examples
uv run --frozen --offline python scripts/export_schema.py --check
npm --prefix frontend run types:check
npm --prefix frontend run build
```

The earlier temporary Python interpreter was gone; the first offline run could not restore all locked dependencies. The frozen online run restored the development environment without changing dependency pins, then the checks passed. Browser E2E was not rerun in this pull review; no local browser executable was found.

FACT: Explicit headless replay through `.venv/bin/lecoach replay --case weak_to_improved --audience engine` computes states at 0, 20, 30, 35 and 40 seconds. `--audience authored` retains the older fixture states at 0, 20.5, 30.5, 36 and 42 seconds. Both use synthetic input; feedback remains authored. The recorder check uses the actual recorder through injection, not the default browser composition. No live capture, model inference or target measurements occurred.

IMPACT: The deck/PDF still describe the dated pre-pull `35e99b2` baseline. They need a content/claim-map refresh for the merged engine and recorder before final package acceptance; INT-03 task 6.1 is reopened. Previous source/PDF export and visual checks remain historical evidence, not a review of an updated deck. INT-02, feedback generation, final narration/recording and external gates remain unfinished.

PROPOSAL: Refresh the proposal and claim map, reconcile authored coaching times with computed engine evidence through Lane 5, and accept live producer composition under INT-02 before final footage. The local publication range changed after this pull and still needs its own explicit push approval.

## INT-03 integration reconciliation

FACT: On 2026-10-07, preserved the six existing INT-01 acceptance edits in local commit `9dd550e`, then merged fetched main `ebdf421` into `agent/integration` in local commit `35e99b2`. TASKS/STATUS conflicts were resolved by retaining the maintainer's acceptance exception and both contributors' preparation/review records. The shared contracts and acceptance artifacts are unchanged from the preservation commit. The coaching/speech preparation directories match fetched main.

FACT: Main contains PR #1 through merge `48597bb` and PR #3 through `ebdf421`. Those merges publish synthetic preparation and reviewed checks, not live producers or generated coaching. Their original validation records below remain attributed to the original host/date; they are not new checks performed by this reconciliation. TASKS now points to the merged preparation and preserves incomplete live tasks.

FACT: Fetch also found resumed `origin/agent/session-analysis` at `5991048`, with a recorder implementation and owner-reported synthetic evidence. Its handoff README and changed-file list were inspected read-only. That continuation is not incorporated or validated on this integration branch, and the owner still needs LIVE-01 reason/transition evidence for feedback generation. No final English demo script was found in the inspected handoff.

IMPACT: INT-03 can produce the local proposal/evidence package against current main without erasing prior acceptance or contributor work. INT-02's live acceptance remains pending. The local INT-03 claim is linked to its [OpenSpec change](../openspec/changes/int-03-submission-and-hardware-evidence/proposal.md); no new push is authorized by apply.

PROPOSAL: Complete the independent deck, requirements and hardware-readiness records; review the recorder continuation separately with its owner and obtain the remaining live subsystem/demo handoffs. Keep INT-03 in progress until final acceptance and submission gates are met.

## INT-03 apply hardware readiness

FACT: Repeated read-only readiness inspection on 2026-10-07 at approximately 15:48 UTC, source checkout `35e99b2` on Linux x86_64, kernel `7.0.0-38-generic`. Sandbox `lsusb` failed to initialize libusb (`-99`); a permitted host read returned USB root hubs, the integrated Chicony camera, wireless device and Logitech receiver, with no identifiable UGen300. `command -v hailortcli` returned no path. The project `.venv/bin/python` reported 3.12.14 and `find_spec('hailo_platform')` returned `None`. [HARDWARE.md](HARDWARE.md#inspect-an-available-host) documents the exact inspection commands. No capture device was opened; no driver, runtime, model or HEF was installed/downloaded.

FACT: Re-fetched and inspected five pinned Hailo sources; [SOURCES](SOURCES.md#int-03-apply-source-recheck) records hashes. The speech candidate documents windowed audio and the pose benchmark uses PCIe conditions. Generic Hailo Apps prerequisites reference PCIe/Hailo-8 installation material; that does not establish the selected Hailo-10H USB setup or a Python 3.12-compatible binding here.

IMPACT: Target-evidence disposition is **unavailable prerequisites / no measured inference** on this host. Approved live adapters, integrated composition and timing instrumentation are also absent from this checkout. Model load/processing, producer delivery, engagement decision, browser render delay, concurrent inference, real device release and actual speech accuracy are all unmeasured. This observation does not establish the team's hardware access elsewhere.

PROPOSAL: Obtain the actual USB host/device/runtime/firmware combination and owner adapter handoffs, then follow HARDWARE's isolated/concurrent procedure with INT-02. Keep the deferred accelerator measurement milestone explicit. The English deck can show a sourced target architecture and synthetic scaffold evidence; it cannot claim target performance, live P0 completion or measured privacy behavior.

## INT-03 apply local validation

FACT: On 2026-10-07 UTC / overnight into 2026-10-08 Asia/Taipei, implemented the local INT-03 package on `agent/integration`: a 12-slide editable [English proposal](submission/proposal.fodp), matching [PDF](submission/proposal.pdf), [readiness/claim map](submission/readiness.md), refreshed canonical requirements/source records, and the hardware inspection/measurement procedure. Application source, event contracts and dependency pins are unchanged by INT-03. The new deck uses native text/vector shapes, not borrowed imagery or a mock claim of a live app screenshot.

FACT: Reproduced the model-free baseline against application source `35e99b2` with the existing project Python 3.12.14 environment on Linux x86_64:

```sh
uv run --frozen --offline lecoach replay --case weak_to_improved
uv run --frozen --offline python scripts/validate_fixtures.py
uv run --frozen --offline pytest -q
```

Observed: headless result reports `mode: fixture` and `output_provenance: hand_authored`; all nine cases / ten sessions validate; **97 tests and 37 subtests pass** in 0.96 s, with the existing Starlette/httpx deprecation warning. The five authored state transitions in the weak-to-improved case occur at 0, 20.5, 30.5, 36 and 42 seconds; authored feedback has two improvements and one strength. No real device, inference model or target accelerator was used.

An initial attempt with a new empty temporary uv cache could not resolve the build dependency offline; no tests ran in that attempt. Reusing the existing populated cache built the editable package and passed the checks above. This is existing-environment/offline-cache reproduction, not a new uncached installation result. The API suite needed permitted local execution for the documented sandbox thread/event-loop limitation.

FACT: Exported with LibreOffice 26.2.6.3 and an isolated temporary profile; `pdfinfo` reports 12 pages. Every source paragraph appears on its corresponding raw-extracted PDF page, and `pdfinfo -url` lists the six intended clickable annotations. All 12 rendered pages were visually inspected; title/card spacing and diagram event flow were corrected before the final review. Artifact hashes, exact export/inspection commands, topic coverage and per-page claim references are in readiness. The current verified page budget is satisfied; final form format/upload limits remain unconfirmed.

FACT: Git ignore checks cover `sessions/`, `recordings/`, `models/` and `.env.*`; no files in those private-data locations are tracked. Only authored proposal content and sanitized observations are prepared for publication. No video/audio capture, transcript export from a real rehearsal, model download, upload, push, organizer message or competition submission occurred during this apply work.

IMPACT: Local deck/evidence preparation is ready for team review. Target inference remains unmeasured; final Lane 5 narration/recording, accepted INT-02 live evidence, registration/cutoff/form/originality confirmation, role-branch publication, video link and actual submission receipt remain pending. The recorder continuation is open as [PR #5](https://github.com/crasni/LeCoach/pull/5), not accepted/integrated by this work.

PROPOSAL: Review the scoped local commit set and authorize publication separately if ready to share; then use the owner handoffs to replace draft/live placeholders with accepted observations. Keep INT-03 in progress and its unmet OpenSpec tasks unchecked. Existing INT-01 acceptance is preserved; archiving remains separate.

## Team assignments and access

FACT: On 2026-10-07 the maintainer supplied all five GitHub usernames and authorized assigning them to the five roles. The canonical named roster, task owners, branches, and reported invitation states are now in [TASKS.md](../TASKS.md). Assignment does not imply work has started.

IMPACT: Each onboarded agent can determine its lane from its collaborator's GitHub username. Some repository invitations are still pending according to the supplied roster, so those owners need to accept before pushing work. No collaborator has been messaged or newly invited by this agent.

PROPOSAL: Assigned owners follow the TASKS.md first-task and dependency instructions; the integration owner starts the scaffold. After accepting an invitation, update the access state in TASKS.md. During initial coordination, GitHub API authentication was unavailable. In the Lane 5 session, WolflordR confirmed invitation acceptance, a branch push succeeded, and the existing Git credential authenticated the GitHub API as `WolflordR`. This does not verify other collaborators' invitation states.

## COACH-01 preparation — pending integration review

Historical preparation evidence follows. PR #1 was subsequently accepted and
merged; the recorder continuation below records the current Lane 5 work.

FACT: Lane 5 prepared commit `dcc280f` on `agent/session-analysis`, following claim commit `8123599`, and published [draft PR #1](https://github.com/crasni/leCoach/pull/1) for integration-owner review. [checks/coaching/README.md](../checks/coaching/README.md) documents nine hand-authored synthetic cases covering ten expected completed sessions. Fixtures include weak-to-improved delivery, missing camera, no usable inputs, empty/startup sessions, late finals and duplicate retries, drain timeout, repeated sessions, and adjacent incidents. Example feedback uses the existing v0 document shapes; positive reason codes remain pending LIVE-01. No real rehearsal data or model output is included.

Validation on the local macOS development host with Python 3.14.5:

```sh
python3 checks/coaching/check_cases.py
python3 -m unittest discover -s checks/coaching -p 'test_*.py' -v
```

Observed result: all 9 cases / 10 expected sessions are internally consistent; all 18 acceptance-utility tests pass. Negative checks reject dropped finals during drain, duplicate retained finals, post-completion callbacks, mixed-session logs, dangling/duplicate feedback evidence, invented moments, missing limitations, and added engagement scores. Output checks accept different feedback wording. These results verify synthetic artifacts and the check utility, not a production recorder, feedback generator, live audience engine, or inference pipeline. The checks use no network, devices, models, or persistent rehearsal storage; temporary synthetic output is cleaned up by the tests.

IMPACT: Lane 5 can use these cases to check actual `CompletedSession` and `Feedback` outputs after dependency handoff. COACH-01 remains blocked on INT-01's scaffold, executable contract/lifecycle and layout handoff, plus LIVE-01's transition/reason evidence. No production logger, additional engagement engine, or new shared contract was created. The preparation claim and artifacts still require integration-owner review; COACH-01 is not complete.

PROPOSAL: The integration owner reviews the claim and fixture placement, supplies the approved application layout and replay seam, and coordinates Lane 4's reason vocabulary/positive evidence. Lane 5 then implements the recorder, moment selector and template feedback in that layout, runs the cases against real consumer outputs, and records integration evidence before marking COACH-01 done.

## COACH-01 recorder continuation — local, pending publication/review

FACT: On 2026-10-07, read-only GitHub checks confirmed PRs #1, #3 and #4 merged.
The remote role branch had been deleted following merge; a safe explicit pull
from `origin/main` fast-forwarded the existing local `agent/session-analysis`
branch to `ebdf421` before editing. INT-01's scaffold/contracts are now available;
LIVE-01 is still `todo` on the shared board with no published engine implementation.
No other lane's claim or task status was changed.

FACT: Implemented the sole `InMemorySessionRecorder` in the approved
`src/lecoach/coaching/` slot using the existing `SessionContext`, event models and
`CompletedSession` protocol. It preserves normalized evidence and revisions,
deduplicates stable retries, rejects changed retry payloads, orders by capture time
and event ID, keeps eligible observations during drain, and ignores foreign/closed
sessions, post-stop audience updates and observations captured after stop.
Completion metadata is checked against the recorded lifecycle. Deep-copy snapshots
protect retained evidence from mutations by producers or consumers.

Retention: one active/completed timeline stays in memory until the recorder's next
start or disposal. Returned copies belong to their callers. The recorder has no
independent clock, media capture, disk persistence or network behavior. Its
[module handoff](../src/lecoach/coaching/README.md) documents injection and retention.
Default API composition remains the integration owner's responsibility; the actual
recorder is exercised through the published consumer factory.

Validation host: local macOS arm64, CPython 3.12.14 and the unchanged frozen uv
lockfile. Local setup provisioned the pinned Python and development packages; no
inference model was downloaded. Commands below were run with the resulting
`.venv/bin/python` and `.venv/bin/ruff`; the equivalent project commands are:

```sh
uv run python checks/coaching/record_replay.py
uv run pytest -q tests/test_coaching.py
uv run pytest -q
uv run python scripts/validate_fixtures.py
uv run python scripts/export_schema.py --check
uv run ruff check src scripts tests examples
```

Observed result: the actual recorder matches all 9 synthetic cases / 10 expected
completed sessions. All 13 recorder tests and 9 fixture subtests pass, including
controller drain/retry, bounded drain timeout with cancellation, empty stop,
snapshot mutation isolation, reused recorder isolation and invalid lifecycle
handling. The full suite passes 110 tests and 46 subtests, with the existing
Starlette/httpx deprecation warning. Fixture validation, schema parity and core
lint pass. UI and shared contracts were not changed.

IMPACT: Lane 5 now has a runnable recorder against INT-01's real seams. Audience
events in these checks remain hand-authored; producer release checks use fake
adapters. No real microphone/camera, engagement inference, computed feedback or
UGen300 behavior is established. Positive coaching semantics and actual transition
evidence still depend on LIVE-01, so COACH-01 remains incomplete.

PROPOSAL: Present the exact local commit and role-branch destination for user push
approval, then open a scoped continuation PR for integration-owner review. Lane 4
supplies its transition/reason evidence before Lane 5 implements and verifies
moment selection/template feedback. No new shared interface or second engagement
engine was introduced, and no commits from this continuation have been pushed.

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

PROPOSAL: Publish the reviewed role-branch commits only after explicit user push approval, obtain another collaborator's scaffold review, and hand off producer and consumer implementation. Keep INT-01 in progress until publication/review/acceptance; do not mark live P0 or UGen300 integration complete. The `openspec/config.yaml` that appeared during implementation was preserved and excluded from the implementation commits; it is now used by the requested migration below.

## OpenSpec plan migration

FACT: On 2026-10-07, `openspec --version` reported 1.14.1. `openspec list --json` and `openspec context --json` resolved this repository as the nearest OpenSpec root, with the installed Codex skills and `spec-driven` configuration. No reinitialization was needed.

FACT: Migrated the separate INT-01 plan into [int-01-local-integration-scaffold](../openspec/changes/int-01-local-integration-scaffold/proposal.md), with proposal, design, four capability delta specs, and an evidence-backed task checklist. `openspec status` reports 4/4 planning artifacts complete; strict validation passes with no issues, and `openspec doctor --json` reports a healthy root. The old plan is a compatibility pointer. Application code and contracts were not changed or retested during this documentation migration.

IMPACT: OpenSpec now tracks the existing local implementation and three remaining publication/review gates. TASKS retains ownership/progress, ARCHITECTURE retains contract semantics, and this file retains observed evidence. Main OpenSpec specs are not synced yet; the active change is not archived.

PROPOSAL: Review the migrated artifacts, then continue remaining handoff work using `$openspec-apply-change int-01-local-integration-scaffold`. Preserve the separate push approval rule and archive only after accepted completion.

FACT: At the user's direction, OpenSpec commands and workflow guidance live in [WORKFLOW.md](WORKFLOW.md), linked from the internal agent handoffs. README contains no OpenSpec workflow section.

## OpenSpec apply — handoff preparation

FACT: Started the requested apply workflow on 2026-10-07. The CLI reports `ready`, with 17/20 tasks complete and publication/review tasks 6.4–6.6 remaining. Reviewed all supplied context artifacts and prepared the migration for a scoped local commit. Strict OpenSpec validation passes with no issues, all 52 local documentation links resolve, and Git whitespace checks pass. Application code is unchanged; the earlier 60 Python tests and four browser checks remain the recorded scaffold evidence.

FACT: A read-only SSH remote check found `main` at `d7d61c1` and no current `agent/integration` remote branch. The reviewed coaching preparation still matches its source commit unchanged. GitHub CLI/API authentication is unavailable in this environment; remote PR and collaborator-review state has not been established through the API.

IMPACT: The local commit set can be proposed for publication on `agent/integration`, creating that role branch remotely after approval. Task 6.4 remains unchecked until explicit approval is received; publication and collaborator acceptance remain separate pending gates. No push, PR creation, remote merge, or archive has occurred during preparation.

## INT-01 publication and remaining acceptance

FACT: The user explicitly approved publication of the existing INT-01 commits through `a7a91ef` in this session. SSH push and remote verification confirmed `agent/integration` at `a7a91ef4dc91f810ac51c96db9d36423f6baa292`, while main remained at `d7d61c1`. [PR #4](https://github.com/crasni/LeCoach/pull/4) subsequently merged on 2026-10-07 at 11:03:57 UTC; fetched main is `c0f6c68` and contains all four approved commits. GitHub removed the remote role branch; its merged local branch/tracking ref were cleaned up, then the assigned branch was recreated from current main for this follow-up.

FACT: Public GitHub API checks of PR #4's reviews, issue comments, and inline comments returned empty arrays. PRs [#1](https://github.com/crasni/LeCoach/pull/1) and [#3](https://github.com/crasni/LeCoach/pull/3) remain open synthetic preparation, not live subsystem handoffs. Public API reads are available; authenticated API writes remain unavailable. The earlier API-access limitation applied to that earlier preparation session.

IMPACT: Publication tasks 6.4 and 6.5 are satisfied. INT-01 is in review with 19/20 OpenSpec tasks complete; task 6.6 is still unchecked because collaborator review and downstream acceptance have not been established. The scaffold is available on main for all lanes. INT-02's live composition dependencies are not yet met.

PROPOSAL: Another collaborator reviews the merged scaffold and records contract/fixture acceptance before INT-01 is marked done or archived. Continue independent INT-03 source verification on `agent/integration`; the new local claim and follow-up remain unpublished until a separate approved push.

## INT-01 maintainer acceptance

FACT: On 2026-10-07 the maintainer explicitly instructed: "just mark INT-01 as complete and /$openspec-archive-change". This accepts the merged, validated scaffold and waives the remaining collaborator-review/downstream signoff gate. The original review evidence is still absent; no collaborator review or new live/hardware validation is claimed.

IMPACT: INT-01 is done with 20/20 tasks closed after updating task 6.6 to record this explicit acceptance exception. The maintainer's instruction supersedes the earlier proposal to wait for signoff. INT-02 can prepare composition and integration checks, but its live acceptance still depends on the assigned subsystem implementations. Closing INT-01 does not complete those tasks.

PROPOSAL: Archive the accepted INT-01 change using the requested skill, preserving its implementation evidence and acceptance exception. Local archive/spec/documentation commits still require their own push approval under AGENTS.

## INT-03 source verification and hardware readiness

FACT: On 2026-10-07, inspected the three supplied PDFs and retrieved the official competition page directly over HTTPS, including its JSON-LD rules description. The browser extraction service returned 404, so that failure was not treated as proof the page was unavailable. [CONTEST.md](CONTEST.md) records verified requirements and unresolved submission details; [SOURCES.md](SOURCES.md) records inspected pages, hashes, exact Hailo documentation revisions and untested adapter candidates. The official rules permit initial Stage I validation without the target accelerator; Stage II requires the selected platform. The cutoff date is verified, but its precise time/timezone is not established by the retrieved metadata.

FACT: Read-only `lsusb` on Linux x86_64 (kernel `7.0.0-38-generic`) showed root hubs, an integrated camera, wireless device and USB receiver; no identifiable UGen300 appeared. `hailortcli` was absent from PATH. The application's `.venv/bin/python` reports Python 3.12.14 and `importlib.util.find_spec('hailo_platform')` returned `None`; system Python 3.14.4 is not the application's pinned runtime. These observations do not prove the team lacks hardware elsewhere. No device capture, driver install, model download or accelerator inference was performed.

IMPACT: Vendor documentation supports specific Hailo-10H Whisper and pose HEF candidates, but LeCoach compatibility and concurrent inference remain unmeasured. The speech reference describes ten-second input windows, and the pose benchmark conditions use PCIe rather than the selected USB path. Neither model availability nor vendor throughput establishes a suitable live engagement delay. The current prototype still displays synthetic authored outputs only.

PROPOSAL: [DEMO.md](DEMO.md) provides a proposed 2:55 recording sequence and existing replay commands for handoff to Lane 5. Complete INT-02 with the subsystem owners, then capture honest live CPU evidence and measured UGen300 evidence when the device/runtime are available. Confirm submission cutoff details and team registration, prepare final English assets, and obtain applicable publication/submission authorization. INT-03 remains in progress; documentation and its claim are local until a separately approved push.

Validation: strict INT-01 OpenSpec validation passes; all 54 local documentation targets in the changed handoff/reference files resolve; Git whitespace checks pass. Five pinned Hailo source documents were retrieved successfully and their runtime/model assumptions checked against the cited content. Application code and contracts were unchanged, so the earlier scaffold test evidence was not rerun or represented as new live validation.

## PR #1 integration-owner review and conflict resolution

FACT: Reviewed the coaching checker, negative tests, fixture/oracle structure and canonical contract compatibility. The coaching directory matches current main byte-for-byte: INT-01 / merged PR #4 already incorporated these artifacts. Merged current main locally into `agent/session-analysis`, resolving three TASKS.md conflicts by preserving the accepted invitation, current board semantics and contributor preparation evidence. No coaching code or fixture was changed.

Validation on Linux: `python3 checks/coaching/check_cases.py` passes 9 cases / 10 sessions; `python3 -m unittest discover -s checks/coaching -p 'test_*.py'` passes 18 tests; the existing project Python 3.12 environment running `python -m pytest -q` passes 60 tests and 9 subtests, with the existing Starlette/httpx deprecation warning.

IMPACT: No new blocking code defect was found in the preparation scope. Exact oracle moments are scenario acceptance targets, not proof of every valid coaching selection; the standalone checker is not a replacement for executable schema validation. Positive reason semantics still require Lane 4. The scaffold is already published, so waiting for scaffold publication is no longer a blocker; COACH-01 implementation is not done.

PROPOSAL: Publish this local branch reconciliation only after explicit push approval. Accept PR #1 as preparation/documentation reconciliation, then let its owner implement the recorder/generator against the published seams and agreed LIVE-01 evidence. No remote review, push or merge was performed in this review.

## LIVE-01 local engine and rehearsal screen

FACT: On 2026-10-08, Lane 4 (@ricebal1) implemented the sole engagement engine in `src/lecoach/engagement/` (rules and defaults in [its README](../src/lecoach/engagement/README.md) and `config.py`) and replaced the inspection shell with a rehearsal screen: eight 2D SVG listeners that ripple through state changes, the current reaction with plain-language reasons, an audience timeline, input status, pace/filler/facing metrics, the live transcript with partials, a camera-preview slot for live mode, and the authored coaching summary. Composition change for integration review: `replay_with_engine()` supplies only the engine; the served app and `lecoach replay` (new `--audience engine|authored`, default `engine`) compute audience states from fixture observations, while live mode still reports unavailable. Proposed reason codes are recorded in ARCHITECTURE.

Validation on Windows 11 x86_64; CPython 3.12.14 via uv 0.12.23; Node 24.14.1; npm 11.11.0; Playwright Chromium. No microphone, camera, model or accelerator was used.

| Check | Observed result |
| --- | --- |
| `uv run pytest -q` | 117 passed, 60 subtests, including 20 engagement tests: deterioration/recovery and determinism on `weak_to_improved`; no negative state for missing inputs, outages, silence-only, unsupported language or delayed delivery; speech-only operation with the camera unavailable; 60 s of threshold-crossing jitter without negative states or transitions faster than the dwell; hysteresis hold; stale speech dropped from reasons; older observations ignored; absent person and camera outage not treated as facing away; restart/stop isolation; live tick; config validation; Lane 2 speech fixtures trigger `pace_high`, `fillers_frequent` and `silence_prolonged`. |
| `uv run lecoach replay --case weak_to_improved` | `NEUTRAL → CONFUSED (20 s, pace_high) → BORED (30 s, pace_high + facing_away_sustained) → INTERESTED (35 s) → ENGAGED (40 s)`, every reason citing earlier fixture events. |
| `uv run ruff check src scripts tests examples`, `scripts/export_schema.py --check`, `scripts/validate_fixtures.py`, `examples/consume_replay.py` | Pass. |
| frontend `npm run build` and `npm run test:e2e` | Build passes; 4 Chromium checks pass, now asserting computed transitions with reasons and that the delayed-transcript case stays `NEUTRAL`. `playwright.config.ts` resolves the backend executable on Windows too. |
| frontend `npm run types:check` | Fails identically on unmodified `main` in this checkout: Git `core.autocrlf=true` checks out the generated file with CRLF line endings. Not caused by this change; generated contracts were not modified. |

IMPACT: Lane 5 can consume real transition events and reason codes; authored coaching in `weak_to_improved` still quotes authored times (20.5 s, 30.5 s, 42 s) that differ from computed ones, so its oracle needs review against engine output. Live adapters can replace fixtures through the unchanged `EngagementEngine` seam. Thresholds are demo heuristics, unvalidated against real rehearsals.

FACT: With the user's approval, `agent/avatar-ui` was pushed at `fc96ec8` and published as [PR #7](https://github.com/crasni/LeCoach/pull/7). The successful push shows @ricebal1 has repository write access.

PROPOSAL: The integration owner reviews PR #7, especially the reason codes and the composition change. LIVE-02 then wires real speech/vision adapters, checks the live tick and camera preview with real devices, and retunes thresholds from recorded rehearsals.

## Evidence to add as work lands

For each completed task, record the commit/PR, exact runnable command, whether inputs are fixtures or live, observed result, and remaining limitation. For hardware measurements also record device, runtime/model version, and measurement method. Record discoveries as FACT / IMPACT / PROPOSAL as GUIDE.md requires.

## PR #3 integration-owner review

FACT: Merged current main locally into `agent/audio-streaming` without Git conflicts and reviewed speech tokenization, fixture generation, semantic checker and tests against the executable contracts. All 214 fixture events validate with `lecoach.contracts.events.parse_event`; all 10 cases / 11 sessions pass the oracles and generator parity check.

FACT: Reproduced acceptance of missing/late lifecycle starts and invalid lifecycle payloads (unknown or duplicated incomplete sources and extra fields). Added regression tests, observed seven failing assertions before the fix, then enforced lifecycle start/order and canonical lifecycle payload shapes. Speech-only exports remain supported. Added speech tests to default pytest discovery; no event schema or production adapter was changed.

Validation on Linux using the existing project Python 3.12 environment: `python -m pytest -q tests checks/coaching checks/speech` passes 97 tests and 37 subtests, with the existing Starlette/httpx deprecation warning. The standalone speech suite passes 37 tests. Fixtures remain synthetic and unchanged.

IMPACT: Preparation is acceptable with the local fixes. The standalone checker is not exhaustive schema validation; continue validating through executable contracts. Extra completed-pause metrics and leading-silence handling fit the current contract. Language and timing constants are fixture assumptions pending central configuration and demo-language agreement. Scaffold publication is no longer a blocker; live capture, inference, latency, filler recall and target hardware remain unverified.

PROPOSAL: Publish the reviewed local branch only after explicit push approval, then accept the preparation PR without marking AUD-01 complete. The owner should implement the live adapter in `src/lecoach/speech/` against SessionContext and the start/stop_capture/drain seams. No remote review, push or merge was performed during this review.

## AUD-01 preparation — original contributor evidence

FACT: Lane 2 prepared commit `1ac7b53` on `agent/audio-streaming`, following claim commit `1412994`, and published [draft PR #3](https://github.com/crasni/LeCoach/pull/3) for integration-owner review. [checks/speech/README.md](../checks/speech/README.md) documents ten synthetic cases covering eleven speech sessions, generated from hand-written scenario scripts. They cover steady and rapid pace, heavy fillers, prolonged silence, model warm-up with late, retried and out-of-order delivery, a hallucinated partial retracted by an empty final, denied and lost microphones, silence only, unsupported language, and repeated sessions. They follow proposed v0 speech rules documented in that README: English tokenizer and filler lexicon, window and coverage rules, null versus zero, and pause reporting. No microphone, audio, model, or accelerator was used.

Validation in the cloud development container (Linux, Python 3.13.16; the tests also pass with Python 3.11 and 3.12):

```sh
python3 checks/speech/check_speech.py
python3 -m unittest discover -s checks/speech -p 'test_*.py' -v
python3 checks/speech/make_fixtures.py --check
```

Observed result: all 10 cases / 11 sessions match their hand-derived oracles, and the committed fixtures match the scenario scripts. All 33 tests pass. They include rejection of:

- double-counted retries;
- revisions after a final;
- overlapping finals;
- unfinalized speech at completion;
- windows counted before their overlapping finals;
- zero instead of null for short or unavailable windows;
- metrics claiming availability during an outage;
- inflated WPM or filler counts;
- leading silence reported as a pause;
- unreported, duplicated or misplaced pauses.

Lane 5's `check_event` from [draft PR #1](https://github.com/crasni/LeCoach/pull/1) accepted all 214 fixture events. These results verify synthetic artifacts and the check utility only. They do not verify microphone capture, transcription accuracy, latency, or a live adapter.

FACT: The official SalesKit in `docs/` lists Whisper-Tiny, Whisper-Base and Whisper-Small as runnable on the UGen300 (Hailo-10H) SKUs through the Hailo GenAI Model Zoo (PDF pages 7, 8 and 15). External reports say Whisper often omits filler words and can produce text on silence or noise; sources are in the README. None of this has been run or measured locally or on UGen300.

IMPACT: Lanes 4 and 5 can develop against realistic speech streams before the live adapter exists, including pace, fillers, pauses, unavailable input, and null versus zero. AUD-01 remains blocked on INT-01's scaffold, configuration location, and executable contract and replay seam. No production speech adapter, capture code, or dependency was added. Filler counts from standard Whisper output may be undercounts, so filler-driven reactions depend on AUD-02 measurements.

PROPOSAL: The integration owner reviews the claim, the fixture placement, and the proposed v0 speech rules and open questions in the README: pause-completion events, leading silence, null reasons, configuration, analysis language, and model-failure status. After INT-01 lands, Lane 2 implements microphone capture → voice activity detection → local Whisper with word timestamps in the approved layout. Recorded sessions are then checked with `check_speech.py --stream`, and AUD-02 measures latency and filler recall per model size before any claim is made.
