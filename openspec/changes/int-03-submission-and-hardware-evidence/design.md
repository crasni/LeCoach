# Design

## Context

See [proposal.md](proposal.md#why) for motivation and the [submission](specs/submission-package/spec.md) and [hardware](specs/hardware-evidence/spec.md) specs for acceptance.

Observed on 2026-10-07:

- The working checkout is `agent/integration` at `b4a05db`, with six pre-existing modified documentation/OpenSpec files recording INT-01 maintainer acceptance. Preserve them. Local/fetched `main` is `ebdf421`, incorporating preparation PRs #1 and #3; these add synthetic checks and review evidence, not live adapters.
- The integration branch already contains `CONTEST.md`, `SOURCES.md`, and `DEMO.md`, but its task/status records have not incorporated the latest preparation merges. Main also has stale INT-01/INT-03 status text. Reconciliation must preserve both the local acceptance exception and contributors' preparation records.
- README and the CLI expose model-free replay and a loopback browser shell. Speech/vision packages are implementation slots. Default live composition is unavailable. The existing fixture checks do not establish latency or capture/inference behavior.
- `openspec list --specs` found no main capability specs. INT-01 remains an active change with 20 checked tasks; archiving it is a separate workflow, not a prerequisite for authoring this plan.
- The official competition page was directly retrieved and its JSON-LD rules inspected during planning. Its Stage I content agrees with the existing CONTEST record; precise cutoff/form details still need confirmation. Browser extraction failed, so it was not used as verification. Current ASUS USB-8G specifications were also inspected; they establish vendor properties only. This planning check does not update STATUS or establish hardware execution.
- `libreoffice`, `pdfinfo`, and `pdftotext` are installed; Pandoc, Marp, and system Chromium are absent from PATH. Existing Playwright setup accepts a separately supplied Chromium binary. Availability is not proof of a successful slide export.

These findings support a deliverable/evidence workflow without application changes.

## Goals / Non-Goals

**Goals:** Make the English deck reproducible from an editable local source; keep each material claim auditable; provide hardware and submission records that downstream reviewers can use despite missing devices or live handoffs.

**Non-Goals:** No runtime instrumentation/schema changes, model installation, alternate subsystem implementation, automatic publishing, or legal eligibility conclusion. This change does not resolve speech-language/timing configuration decisions by embedding fixture assumptions in the deck.

## Current maintainer refinement — 2026-10-09

No UGen300 is available before qualification. Stage I implementation and actual
live acceptance use local CPU inference on the confirmed ordinary computer;
accelerator compatibility/performance moves to the retained Stage II milestone.
Do not limit independent work to model-free preparation or treat accelerator
absence as a Stage I blocker. CPU speech/vision/UI responsiveness, failures,
release and repeated-session behavior still require actual evidence.

Product/rehearsal language is Mandarin and every client surface native zh-TW.
The previous English-only measurement/model decision is superseded. The proposed
`mandarin-first-stage1` delta and #6 coordinate measurement/script/reason changes;
this submission change does not invent them. English deck and mainly English
explanatory video narration remain compliant after the 2026-10-09 official
recheck; show Mandarin/zh-TW behavior with explanatory captions. Existing English
script/screens are historical preparation pending revision, not final acceptance.
Lucas is likely operator; confirm computer/configuration and recording arrangement
before final validation. Existing owners, branches, completed evidence and final
authorization gates remain preserved.

## Decisions

### 1. Reconcile branch history before changing shared records

On apply, inspect current status and upstream history again. Record the exact pre-existing edits and preserve them with a recoverable scoped stash or an appropriately scoped local commit before merging current main into the assigned integration branch. Restore preserved work, resolve overlapping TASKS/STATUS edits by retaining both facts, and verify that acceptance edits and contributor evidence survive. Do not reset, overwrite, rebase other collaborators' branches, or switch development to main.

The refreshed board records merged PRs as preparation and preserves incomplete live tasks. INT-03 keeps its single existing owner/branch and links this change; claim publication still follows AGENTS. Alternative: build the package from this stale checkout. Rejected because that would omit reviewed evidence and could misreport current blockers.

### 2. Keep requirements and evidence in their canonical locations

Use existing CONTEST/SOURCES for external requirements and provenance, STATUS for actual results, ARCHITECTURE for contracts, and TASKS for owners/progress. Add `docs/HARDWARE.md` for reproduction procedures and measurement definitions, linking to STATUS for outcomes. Add `docs/submission/readiness.md` for the package's artifact versions, review checklist, claim-to-source/evidence map, and pending submission gates; it is not another team board.

For each material claim, identify its slide/shot, evidence reference or official source, mode, revision/date, and limitation. The deck summarizes for judges; it does not become the authority for facts. Inspect official rules again before final review, record section/retrieval provenance in SOURCES, and keep form-specific cutoff/registration questions pending until supported by the form or team-provided evidence. No outbound organizer/team messaging is assumed authorized.

Alternative: copy all canonical facts into a large new submission spec. Rejected because later implementation and rule changes would make those copies conflict.

### 3. Use an editable local presentation source and installed PDF tooling

Create `docs/submission/proposal.fodp` as an English Flat OpenDocument presentation source and export `docs/submission/proposal.pdf` with LibreOffice. FODP is editable in Impress and inspectable in Git. Use a fresh temporary LibreOffice profile and record the actual tool version, export command, and output hash in readiness. Check page count/text with `pdfinfo`/`pdftotext` and visually inspect every rendered page for clipping, diagram readability, source links, and provenance labels. A successful CLI exit alone does not pass deck review.

Start from the 12-slide outline already proposed in CONTEST and keep within its current official main-page budget. Use native text/vector diagrams and approved assets. Label intended local processing and target architecture separately from the measured replay behavior. Do not invent customer outcomes, accuracy, hardware speedups, or business figures.

This format is a recorded authoring assumption, not a new product requirement. Confirm accepted PDF/upload formats in the submission form before final review; if necessary, export another accepted format from the same editable source and document it. Alternatives: introduce Marp/Pandoc or build a slide renderer into the app. Rejected because no installed Markdown renderer exists and deck authoring does not justify core dependency changes.

### 4. Separate readiness inspection from performance evidence

HARDWARE provides read-only host/device/runtime inspection and a run-record template, not a driver installer. Report host/OS/architecture, device/interface, runtime visibility, and model availability; reference pinned vendor candidates from SOURCES. If anything is missing, record the observed limitation and next owner/handoff action. Do not infer that the team lacks hardware elsewhere.

For a real run, collect source revision, exact setup/launch/configuration, driver/runtime/firmware, model/HEF hashes, input preprocessing/postprocessing, host/device, workload, timing endpoints, warm-up, sample count, failures, and sanitized results. Keep raw media, transcripts, logs containing rehearsal data, and model weights in ignored local storage. Use the existing canonical capture clocks and owner-provided received/decision timing; request any missing instrumentation through those owners/INT-02 rather than changing contracts here.

Timing definitions are: input-window duration; capture/window-end to producer emission; capture-to-engine decision with smoothing reported separately where observable; decision-to-browser receipt/display only when instrumented. A receipt measurement is not automatically a rendered-display measurement. Summarize comparable producer samples with count, median, p95 when justified, and range; identify dropped/unavailable observations. Record unmeasured phases explicitly.

Individual model tests can establish isolated execution. A claim about integrated accelerator responsiveness additionally requires concurrent speech/vision, audience and feedback evidence, shutdown/device release, restart isolation, and failure checks from INT-02. No new numeric latency target is invented in this change. Alternative: cite vendor FPS/TOPS as application results. Rejected because windowing, USB transport, concurrent load, and smoothing affect the experience.

### 5. Deliver useful local preparation while keeping final gates visible

Local deck/evidence preparation can finish before live or accelerator handoffs. Coordinate the DEMO shot plan with Lane 5's script/scenario; Lane 1 owns launch and claim checks. Keep recordings in ignored storage, with narration primarily English and mode/provenance visible. Document default accelerated replay when used.

| Gate | What passes it | What remains pending if absent |
| --- | --- | --- |
| Local proposal | Editable source, readable matching PDF, current requirement checks, and evidence-linked claims | Local package review |
| Live demo | INT-02 accepted run and Lane 5 scenario/script, reviewed footage | Live proof and final recording |
| Hardware status | Reproducible inspection plus measured results or explicit missing-device/runtime disposition | Accelerator execution/measurements when unavailable |
| External delivery | Approved reviewed versions, verified video link, registration/form checks, and submission receipt | Publication and submission |

The official Stage I hardware flexibility permits an honest missing-device disposition; it does not waive the team's desired live P0 milestone or establish accelerator performance. If the team later chooses a clearly labeled synthetic-only submission because live dependencies are late, record that explicit decision and its limitations; do not silently treat it as live-demo acceptance. Keep INT-03 in progress while required final deliverable/submission gates remain outstanding.

### 6. Keep publication distinct from artifact creation

Prepare and review local deliverables first. Any Git publication request must name the exact commit set and `git@github.com:crasni/LeCoach.git` / `agent/integration`, then wait for a new explicit approval. Main is updated only through the project PR/review workflow. Video upload and competition submission require their applicable explicit team authorization, separate from planning/apply or branch-publication approval. After authorized actions, verify the unlisted link and actual receipt; retain private registration/receipt data outside Git and record a sanitized confirmation.

Alternative: automatically upload after export. Rejected because a reviewable local package is needed before external actions and authorization is not supplied by this proposal.

## Risks / Trade-offs

- [Live implementations arrive late] → Complete independent preparation now; retain visible demo gates and coordinate evidence through INT-02/Lane 5.
- [No target hardware/runtime] → Publish a dated readiness limitation and sourced adapter plan; make no measured-target claim.
- [Divergent documentation loses facts] → Preserve edits before reconciliation, inspect conflicts, and retain historical validation with its original host/date rather than claiming a fresh rerun.
- [Rule/form or eligibility interpretation changes] → Recheck authoritative sources and obtain team confirmation for unresolved registration/originality terms; do not infer legal conclusions.
- [PDF export differs from source] → Record the renderer/version and inspect every page plus extracted text/page count before review.
- [Measurement endpoints are incomplete] → Label missing phases and request the owner handoff; report only measured intervals.
- [Sanitized summaries limit independent replay of private inputs] → Retain reproducible procedures/configuration and private local run artifacts, without committing rehearsal content.

## Migration Plan

No application deployment or runtime migration is required. During apply: reconcile preserved integration work; refresh canonical references/status; add hardware procedures and readiness records; author/export/review the deck; incorporate owner-provided live/hardware/demo evidence as it becomes available; prepare a scoped local commit set for review. Keep unfinished gates pending.

Rollback is a scoped revert of the new deliverables and this change's documentation edits on `agent/integration`, preserving prior acceptance records and contributor work. No remote refs, uploads, or submissions are rolled back automatically.

## Open Questions

- What exact cutoff time/timezone and upload limits does the submission form specify? The local package structure does not depend on the answer; final submission checks do.
- Which registration format did the team select, and is there a receipt? Record team-provided confirmation privately and reference only a sanitized outcome.
- Which confirmed CPU demo computer/configuration will Lucas use? UGen300
  availability is no longer an open Stage I question: target-device validation
  remains a later Stage II requirement when hardware is supplied.
- Has the team clarified the organizer's original-work terms for this development repository? Keep that final submission gate unresolved until the team provides a supported interpretation.
