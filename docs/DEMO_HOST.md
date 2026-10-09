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

Speech owner supplies the exact model preparation/load command after #13's live
implementation. Initial English `base.en`/CPU/int8 remains an unmeasured baseline.
Prepare ignored model assets before sessions; do not download/load expensive
models during session start. No command is invented for an unimplemented speech
module. Vision's merged README documents `pose_landmarker_lite.task`, camera
selection and probe; use its public factory after composition acceptance.

## Launch and identify the mode

The currently runnable launch is:

```sh
uv run --group speech --group vision lecoach serve
```

Open `http://127.0.0.1:8000`. This preparation revision serves the synthetic fixture
app with computed audience and authored feedback; it is not the accepted live
CPU demo. Installing runtimes does not supply missing production speech.
Integration will record the exact live launch after owner handoffs are accepted.

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
