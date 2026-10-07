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
- Current competition requirement verification is recorded under INT-03 below; final submission, cutoff details and target-device inference remain unverified.
- Executable event contracts and lifecycle/transport behavior are validated below. Subsystem role handoffs remain requirements for the live MVP.

## Team assignments and access

FACT: On 2026-10-07 the maintainer supplied all five GitHub usernames and authorized assigning them to the five roles. The canonical named roster, task owners, branches, and reported invitation states are now in [TASKS.md](../TASKS.md). Assignment does not imply work has started.

IMPACT: Each onboarded agent can determine its lane from its collaborator's GitHub username. Some repository invitations are still pending according to the supplied roster, so those owners need to accept before pushing work. No collaborator has been messaged or newly invited by this agent.

PROPOSAL: Assigned owners follow the TASKS.md first-task and dependency instructions; the integration owner starts the scaffold. After accepting an invitation, update the access state in TASKS.md. During initial coordination, GitHub API authentication was unavailable. In the Lane 5 session, WolflordR confirmed invitation acceptance, a branch push succeeded, and the existing Git credential authenticated the GitHub API as `WolflordR`. This does not verify other collaborators' invitation states.

## COACH-01 preparation — pending integration review

FACT: Lane 5 prepared commit `dcc280f` on `agent/session-analysis`, following claim commit `8123599`, and published [draft PR #1](https://github.com/crasni/leCoach/pull/1) for integration-owner review. [checks/coaching/README.md](../checks/coaching/README.md) documents nine hand-authored synthetic cases covering ten expected completed sessions. Fixtures include weak-to-improved delivery, missing camera, no usable inputs, empty/startup sessions, late finals and duplicate retries, drain timeout, repeated sessions, and adjacent incidents. Example feedback uses the existing v0 document shapes; positive reason codes remain pending LIVE-01. No real rehearsal data or model output is included.

Validation on the local macOS development host with Python 3.14.5:

```sh
python3 checks/coaching/check_cases.py
python3 -m unittest discover -s checks/coaching -p 'test_*.py' -v
```

Observed result: all 9 cases / 10 expected sessions are internally consistent; all 18 acceptance-utility tests pass. Negative checks reject dropped finals during drain, duplicate retained finals, post-completion callbacks, mixed-session logs, dangling/duplicate feedback evidence, invented moments, missing limitations, and added engagement scores. Output checks accept different feedback wording. These results verify synthetic artifacts and the check utility, not a production recorder, feedback generator, live audience engine, or inference pipeline. The checks use no network, devices, models, or persistent rehearsal storage; temporary synthetic output is cleaned up by the tests.

IMPACT: Lane 5 can use these cases to check actual `CompletedSession` and `Feedback` outputs after dependency handoff. COACH-01 remains blocked on INT-01's scaffold, executable contract/lifecycle and layout handoff, plus LIVE-01's transition/reason evidence. No production logger, additional engagement engine, or new shared contract was created. The preparation claim and artifacts still require integration-owner review; COACH-01 is not complete.

PROPOSAL: The integration owner reviews the claim and fixture placement, supplies the approved application layout and replay seam, and coordinates Lane 4's reason vocabulary/positive evidence. Lane 5 then implements the recorder, moment selector and template feedback in that layout, runs the cases against real consumer outputs, and records integration evidence before marking COACH-01 done.

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
