# Stage I package readiness

Local review draft, updated 2026-10-08 (Asia/Taipei). INT-03 is **in progress**, with the claim and new deliverables unpublished. This records package checks and evidence references, not team assignments or a submission receipt. [TASKS.md](../../TASKS.md) owns progress; [CONTEST.md](../CONTEST.md) owns requirements; [STATUS.md](../STATUS.md) owns observed behavior.

**After the latest main pull:** the deck and its claim map below remain the earlier `35e99b2` evidence snapshot. Main `c88386a`, pulled in merge `8345c98`, adds the engine/rehearsal screen and recorder; [fresh checks](../STATUS.md#latest-main-reconciliation--2026-10-08) pass. Refresh the deck/claim map and repeat final package review before acceptance. Earlier export/visual checks apply to the unchanged draft, not an updated proposal. INT-03 task 6.1 is reopened.

## Artifact versions and current gates

| Item | Version / outcome | Remaining action |
| --- | --- | --- |
| Editable English deck | [proposal.fodp](proposal.fodp), 12 slides, no appendices; SHA-256 `f9d5cbaf363e80761a55ff618e5ff85a97cd390d0f2c65e4063ce7821a46cfaa`. | Team content review and any revisions after live evidence lands. |
| PDF | [proposal.pdf](proposal.pdf), 12 pages; SHA-256 `06670bd033e8710bd7bc8abc532f8d42168d347e758f7b78aecd0ab857744aa1`. | Confirm accepted file format/upload limits in the actual form. |
| Demo | [DEMO.md](../DEMO.md) is a proposed 2:55 shot plan with synthetic replay instructions. No final recording, final narration, or video hash exists. | Lane 5 script/scenario and accepted INT-02 evidence, then reviewed local recording. |
| Evidence baseline | Deck uses application source `35e99b2`, main `ebdf421`; [earlier checks](../STATUS.md#int-03-apply-local-validation). New merged source `8345c98` passes 130 tests / 69 subtests. | Refresh deck/claims for the engine and recorder; live producers and generated coaching remain pending. |
| Hardware | [Observed host outcome](../STATUS.md#int-03-apply-hardware-readiness) and [procedure](../HARDWARE.md). | No identifiable target device/runtime on this host; obtain supported setup and owner handoffs for measurements. |
| Git publication | New local work on `agent/integration`; no INT-03 push or PR yet. | Review exact local commit set, receive separate push approval, then role-branch PR/review. |
| YouTube | No upload or URL. | Separate publication authorization, unlisted upload and link verification after recording review. |
| Registration/submission | Team format, registration receipt, precise cutoff/timezone, upload limits and final receipt unknown. | Team/form confirmation; retain private details outside Git. |

The PDF and FODP are draft proposal deliverables. Their existence does not pass the live-demo gate or establish that a synthetic-only submission has been accepted by the team.

## Requirement review

Verified external content remains in CONTEST/SOURCES rather than being copied here. The local deck review found English text, the required topic coverage, a repository link and references, and 12 main pages within the current verified budget. Final form details and later announcements must still be checked before delivery.

| Required topic | Deck pages | Review result |
| --- | --- | --- |
| Context/problem and intended user | 1–2 | Present; intended users are hypotheses, not a reported study. |
| Solution, tools and methods | 3–7 | Planned audience response, sole deterministic engine, existing stack/contracts and explicit failure states. |
| Software/hardware architecture and planning | 6–8, 11 | Implemented seams separated from planned adapters; hardware identified as an untested target. |
| Expected impact/results | 9–11 | Actual synthetic checks separated from expected value and proposed evaluation. No invented user outcomes or speedups. |
| References/repository | 12 | Six exported clickable annotations, including repository and official/pinned references. |
| Language/page budget | All | English throughout; 12 main pages, no appendix; visual/text checks passed. |

Local proposal review does not resolve section IX's original-work/licensing interpretation for the public development repository. Team clarification remains required as recorded in CONTEST. No organizer was contacted, account used, registration made, or form submitted.

## Claim-to-evidence map

Each row covers all material claims on the named page(s), including headline/body text and provenance labels. Planned statements are reviewed as plans; a vendor property is not a LeCoach measurement.

| Page / material claim | Basis | Mode and limits |
| --- | --- | --- |
| 1: product identity, private audience concept, practice-alone problem | [GUIDE](../../GUIDE.md#3-the-product) and agreed product intent. | Concept; current authored replay is labeled on the cover. No measured market need. |
| 2: team-update/proposal/review users | Initial user hypothesis in this proposal; product direction in GUIDE. | Proposed users; no customer interviews or user study claimed. |
| 3: prepare/deliver/feel/review journey | GUIDE's frozen MVP and [architecture](../ARCHITECTURE.md#ownership-and-flow). | Planned live journey; current shell is synthetic playback. |
| 4: pace/fillers/pauses, approximate facing/movement, sole rules engine and gradual reactions | [GUIDE](../../GUIDE.md#6-mvp--freeze-this-scope), canonical contracts and owner boundaries. | Intended behavior; no working live engine, precise eye tracking or emotion detection claimed. |
| 5: 50-second scenario, state times and example suggestions | [fixture](../../checks/coaching/fixtures/weak_to_improved.json), [expectations](../../checks/coaching/expectations.json), reproduced headless output in STATUS. | Hand-authored synthetic input, audience and feedback. Times preserved exactly; example advice paraphrases the authored moments at 10 and 40 seconds. Devices stay off. |
| 6: stack, shared clock, injected adapters, audience/recorder boundaries | [ARCHITECTURE](../ARCHITECTURE.md#int-01-implementation-decisions-and-handoff), [README](../../README.md#development), current source/interfaces. | Contracts/lifecycle/replay/loopback shell implemented; live blocks still require handoffs. Recorder continuation PR #5 is not integrated here. |
| 7: capture times, session IDs, null/unavailable states, bounded startup/drain | Architecture and [new synthetic suite result](../STATUS.md#int-03-apply-local-validation). | Tested contracts/fake adapters; real device cleanup remains unmeasured. |
| 7: local processing/no cloud inference/raw recording off | [Architecture's local-data design](../ARCHITECTURE.md#ownership-and-flow) and README replay behavior. | Design intention and device-free replay; actual live privacy behavior remains unverified, as the page states. |
| 8: Hailo-10H, 8 GB LPDDR4, USB 3.1 Gen2 Type-C | [Official ASUS specifications](https://www.asus.com/motherboards-components/ai-accelerator/ugen/ugen300-usb-8g/techspec/); provenance in SOURCES. | Vendor properties, not measured host power/throughput. |
| 8: Whisper and pose candidates, window/USB/concurrency limitations | [Pinned candidate sources](../SOURCES.md#candidate-adapter-paths--untested), re-fetched during apply. | Untested adapter plan; no model/HEF installed or run. |
| 8: no identifiable UGen300 on development host | [Read-only host inspection](../STATUS.md#int-03-apply-hardware-readiness). | One Linux host observation; does not establish hardware access elsewhere. |
| 9: 97 tests, 37 subtests, nine fixture cases/ten sessions | Exact commands/results in [STATUS](../STATUS.md#int-03-apply-local-validation), source `35e99b2`. | Synthetic fixtures/fake adapters, Linux x86_64/Python 3.12.14; no live accuracy, latency or accelerator measurements. |
| 10: intuitive reactions, actionable practice loop, workplace pilot | Intended value in GUIDE; proposed pilot/evaluation in this deck. | Hypotheses and future evaluation, with no claimed study, ROI, adoption or accuracy benefit. |
| 11: implementation milestones and separate Stage I/II hardware requirements | TASKS/STATUS for project state; [official rules](https://contest.bhuntr.com/tw/39jg9vimiynrhlksze/home/), recorded in CONTEST. | Synthetic baseline observed; live loop and target measurements pending. Host validation is allowed in Stage I; it does not complete live P0. |
| 12: source/repository access and pending delivery | [Repository](https://github.com/crasni/LeCoach), SOURCES, this readiness record. | Reference links checked in the exported PDF; no submitted package or video exists. |

## Export and visual review

Authoring source is Flat OpenDocument, editable in LibreOffice Impress. All graphics are native text/shapes, with no borrowed imagery or external font/image dependency introduced into the app. Renderer observed: **LibreOffice 26.2.6.3 620(Build:3)** on this host.

Re-export from the repository root:

```sh
libreoffice -env:UserInstallation=file:///tmp/lecoach-int03-lo-export \
  --headless --convert-to pdf --outdir docs/submission \
  docs/submission/proposal.fodp
pdfinfo docs/submission/proposal.pdf
pdfinfo -url docs/submission/proposal.pdf
pdftotext -raw docs/submission/proposal.pdf /tmp/lecoach-int03-deck-raw.txt
pdftoppm -scale-to 1400 -png docs/submission/proposal.pdf /tmp/lecoach-int03-slide
sha256sum docs/submission/proposal.fodp docs/submission/proposal.pdf
```

Use an isolated temporary profile; a restricted agent sandbox may need permitted local execution for LibreOffice startup. Export metadata includes creation time, so a later export may have a different byte hash; update this record after checking the new source/PDF pair. The exact command above was exercised, with `GSETTINGS_BACKEND=memory` for local execution. No upload occurred.

All 12 rendered pages were visually reviewed. Review corrected title/subtitle spacing, journey-card text length, and the architecture diagram's event fan-out to engine and recorder; audience output goes from the engine to UI. Final text is legible with no observed clipping/overlap. Raw PDF extraction preserves text-object order; layout extraction interleaves column text and is not a valid whole-paragraph comparison. Every source paragraph is checked against its corresponding raw-extracted page. PDF annotations retain the six intended URLs.

## Capability review and pending scenarios

This is a review of delivered records, not proof that every conditional run or external action occurred. Spec scenario groups below are either supported by observed local evidence, covered by the procedure, or explicitly pending.

Before the latest main pull, local package review passed: 105 local Markdown targets/anchors resolve; all 12 source/PDF pages match; recorded artifact hashes and six exported reference links match. Both INT-03 and INT-01 passed OpenSpec strict validation, and Git whitespace checks passed. Final review is now reopened for updated implementation claims. No final video exists to compare; its version review remains pending with the recording gate.

| Capability / scenario group | Result and evidence |
| --- | --- |
| Submission: rules refreshed / source unavailable | Direct rules retrieval inspected and hashed in SOURCES; browser extractor failed and was not treated as verification. Final announcement/form inspection pending. |
| Submission: proposal review | Source/PDF, required topic/page/language checks and visual review passed. |
| Submission: synthetic example / live replacement | Synthetic claims match the fixture and are labeled; replacement with accepted INT-02 evidence is pending. |
| Submission: demonstration ready / live unavailable | Live-unavailable gate exposed in DEMO/readiness; final script and recording review pending. |
| Submission: local readiness with external dependencies | Registration, cutoff, form, originality interpretation, live/video and external receipt gates remain explicit. |
| Submission: local-only authorization / authorized delivery | Local artifacts prepared; authorized upload/submission and receipt scenarios remain pending. No new push was performed. |
| Submission: commit contains no private rehearsal artifacts | Ignore patterns and staged files checked; the staged diff contains only sanitized documents, OpenSpec artifacts and the authored deck, with no private recordings, receipts, credentials or model weights. |
| Hardware: synthetic validation / CPU rehearsal | Synthetic validation observed; live CPU rehearsal pending. |
| Hardware: target absent / target prerequisites fail | No identifiable UGen300/CLI/module on inspected host; absent outcome recorded. An actual present-device failure is not exercised. |
| Hardware: candidate documented | Five pinned sources re-fetched; USB/runtime/model compatibility remains untested. |
| Hardware: windowed benchmark / producer-only timing | Timing endpoints and unmeasured-phase reporting documented in HARDWARE; no real benchmark or producer delay collected. |
| Hardware: concurrent rehearsal / isolated model | Both actual run scenarios pending; no integrated or isolated target-inference claim. |
| Hardware: missing adapter / private run retained | Adapter/INT-02 dependency explicit; local data rules and storage procedure checked, without creating a private measured run. |

## Final gates and next actions

- Team: confirm registration format/status and retain its private receipt; inspect the actual form for cutoff/timezone, accepted formats and upload limits, and review unresolved original-work terms.
- Lane 5: provide/review the final English script and scenario. The checked-in preparation fixture is usable for development but is not a finished narration handoff.
- Integration / Lane 5: refresh proposal claims for merged PRs #5/#7 and reconcile computed audience times with authored coaching. Deliver and accept the live INT-02 run before claims/footage change to live processing.
- Hardware owner / integration: provide supported target setup and adapters for measured evidence, or preserve the explicit unavailable-device disposition and deferred milestone.
- Maintainer: review the local deck/records and exact role-branch commit set, then separately authorize a push if ready to share.
- Team: separately authorize final video publication and competition submission, verify unlisted access, and obtain a real receipt before claiming submission complete.

No final gate is satisfied by silence, an apply request, a local PDF, or earlier branch deletion approval. INT-01 archival remains a separate workflow.
