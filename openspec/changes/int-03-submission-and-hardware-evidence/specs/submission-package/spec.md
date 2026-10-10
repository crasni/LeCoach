# Spec Delta

## Purpose

Provide a reviewable Stage I proposal and demo package whose claims match LeCoach's demonstrated behavior and whose external submission status is explicit.

## ADDED Requirements

### Requirement: Use current authoritative requirements
The submission package SHALL reference the canonical competition requirements and source records, including retrieval date and official provenance. Unconfirmed form details and conflicts SHALL remain explicit; failed retrieval SHALL NOT be treated as verification.

#### Scenario: Requirements refreshed
- **WHEN** official rules are successfully retrieved and inspected before final package review
- **THEN** the canonical records identify the source, retrieval date, applicable requirements, and unresolved details without silently replacing conflicting project assumptions

#### Scenario: Rule source unavailable
- **WHEN** current rules cannot be inspected
- **THEN** the last verified record remains dated and final requirement verification stays pending

### Requirement: Deliver a reviewable English proposal
The package SHALL include editable English slide content and a matching PDF, covering the official required topics and repository link within the verified main-page budget. Appendix pages SHALL be identifiable. Planned value and milestones SHALL be distinguishable from demonstrated outcomes.

#### Scenario: Proposal review
- **WHEN** a reviewer opens the source and exported PDF
- **THEN** slide content matches, required topics and references are present, text and diagrams are readable, and main pages satisfy the current official budget

### Requirement: Trace material claims to evidence
The package SHALL map material prototype, privacy, hardware, performance, and outcome claims to verified implementation evidence, vendor sources, or identified plans. Synthetic authored output SHALL NOT imply live recognition, computed engagement, or generated coaching. No unsupported numeric benefit or performance claim SHALL appear.

#### Scenario: Synthetic prototype shown
- **WHEN** the package illustrates the current authored replay
- **THEN** slides and footage identify its synthetic input and authored outputs, while live analysis remains a planned milestone

#### Scenario: Live evidence replaces a draft illustration
- **WHEN** INT-02 supplies a validated live run
- **THEN** the revised claim points to that run's mode, configuration, observations, and limitations rather than relying on an earlier fixture result

### Requirement: Validate demo against its actual mode
The package SHALL pair the reviewed demo with its scenario, launch instructions, and evidence basis. The final video SHALL follow verified language, runtime guidance, and visibility requirements; replay acceleration and authored outputs SHALL be disclosed when used. Lane 5 SHALL retain ownership of the script and rehearsal scenarios.

#### Scenario: Demonstration ready for review
- **WHEN** a final recording is offered for package review
- **THEN** a reviewer can identify the demonstrated mode, reproduce the documented scenario where its dependencies are available, and verify narration, timing, labels, audience changes, and feedback against the cited evidence

#### Scenario: Live rehearsal is unavailable
- **WHEN** INT-02's live acceptance has not passed
- **THEN** local proposal preparation can proceed, any replay recording remains explicitly synthetic, and the live-demo gate remains pending

### Requirement: Expose submission readiness and remaining gates
The package SHALL include a readiness record covering deliverable versions, requirement checks, registration choice and confirmation, cutoff/form details, team review of unresolved originality/licensing terms, demo evidence, and publication/submission status. Unknown or blocked items SHALL state the required next action; local readiness SHALL NOT imply an external receipt.

#### Scenario: Local review complete with external dependencies
- **WHEN** the proposal passes local review but registration, recording, or form details are unresolved
- **THEN** the record identifies passed checks and each pending gate without claiming the package was submitted or INT-03 fully completed

### Requirement: Respect authorized publication boundaries
Each remote Git ref update SHALL use the exact commits and destination separately approved under AGENTS.md, with no direct push to main. Video publication and competition submission SHALL require applicable explicit team authorization. After authorized actions, the record SHALL distinguish upload/link verification from actual submission receipt.

#### Scenario: Only local preparation is authorized
- **WHEN** the team authorizes planning or local implementation
- **THEN** reviewable local artifacts can be prepared and no push, video upload, or competition submission occurs under that authorization alone

#### Scenario: Authorized external submission succeeds
- **WHEN** an approved package is published and submitted
- **THEN** the record identifies the submitted artifact versions, verified unlisted video link, and confirmed submission receipt, while private receipt details remain outside Git

### Requirement: Keep rehearsal data out of version control
The package SHALL include no private voice, video, transcripts, session exports, credentials, or model weights in Git. Reviewer-facing evidence SHALL use sanitized observations and explicitly approved demonstration content; private recordings and receipts SHALL remain in ignored or separately managed local storage.

#### Scenario: Package prepared for a commit
- **WHEN** local deliverables are staged for review
- **THEN** the staged files contain the proposal and sanitized evidence documents, and exclude private rehearsal artifacts, credentials, receipts, and downloaded weights

### Requirement: Confirm the actual Stage I demo environment
Final Stage I validation SHALL identify the actual ordinary computer, OS/CPU/architecture/RAM, devices, local model/configuration and exact setup/launch. A likely operator SHALL NOT establish a confirmed computer, narrator or recording arrangement. UGen300 absence SHALL NOT block this CPU validation.

#### Scenario: Lucas likely operates the demo
- **WHEN** Lucas is the planned operator but the computer and recording arrangement are unconfirmed
- **THEN** setup/scenario preparation continues and final actual-host live and recording acceptance remain pending
