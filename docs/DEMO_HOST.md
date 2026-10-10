# Stage I CPU demo host and rehearsal preparation

Lucas (@crasni) will probably operate/present. Confirm the actual computer and
recording arrangement before final validation. No UGen300 before qualification;
actual accelerator validation remains required for Stage II. Product, rehearsal,
UI and coaching remain English. See [GUIDE](../GUIDE.md).

## Confirm the computer

Record a sanitized host description in #11: OS/version, CPU/architecture, RAM,
microphone/webcam permissions, Python/uv/Node versions, revision, exact launch,
local model/configuration and hashes. Keep private media, transcripts, account
paths and device serials out of Git. Verify native runtime wheels on that host;
Linux import checks do not establish other-host compatibility.

## Prepare packages and models

After the reviewed dependency change is available on the intended checkout:

```sh
uv sync --frozen --group speech --group vision
npm --prefix frontend ci
npm --prefix frontend run build
```

Python 3.12.14 is pinned; Node.js 24 is the documented frontend prerequisite.
Linux sounddevice needs PortAudio (`libportaudio2` on Debian/Ubuntu); verify device
permissions on other systems. Include the groups on subsequent sync/run commands.
[Runtime setup](LOCAL_RUNTIME.md) records #6's English defaults and dependencies.

Prepare the speech owner's local model outside sessions:

```sh
uv run --group speech --group vision python -m lecoach.speech.model --download
uv run --group speech --group vision python -m lecoach.speech.model --check
```

Initial English `base.en`/CPU/int8 remains a baseline pending actual-host
measurements. Weights live in ignored `models/`; inference never downloads them.
Vision's merged README documents `pose_landmarker_lite.task`, camera selection,
`LECOACH_POSE_MODEL` and `LECOACH_CAMERA_INDEX`. Prepare that asset separately.

To choose a microphone, list the inputs before the rehearsal:

```sh
uv run --group speech --group vision python -m lecoach.speech.probe --list-devices
```

Set `LECOACH_SPEECH_DEVICE` to an input index or a name query before launching
the server; unset or blank uses the system default. On Windows, the same physical
microphone may appear under several host APIs; use the listed index or a name
including the host API. See the [speech setup](../src/lecoach/speech/README.md).

## Launch and identify the mode

Launch the opt-in local CPU composition:

```sh
uv run --group speech --group vision lecoach serve --live
```

Open `http://127.0.0.1:8000` and select **Live microphone and camera**. Speech
warm-up and VAD preparation happen before serving; camera runtime imports warm
in the background. Devices open only after preparing, subscribing and starting
the rehearsal. Each live session uses fresh speech/vision adapters, the sole
engine/recorder and generated template coaching. Missing models/runtimes/devices
remain input limitations; composition availability does not certify usable input.
Use `--speech-model-dir /path/to/models` for a different prepared speech directory.

Plain `lecoach serve` retains the synthetic replay app; its audience is computed
and its coaching authored. The same synthetic examples remain available in the
opt-in app and do not acquire devices. This implementation is not an accepted
actual-host live demo; capture/model quality, browser responsiveness and final
rehearsal evidence still need verification in #11. Startup/drain/feedback bounds
remain 5/2/5 s. Vision's proposed longer startup bound is not silently applied;
an API client can explicitly supply `startup_timeout_s: 10.0` for a reviewed run.

## Rehearse without models

Model downloads are unnecessary for UI checks and presentation practice. From
the repository root, prepare only the core packages and frontend:

```sh
uv sync --frozen
npm --prefix frontend ci
npm --prefix frontend run build
uv run lecoach serve
```

Open `http://127.0.0.1:8000`, select **Finding your rhythm**, and click **Start
replay**. Let it finish: the 50-second example plays in about ten seconds at the
default 5× speed. Audience changes are NEUTRAL, CONFUSED, BORED, INTERESTED and
ENGAGED at session times 0/20/30/35/40 s. Inspect the authored example coaching.
Repeat, stop midway, then start another example; the early-stop summary should
be unavailable and the next session should clear prior transcript/reactions.
The unavailable-input and empty examples should remain neutral with unknown
metrics. Speak your narration aloud while presenting the replay; your voice does
not drive it. Microphone/camera remain off.

This checks the UI and presentation flow. Actual speech recognition, camera
signals and coaching generated from a real rehearsal still need a host with
prepared models, which may be a teammate's computer.

For independent synthetic checks with devices off:

```sh
uv run python -m pytest -q
uv run python scripts/validate_fixtures.py
```

These do not establish microphone/camera or local model inference acceptance.

## Repeatable rehearsal after live handoff

1. Confirm the accepted revision, English model/configuration and live launch.
   Frame face and elbows/wrists; verify microphone/camera status and permissions.
2. Read the owner-provided English workplace scenario. Check partial/final
   transcript revisions, measured pace/fillers and source timestamps on the actual
   microphone. Unsupported measurements must remain unknown.
3. Look toward notes, then face the camera and deliver the next key sentence.
   Check deterioration/recovery and evidence IDs. Facing-only reactions do not
   establish speech acceptance.
4. Deliberately vary pace, use the agreed English fillers, then pause. Compare
   actual observations with the scenario; report recognition errors and missing
   measurements rather than fabricated results.
5. Stop and inspect timestamped coaching. Repeat to check bounded drain, device
   release and isolation. Exercise short/empty sessions, missing devices/models
   and no-person cases.
6. Record sanitized timing/load/failure evidence with owners, including browser
   responsiveness during concurrent CPU capture/inference. Time the actual script
   and edit; authored word count alone does not validate duration.

Lane 5 supplies the English scenario and competition explanation. Real recording,
publication and external submission require their separate authorization.
