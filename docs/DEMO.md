# Stage I demo preparation

## Current English CPU demonstration direction — 2026-10-10

Product, rehearsal, UI and coaching remain English. The maintainer canceled the
Mandarin/zh-TW direction; existing English scenarios and component work continue.
The maintainer selected their Ubuntu computer and Bluetooth microphone and
reports the first live functional/reliability checks passed. Final recording
arrangement and reviewed footage remain pending. [Demo host preparation](DEMO_HOST.md) covers setup and rehearsal.
Stage I requires actual local CPU microphone/camera behavior on that computer;
UGen300 validation remains Stage II. Existing authored scenarios/replays are
preparation, not final live evidence. Keep the English deck and mainly English
competition explanation and measure the final script/edit duration.

Proposed 2:55 shot plan for INT-03, checked against [CONTEST.md](CONTEST.md). The official three-minute guidance is a recommendation; 2:55 is the team's planning target. This is not a recorded or published demo. Lane 5 owns the rehearsal scenarios and final script; integration maintains launch, evidence and claim checks here. [Issue #12](https://github.com/crasni/LeCoach/issues/12) owns package acceptance and current dependencies; [STATUS.md](STATUS.md) preserves dated observations.

## Run the current prototype

Follow [README development setup](../README.md#development), then launch:

```sh
uv run lecoach serve
```

Open `http://127.0.0.1:8000`, select `weak_to_improved`, start replay and let it finish. The current UI computes audience reactions from synthetic observations and displays authored example feedback, with microphone/camera off. At the default 5× speed, its 50-second fixture lasts about ten seconds of wall time. The computed audience sequence is NEUTRAL → CONFUSED → BORED → INTERESTED → ENGAGED at 0, 20, 30, 35 and 40 seconds. These are shared-clock decision times, not browser playback elapsed time.

The headless reproduction is:

```sh
uv run lecoach replay --case weak_to_improved
uv run lecoach replay --case weak_to_improved --audience authored
uv run python scripts/validate_fixtures.py
```

Default replay computes engagement with the sole engine; feedback stays authored and the recorder is not enabled by the default composition. The explicit authored option reproduces the older deck's audience times. An early stop leaves the full authored summary unavailable.

## Versioned Lane 5 live-script handoff

Lane 5 supplied the [English narration](https://github.com/crasni/LeCoach/blob/1f4607ab95e50a115468339e7d4dc070a9b860fb/checks/coaching/demo/narration.md) and [scenario/runbook](https://github.com/crasni/LeCoach/blob/1f4607ab95e50a115468339e7d4dc070a9b860fb/checks/coaching/demo/README.md) in [PR #33](https://github.com/crasni/LeCoach/pull/33), approved and delivered at `1f4607a`. Keep these owner-maintained sources rather than copying the script into this guide. This CPU live draft describes delivered browser coaching and uses no fixed live timestamps or insight quotas. Final script acceptance still needs actual supported shots and measured timing. Its six spoken segments align with the slots below.

These standalone synthetic generated-coaching commands remain available in this integration checkout:

```sh
uv run python checks/coaching/feedback_replay.py --case weak_to_improved --show-feedback
uv run python checks/coaching/feedback_replay.py --case camera_unavailable --show-feedback
uv run python checks/coaching/feedback_replay.py --case drain_timeout --show-feedback
uv run python checks/coaching/record_replay.py
```

For synthetic footage, show the generated summary in the terminal separately from the browser's authored card and label both as replay. The verified synthetic moments remain improvements at capture times 10 s (200–205 WPM) and 25 s (approximate facing 0.2), plus a strength at 40 s (144 WPM and cited facing 0.85). Those capture anchors differ from the smoothed audience decisions at 20/30/35/40 s. The same-time `vision-40` event is not cited by the 40 s decision; use its actual evidence IDs rather than adding a convenient observation. Live footage instead shows the browser's actual generated feedback after stop, labeled **Live · local CPU**; do not substitute these fixture anchors for observed live moments.

The delivered narration totals 309 words, with per-slot counts 35/32/90/76/43/33. At the earlier approximately 135 WPM pace, speech is estimated at 137.3 s, leaving 37.7 s for screen holds in the 175 s plan. This revision has not been timed. The maintainer's comfortable approximately 2:20 read-through belongs to the earlier 316-word script at `03028dd`. Time each revised slot: the final 15 s slot allows only about 0.3 s spare at 135 WPM, and the mode slot about 0.8 s. Rebalance holds after the read-through; final edited duration remains a separate measurement. Retain replay/speed labels for fixture shots; real recording requires its applicable authorization.

## Proposed recording sequence

| Video time | Shot / purpose | Evidence needed |
| --- | --- | --- |
| 0:00–0:20 | Explain the problem: practicing alone gives little sense of audience response. | Product intent from GUIDE. |
| 0:20–0:35 | Show LeCoach and session controls. Identify the demonstrated mode. | Opt-in live composition is delivered; final live footage needs accepted INT-02 evidence. |
| 0:35–1:35 | Show weak delivery and recovery through visible audience changes. | Preview: synthetic observations and computed reactions. Live footage: actual speech/vision and the same engine, with real observed timestamps. |
| 1:35–2:15 | Show generated live feedback: timestamp, observation and one practice action. | Match each actual card to its cited evidence and run configuration. Show fewer cards when evidence is limited; fixture summaries need replay labels. |
| 2:15–2:40 | Show local architecture, Stage I CPU target and Stage II UGen300 plan. | Architecture and SOURCES distinguish automated checks, maintainer-reported live behavior and unmeasured accelerator plans. |
| 2:40–2:55 | Choose one supported suggestion for the next rehearsal. | Avoid invented user outcomes or performance figures; measure the revised closing slot. |

Use English narration for the final video. Keep mode/provenance visible in edited shots. Do not replace replay labels with claims of live recognition. A CPU-based live rehearsal, once verified, can demonstrate Stage I behavior without implying accelerator execution.

## Remaining live evidence pickup

The maintainer-reported functional/reliability batch in [#11](https://github.com/crasni/LeCoach/issues/11#issuecomment-6095334266) already covers transcription/camera/audience, stop/feedback, repeat isolation, release, short/no-person and missing-microphone behavior. Do not request its repetition. For coaching review, obtain an actual moment's kind, timestamp, observation, practice action and cited IDs, together with a sanitized source revision, exact launch and run/configuration reference. Match the cited measurements to the advice; current model hashes cannot retrospectively establish an earlier run's configuration. Keep private transcript/media out of Issues and Git. Store explicitly requested development artifacts under ignored `sessions/`.

The Ubuntu vision startup/inference/repeat-release measurement is recorded in [STATUS](STATUS.md#plain-advice-delivery-and-ubuntu-vision-timing--2026-10-10) and supplied to the vision owner in #16. [DEMO_HOST](DEMO_HOST.md#ubuntu-camera-timing-handoff) describes its scope and the existing guided probe. Quantitative speech quality/timing/filler recall remains with its owner. Use pace/facing for the demo rather than relying on unverified filler recall. Actual operator reports, model checks and quantitative measurements retain their own attribution.

For an accelerator run, add device/runtime/firmware identification, exact model/HEF hashes, input preprocessing and the measurement method. Report producer latency separately from window duration, engagement smoothing and browser delivery. Measure concurrent speech/vision operation; vendor FPS and TOPS do not substitute for this run.

The final recording, YouTube upload and competition submission remain pending. Verify the resulting unlisted link and submission receipt under the team's authorization workflow.

## Evidence handoff format

Use the existing Issues for handoff and acceptance: [INT-02 #11](https://github.com/crasni/LeCoach/issues/11) for the integrated run, [COACH-02 #21](https://github.com/crasni/LeCoach/issues/21) for the script/scenario, and [INT-03 #12](https://github.com/crasni/LeCoach/issues/12) for package review. This format describes evidence to supply; it neither assigns work nor establishes a new interface.

| Record | Fields needed for package review |
| --- | --- |
| Integrated run | Commit/PR and observation date; host, model/backend and configuration; exact setup/launch commands; actual input mode; scenario steps and session-clock audience transitions; generated feedback with evidence IDs; unavailable-input, stop/drain/resource-release and repeated-session observations; limitations and acceptance reference. |
| Script/scenario | Version/commit; English narration and shot timings; rehearsal steps and reproduction commands; links to the accepted run and coaching evidence; on-screen mode labels; any accelerated replay disclosure; intended and observed runtime, distinguished explicitly. |
| Reviewed recording | Separate recording authorization reference; ignored local artifact location and SHA-256; script/run revisions; measured video duration and narration language; legibility/provenance review; reviewer and outcome. Do not put private footage or transcripts in an Issue, PR or Git. |

Before substituting live shots or revising deck claims, compare the run's source/configuration and observed transitions with the script, footage and readiness claim map. An authored coaching card or an isolated model run cannot establish integrated generated feedback. Preserve unknown timing phases as unmeasured; follow [HARDWARE.md](HARDWARE.md) for target evidence. Keep acceptance and unmet handoffs in the Issues, rather than checking them off in this document.

## INT-03 package handoff

The [local English proposal](submission/proposal.pdf) is paired with a [readiness/claim map](submission/readiness.md). Headless reproduction was repeated during INT-03 apply; [STATUS](STATUS.md#int-03-apply-local-validation) records synthetic inputs, exact state times and authored outputs. This does not establish a recorded demo or live behavior.

The versioned Lane 5 handoff supplies the delivered CPU live narration and separate synthetic coaching anchors. Recorder [PR #5](https://github.com/crasni/LeCoach/pull/5), coaching PR #24 and plain-advice/script PR #33 are merged; opt-in live sessions generate browser coaching. Default replay browser cards remain authored examples. Before final script acceptance, match the visible advice to accepted actual evidence and measure revised narration/edit timing. The existing proposal is an unaccepted draft; its replacement is delegated in [#34](https://github.com/crasni/LeCoach/issues/34) for integration review. This guide does not accept the proposal or approve a synthetic-only final submission.
