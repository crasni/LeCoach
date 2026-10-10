# Stage I demo preparation

## Current English CPU demonstration direction — 2026-10-09

Product, rehearsal, UI and coaching remain English. The maintainer canceled the
Mandarin/zh-TW direction; existing English scenarios and component work continue.
Lucas (@crasni) is the likely operator, with actual computer/recording arrangement
unconfirmed. [Demo host preparation](DEMO_HOST.md) covers setup and rehearsal.
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

## Versioned Lane 5 preview handoff

Lane 5 supplied the [English narration](https://github.com/crasni/LeCoach/blob/03028dd42a751c22d28c98889d17ba442e5da84f/checks/coaching/demo/narration.md) and [scenario/runbook](https://github.com/crasni/LeCoach/blob/03028dd42a751c22d28c98889d17ba442e5da84f/checks/coaching/demo/README.md) in [PR #24](https://github.com/crasni/LeCoach/pull/24), reviewed here at `03028dd`. Keep these owner-maintained sources rather than copying the script into this guide. This revision is a synthetic development preview, not an accepted final live script. Its six spoken segments align with the slots below.

PR #24 is now delivered; these standalone synthetic generated-coaching commands are available in this integration checkout:

```sh
uv run python checks/coaching/feedback_replay.py --case weak_to_improved --show-feedback
uv run python checks/coaching/feedback_replay.py --case camera_unavailable --show-feedback
uv run python checks/coaching/feedback_replay.py --case drain_timeout --show-feedback
uv run python checks/coaching/record_replay.py
```

Show the generated summary in the terminal separately from the browser's authored card. The verified synthetic moments are improvements at capture times 10 s (200–205 WPM) and 25 s (approximate facing 0.2), plus a strength at 40 s (144 WPM and cited facing 0.85). Those capture anchors differ from the smoothed audience decisions at 20/30/35/40 s. The same-time `vision-40` event is not cited by the 40 s decision; use its actual evidence IDs rather than adding a convenient observation.

The revised narration totals 316 words, with per-slot counts 35/28/95/76/51/31. At an assumed 135 WPM, speech takes about 140.4 s, leaving 34.6 s for screen holds in the 175 s plan. This is a calculation, not measured narration or edited-video duration. Retain visible **Synthetic development preview** and 5× replay labels. Actual read-through and recording require their applicable authorization.

## Proposed recording sequence

| Video time | Shot / purpose | Evidence needed |
| --- | --- | --- |
| 0:00–0:20 | Explain the problem: practicing alone gives little sense of audience response. | Product intent from GUIDE. |
| 0:20–0:35 | Show LeCoach and session controls. Identify the demonstrated mode. | Current shell can show synthetic mode; live mode requires INT-02. |
| 0:35–1:35 | Show weak delivery and recovery through visible audience changes. | Today: synthetic observations and computed audience reactions. Later: Lane 5 scenario with actual speech/vision and the same engine. |
| 1:35–2:15 | Explain generated moments, observations, actions and evidence in the Lane 5 terminal viewer. | PR #24 computes coaching from synthetic observations; the default browser card remains authored. Actual live generated feedback still requires accepted composition. |
| 2:15–2:40 | Show local architecture, Stage I CPU target and Stage II UGen300 plan. | Architecture plus SOURCES; synthetic checks do not establish CPU inference or accelerator execution. |
| 2:40–2:55 | State the intended practical value and next validated milestone. | Avoid invented user outcomes or performance figures. |

Use English narration for the final video. Keep mode/provenance visible in edited shots. Do not replace replay labels with claims of live recognition. A CPU-based live rehearsal, once verified, can demonstrate Stage I behavior without implying accelerator execution.

## Evidence to capture when dependencies land

Coordinate the weak-to-improved scenario with Lane 5. For INT-02, record host/configuration, actual input mode, capture/decision timestamps, visible transitions, and feedback evidence IDs. Repeat after stop and check camera/microphone release, unavailable input, and session isolation. Store consented development artifacts under ignored `sessions/`, not Git.

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

The versioned Lane 5 preview handoff above supplies narration, scenario commands and computed coaching anchors. Recorder [PR #5](https://github.com/crasni/LeCoach/pull/5) is merged; generated coaching is delivered by PR #24 and enabled for opt-in live sessions; this checkout's default replay browser still displays authored example coaching. Before final script acceptance, replace fixture-specific statements with the accepted INT-02 run's actual host/input/configuration, timestamps, supported moments and viewer, then measure narration/edit timing. Keep accepted live evidence and reviewed local footage pending. The deck still reflects merged synthetic functionality and explicitly authored example coaching; this handoff does not update its claims or approve a synthetic-only final submission.
