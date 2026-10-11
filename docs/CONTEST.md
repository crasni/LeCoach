# Competition requirements and submission preparation

Rules content rechecked 2026-10-11 against the [official competition rules](https://contest.bhuntr.com/tw/39jg9vimiynrhlksze/home/); the exact rendered cutoff retains its 2026-10-10 verification. Retrieval details and reference provenance are in [SOURCES.md](SOURCES.md). [GUIDE.md](../GUIDE.md) controls LeCoach's product scope; [GitHub Issues](https://github.com/crasni/LeCoach/issues?q=is%3Aissue+label%3Acoordination) control ownership and live task acceptance; [STATUS.md](STATUS.md) records demonstrated behavior.

## Verified requirements

| Item | Official requirement / section |
| --- | --- |
| Stage I deadline | **2026-10-14 17:00, Asia/Taipei (UTC+8)**; rendered public Submission period / Competition timezone fields checked 2026-10-10, with the date confirmed by sections V–VI. |
| Deck | English throughout; at most 20 main pages, excluding appendix. Cover problem, solution, architecture, expected outcomes, references and GitHub source link; VI. |
| Video | Mainly English; three minutes or less is recommended. Supply an unlisted YouTube link; VI. |
| Stage I hardware | A laptop, SBC or virtual host may support initial validation; the selected accelerator is not mandatory yet; V. |
| Stage II hardware | Validate on the selected platform. Lightning finalists receive a UGen300; version and delivery details are announced separately; III, V. |
| Team / format | One to five eligible adults; choose one theme, platform and online/onsite format; III–IV. |
| Judging | Feasibility/business 35%, creativity 30%, practical value 25%, presentation 10%; VII. |
| Final deliverables | Online: December 4, including actual platform operation and repository evidence. Onsite: deck December 10, event December 19; V–VI. |

## Preparation for LeCoach

The delivered replacement in [PR #35](https://github.com/crasni/LeCoach/pull/35)
has 15 English main pages and no appendix: workplace problem, audience experience,
rehearsal loop, local speech/camera limits, generated synthetic coaching,
architecture/retention, limited actual vision advice, isolated camera timings,
failures, proposed value/pilot, demo plan, Stage I/II and source references.
Use its versioned [PDF](https://github.com/crasni/LeCoach/blob/d34a58c/docs/submission/proposal.pdf)
and [editable source](https://github.com/crasni/LeCoach/blob/d34a58c/docs/submission/proposal.fodp)
for the reviewed artifact revision. PR #35 merged as `319d274` on 2026-10-11
under explicit maintainer authorization; the local [PDF](submission/proposal.pdf)
and [source](submission/proposal.fodp) are now that replacement. The rejected
refreshed draft is absent from PR #32's final diff.
[Readiness](submission/readiness.md) pins the replacement hashes and distinguishes
artifact checks from final live/package acceptance. Synthetic coaching, actual
CPU observations and unmeasured hardware plans retain their respective labels.

Build the video from [DEMO.md](DEMO.md), using the evidence available in STATUS. The default shell demonstrates synthetic playback; opt-in `lecoach serve --live` composes local speech/vision and generated coaching. Its final integrated rehearsal acceptance remains pending in INT-02. Replace example shots with accepted actual rehearsal behavior; label every input/inference mode accurately. Vendor specifications support intended architecture, not claims that LeCoach has already run on that hardware.

## Unresolved submission details

- Registration completion and submission receipt have not been checked. The maintainer selected Global Online Track on 2026-10-10; registration is not yet completed.
- Any form-specific constraints will be addressed if they prevent the selected artifacts from being submitted; upload limits have not been inspected.
- Review section IX's original-work and licensing terms with the team. Clarify the treatment of a public development repository alongside the required GitHub link; do not assume an eligibility interpretation.
- Recheck the official rules immediately before submission. External upload, publication and submission follow the team's authorization requirements.

Earlier INT-03 checks on 2026-10-07 were superseded by the rules rechecks and
rendered cutoff verification below. The public rules description is unchanged
on 2026-10-11. No authenticated registration page or receipt was accessed.
Registration/form details and team interpretation of originality remain unknown;
the Global Online Track choice and rendered cutoff are already confirmed.

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

## Exact cutoff verified — 2026-10-10

The rendered official home page displays a submission period ending
**2026-10-14 17:00** and explicitly identifies **Asia/Taipei** as the competition
timezone. This resolves the earlier cutoff uncertainty; prior dated retrieval
notes above describe earlier checks. The timezone-free JSON-LD value alone was
not used to infer the time. The maintainer selected **Global Online Track**;
registration and delivery receipts remain separate from that participation choice.
