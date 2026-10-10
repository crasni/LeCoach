# LeCoach implementation status

Last updated: 2026-10-10 (Asia/Taipei).

This file preserves dated implementation evidence. [GitHub Issues](https://github.com/crasni/LeCoach/issues?q=is%3Aissue+label%3Acoordination) alone own current assignments, branches, progress, blockers, remaining work and acceptance; product scope lives in [GUIDE.md](../GUIDE.md).

**Historical-record rule:** older sections retain the facts/proposals as recorded at their host/date/commit, including then-current task states, pending PRs, access limitations and the former per-push approval policy. They are not current instructions. Later merges and maintainer acceptance may supersede them. Read the Issue/actual remote code and [current AGENTS workflow](../AGENTS.md) before work; do not restart a component or delete a branch because an old proposal suggested it.

## Accepted scaffold archive — 2026-10-09

Archived INT-01 to `openspec/changes/archive/2026-10-09-int-01-local-integration-scaffold`.
Synced four capability specs (22 requirements) into `openspec/specs/`: event
contracts, local transport, session lifecycle and synthetic replay. Requirement
bodies are unchanged; relative references follow their new locations. Preserved
all 20 completed tasks, original authorship/evidence and the prior maintainer
acceptance/peer-review waiver. No runtime, event schema or live acceptance changes.

Strict spec/remaining-change validation and local archive/spec/reference targets
pass. This documentation archive does not claim new device, model or browser runs.

## English restoration — 2026-10-09

The maintainer canceled Mandarin/zh-TW preparation. English product, speech
analysis, UI/coaching and rehearsal guidance are restored. The unaccepted Mandarin
OpenSpec delta, authored fixtures/copy and six dedicated checks were removed;
commit `4580eee` preserves their history. Runtime source, v0 contracts and existing
assignments are unchanged. Stage I CPU validation, confirmed-host rehearsal setup
and eventual Stage II accelerator validation remain required.

Checks on Linux/CPython 3.12.14: 130 tests / 69 subtests; Ruff, unchanged-schema
parity, nine synthetic fixture cases / ten sessions, both retained strict OpenSpec
validations and whitespace pass. No microphone/camera, model inference, final
recording or accelerator validation was performed in this restoration.

## Historical Mandarin preparation — canceled 2026-10-09

This direction was subsequently canceled by the maintainer. The following is
historical evidence for commit `4580eee`, not current guidance. At that checkpoint:
Mandarin rehearsal, native Taiwan Traditional Chinese product content and local
CPU Stage I validation. No UGen300 before qualification; actual accelerator
compatibility/performance is retained as later Stage II validation. Lucas is the
likely operator; the actual computer/recording arrangement remains unconfirmed.
Current Issues were updated without reassigning owners or accepting unmet gates.

Reconciled GUIDE/ARCHITECTURE/runtime/demo/host/hardware/submission guidance and
the existing INT-03 planning artifacts. Added the `mandarin-first-stage1` proposal,
design, two capability deltas and task breakdown for affected-owner agreement.
No v0 schema, producer, engine, frontend or coaching-template behavior changed.
Speech's English-only model/tokenizer and current English product copy remain
implementation gaps in their owning lanes; this preparation does not localize
the application or establish Mandarin speech support.

Added five authored synthetic Mandarin fixture cases and native zh-TW handoff
copy in `checks/integration/mandarin/`. Six conformance tests exercise the existing
sole engine/controller/recorder: facing deterioration/recovery, Taiwan vocabulary
and mixed-script content, missing camera, a known active pause, short observations
and repeated-session isolation. WPM/filler fields stay null; computed reasons
cite only supported synthetic facing/pause observations. Recorder-only composition
does not present authored sample advice as computed coaching. Copy review covers
all requested surfaces, but actual localized browser fonts/wrapping and native
coaching templates remain owner acceptance work.

Linux x86_64, CPython 3.12.14:

```sh
.venv/bin/python -m pytest -q
.venv/bin/ruff check src scripts tests examples
.venv/bin/python scripts/export_schema.py --check
.venv/bin/python scripts/validate_fixtures.py
openspec validate mandarin-first-stage1 --strict
openspec validate int-03-submission-and-hardware-evidence --strict
git diff --check
```

Result: **136 tests / 69 subtests**, including six new Mandarin conformance tests.
Lint, unchanged-schema parity, historical English fixtures and both strict
OpenSpec checks pass. Local file-target checks pass for reviewed guidance/new
artifacts. Synthetic data only; no microphones, cameras, weights, model inference,
recording, localized browser E2E or accelerator execution. Existing proposal/PDF
and narration drafts were preserved, not re-exported or accepted as final footage.

Official rules were re-fetched directly and their JSON-LD content inspected after
browser extraction failed. Sections V/VI retain ordinary Stage I hosts, English
deck and mainly English video explanation. CONTEST/SOURCES record response hash,
provenance and the Mandarin-product/English-explanation recommendation; exact form
cutoff and final recording/submission checks remain pending.

## Optional runtime setup and independent component review — 2026-10-09

Linux x86_64, CPython 3.12.14. Added integration-owned optional `speech` and
`vision` dependency groups; all pre-existing core/dev lockfile versions are
preserved. `uv sync --frozen --group speech --group vision` installs the runtimes;
`uv sync --frozen --dry-run` confirms default setup excludes the 32 optional
packages. Selected one OpenCV provider (`opencv-contrib-python`) because
MediaPipe requires it and OpenCV wheel variants share `cv2`.

Resolved/runtime imports: faster-whisper 1.2.1, sounddevice 0.5.6, numpy 2.5.3,
MediaPipe 0.10.35 and OpenCV contrib 4.14.0.94. Whisper imports, bundled VAD factory
imports, MediaPipe Tasks Pose APIs and in-memory JPEG encoding pass. Sounddevice
cannot import on this host because the PortAudio system library is absent;
`docs/LOCAL_RUNTIME.md` documents `libportaudio2` and host setup. No devices were
opened and no weights were downloaded or loaded.

Independent detached-checkout reviews against the existing core/dev environment:

| Revision | Check | Result |
| --- | --- | --- |
| Speech PR #26 `4c184c9` | `PYTHONPATH=src <project-venv>/bin/python -m pytest -q` | 161 tests / 286 subtests |
| Coaching PR #24 `9850ae0` | Same command in its checkout | 148 tests / 106 subtests |
| Speech PR #26 | `checks/speech/check_speech.py`; standalone unittest discovery | 10 cases / 11 sessions; 37 tests |
| Coaching PR #24 | `checks/coaching/feedback_replay.py`; `record_replay.py` | Each: 9 cases / 10 sessions |
| Integration dependency increment | `.venv/bin/python -m pytest -q` | 130 tests / 69 subtests |

The independent PR suites passed with the existing Starlette/httpx deprecation
warning. Async/loopback runs required execution outside the restricted sandbox.
Integration lint, schema parity, fixture validation, both existing strict
OpenSpec validations and whitespace checks pass. Approval was recorded for each
submitted component scope; no feature PR was merged. These are synthetic checks,
not browser E2E, actual speech/vision inference, intended-host performance or
UGen300 evidence. Existing authored default feedback and application composition
were not changed. Current decisions, remaining review and acceptance stay in
Issues #6/#11/#15/#16/#18/#20/#21.

## Coordination migration audit — 2026-10-08

FACT: Audited GitHub branches, complete Issue/PR lists, existing contracts and owner evidence. Main `558f56f` includes PRs #4 (accepted scaffold), #3/#1 (synthetic preparation), #5 (injected recorder), #7 (engine/rehearsal UI), and #8 (submission/evidence package). No open PR existed at audit start. Isolated integration checkout preserved local documentation record `bfef7c9` and merged current main without modifying the user's reference checkout.

FACT: Audio `cea23e2` has four unmerged commits containing the model-free core and adapter lifecycle; actual source/VAD/transcriber/model work is not established. Its owner-reported tests were inspected, not rerun. Avatar `6f276eb` and coaching `5991048` are fully contained in main; their role refs remain intact. Vision has no remote role ref at inspection; local/offline work is unknown. Revert `7d760b2` has one unmerged rollback commit and is preserved for owner/maintainer disposition.

FACT: Migrated existing assignments and task acceptance into GitHub Issues with one assignee, explicit branch/status, done-versus-remaining work, exact handoffs and verified native blocker relationships. Existing speech decision #6 and its original proposal were preserved. No shared behavior/configuration decision, new lane assignment, implementation restart or feature/revert merge was made.

IMPACT: File task boards/role prompts no longer duplicate live Issue fields. OpenSpec remains the agreed behavior/interface workflow. Maintainer authorized scoped autonomous publication to assigned role branches; main pushes, destructive ref operations, merges, private-data publication and external competition delivery are outside that scope. This audit is not new live/model/target validation.

Validation of the documentation migration on Linux/Python 3.12.14: `PYTHONPATH=src <reference-checkout>/.venv/bin/python -m pytest -q` passes 130 tests and 69 subtests with the existing Starlette/httpx deprecation warning. Both existing OpenSpec changes validate strictly; all 149 local Markdown targets/anchors resolve; Git whitespace checks pass. Read-back verification confirms 14 Issue records, their assignees/branches/status/acceptance and 19 native dependency relationships; the graph is acyclic. Application source, fixtures, dependencies, generated contracts and submission binary artifacts are unchanged.


## COACH-01 computed coaching — synthetic validation

FACT: On 2026-10-08, @WolflordR pulled the role branch safely and fast-forwarded
`agent/session-analysis` from `main` at `558f56f` before implementation; then
reconciled documentation-only migration `57aab92` before committing.
Read-only GitHub inspection confirmed recorder PR #5 merged and issue #20 assigned
to this owner. The merged LIVE-01 engine supplies usable reason codes now; final
handoff acceptance in [issue #18](https://github.com/crasni/LeCoach/issues/18) and
the referenced revert disposition remain pending.

FACT: Implemented `TemplateFeedbackGenerator`, deterministic selection and plain
templates in [the coaching module](../src/lecoach/coaching/README.md), consuming
only canonical completed events and the existing engine's explicit reason
citations. The optional `replay_with_coaching()` factory supplies the sole engine,
accepted recorder and generator through existing component injection; it rejects
live requests. Shared contracts, root configuration, default app/CLI composition,
frontend and other lanes' implementations are unchanged.

FACT: Added a separate hand-derived computed baseline and
[`feedback_replay.py`](../checks/coaching/feedback_replay.py), retaining historical
authored fixtures. In `weak_to_improved`, computed audience transitions are at
0/20/30/35/40 seconds; direct-evidence feedback anchors are 10 seconds (pace),
25 seconds (approximate facing), and 40 seconds (strength). The strength uses the
engine-cited `vision-35`, not the uncited same-time `vision-40`. Repeated negative
causes merge; missing/unknown/stale evidence is omitted with limitations, without
filling quotas. The generator writes no files and retains no session state.

Validation host: local macOS arm64, existing pinned CPython 3.12.14 environment
and unchanged frozen dependency lockfile. Commands were run with `.venv/bin/python`
and `.venv/bin/ruff`; equivalent project commands:

```sh
uv run pytest -q
uv run python checks/coaching/feedback_replay.py
uv run python checks/coaching/record_replay.py
uv run python scripts/validate_fixtures.py
uv run python scripts/export_schema.py --check
uv run ruff check src scripts tests examples checks/coaching/feedback_replay.py
git diff --check
```

Observed result: 148 tests and 106 subtests pass, including 18 new feedback/API
tests and 37 subtests, with the existing Starlette/httpx deprecation warning.
Computed engine/recorder/generator replay and recorder-only replay each pass all
9 synthetic cases / 10 sessions. Fixture validation, schema parity, lint and
whitespace checks pass. Checks cover direct reason templates, historical versus
stale citations, future/wrong-source/missing evidence, absent person/pose/null
metrics, outages, deduplication, quotas, custom shared freshness configuration,
drain limitations, deterministic repeats, session isolation, and existing API
transport with the factory injected. No browser E2E, live camera/microphone,
inference model or UGen300 measurement was exercised.

IMPACT: Issue #20's selector/template work can now be reviewed independently of
live adapters. Default UI feedback is still authored; computed feedback is
available only with the documented optional factory. This does not complete
COACH-01 or close issue #20. The original PR #5 validation below remains historical
and attributed, with its publication status corrected to merged.

Publication-policy follow-up: @WolflordR supplied the migrated working agreement
after local implementation commit `50fb3cb`, adopting scoped autonomous assigned-
role-branch publication for this session. This supersedes the earlier wait for
per-push approval. The current publication/PR and review state belongs in issue #20.

PROPOSAL: Submit the validated increment through the assigned role branch and a
scoped PR referencing issue #20 without closing it.
Lane 1 reviews the optional composition and consumer baseline; Lane 4 confirms
the evidence handoff and renders the canonical feedback. Resolve issue #18's
pending decision and validate integrated behavior before final task acceptance.


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

## INT-03 publication and cleanup review

FACT: On 2026-10-08, the user approved checking and publishing the previously proposed eight-commit range `c88386a..b9e4cff` to `git@github.com:crasni/LeCoach.git`, branch `agent/integration`. The range and clean checkout were verified unchanged. Final checks pass: 130 tests / 69 subtests (0.82 s), four Node 24/Chromium browser checks (24.6 s), frontend build/types, core lint/schema parity, nine fixture cases / ten sessions and actual recorder injection. Both OpenSpec changes validate strictly; 138 local links/anchors, source/PDF parity, six reference annotations, recorded hashes and Git whitespace/private-data checks pass.

FACT: Pushed exactly `b9e4cff721bfb85831c85dd4e4aeda95ff0630a1` to `origin/agent/integration` and verified the remote tip. Main remains `c88386a83a39fb08019789d1b6350cbacf7d741d`. Created [draft PR #8](https://github.com/crasni/LeCoach/pull/8); it contains the approved eight commits, targets main, and is mergeable. No hosted status checks are reported; the evidence above is local. Another collaborator's review and merge are pending; no merge or named review request occurred.

FACT: `git fetch --prune origin` refreshed tracking refs. Only `main` and `agent/integration` remain as local branches; the three detached review worktrees were preserved. Remote cleanup audit found:

| Remote branch / inspected tip | Evidence / disposition |
| --- | --- |
| `agent/avatar-ui` at `6f276eb6fb83926b69a07e6e7eea4b538b8c912d` | Fully reachable from main, zero unmerged commits; proposed stale-ref deletion with an exact-tip lease. |
| `agent/session-analysis` at `5991048283b5e55af0a3de88fb66f89372bd03d3` | Fully reachable from main, zero unmerged commits; proposed stale-ref deletion with an exact-tip lease. |
| `agent/audio-streaming` at `cea23e2ee906d4443a28102891c93acd73b54ba8` | Four commits outside main, including new speech adapter work; preserved. |
| `revert-7-agent/avatar-ui` at `7d760b27ec1bff0e8e058ceedd29d5c92a0b4b45` | One unmerged revert commit; preserved. |

IMPACT: INT-03's publication/handoff task 6.3 is complete; implementation remains in progress with registration/form, script, live evidence, final recording and external delivery gates open. This publication/task-board record was prepared after the initial push; its publication needs separate approval. The exact remote cleanup candidates likewise need ref-specific approval under AGENTS.md before deletion; the initial approved range did not list those remote refs.

PROPOSAL: Approve publishing the follow-up record and deleting only the two inspected, fully merged refs. Verify expected tips immediately before deletion and abort if they changed. Keep PR #8 for collaborator review and preserve all unmerged work and private local artifacts.

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

## COACH-01 recorder continuation — merged PR #5

Current publication: [PR #5](https://github.com/crasni/LeCoach/pull/5), head
`5991048`, was reviewed and merged on 2026-10-08. Recorder-only acceptance does
not complete COACH-01; [issue #20](https://github.com/crasni/LeCoach/issues/20)
tracks the remaining selection/template-feedback work. The dated macOS evidence
below remains attributed to the original contributor run.

The review supplied by the maintainer reports Linux / pinned CPython 3.12.14
validation of the unchanged `5991048` head: 110 tests and 46 subtests pass,
recorder replay matches 9 synthetic cases / 10 sessions, and fixture/schema/lint
and whitespace checks pass, with the existing Starlette/httpx warning. This is
reviewer-attributed evidence, not a new owner run or live-device validation.

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

PROPOSAL: Preserve the accepted recorder and implement the remaining moment
selection/template feedback against the merged LIVE-01 reasons, with final
handoff acceptance still pending. No new shared interface or second engagement
engine was introduced by PR #5. New work follows the user's current approval
requirements; the original recorder continuation has already been published
and merged.

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

FACT: Migrated the separate INT-01 plan into [int-01-local-integration-scaffold](../openspec/changes/archive/2026-10-09-int-01-local-integration-scaffold/proposal.md), with proposal, design, four capability delta specs, and an evidence-backed task checklist. `openspec status` reports 4/4 planning artifacts complete; strict validation passes with no issues, and `openspec doctor --json` reports a healthy root. The old plan is a compatibility pointer. Application code and contracts were not changed or retested during this documentation migration.

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

## AUD-01 first microphone rehearsal — 2026-10-10

FACT: The owner ran the guided probe once with a real microphone on a Windows 11 laptop: build 26200, Intel Core i7-13620H with 16 logical CPUs, and 16 GB RAM. Inference ran on the CPU only; the laptop's GPU was not used.
- **Revision:** `agent/integration` at `b415994`, with PR #23's `speech` group on uv-managed CPython 3.12.14. Its speech package equals main `5d2bcd0`.
- **Model and configuration:** the #6 defaults, with `base.en` int8.
- **Input:** the Windows default input, a wireless headset microphone. It opened at 16 kHz with no resampling, and reported 0 overflows.
- **Commands:**

  ```powershell
  uv run --frozen --group speech python -m lecoach.speech.probe --out sessions\speech-probe.json
  uv run --frozen --group speech python checks\speech\check_speech.py --stream sessions\speech-probe.json --summary
  ```

FACT: Results of the 71.4 s take:
- **Checks:** `check_speech.py --stream` passes. No speech status was reported, and no window was null or unavailable.
- **Events:** 12 finals, 116 finalized words, 0 fillers, and 4 completed pauses. The silence produced an active pause that reached 13.7 s.
- **WPM:** windows read 114–132 WPM at normal reading pace, and reached 192 WPM over the fast reading.
- **Timing:**
  - model load and warm-up took 1.81 s; this was not the first run, so model files were not loaded cold;
  - session start took 0.23 s;
  - stop and drain took 0.95 s, with no incomplete sources;
  - finals arrived 1.77 s median, 2.73 s p95, and 3.22 s max after their speech ended;
  - windows arrived 0.26 s median, 2.15 s p95, and 3.23 s max after their end.
- **Recognition:** the scripted passage was mostly correct, with errors such as "built" heard as "feels" and "pauses" as "pulse".
- **Fillers:** the deliberate-filler part has no "um", "uh", "like", or "you know" in its finals. Its only interjection is "Aww.", which the English filler rules do not count.

FACT: On the same laptop, `python -m lecoach.speech.probe --device nosuchmic` reported `unavailable / microphone_not_found` 0.1 s into the session. Later windows reported `unavailable` with null WPM and fillers until the run was stopped with Ctrl+C.

IMPACT: AUD-01's live capture works on an ordinary Windows laptop with local CPU inference, and its events pass the shared checks.
- Filler counts from `base.en` are undercounts: the deliberate-filler part reported none.
- Final delays reached 3.2 s, about the 3 s coverage wait, although no window went null.
- The speaker started late in two parts. The stop-while-speaking case covered only about 1 s of speech, so the drain figure is not a worst case.
- This is one take by one speaker with a headset microphone. It is not a recognition-quality or latency benchmark, nor demo-host evidence.

PROPOSAL: AUD-02 (#14) measures and improves filler recall, retakes the stop-while-speaking case, and repeats the probe on the demo host. [Issue #13](https://github.com/crasni/LeCoach/issues/13) and [Issue #14](https://github.com/crasni/LeCoach/issues/14) track the remaining work.

## AUD-01 production speech seams — 2026-10-09

FACT: On `agent/audio-streaming`, based on main `91f6e63`, Lane 2 added the production speech seams in [`src/lecoach/speech/`](../src/lecoach/speech/README.md):

- `PortAudioSource` and `WavFileSource`;
- streaming Silero voice activity detection (`SileroSegmenter`, `SpeechGate`);
- a process-wide faster-whisper `WhisperTranscriber` with `warm_up`;
- `python -m lecoach.speech.model --download / --check`;
- `build_local_adapter()` and the guided `python -m lecoach.speech.probe`.

Optional packages load lazily; the core install and suite are unchanged.

Validation, core environment: `uv run pytest -q` passes 202 tests with 12 skipped (speech runtime and optional vision tests) and 342 subtests; ruff and the speech checks pass.

Validation, speech environment: PR #23's `speech` group in a scratch environment, with `libportaudio2` 19.6.0, espeak-ng 1.51, and `base.en` int8, on Linux with 4 CPUs and no audio device. Every speech test passes, including:
- Silero streaming equal to whole-file probabilities;
- silence giving an empty final;
- synthesized English transcribed with word times;
- a synthesized talk through the adapter and session controller that passes `check_speech.py`.

Real PortAudio without a device reports `microphone_not_found`.

FACT: The probe replayed a 27 s espeak-ng English talk in real time.
- It produced 4 accurate finals, and the checker passes: 53 words, 1 filler, and completed pauses at 2.76–5.02 s and 18.50–21.44 s.
- Finals arrived 2.5 s median and 3.4 s max after speech ended; windows arrived 0.36 s median after their end. Stop and drain took 2 ms.
- "Umm" was kept as a filler, but "uh" was dropped.
- On 2 s of silence, `base.en` produced "You" with a no-speech probability of 0.81; the transcriber now drops such segments.

IMPACT: Integration can compose live speech with `warm_up` and `build_local_adapter()` once PR #23's group is on main. These are synthetic-speech results on a container CPU, not microphone, recognition-quality, or demo-host evidence. The cold model load (14.7 s once) must happen before sessions.

PROPOSAL: Run the probe on the development computer and the demo host for #13's live acceptance and #14's measurements. Remaining work is tracked in [Issue #13](https://github.com/crasni/LeCoach/issues/13).

## AUD-01 speech adapter core — 2026-10-09

FACT: On `agent/audio-streaming` (first published at `cea23e2`, then merged with main `558f56f` and with the coordination migration `57aab92`), Lane 2 implemented task groups 1–3 of the OpenSpec change [`aud-01-live-speech-adapter`](../openspec/changes/aud-01-live-speech-adapter/tasks.md) in [`src/lecoach/speech/`](../src/lecoach/speech/README.md):

- `SpeechConfig` with the defaults proposed in [issue #6](https://github.com/crasni/LeCoach/issues/6);
- the English tokenizer and filler lexicon, kept equal to `checks/speech/speech_text.py` by a parity test;
- utterance and metrics tracking that follows the fixture rules, and v0 event emission with stable IDs;
- `SpeechAdapter` with `start` / `stop_capture` / `drain`, a voice-activity thread, a transcription thread, emission on the event loop, degraded mode, and release.

The microphone, voice activity detection, and transcriber sit behind protocols; the tests use scripted implementations. No microphone, audio, model, accelerator, or dependency was used or added.

Validation in the cloud development container (Linux). The project environment used Python 3.12.3, selected with `UV_PYTHON=/usr/bin/python3.12` because uv could not install the pinned 3.12.14; the standalone checks used Python 3.13.16.

```sh
uv run pytest -q
uv run ruff check src scripts tests examples
python3 checks/speech/check_speech.py
python3 -m unittest discover -s checks/speech -p 'test_*.py'
python3 checks/speech/make_fixtures.py --check
openspec validate aud-01-live-speech-adapter --strict
```

Observed result after merging main `57aab92`: 161 tests and 286 subtests pass, with the existing Starlette/httpx deprecation warning; 31 of the tests are new speech tests (128 tests and 254 subtests before the merge). Ruff passes. The 10 speech cases / 11 sessions match their oracles, the 37 standalone speech tests pass, the fixtures match the scenario scripts, and all three OpenSpec changes validate. `numpy`, `sounddevice`, and `faster_whisper` are not installed, and importing `lecoach.speech` loads none of them.

The new tests show:

- Replaying every fixture scenario through the production pipeline reproduces the committed metric, transcript, and status payloads. Each replayed stream passes `parse_event` and `check_speech.py`.
- Through `SessionController`, with real worker threads and scripted seams:
  - timestamps come from sample offsets on the shared clock, unaffected by transcription delay;
  - `start` returns within the startup bound without model work;
  - nothing is emitted after capture end, including for a stop time with a sub-millisecond fraction and for audio that runs ahead of the clock;
  - specific statuses with null windows follow an unavailable model, denied permission, a missing device, another microphone error, a device lost mid-utterance, queue overflow, a transcription failure, and a segmenter failure;
  - speech longer than `max_utterance_s` is split;
  - the microphone is closed exactly once on repeated stop and cancelled drain, and a slow final leaves speech in `incomplete_sources`;
  - `SessionManager` composes the adapter per session.
- Every recorded session stream passes `check_speech.py`, every emission runs on the event-loop thread, and the controller rejects none.
- Before the merge, the adapter tests passed 40 consecutive runs and 30 runs under parallel load. Removing the clock cap, the capture-end flooring, the outage-start rule, the unmeasurable-final rule, or the utterance backstop each made its targeted test fail.

FACT: Rounding capture times to the nearest millisecond can stamp an observation up to 0.5 ms after the controller's capture end, and the controller drops it. In the cut-at-stop test, a stop at 6.0006 s without capture-end flooring lost the capture-end window, so that session had no speech metrics at all. A monotonic clock gives a sub-millisecond fraction of 0.5 ms or more on about half of stops, and finals cut at stop have the same exposure. The adapter therefore floors capture times. The committed fixtures use whole milliseconds, so they could not show this.

IMPACT: The speech rules and session lifecycle are ready for the production seams, and the issue #6 outcomes become configuration edits. Any producer that rounds capture times to the nearest unit risks the same dropped capture-end observations. AUD-01 is not complete: there is no live microphone capture, voice activity detection, or transcription yet, and no latency, drain-time, filler-recall, or UGen300 evidence. Degraded mode does not recover within a session.

FACT: After merging main `558f56f`, an ad-hoc script (kept outside the repository) composed the speech adapter with scripted seams, the LIVE-01 `RuleEngine`, and the COACH-01 `InMemorySessionRecorder` through `SessionController` in live mode with a fake clock. Fast scripted speech ran from 0.5 to 25.5 s, followed by silence until stop at 40 s. In three identical runs, the audience went:

- NEUTRAL at 0 s;
- CONFUSED at 18 s (`pace_high`, citing `metrics-8.9`, `metrics-13`, `metrics-13.1`, `metrics-17.3`);
- INTERESTED at 29 s (`pace_steady`, citing `metrics-29`: 162 WPM with an `active` pause of 3.5 s);
- BORED at 32 s (`silence_prolonged`, citing `metrics-32`: active pause of 6.5 s).

The recorder completed with every event, no source was incomplete, and no emission failed.

IMPACT: The adapter's output is consumable by the merged engine and recorder. After speech stops, the 10 s trailing window's WPM falls through the comfortable band (162, 138, 114) while the window already reports an active pause. `pace_steady` therefore cites windows that are mostly silence, and the audience shows INTERESTED for 3 s before BORED.

PROPOSAL: Lane 4 decides whether `pace_steady` should require no active pause in the cited window. It bears on [Issue #6](https://github.com/crasni/LeCoach/issues/6), whose acceptance includes engine staleness/gap compatibility. Lane 2 changed no engine code.

PROPOSAL: Producers stamp capture times rounded down, never to the nearest unit; integration may add this to the producer guidance in ARCHITECTURE. Remaining AUD-01 work, blockers and handoffs are tracked in [Issue #13](https://github.com/crasni/LeCoach/issues/13), blocked by Issue #6; measurements are [Issue #14](https://github.com/crasni/LeCoach/issues/14).

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
## Integration reconciliation and failure-notice regression — 2026-10-10

With explicit maintainer authorization, `agent/integration` merged main
`e5c0838` as `42bd657` without conflicts. Existing integration setup/archive/demo
work and speech/vision contributor evidence are preserved. No feature PR was
merged and no live acceptance is implied.

Cross-component checks in `tests/test_integration_composition.py` use the merged
speech and vision adapters, sole RuleEngine and InMemorySessionRecorder with
scripted capture/model seams and a fake shared clock. They verify usable speech
with missing pose, usable vision with missing microphone, both-missing neutral
behavior, bounded completion/resource release and isolated repeated recordings.
No feedback generator is supplied; feedback correctly remains unavailable.

The first concurrent check reproduced a controller display bug: unavailable
speech windows replaced `microphone_not_found` with `observation_unavailable`.
The controller now retains a current explicit failure through degraded windows,
clears it on available observations and does not resurrect old failures after
recovery. Existing event fields, producer semantics, engine rules and timeout
defaults are unchanged. Runtime regressions cover unavailable/error reasons,
recovery and out-of-order status delivery.

Linux x86_64 / pinned CPython 3.12.14, core frozen environment:

```sh
uv run --frozen python -m pytest -q  # 195 passed, 335 subtests
uv run --frozen ruff check src scripts tests examples
openspec validate --all --strict  # 6 items passed
uv run --frozen python scripts/validate_fixtures.py  # 9 cases / 10 sessions
python3 checks/vision/make_fixture.py --check
git diff --check
```

All checks pass. The pre-fix merged baseline separately passed 191 tests / 333
subtests. Inputs are synthetic; no microphone/camera, optional model inference,
browser responsiveness, intended-host timing, accelerator or recording was
exercised. Current live acceptance and required component delivery remain in
[Issue #11](https://github.com/crasni/LeCoach/issues/11).

## Integration component agreement and status ties — 2026-10-10

Reviewed temporary combined sources: integration `8ebb5c3`, production speech
PR #28 `c84fce4`, coaching PR #24 `03028dd`, and engine/UI PR #29 `d76d373`.
No feature branch was merged. Integration agrees the existing reason vocabulary,
explicit trigger citations, public stale ages, pause hold, uninterrupted-positive
ENGAGED and post-outage observation boundaries; Lane 5's affected-consumer review
is separately recorded on PR #29. Component approvals do not accept live tasks.

The controller now lets explicit status win a metric capture-time tie in either
arrival order, with later available metrics still indicating recovery. This
matches PR #29's display semantics. Canonical replay specs clarify the already
implemented distinction: no-factory replay is authored; app/CLI replay injects
the sole engine and labels synthetic input, computed audience and authored
coaching separately. The coarse v0 provenance field and historical archive are
preserved; no new event fields or default runtime are introduced.

The pre-tie combined snapshot passed 259 tests / 387 subtests with three
weight-dependent skips. Both display environment variables were unset for the
Linux probe tests; inherited `DISPLAY=:0` / `WAYLAND_DISPLAY=wayland-0` had
stalled the unrelated OpenCV viewer check. Frontend build and generated types
pass using Node 24.11.0; Ruff, schema parity and all nine coaching cases / ten
sessions pass. With the final controller tie regression overlaid, the combined
snapshot passes 260 tests / 389 subtests with three weight-dependent skips.
Current integration alone passes 196 tests / 337 subtests;
strict validation passes all six OpenSpec items. No browser E2E, real capture,
model-weight inference, demo-host timings, recording or accelerator validation
was performed. Review/merge readiness and final acceptance remain in Issues.

## Opt-in CPU composition and authorized component delivery — 2026-10-10

The maintainer explicitly authorized merging reviewed component PRs #24, #28 and
#29. GitHub merge receipts are `5000c23`, `a9fe503` and `5d2bcd0`; their branches
were retained. Assigned `agent/integration` reconciles main `5d2bcd0` in clean merge
`8800971`, preserving existing integration fixes/setup/archive/evidence.

`lecoach serve --live` now composes the owners' public local speech/vision
factories, sole RuleEngine/InMemorySessionRecorder and TemplateFeedbackGenerator.
Coaching reads the same public rule freshness ages. Speech/model/VAD preparation
runs before serving; camera runtime imports warm in the background. Models are
local-files-only, with explicit preparation/download outside sessions. Each live
session gets fresh adapter/engine/recorder/generator state; fixture sessions keep
computed audience and authored coaching. No schema, thresholds or timeout defaults
change. Prepared-session cancellation/shutdown completes an empty lifecycle
without opening devices; this corrects a controller path that previously called
capture start in order to stop a prepared session.

Linux x86_64 / CPython 3.12.14, existing environment:

```sh
env -u DISPLAY -u WAYLAND_DISPLAY .venv/bin/python -m pytest -q
# 264 passed, 3 weight-dependent skips, 389 subtests
.venv/bin/ruff check src scripts tests examples
.venv/bin/python scripts/export_schema.py --check
.venv/bin/python scripts/validate_fixtures.py
openspec validate --all --strict  # 7 items
git diff --check
```

All checks pass. New composition tests use synthetic capture seams with the real
engine/recorder/coach: repeat sessions compute the supported 10/25/40 s moments;
both failed inputs remain NEUTRAL and return empty moments/limitations; preparation
alone and prepared-session shutdown never start capture. A real launch smoke check
of `serve --live --speech-model-dir /tmp/lecoach-no-models` reached loopback health
ready with `live_integrated: true` and shut down cleanly. No session was prepared
or started in that smoke check; no devices were acquired or weights downloaded.

Composition availability does not establish real microphone/camera inference,
quality, measured host latency/browser responsiveness, final recording, Stage II
accelerator compatibility or task acceptance. The actual demo host remains
unconfirmed; live validation and component downstream acceptance remain in #11.
PR #23 still requires collaborator review; it was not merged under the separate
three-component authorization.

## Maintainer-reported integrated live checks — 2026-10-10

FACT: The maintainer tested live mode on their Ubuntu 26.04.1 / Ryzen AI 7 450 /
approximately 30 GiB RAM computer using a Bluetooth microphone. They report
transcription, camera detection and audience reactions work; their UI screenshot
shows BORED with “A long silence” after the audience lost focus.

FACT: In response to the requested manual reliability batch, the maintainer
confirmed all checks work: coaching after stop, repeat-session transcript reset
and working inputs, camera indicator release, short/no-person handling and the
missing-microphone scenario. They also report a comfortable approximately 2:20
read-through of the 316-word preview narration.

LIMITATIONS: These are user-reported checks, not independently observed or
instrumented timings/accuracy measurements. Exact run revision/model hashes,
per-slot video timing and coaching moment text/evidence IDs were not supplied.
Advice usefulness and client experience remain areas the maintainer wants improved.
This record does not establish Stage II accelerator operation or final submission.
