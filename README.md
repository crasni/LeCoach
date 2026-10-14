# LeSpeech

Your Private AI Audience.

LeSpeech is a local, multimodal presentation coach for the ASUS UGen AI League Hackathon 2026. It combines speech and body-language signals to make a virtual audience react in real time, then highlights specific moments and practical improvements after each rehearsal.

## MVP

- Local speech transcription, speaking pace, fillers, and pauses.
- Webcam-based pose, approximate facing direction, and gesture activity.
- A deterministic engagement engine with smooth audience reactions.
- A synchronized session timeline and concise, actionable feedback.

Product and rehearsal language: English. Stage I validates local CPU inference
on an ordinary computer; UGen300 will not be available before qualification.
Target track: Workplace AI / Battlefield Lightning, with UGen300 retained as the
intended accelerator for actual Stage II validation. See [GUIDE](GUIDE.md) and
[demo host preparation](docs/DEMO_HOST.md).

## Project status

The current prototype implements local speech/vision, a deterministic audience
engine, session recording and generated template coaching through opt-in live mode.
The default app retains labeled synthetic replay with authored example coaching.
The maintainer reports a working live rehearsal and reliability checks on their
Ubuntu computer with a Bluetooth microphone. Measured quality/performance and
final live acceptance remain separate; see [dated evidence](docs/STATUS.md) and
[#11](https://github.com/crasni/LeSpeech/issues/11). Vision Stage I is
[accepted with an activity-measurement limitation](https://github.com/crasni/LeSpeech/issues/16#issuecomment-6097454631).

Start at [AGENTS.md](AGENTS.md), the shared entry point for all five collaborators. Follow the canonical documents linked there:

- [GUIDE.md](GUIDE.md): agreed product scope and priorities.
- [GitHub Issues](https://github.com/crasni/LeSpeech/issues?q=is%3Aissue+label%3Acoordination): assignments, branches, live status, blockers and acceptance.
- [Architecture](docs/ARCHITECTURE.md): shared event contracts.
- [Implementation evidence](docs/STATUS.md): dated checks and limitations, not live task state.
- [Lane boundaries](docs/AGENT_ROLES.md): stable responsibilities; assigned Issues provide the handoff.

Official competition and hardware reference PDFs are in [docs/](docs/).

## Development

Prerequisites: [uv](https://docs.astral.sh/uv/), Node.js 24, and npm. Python 3.12.14
is pinned in `.python-version`; uv provisions it if necessary. Core setup downloads
dependencies but no inference models. The maintainer reports functional live
checks on Ubuntu x86_64; other hosts require their own device/runtime checks.

From the repository root:

```sh
uv sync --frozen
npm --prefix frontend ci
npm --prefix frontend run build
uv run lespeech serve
```

Open **http://127.0.0.1:8000**. Select an example, start replay, watch the audience
react (computed by the engagement engine from the example observations), and let
playback finish to see authored example coaching.
Stopping early leaves that example summary unavailable. The microphone and camera
stay off. Use the opt-in CPU launch below for live input.

### Try the current prototype

Select an example and press **Start replay**. The default 5× playback compresses
the 50-second "Finding your rhythm" example to about ten seconds; the displayed
times remain session times. Watch the eight listeners, reaction reasons, audience
timeline, example pace/fillers/facing metrics and transcript.

| Example / action | Expected behavior |
| --- | --- |
| Finding your rhythm (`weak_to_improved`) | NEUTRAL → CONFUSED at 20 s → BORED at 30 s → INTERESTED at 35 s → ENGAGED at 40 s. Finishing shows three authored coaching moments. |
| Stop early, then start another example | Early stop leaves example coaching unavailable; the next session clears the prior transcript and reactions. |
| Delayed transcript (`late_final_and_duplicates`) | The final text is "Our synthetic example is ready." Retries/revisions do not duplicate it; audience stays NEUTRAL and there are no supported coaching moments. |
| Speech with camera unavailable (`camera_unavailable`) | Camera status is unavailable; sustained fast speech still produces CONFUSED. Missing camera input alone is not negative evidence. |
| Unavailable inputs / An empty rehearsal | Audience stays NEUTRAL, missing metrics stay unknown, and completion invents no coaching moments. |

These are synthetic observations with computed reactions and authored example
coaching. Generated coaching can be checked against the same synthetic
observations through the existing engine/recorder/generator seam.

Exercise generated feedback and the in-memory recorder with devices off:

```sh
uv run python checks/coaching/feedback_replay.py --show-feedback
uv run python checks/coaching/record_replay.py
```

Each replay checks nine synthetic cases / ten sessions. The feedback replay
computes evidence-linked moments; plain browser replay displays authored examples.
Live mode uses the same sole recorder and generator. Existing browser checks
also cover connection recovery and a narrow screen. See [dated evidence](docs/STATUS.md#int-03-refreshed-package-and-browser-validation).

For frontend development, keep the backend running and use a second terminal:

```sh
npm --prefix frontend run dev
```

The development UI is at http://127.0.0.1:5173 and proxies the local API. The
built UI is served directly from the backend.

### Opt-in local CPU rehearsal

Prepare optional packages, build the UI and explicitly download models before
the first live rehearsal. Ubuntu needs the PortAudio system library
(`libportaudio2`); see [runtime setup](docs/LOCAL_RUNTIME.md).

```sh
uv sync --frozen --group speech --group vision
npm --prefix frontend ci
npm --prefix frontend run build
uv run --group speech --group vision python -m lespeech.speech.model --download
uv run --group speech --group vision python -m lespeech.speech.model --check
mkdir -p models
curl -L -o models/pose_landmarker_lite.task \
  https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task
uv run --group speech --group vision python -m lespeech.speech.probe --list-devices
uv run --group speech --group vision lespeech serve --live
```

Initial package/model preparation requires downloads. Prepared rehearsals use
local inference; session start does not download model weights. See
[demo host setup](docs/DEMO_HOST.md) for model paths and camera selection.
Set `LESPEECH_SPEECH_DEVICE` to a listed input index or name query before launch
if the system default is not the intended microphone.

Open **http://127.0.0.1:8000** and select **Live microphone and camera**.
Starting the session opens
the devices; stopping drains observations and generates evidence-linked template
coaching. Models warm before the API starts, with no automatic weight download or
raw recording. Missing inputs produce notices and coaching limitations. Actual
speech quality, concurrent responsiveness and final presenter/browser coaching
acceptance remain in [#11](https://github.com/crasni/LeSpeech/issues/11).
Camera direction is approximate; no eye tracking or emotion detection is claimed.
UGen300 inference remains unmeasured Stage II work.

Raw audio/video recording is off by default. Normalized observations, transcript
text and feedback are held transiently in memory for the current session,
replaced when a new session starts and released on application exit. Explicit
development exports belong in ignored `sessions/`; keep private media,
transcripts, credentials and weights out of Git.

Plain `lespeech serve` retains synthetic replay with authored example coaching.

### Headless replay and checks

```sh
uv run lespeech replay --case weak_to_improved
uv run python scripts/validate_fixtures.py
uv run python examples/consume_replay.py
uv run pytest -q
uv run ruff check src scripts tests examples
uv run python scripts/export_schema.py --check
npm --prefix frontend run types:check
```

Headless replay uses fake time and reports a delivery trace plus authored feedback.
Audience states are computed by the engagement engine; `--audience authored` keeps the
fixtures' authored transitions instead.
It is not a production session log or computed coaching. All nine reviewed cases
are available, including the multi-session `repeated_sessions` case. Explicit trace
exports can use `--output sessions/replay.json`; nothing is automatically persisted.

To regenerate contracts after an agreed interface change:

```sh
uv run python scripts/export_schema.py
npm --prefix frontend run types
```

Browser checks require a Playwright browser installation:

```sh
cd frontend
npx playwright install chromium
npm run test:e2e
```

They launch the loopback backend, check deterioration/recovery, stop/restart,
transcript revisions, an empty rehearsal, mobile layout, reconnection, and local-only
runtime requests. A system test browser can be selected with `LESPEECH_CHROMIUM_PATH`.
Browser checks require a free port 8000. In a restricted coding-agent sandbox,
HTTP/WebSocket tests may require permission to run outside the sandbox; the checks
do not contact external inference services.

### Subsystem handoff

Optional speech and vision runtimes are installed separately from the core app:

```sh
uv sync --frozen --group speech --group vision
```

See [local runtime setup](docs/LOCAL_RUNTIME.md) for configuration decisions,
system libraries, model preparation and the distinction between runtime setup
and actual device/model acceptance. After preparing assets, launch with `--live`
to select the delivered live composition.

[ARCHITECTURE.md](docs/ARCHITECTURE.md#int-01-implementation-decisions-and-handoff)
defines directories, protocols, clock/capture semantics, and transport boundaries.
Import executable types from `lespeech.contracts` and public seams from
`lespeech.contracts.interfaces`. Implement inside your assigned subsystem directory;
ask integration to add dependencies or change shared files.

The integrator supplies a fresh `Components` instance through
`SessionManager(factory)` / `create_app(factory)` for each session. The replay seam
also accepts a consumer factory, replacing authored audience/feedback with the
real engine and recorder/generator. [The subscription example](examples/consume_replay.py)
demonstrates consumption without importing model internals.

Speech and vision adapters, the sole deterministic engine and the sole
recorder/generator are delivered on main. Public integration seams and checks
are documented in the subsystem READMEs and local runtime setup. Component
delivery and synthetic checks do not complete final live or hardware acceptance;
follow the assigned GitHub Issues. Keep local rehearsal data, credentials and
weights out of Git, and follow the scoped publication rules in AGENTS.md.
