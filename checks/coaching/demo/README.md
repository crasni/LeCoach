# COACH-02 scenario and narration handoff

This Lane 5 preparation connects the existing [2:55 shot plan](../../../docs/DEMO.md)
to [an English narration draft](narration.md), computed coaching and a proposed
live rehearsal. Issues [#21](https://github.com/crasni/LeCoach/issues/21),
[#20](https://github.com/crasni/LeCoach/issues/20) and
[#11](https://github.com/crasni/LeCoach/issues/11) own current progress, blockers
and acceptance. This supplies scenarios and evidence procedures, not another
task board. Integration owns launch/composition; video recording and external
publication require the applicable team authorization.

## Reproduce the current synthetic preview

Use the pinned setup in [README](../../../README.md#development). From the
repository root, these existing commands need no camera or microphone:

```sh
uv run python checks/coaching/feedback_replay.py
uv run python checks/coaching/record_replay.py
uv run python checks/coaching/feedback_replay.py --case weak_to_improved --show-feedback
uv run python checks/coaching/feedback_replay.py --case camera_unavailable --show-feedback
uv run python checks/coaching/feedback_replay.py --case drain_timeout --show-feedback
```

The optional factory runs the existing engine, sole recorder and generator.
Output is computed from hand-authored synthetic observations and writes no
rehearsal files. See [consumer behavior](../../../src/lecoach/coaching/README.md)
and the test-only [computed baseline](../engine_expectations.json).

For the audience shot, follow integration's launch instructions in DEMO and
select `weak_to_improved`. Default browser replay computes audience states and
displays authored example coaching. Show the CLI's generated summary separately
and retain the synthetic-mode label in both views. These demonstrations share
the scenario, but are not an accepted live UI/coaching integration.

### Evidence anchors to point out

| What to show | Session capture/decision time | Observed support |
| --- | --- | --- |
| Deterioration | CONFUSED 20 s; BORED 30 s | `pace_high`: `speech-10`, `speech-20`; facing-away at 30 s adds `vision-25`, `vision-30` |
| Recovery | INTERESTED 35 s; ENGAGED 40 s | `pace_steady` and `facing_audience` reasons from the existing engine |
| Pace improvement | 10 s | Windows 200–205 WPM; pause after key points |
| Approximate-facing improvement | 25 s | Cited facing estimates 0.2; look toward the camera and move notes closer |
| Supported strength | 40 s | Speech 144 WPM and cited facing estimate 0.85; maintain similar delivery |

Moments anchor at direct observations, which can precede a smoothed audience
decision. At 40 s the engine cites `speech-35`, `speech-40` and `vision-35`;
same-time `vision-40` is not cited. Repeated pace reasons at 20/30 s produce one
improvement. Numbers are synthetic examples, not live measurements, validated
thresholds or hardware results.

### Limitation and repeat checks

The all-case commands check these nine cases / ten sessions. These observations
are not minimum insight quotas for arbitrary rehearsals.

| Case | Computed result to inspect |
| --- | --- |
| `weak_to_improved` | Two improvements, one strength, no missing-source limitation |
| `camera_unavailable` | One pace improvement; camera limitation; no invented facing critique or strength |
| `no_usable_signals` | No moments; speech/camera and insufficient-evidence limitations |
| `empty_session` | Zero duration, no moments, insufficient-evidence limitation |
| `insufficient_window` | Null startup metrics remain unknown; no moments |
| `late_final_and_duplicates` | Eligible late transcript retained once; no supported moments |
| `drain_timeout` | No moments; incomplete speech/drain limitation; closed-session callback excluded |
| `repeated_sessions` | Two isolated sessions, no moments; old-session events excluded |
| `adjacent_incidents` | One pace improvement; repeated incident does not fill another slot |

## Proposed live rehearsal after accepted integration

Use the launch/configuration and producer handoffs accepted under INT-02. The
current optional coaching factory rejects live mode. This preparation supplies
no live command or model configuration.

Have an authorized presenter use this invented, nonconfidential passage. It is
synthetic rehearsal material, not a participant's transcript:

> Our team is preparing a short weekly update. We will explain the problem,
> show one example, and finish with a clear next step. The first goal is to
> make the message easy to follow. The second is to give listeners enough time
> to understand the important point. We will review what happened, choose one
> change, and try the same passage again in the next rehearsal.

| Phase | Presenter cue | Evidence to inspect |
| --- | --- | --- |
| Settle | Start the accepted live session; face the camera and establish usable inputs. | Actual session ID, input status and finalized windows; unavailable startup is not weak delivery. |
| Weak, roughly 25–30 s | Repeat the passage quickly, with few gaps; look toward notes beside the camera for a sustained interval. | Actual pace/facing and negative engine reasons/citations; no prescribed transition timestamp. |
| Improved, roughly 25–30 s | Repeat at a comfortable pace, pause between key ideas, and orient toward the camera. | Recovery after configured windows/smoothing; cite actual positive evidence. |
| Stop/review | Stop capture, allow bounded drain, then open generated feedback/timeline. | Capture/decision times, evidence IDs, limitations and supported moments; fewer when evidence is insufficient. |
| Repeat/failure | Start a new session; separately try camera denial/disconnection, missing speech and an empty/short stop. | New IDs/zero-based clocks, no old evidence, honest missing-input behavior, device release and bounded stop. |

Timing is a rehearsal cue, not producer configuration or an acceptance threshold.
Use agreed rules; do not retune them to force a shot. If the story does not occur,
retain the outcome, inspect events with the responsible owner, and revise the
scenario or claims. This example claims no filler-driven reaction; add one only
with its own measured producer evidence.

## Run record for the accepted live handoff

Fill these fields in an authorized run under ignored `sessions/`; link only
sanitized evidence in the Issue/PR. Exports use canonical event/session models,
not a new JSON contract. Raw media, transcripts and private outputs stay out of Git.

| Field | Record after the run |
| --- | --- |
| Identity/provenance | Date, operator/authorization reference, host/OS, commit, actual mode; distinguish synthetic, live CPU and measured accelerator evidence |
| Configuration | Accepted launch command, producer/model/runtime versions and configuration; target device/firmware/model hashes and method from [HARDWARE](../../../docs/HARDWARE.md) |
| Session/time | Session ID, capture start/end/duration, source-event IDs, decision times and separate elapsed wall time |
| Weak/recovery | Metric windows and reasons for actual transitions, missing/outage intervals; no assumed target timestamps |
| Coaching | Actual kind/time/observation/action and evidence links for each moment, limitations and incomplete sources |
| Lifecycle/failures | Stop/drain, device release, second-session isolation, unavailable-camera/speech and empty-session results |
| Review | Reviewer/run reference for accepted integration/coaching; inaccurate-claim or missing-evidence notes |
| Media, when authorized | Local artifact references, visible mode/speed labels, actual read-through/edit durations; publication approval separately |

## Narration timing estimate

The six spoken blocks total **310 words**. Count hyphenated words and words
with apostrophes as one; exclude directions and live pickup notes. At an assumed
135 words/minute, reading takes about 137.8 seconds, leaving 37.2 seconds of screen
holds within the existing 175-second plan. Each slot fits this assumed pace.
At 125–145 words/minute, reading alone is approximately 128.3–148.8 seconds;
adjust holds after a timed read-through. None of these are measured durations.

| Video slot | Words | Estimated speech at 135 WPM | Available screen hold |
| --- | ---: | ---: | ---: |
| 0:00–0:20 | 35 | 15.6 s | 4.4 s |
| 0:20–0:35 | 28 | 12.4 s | 2.6 s |
| 0:35–1:35 | 95 | 42.2 s | 17.8 s |
| 1:35–2:15 | 76 | 33.8 s | 6.2 s |
| 2:15–2:40 | 45 | 20.0 s | 5.0 s |
| 2:40–2:55 | 31 | 13.8 s | 1.2 s |

Recount after editing, from the repository root:

```sh
uv run python - <<'PY'
import re
from pathlib import Path
text = Path("checks/coaching/demo/narration.md").read_text()
blocks = re.findall(r"```text\n(.*?)\n```", text, re.S)
counts = [len(re.findall(r"\b[\w]+(?:[-'][\w]+)*\b", block)) for block in blocks]
print("Per slot:", counts, "Total:", sum(counts))
print("Estimated seconds at 135 WPM:", round(sum(counts) / 135 * 60, 1))
PY
```

## INT-03 handoff

Provide integration with versioned narration, verified scenario commands,
generated-feedback anchors, actual run record and measured read-through/edit
duration. Integration owns DEMO/deck/readiness updates; link current Issues/PRs
instead of copying live task fields into these files.

Replace fixture timestamps and the preview-mode paragraph using the accepted
run's evidence, following the narration pickups. Review wording against actual
local retention/data flow and measured target behavior. An estimated read time
or successful synthetic replay is not a live demo, accepted final script or
permission for video/competition delivery.

## Preparation evidence — 2026-10-08

Local macOS arm64 / pinned CPython 3.12.14, using the existing environment:

```sh
.venv/bin/python checks/coaching/feedback_replay.py --show-feedback
.venv/bin/python checks/coaching/record_replay.py
git diff --check
```

Both replays passed all 9 synthetic cases / 10 sessions. The displayed generated
values match the narration and evidence table. Word recount produced
`[35, 28, 95, 76, 45, 31]` (310 total); every slot fits the assumed 135 WPM.
All 11 local Markdown targets/anchors in the three coaching handoff/check pages
resolved, and whitespace checks passed. No application code was changed by this
draft; no new full-suite, browser, device, voiceover, live inference or hardware
validation is claimed. Actual read-through and edited-video timing remain to be
measured with the reviewed script.
