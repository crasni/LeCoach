# Stage I package readiness

## Stage I CPU direction — 2026-10-09

The product, rehearsal and submission preparation remain English. The maintainer
canceled Mandarin/zh-TW work. Stage I validates local CPU behavior on the confirmed
ordinary computer; no UGen300 before qualification, with actual target validation
retained for Stage II. Lucas is likely operator, not a confirmed recording plan.

Existing proposal/PDF hashes below describe the reviewed draft; no deck export or
visual revalidation was performed in this direction update. Final claim-map and
script review still require accepted live evidence, actual-host checks and timing.
Official rules retain an English deck and mainly English video explanation.

Package evidence record, updated 2026-10-10 (Asia/Taipei). The proposal/evidence range merged through [PR #8](https://github.com/crasni/LeCoach/pull/8). Current remaining work, dependencies and task acceptance live only in [INT-03 Issue #12](https://github.com/crasni/LeCoach/issues/12); follow [AGENTS](../../AGENTS.md) for scoped publication. This document records artifact versions, checks and claim provenance, not assignments, a live status board or a submission receipt. Older check/disposition entries are dated package evidence, not acceptance of the final task. [CONTEST.md](../CONTEST.md) owns requirements; [STATUS.md](../STATUS.md) preserves observed behavior.

**Refreshed after the main pull:** the deck and claim map now reflect merged engine/rehearsal-screen and recorder work, with application source `8345c98` (main `c88386a`). [Fresh backend and browser evidence](../STATUS.md#int-03-refreshed-package-and-browser-validation) distinguishes computed reactions, injected recording and authored coaching. Live input and final recording remain pending.

## Artifact versions and dated dispositions

| Item | Version / outcome | Remaining action |
| --- | --- | --- |
| Editable English deck | [proposal.fodp](proposal.fodp), 12 slides, no appendices; SHA-256 `454ff035a8859bc5517b336239d2ad1c656246ac12edd97286d26d0c90fc4f71`. | Team content review and any revisions after live evidence lands. |
| PDF | [proposal.pdf](proposal.pdf), 12 pages; SHA-256 `74dadc3ca5665d1ec20ae0800ca182ef2a70a82bdff20ec497e29dc22ce0238e`. | Confirm accepted file format/upload limits in the actual form. |
| Demo | [DEMO.md](../DEMO.md#versioned-lane-5-preview-handoff) pairs the 2:55 shot plan with Lane 5's 316-word English preview at `03028dd` in PR #24, synthetic commands and generated-coaching evidence anchors. No final live narration, recording, measured duration or video hash exists. | Adapt the preview to accepted INT-02 evidence on the confirmed CPU host, time/review the final script and local recording. |
| Evidence baseline | Deck uses application source `8345c98`, main `c88386a`; 130 tests / 69 subtests and four browser checks pass. | Live producers and generated coaching remain pending; update claims after accepted live evidence. |
| Hardware | [Observed host outcome](../STATUS.md#int-03-apply-hardware-readiness) and [procedure](../HARDWARE.md). | No identifiable target device/runtime on this host; obtain supported setup and owner handoffs for measurements. |
| Git publication | Eight-commit range published at `b9e4cff`; [PR #8](https://github.com/crasni/LeCoach/pull/8) subsequently merged as `558f56f`. | Publication/merge evidence, not final INT-03 acceptance; new scoped role-branch work follows AGENTS. |
| YouTube | No upload or URL. | Separate publication authorization, unlisted upload and link verification after recording review. |
| Registration/submission | Team format, registration receipt, precise cutoff/timezone, upload limits and final receipt unknown. | Team/form confirmation; retain private details outside Git. |

The PDF and FODP are draft proposal deliverables. The earlier deck hashes and 97-test baseline remain recorded in history; this version reflects the merged synthetic functionality. Their existence does not pass the live-demo gate or establish that a synthetic-only submission has been accepted by the team.

## Requirement review

Verified external content remains in CONTEST/SOURCES rather than being copied here. The local deck review found English text, the required topic coverage, a repository link and references, and 12 main pages within the current verified budget. Final form details and later announcements must still be checked before delivery.

| Required topic | Deck pages | Review result |
| --- | --- | --- |
| Context/problem and intended user | 1–2 | Present; intended users are hypotheses, not a reported study. |
| Solution, tools and methods | 3–7 | Computed synthetic audience response, sole deterministic engine, existing stack/contracts and explicit failure states; live journey planned. |
| Software/hardware architecture and planning | 6–8, 11 | Implemented seams separated from planned adapters; hardware identified as an untested target. |
| Expected impact/results | 9–11 | Actual synthetic checks separated from expected value and proposed evaluation. No invented user outcomes or speedups. |
| References/repository | 12 | Six exported clickable annotations, including repository and official/pinned references. |
| Language/page budget | All | English throughout; 12 main pages, no appendix; visual/text checks passed. |

Local proposal review does not resolve section IX's original-work/licensing interpretation for the public development repository. Team clarification remains required as recorded in CONTEST. No organizer was contacted, account used, registration made, or form submitted.

## Claim-to-evidence map

Each row covers all material claims on the named page(s), including headline/body text and provenance labels. Planned statements are reviewed as plans; a vendor property is not a LeCoach measurement.

| Page / material claim | Basis | Mode and limits |
| --- | --- | --- |
| 1: product identity, private audience concept, practice-alone problem | [GUIDE](../../GUIDE.md#3-the-product) and agreed product intent. | Concept; cover labels synthetic input, computed audience and authored coaching. No measured market need. |
| 2: team-update/proposal/review users | Initial user hypothesis in this proposal; product direction in GUIDE. | Proposed users; no customer interviews or user study claimed. |
| 3: prepare/deliver/feel/review journey | GUIDE's frozen MVP and [architecture](../ARCHITECTURE.md#ownership-and-flow). | Planned live journey; current screen computes reactions from synthetic observations and displays authored coaching. |
| 4: pace/fillers/pauses, approximate facing/movement, sole rules engine and gradual reactions | [GUIDE](../../GUIDE.md#6-mvp--freeze-this-scope), canonical contracts and owner boundaries. | Sole engine/rules/smoothing tested against synthetic speech/vision observations; real capture still pending. No precise eye tracking or emotion detection claimed. |
| 5: 50-second scenario, state times and example suggestions | [fixture](../../checks/coaching/fixtures/weak_to_improved.json), [expectations](../../checks/coaching/expectations.json), reproduced headless output in STATUS. | Hand-authored synthetic input; engine computes states at 0, 20, 30, 35 and 40 s. Example advice remains authored at 10/40 s and is not generated from those decisions. Devices stay off; Lane 5 must reconcile advice evidence before final footage. |
| 6: stack, shared clock, injected adapters, audience/recorder boundaries | [ARCHITECTURE](../ARCHITECTURE.md#int-01-implementation-decisions-and-handoff), [README](../../README.md#development), current source/interfaces. | Contracts/lifecycle, engine and rehearsal screen tested. Recorder from merged PR #5 passes injection checks; default API composition does not enable it. Feedback generation and live producers still require handoffs. |
| 7: capture times, session IDs, null/unavailable states, bounded startup/drain | Architecture and [merged synthetic suite result](../STATUS.md#latest-main-reconciliation--2026-10-08). | Tested contracts/fake adapters; real device cleanup remains unmeasured. |
| 7: local processing/no cloud inference/raw recording off | [Architecture's local-data design](../ARCHITECTURE.md#ownership-and-flow) and README replay behavior. | Design intention and device-free replay; actual live privacy behavior remains unverified, as the page states. |
| 8: Hailo-10H, 8 GB LPDDR4, USB 3.1 Gen2 Type-C | [Official ASUS specifications](https://www.asus.com/motherboards-components/ai-accelerator/ugen/ugen300-usb-8g/techspec/); provenance in SOURCES. | Vendor properties, not measured host power/throughput. |
| 8: Whisper and pose candidates, window/USB/concurrency limitations | [Pinned candidate sources](../SOURCES.md#candidate-adapter-paths--untested), re-fetched during apply. | Untested adapter plan; no model/HEF installed or run. |
| 8: no identifiable UGen300 on development host | [Read-only host inspection](../STATUS.md#int-03-apply-hardware-readiness). | One Linux host observation; does not establish hardware access elsewhere. |
| 9: 130 tests, 69 subtests, nine fixture cases/ten sessions, UI checks | Exact backend commands/results in [STATUS](../STATUS.md#latest-main-reconciliation--2026-10-08), application source `8345c98`; [browser checks](../STATUS.md#int-03-refreshed-package-and-browser-validation). | Synthetic fixtures/fake adapters, Linux x86_64/Python 3.12.14; no live accuracy, latency or accelerator measurements. |
| 10: intuitive reactions, actionable practice loop, workplace pilot | Intended value in GUIDE; proposed pilot/evaluation in this deck. | Hypotheses and future evaluation, with no claimed study, ROI, adoption or accuracy benefit. |
| 11: implementation milestones and separate Stage I/II hardware requirements | [INT-03 Issue](https://github.com/crasni/LeCoach/issues/12) for current task state and STATUS for dated evidence; [official rules](https://contest.bhuntr.com/tw/39jg9vimiynrhlksze/home/), recorded in CONTEST. | Synthetic baseline observed; live loop and target measurements pending. Host validation is allowed in Stage I; it does not complete live P0. |
| 12: source/repository access and pending delivery | [Repository](https://github.com/crasni/LeCoach), SOURCES, this readiness record. | Reference links checked in the exported PDF; no submitted package or video exists. |

## Export and visual review

Authoring source is Flat OpenDocument, editable in LibreOffice Impress. All graphics are native text/shapes, with no borrowed imagery or external font/image dependency introduced into the app. Renderer observed: **LibreOffice 26.2.6.3 620(Build:3)** on this host.

Re-export from the repository root:

```sh
libreoffice -env:UserInstallation=file:///tmp/lecoach-int03-refresh-lo \
  --headless --convert-to pdf --outdir docs/submission \
  docs/submission/proposal.fodp
pdfinfo docs/submission/proposal.pdf
pdfinfo -url docs/submission/proposal.pdf
pdftotext -raw docs/submission/proposal.pdf /tmp/lecoach-int03-deck-raw.txt
pdftoppm -scale-to 1400 -png docs/submission/proposal.pdf /tmp/lecoach-int03-slide
sha256sum docs/submission/proposal.fodp docs/submission/proposal.pdf
```

Use an isolated temporary profile; a restricted agent sandbox may need permitted local execution for LibreOffice startup. Export metadata includes creation time, so a later export may have a different byte hash; update this record after checking the new source/PDF pair. The exact command above was exercised, with `GSETTINGS_BACKEND=memory` for local execution. No upload occurred.

All 12 refreshed pages were visually reviewed on 2026-10-08 after updating computed transition times, implemented engine/recorder labels, test counts and milestones. The architecture diagram retains event fan-out to engine and recorder; audience output goes from the engine to UI. Final text is legible with no observed clipping/overlap. Raw PDF extraction preserves text-object order; layout extraction interleaves column text and is not a valid whole-paragraph comparison. Every source paragraph is checked against its corresponding raw-extracted page. PDF annotations retain the six intended URLs.

## Capability review and pending scenarios

This is a review of delivered records, not proof that every conditional run or external action occurred. Spec scenario groups below are either supported by observed local evidence, covered by the procedure, or explicitly pending.

Local package review for the refreshed draft passed: 106 local Markdown targets/anchors resolve; all 12 source/PDF pages match; recorded artifact hashes and six exported reference links match. Both INT-03 and INT-01 pass strict OpenSpec validation, and Git whitespace checks pass. Each scenario below retains observed evidence or its explicit pending gate. No final video exists to compare; its version review remains pending with the recording gate.

| Capability / scenario group | Result and evidence |
| --- | --- |
| Submission: rules refreshed / source unavailable | Direct rules retrieval rechecked 2026-10-08; inspected rules-description hash unchanged in SOURCES. Browser extractor failed and was not treated as verification. Rendered announcements page inspected with none shown; final form/team details and a pre-delivery rules recheck remain pending. |
| Submission: proposal review | Source/PDF, required topic/page/language checks and visual review passed. |
| Submission: synthetic example / live replacement | Synthetic input/authored coaching and computed engine output are separately labeled, with exact replay times. Replacement with accepted INT-02 evidence is pending. |
| Submission: demonstration ready / live unavailable | Live-unavailable gate exposed in DEMO/readiness; final script and recording review pending. |
| Submission: local readiness with external dependencies | Registration, cutoff, form, originality interpretation, live/video and external receipt gates remain explicit. |
| Submission: local-only authorization / authorized delivery | Initial preparation stayed local; the separately approved Git range is now published in PR #8. Authorized video/submission and receipt scenarios remain pending. |
| Submission: commit contains no private rehearsal artifacts | Ignore patterns and staged files checked; the staged diff contains only sanitized documents, OpenSpec artifacts and the authored deck, with no private recordings, receipts, credentials or model weights. |
| Hardware: synthetic validation / CPU rehearsal | Synthetic validation observed; live CPU rehearsal pending. |
| Hardware: target absent / target prerequisites fail | No identifiable UGen300/CLI/module on inspected host; absent outcome recorded. An actual present-device failure is not exercised. |
| Hardware: candidate documented | Five pinned sources re-fetched; USB/runtime/model compatibility remains untested. |
| Hardware: windowed benchmark / producer-only timing | Timing endpoints and unmeasured-phase reporting documented in HARDWARE; no real benchmark or producer delay collected. |
| Hardware: concurrent rehearsal / isolated model | Both actual run scenarios pending; no integrated or isolated target-inference claim. |
| Hardware: missing adapter / private run retained | Adapter/INT-02 dependency explicit; local data rules and storage procedure checked, without creating a private measured run. |

## Resume audit — 2026-10-08

Authenticated GitHub identity `crasni` matches Issue #12's existing owner and `agent/integration` branch. The clean checkout fast-forwarded from `bfef7c9` to `63cff49`; the earlier publication record is preserved in ancestry. PR #8 is merged as `558f56f`, and the fetched main workflow is incorporated. No application, event-contract, dependency or deck change occurred in this audit.

Issue #12's full body/comments and native dependencies were inspected alongside PR #8's review. The native blockers are #11 and #21; their exact evidence handoffs are recorded in the Issue. [DEMO's handoff format](../DEMO.md#evidence-handoff-format) supports incoming evidence review without taking the script owner's work. The historical 130-test/69-subtest and four-browser-check results remain dated observations; this resume does not claim a new live or target run.

Fresh package-only checks pass: both recorded artifact SHA-256 values match; `pdfinfo` confirms 12 pages; all 245 FODP paragraphs match their corresponding pages extracted with `pdftotext -raw`; all 31 local file/anchor references in DEMO and this record resolve; `openspec validate int-03-submission-and-hardware-evidence --strict` and `git diff --check` pass. The source/PDF pair is unchanged, so the earlier visual review remains historical rather than a claimed fresh visual inspection. No backend/browser suite was rerun for this documentation increment.

## Live task follow-up

Remaining decisions, owner handoffs, final review/recording, authorization and delivery acceptance are maintained exclusively in [INT-03 Issue #12](https://github.com/crasni/LeCoach/issues/12). Read that Issue and its native dependencies rather than maintaining a parallel checklist here. The artifact checks and unresolved scenario dispositions above are historical package evidence, not a submission receipt or a live task board. INT-01 archival is a separate Issue/workflow.


## Lane 5 preview reconciliation — 2026-10-10

Reviewed Lane 5 PR #24 at `03028dd` in an isolated source snapshot. Both `feedback_replay.py` and `record_replay.py` pass all nine synthetic cases / ten sessions. Generated improvement/strength anchors match the narration at 10/25/40 s; recount gives 316 words in six blocks. [DEMO](../DEMO.md#versioned-lane-5-preview-handoff) now pairs this version with the shot plan, exact PR-scoped commands, terminal/browser provenance and CPU/Stage II captions. All 31 local file targets in DEMO/readiness resolve; strict all-spec OpenSpec validation and whitespace pass. No deck/PDF regeneration or recording was performed.

This completes independent preview reconciliation only. INT-03 task 5.1 remains unchecked under the current maintainer refinement until the final script/screens agree with accepted actual CPU evidence and measured timing. Existing live, final recording, form/team and external-delivery gates remain open in Issue #12.


## Opt-in composition implementation — 2026-10-10

The authorized component PRs #24/#28/#29 are merged. Integration now provides
`lecoach serve --live`, using the existing public speech/vision factories and
sole engine/recorder/template coach. [Host setup](../DEMO_HOST.md) documents
model preparation, launch and missing-input behavior. Default replay retains
computed audience and authored coaching. Composition implementation and synthetic
generated-feedback checks do not replace actual-host live evidence, measured
narration/edit timing, reviewed recording or external submission gates in #12.
The deck/PDF and their recorded hashes remain unchanged.

## Package verification after integration delivery — 2026-10-10

PR #23 is merged as `fae1553`; speech follow-up PR #31 as `b419a61`. This is
implementation delivery, not final integrated live acceptance. The speech
follow-up was reviewed on a current-main isolated source overlay: 41 focused
tests / 12 subtests, ten speech cases / eleven sessions, Ruff and whitespace
pass. A concurrent documentation-only update was inspected before the exact-head
merge. Owner-reported Windows capture/missing-device evidence remains scoped to
that host; filler undercount and stop-while-speaking measurements remain open.

Fresh package checks: the 12-page proposal source's 245 paragraphs match their
corresponding raw-extracted PDF pages; the recorded FODP/PDF hashes remain
`454ff035a8859bc5517b336239d2ad1c656246ac12edd97286d26d0c90fc4f71` /
`74dadc3ca5665d1ec20ae0800ca182ef2a70a82bdff20ec497e29dc22ce0238e`.
Changed setup/provenance file targets resolve, frozen lock consistency and seven
strict OpenSpec items pass. No PDF regeneration or fresh all-page visual review
was needed because the deck is unchanged.

[SOURCES](../SOURCES.md#public-rules-recheck--2026-10-10) records the unchanged
public rules content and rendered announcements/FAQ inspection. Authenticated
registration/form facts, accepted integrated CPU rehearsal, measured narration,
reviewed video and external receipts remain pending in Issue #12.
