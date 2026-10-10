# Competition requirements and submission preparation

Content rechecked 2026-10-10 against the [official competition rules](https://contest.bhuntr.com/tw/39jg9vimiynrhlksze/home/). Retrieval details and reference provenance are in [SOURCES.md](SOURCES.md). [GUIDE.md](../GUIDE.md) controls LeCoach's product scope; [GitHub Issues](https://github.com/crasni/LeCoach/issues?q=is%3Aissue+label%3Acoordination) control ownership and live task acceptance; [STATUS.md](STATUS.md) records demonstrated behavior.

## Verified requirements

| Item | Official requirement / section |
| --- | --- |
| Stage I deadline | 2026-10-14; sections V–VI. Exact cutoff time/timezone needs confirmation. |
| Deck | English throughout; at most 20 main pages, excluding appendix. Cover problem, solution, architecture, expected outcomes, references and GitHub source link; VI. |
| Video | Mainly English; three minutes or less is recommended. Supply an unlisted YouTube link; VI. |
| Stage I hardware | A laptop, SBC or virtual host may support initial validation; the selected accelerator is not mandatory yet; V. |
| Stage II hardware | Validate on the selected platform. Lightning finalists receive a UGen300; version and delivery details are announced separately; III, V. |
| Team / format | One to five eligible adults; choose one theme, platform and online/onsite format; III–IV. |
| Judging | Feasibility/business 35%, creativity 30%, practical value 25%, presentation 10%; VII. |
| Final deliverables | Online: December 4, including actual platform operation and repository evidence. Onsite: deck December 10, event December 19; V–VI. |

## Preparation for LeCoach

The local [English deck](submission/proposal.pdf) and [editable source](submission/proposal.fodp) now follow the 12-slide structure: problem; intended user; rehearsal journey; live audience response; demonstrated prototype; local architecture; event timing and failure handling; hardware adapter approach; validation evidence; practical value; delivery milestones; references and repository. [Readiness](submission/readiness.md) records local page/language/content/visual checks and the claim map. This is a review draft, not a finished submission or a change to the MVP; current prototype claims remain synthetic.

Build the video from [DEMO.md](DEMO.md), using the evidence available in STATUS. The default shell demonstrates synthetic playback; opt-in `lecoach serve --live` composes local speech/vision and generated coaching. Its final integrated rehearsal acceptance remains pending in INT-02. Replace example shots with accepted actual rehearsal behavior; label every input/inference mode accurately. Vendor specifications support intended architecture, not claims that LeCoach has already run on that hardware.

## Unresolved submission details

- Confirm the cutoff time/timezone and any upload limits in the actual submission form; the retrieved structured dates do not reliably establish them.
- The team's online/onsite registration choice and completion receipt have not been checked.
- Review section IX's original-work and licensing terms with the team. Clarify the treatment of a public development repository alongside the required GitHub link; do not assume an eligibility interpretation.
- Recheck the official rules immediately before submission. External upload, publication and submission follow the team's authorization requirements.

INT-03 apply rechecked the accessible public rules on 2026-10-07; no change to the table above was found. The public response is a client-loaded application shell with rules metadata, so final form/announcement inspection remains pending. No authenticated registration page or receipt was accessed. Team confirmation of format, cutoff and originality interpretation was requested; unanswered details remain unknown, not accepted by default.

## Review before submission

- [ ] Compare the final deck with the verified content and page requirements.
- [ ] Check the finished video language, runtime, labels and unlisted-link accessibility.
- [ ] Verify that repository setup and model/hardware claims match STATUS.
- [ ] Confirm registration format, cutoff details and the submission receipt.

These are submission checks for INT-03, not a second task ownership board.

On 2026-10-08, the rules content was rechecked unchanged and the rendered public announcements page showed no announcements at inspection. This does not establish registration completion, form limits or the precise cutoff. Those team/form gates remain pending.

## Product language versus submission language — 2026-10-09

Direct official response/JSON-LD rules content was re-fetched: section VI still
requires an English deck and mainly English video explanation; section V permits
ordinary computers for Stage I and requires selected-platform validation later.
Browser extraction failed, so this check used the direct response and content
inspection, not that failed extraction. Provenance/hash are in SOURCES.

The maintainer has restored English for the product, UI, coaching and rehearsal,
canceling the Mandarin/zh-TW proposal. Continue the English deck and mainly English
video explanation. Final narration/artifact checks remain Lane 5/integration
review; recheck official requirements before submission.

No UGen300 before qualification is a maintainer-confirmed team constraint. Stage I
must validate the ordinary-computer CPU path; actual accelerator operation remains
required for Stage II rather than blocking Stage I. Lucas is likely operator,
with actual demo computer and recording arrangement unconfirmed.
