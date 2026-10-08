# Stage I demo preparation

Proposed 2:55 shot plan for INT-03, checked against [CONTEST.md](CONTEST.md). The official three-minute guidance is a recommendation; 2:55 is the team's planning target. This is not a recorded or published demo. Lane 5 owns the rehearsal scenarios and final script; integration maintains launch, evidence and claim checks here. [STATUS.md](STATUS.md) determines what can honestly be shown.

## Run the current prototype

Follow [README development setup](../README.md#development), then launch:

```sh
uv run lecoach serve
```

Open `http://127.0.0.1:8000`, select `weak_to_improved`, start replay and let it finish. The current UI displays authored synthetic reactions and example feedback, with microphone/camera off. At the default 5× speed, its 50-second fixture lasts about ten seconds of wall time. The synthetic audience sequence is NEUTRAL → CONFUSED → BORED → INTERESTED → ENGAGED. Its timestamps are fixture capture times, not browser playback elapsed time.

The headless reproduction is:

```sh
uv run lecoach replay --case weak_to_improved
uv run python scripts/validate_fixtures.py
```

Default replay is a delivery trace with authored feedback, not an implemented engagement algorithm or a production coaching recorder. An early stop leaves the full authored summary unavailable.

## Proposed recording sequence

| Video time | Shot / purpose | Evidence needed |
| --- | --- | --- |
| 0:00–0:20 | Explain the problem: practicing alone gives little sense of audience response. | Product intent from GUIDE. |
| 0:20–0:35 | Show LeCoach and session controls. Identify the demonstrated mode. | Current shell can show synthetic mode; live mode requires INT-02. |
| 0:35–1:35 | Show weak delivery and recovery through visible audience changes. | Today: labeled authored replay. Later: Lane 5 scenario with actual speech/vision and Lane 4's sole engine. |
| 1:35–2:15 | End the session and explain a few timestamped observations and actions. | Today: authored example. Later: recorder/generator outputs with traceable evidence. |
| 2:15–2:40 | Show local architecture and the intended UGen300 adapter path. | Architecture plus SOURCES; label hardware work according to STATUS. |
| 2:40–2:55 | State the intended practical value and next validated milestone. | Avoid invented user outcomes or performance figures. |

Use English narration for the final video. Keep mode/provenance visible in edited shots. Do not replace replay labels with claims of live recognition. A CPU-based live rehearsal, once verified, can demonstrate Stage I behavior without implying accelerator execution.

## Evidence to capture when dependencies land

Coordinate the weak-to-improved scenario with Lane 5. For INT-02, record host/configuration, actual input mode, capture/decision timestamps, visible transitions, and feedback evidence IDs. Repeat after stop and check camera/microphone release, unavailable input, and session isolation. Store consented development artifacts under ignored `sessions/`, not Git.

For an accelerator run, add device/runtime/firmware identification, exact model/HEF hashes, input preprocessing and the measurement method. Report producer latency separately from window duration, engagement smoothing and browser delivery. Measure concurrent speech/vision operation; vendor FPS and TOPS do not substitute for this run.

The final recording, YouTube upload and competition submission remain pending. Verify the resulting unlisted link and submission receipt under the team's authorization workflow.

## INT-03 package handoff

The [local English proposal](submission/proposal.pdf) is paired with a [readiness/claim map](submission/readiness.md). Headless reproduction was repeated during INT-03 apply; [STATUS](STATUS.md#int-03-apply-local-validation) records synthetic inputs, exact state times and authored outputs. This does not establish a recorded demo or live behavior.

Lane 5's checked-in [scenario preparation](../checks/coaching/README.md) covers weak-to-improved delivery and limitation cases, but a final English narration/script has not been provided in the inspected handoff. Its new recorder [PR #5](https://github.com/crasni/LeCoach/pull/5) still needs separate integration review; it does not supply generated coaching or final footage here. Keep the script/scenario, accepted INT-02 run and final local recording gates pending. No synthetic-only final submission exception has been approved.
