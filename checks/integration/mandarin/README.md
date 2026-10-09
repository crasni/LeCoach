# Mandarin integration conformance fixtures

All passages, observations and copy samples are authored synthetic data. No
microphone/camera, ASR model, filler detector or person was used. These files do
not replace the speech/UI/coaching owners' implementations or final demo script.
Existing English regression cases remain intact.

Run from the repository root:

```sh
uv run python -m pytest -q tests/test_mandarin_integration.py
```

The existing sole engine/controller/recorder consume v0 observations with null
WPM/filler fields. There is no Chinese character rate hidden in WPM. Known pause
states and approximate facing are synthetic independent observations; low
movement/activity is not invented as a negative rule. Tests check computed
audience transitions, actual cited source identities, transcript/number/name
preservation and repeated-session isolation. Recorder-only composition does not
promote authored copy to computed coaching.

| Case | Expected behavior |
| --- | --- |
| `mandarin_facing_recovery` | NEUTRAL → BORED → INTERESTED → ENGAGED using facing evidence only; unknown speech pace never supports a reason. |
| `mandarin_mixed_content` | Taiwan terms, LeCoach and 12 survive final text; "那個部門"/"就是這項功能" do not acquire fabricated filler counts. Known facing can support a positive response. |
| `mandarin_camera_missing` | Mandarin transcript remains usable, but unknown pace/fillers with no vision do not create speech-quality reactions. |
| `mandarin_long_pause` | Only the known synthetic active pause supports a negative reaction, not a fabricated low WPM. |
| `mandarin_short` | Brief observations stay NEUTRAL; no unsupported strength or criticism. |
| Repeated replay | Two sessions retain separate canonical transcripts/events. |

`presentation.json` contains **proposed native zh-TW handoff copy**, not installed
frontend/backend strings. Authored review covers navigation, buttons, onboarding,
input/error/fallback notices, audience/reasons, unknown metric explanations,
timeline, coaching, empty state and example provenance. Taiwan wording includes
"攝影機", "麥克風", "權限", "本機", "練習簡報" and concrete rehearsal advice;
LeCoach and internal event codes keep their identifiers. The unknown pace text
does not display 0, WPM or an unvalidated Chinese unit.

This checks fixture behavior and reviewed Traditional Chinese handoff wording.
The current English app is not thereby localized. UI owner still needs actual
desktop/narrow browser font/wrapping, notices/fallbacks and localized feedback
checks; coaching owner needs actual evidence-linked zh-TW templates; speech owner
needs real Taiwan Mandarin capture/transcription/measurement tests. Those owners
review the [proposed shared delta](../../../openspec/changes/mandarin-first-stage1/proposal.md)
and decisions in existing Issues before changing shared semantics.
