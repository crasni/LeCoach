# Stage I CPU demo host and rehearsal preparation

Lucas (@crasni) will probably operate/present. This is a plan, not a confirmed
computer, narrator or recording arrangement. Final validation must confirm the
actual machine. No UGen300 is available before qualification; keep actual target
validation for Stage II. See [current product direction](../GUIDE.md).

## Confirm the computer before final validation

Record a sanitized host description in #11: OS/version, CPU/architecture, RAM,
microphone/webcam availability and permissions, Python/uv/Node versions, source
revision, exact launch/configuration and local model files/hashes. Do not publish
device serial numbers, account paths, credentials, private transcripts or footage.
Check native runtime wheels on that host rather than assuming Linux import checks
establish macOS/Windows/ARM compatibility.

## Prepare packages and models

After the reviewed integration dependency change is available on the intended
checkout:

```sh
uv sync --frozen --group speech --group vision
npm --prefix frontend ci
npm --prefix frontend run build
```

Python 3.12.14 is pinned; Node.js 24 is the documented frontend prerequisite.
Linux sounddevice needs PortAudio (`libportaudio2` on Debian/Ubuntu); macOS/Windows
need device permissions. [Runtime setup](LOCAL_RUNTIME.md) covers the groups.
Include the groups on later sync/run commands to keep those packages installed.

Speech owner must supply the exact multilingual Mandarin model download/load
command and model/configuration hash after #6 agreement and #13 implementation.
`base.en` is not the Mandarin demo model; multilingual CPU/int8 `base` is only a
candidate until measured. Do not invent a download command for an unimplemented
speech model module. Prepare ignored `models/` assets before any session; no
download or expensive model load during session start. Vision's merged README
documents `pose_landmarker_lite.task`, camera index and its local probe. Use its
public factory after composition acceptance; never a second browser capture stack.

## Launch and distinguish currently available modes

The existing runnable launch is:

```sh
uv run --group speech --group vision lecoach serve
```

Open `http://127.0.0.1:8000`. At this preparation revision it serves the existing
synthetic fixture app with English examples, computed audience and authored
feedback; it is not the accepted Mandarin live demo. Installing runtimes cannot
enable missing production speech or localize that UI. Integration will update
this procedure with the exact accepted live factory/command after owner handoffs.
Do not replace that missing command with a simulated live-mode claim.

Independent Mandarin conformance check (devices stay off):

```sh
uv run python -m pytest -q tests/test_mandarin_integration.py
```

See [fixture handoff](../checks/integration/mandarin/README.md). These checks do not
validate Mandarin recognition, filler accuracy, actual Chinese UI rendering or
the demo computer.

## Repeatable actual rehearsal after live handoff

1. Confirm the accepted revision, Mandarin analysis method/units, native zh-TW
   UI/coaching and model/configuration. Frame face and elbows/wrists; verify
   microphone/camera status. Model/setup failures must be understandable in zh-TW.
2. Speak a short Taiwan Mandarin workplace passage with names, numbers and an
   English product name. Confirm partial/final revisions and meaning/script on
   the actual microphone; do not translate the speech into English for analysis.
3. Look toward notes for several seconds, then face the camera and say the next
   key sentence. Verify supported audience deterioration/recovery and source IDs.
   Unknown Mandarin pace/fillers must stay unknown and cannot support speech-rate
   coaching. Do not treat facing-only reactions as full speech acceptance.
4. Check natural hesitations and filler-like content (for example, "那個部門會先
   試用" and "就是這項功能"). Evaluate the agreed contextual method; no unsupported
   substring count. Test a deliberate pause and silence using actual detection.
5. Stop, inspect timestamped native zh-TW coaching/limitations, then repeat.
   Confirm device release, bounded drain and no event/transcript mixing. Repeat
   short/empty, unavailable device/model and no-person cases without blaming the
   speaker for missing inputs.
6. Record sanitized timing/load/failure observations with speech/vision owners,
   including concurrent browser responsiveness. Retain unknown measurements and
   bring any required unsupported Mandarin capability to the maintainer as a
   concrete scope trade-off.

Real rehearsal recording needs separate authorization. Lane 5 supplies Mandarin
scenario/zh-TW content and mainly English competition explanation/captions; actual
read-through/edit timing and final official-language review remain required.
