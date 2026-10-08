# Tasks

These tasks implement the [proposal](proposal.md), [design](design.md), and two capability specs. All are initially unchecked: existing research is a baseline, not newly completed implementation. [TASKS.md](../../../TASKS.md) remains authoritative for ownership and overall INT-03 status.

Groups 1–4 can proceed with local artifacts and available evidence. Group 5's live recording depends on INT-02 and Lane 5. Group 6's external actions depend on separate approvals and confirmed form/registration details. Completing an unavailable-hardware disposition does not complete a measured-inference milestone. Leave unmet final gates unchecked and record their next actions.

## 1. Reconcile integration work and shared records

- [x] 1.1 Recheck status/history, preserve pre-existing edits recoverably, and incorporate current main into `agent/integration`; verify the final branch, retained INT-01 acceptance edits, and ancestry with Git status/diffs/logs, without resetting work or developing on main.
- [x] 1.2 Reconcile TASKS/STATUS with merged PRs #1 and #3, retaining contributor evidence and historical test provenance; verify that audio/coaching preparation is identified as merged while their live tasks remain incomplete and obsolete scaffold-publication blockers are corrected.
- [x] 1.3 Link this change to the existing single-owner INT-03 row and refresh the relevant internal handoff references; verify all changed local Markdown targets resolve and the claim's local/unpublished state is accurate. Keep INT-01 archiving separate.

## 2. Refresh requirements and create package readiness

- [x] 2.1 Retrieve and inspect current official rules and applicable announcements, update CONTEST/SOURCES with dated section/retrieval provenance, and record conflicts before changing assumptions; verify content inspection, source links, and retrieval hash rather than relying on HTTP success or dynamic metadata alone.
- [ ] 2.2 Inspect accessible submission-form requirements and obtain team-provided registration/cutoff/originality clarification where needed; verify supported details in canonical records and record any remaining unknown with its next action, without outbound messages or a fabricated eligibility interpretation.
- [x] 2.3 Create `docs/submission/readiness.md` with deliverable versions, requirement checks, claim references, and distinct local/live/hardware/external gates; verify that every unresolved detail from 2.2 is pending and that no upload or receipt is implied.

## 3. Produce and review the English proposal

- [x] 3.1 Draft the English slide content in `docs/submission/proposal.fodp` from CONTEST's existing outline; verify all official required topics, repository/reference links, native diagrams, identified appendices, and a clear distinction between intended value and demonstrated outcomes.
- [x] 3.2 Populate the readiness claim map for every material prototype/privacy/hardware/performance/outcome claim in the deck; verify each claim links to dated STATUS evidence, a vendor source, or an explicit plan, and that synthetic/authored results do not imply live inference or unsupported numerical benefits.
- [x] 3.3 Export `docs/submission/proposal.pdf` using LibreOffice with an isolated temporary profile and document the exact tool version, command, and artifact hash; verify successful export, matching extracted content, and page count with `pdftotext`/`pdfinfo` against the current main-page budget.
- [x] 3.4 Visually inspect every PDF page and correct clipping, diagram/text readability, provenance labels, and links; verify the source/PDF match and record the visual review outcome in readiness. Confirm or explicitly retain the final upload-format gate.

## 4. Document hardware readiness and measurement procedures

- [x] 4.1 Create `docs/HARDWARE.md` with read-only readiness commands and a sanitized run-record template linked to SOURCES/STATUS; verify coverage of host/device/interface, driver/runtime/firmware, model hashes, preprocessing/postprocessing, exact commands, timing endpoints, warm-up, workload, sample counts, and failures without changing core dependencies or contracts.
- [x] 4.2 Execute available read-only host/device/runtime inspection and record the dated results in STATUS; verify commands reproduce the inspected host's outcome and distinguish detection/runtime visibility from successful inference, with a next action for missing prerequisites.
- [x] 4.3 Review the pinned official speech/pose candidates against actual available host/interface/runtime prerequisites; verify sourced revisions and compatibility gaps in SOURCES/HARDWARE, including window duration versus delivery delay and vendor benchmark conditions versus the USB path.
- [x] 4.4 Record the target-evidence disposition: if approved adapters, device, runtime, and instrumentation are available, run isolated then concurrent validation and summarize comparable timings, failures, stop/release, and repeat-session behavior; otherwise document the missing prerequisites and deferred measurement milestone. Verify measured scope and sample provenance, with no fabricated accelerator or end-to-end result.
- [x] 4.5 Check private-data storage and the sanitized summaries; verify raw media/transcripts/session exports/credentials/weights are excluded from Git and that model-free setup/replay remains usable under README's existing commands. Record any reproduction result as synthetic, not live evidence.

## 5. Coordinate and validate the demonstration

- [ ] 5.1 Incorporate Lane 5's provided scenario/script into the existing DEMO launch and shot plan without taking its ownership; verify reproduction instructions, narration plan, capture/evidence references, and runtime target agree with CONTEST and the package's demonstrated mode.
- [ ] 5.2 Obtain INT-02's accepted live evidence and update the deck/readiness claim map to that exact run; verify host/configuration, real input, audience deterioration/recovery, supported feedback, stop/restart/resource-release, and unavailable-input results. Keep this unchecked if the handoff is missing; a team-approved synthetic-only alternative must be recorded as an explicit limited-submission decision, not live acceptance.
- [ ] 5.3 Prepare and review the final local recording using the accepted scenario/mode, keeping private footage in ignored storage; verify English narration, actual runtime, legible audience/feedback shots, mode/provenance labels, any accelerated replay disclosure, and correspondence to the claim map. Record recording/version checks in readiness, without uploading.

## 6. Final review and authorized delivery

- [ ] 6.1 Review the complete local package against both specs and current official requirements; verify each requirement/scenario has a documented result or explicit pending gate, all local references resolve, source/PDF/video versions match, OpenSpec strict validation passes, and Git whitespace checks pass. Keep INT-03 in progress while required final gates are unmet.
- [x] 6.2 Prepare scoped local commits on `agent/integration` and present the exact commit set, validation, limitations, and `git@github.com:crasni/LeCoach.git` destination for push approval; verify the staged diff excludes private data and unrelated work, then wait for explicit approval before publishing.
- [ ] 6.3 After matching approval, publish only the approved role-branch commits and prepare the scoped reviewed PR/handoff; verify remote tips and approved commits, link the PR/validation in TASKS/STATUS, and follow integration-owner review rules without a direct push to main.
- [ ] 6.4 After separate applicable team authorization and resolved registration/form gates, publish the reviewed video and submit the approved package; verify unlisted link accessibility, submitted artifact versions, cutoff compliance, and actual receipt. Retain private registration/receipt details outside Git and record only a sanitized confirmation.
- [ ] 6.5 Reconcile final INT-03 status and readiness with actual review/delivery outcomes; verify required task acceptance and external gates before marking done, preserve deferred target-device measurements explicitly, and prepare any new local status commit for its own separate push approval.

## Workflow follow-up

- Begin implementation only after a new explicit apply request; proposing this change does not authorize implementation, publication, or submission.
- Complete the existing INT-01 archive separately through its requested archive workflow; do not fold it into this change's task completion.
- Archive this change only after accepted completion, then verify the two resulting main capability specs and archive record.
- If target hardware is unavailable for Stage I, retain the documented measurement milestone for the relevant future validation work; do not convert a readiness disposition into a claimed accelerator run.
