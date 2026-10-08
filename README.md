# LeCoach

Your Private AI Audience.

LeCoach is a local, multimodal presentation coach for the ASUS UGen AI League Hackathon 2026. It combines speech and body-language signals to make a virtual audience react in real time, then highlights specific moments and practical improvements after each rehearsal.

## MVP

- Local speech transcription, speaking pace, fillers, and pauses.
- Webcam-based pose, approximate facing direction, and gesture activity.
- A deterministic engagement engine with smooth audience reactions.
- A synchronized session timeline and concise, actionable feedback.

Target track: Workplace AI / Battlefield Lightning, with ASUS UGen300 as the intended accelerator. Hardware integration and performance remain to be validated.

## Project status

The current prototype has validated event contracts, session lifecycle, a loopback
API, a deterministic engagement engine and a rehearsal screen driven by synthetic
observations. An in-memory recorder is available through injection. Live microphone,
camera and coaching generation await their assigned subsystem handoffs.

Start at [AGENTS.md](AGENTS.md), the shared entry point for all five collaborators. Follow the canonical documents linked there:

- [GUIDE.md](GUIDE.md): agreed product scope and priorities.
- [GitHub Issues](https://github.com/crasni/LeCoach/issues?q=is%3Aissue+label%3Acoordination): assignments, branches, live status, blockers and acceptance.
- [Architecture](docs/ARCHITECTURE.md): shared event contracts.
- [Implementation evidence](docs/STATUS.md): dated checks and limitations, not live task state.
- [Lane boundaries](docs/AGENT_ROLES.md): stable responsibilities; assigned Issues provide the handoff.

Official competition and hardware reference PDFs are in [docs/](docs/).

## Development

Prerequisites: [uv](https://docs.astral.sh/uv/), Node.js 24, and npm. Python 3.12.14
is pinned in `.python-version`; uv provisions it if necessary. Core setup downloads
dependencies but no inference models. Tested on Linux x86_64; live device/platform
setup is not established by the scaffold.

From the repository root:

```sh
uv sync --frozen
npm --prefix frontend ci
npm --prefix frontend run build
uv run lecoach serve
```

Open **http://127.0.0.1:8000**. Select an example, start replay, watch the audience
react (computed by the engagement engine from the example observations), and let
playback finish to see authored example coaching.
Stopping early leaves that example summary unavailable. The microphone and camera
stay off. Live mode is unavailable in the default composition.

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
coaching. Example coaching timestamps still need Lane 5's reconciliation with the
computed transitions. Live capture, transcription, pose inference, generated
coaching and UGen300 execution cannot be tested in the default app yet.

The recorder can be exercised separately, without recording media:

```sh
uv run python checks/coaching/record_replay.py
```

It checks the actual in-memory recorder against nine synthetic cases / ten sessions;
the default browser composition does not use this recorder. Existing browser checks
also cover connection recovery and a narrow screen. See [current evidence](docs/STATUS.md#int-03-refreshed-package-and-browser-validation).

For frontend development, keep the backend running and use a second terminal:

```sh
npm --prefix frontend run dev
```

The development UI is at http://127.0.0.1:5173 and proxies the local API. The eventual
demo uses the built UI served directly from the backend.

### Headless replay and checks

```sh
uv run lecoach replay --case weak_to_improved
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
runtime requests. A system test browser can be selected with `LECOACH_CHROMIUM_PATH`.
Browser checks require a free port 8000. In a restricted coding-agent sandbox,
HTTP/WebSocket tests may require permission to run outside the sandbox; the checks
do not contact external inference services.

### Subsystem handoff

[ARCHITECTURE.md](docs/ARCHITECTURE.md#int-01-implementation-decisions-and-handoff)
defines directories, protocols, clock/capture semantics, and transport boundaries.
Import executable types from `lecoach.contracts` and public seams from
`lecoach.contracts.interfaces`. Implement inside your assigned subsystem directory;
ask integration to add dependencies or change shared files.

The integrator supplies a fresh `Components` instance through
`SessionManager(factory)` / `create_app(factory)` for each session. The replay seam
also accepts a consumer factory, replacing authored audience/feedback with the
real engine and recorder/generator. [The subscription example](examples/consume_replay.py)
demonstrates consumption without importing model internals.

Lane 5's preparation files in `checks/coaching/` are reused unchanged from PR #1
(`dcc280f`, preparation head `b8f5597`), now merged as preparation. Lane 2's
synthetic checks in `checks/speech/` are merged through PR #3. These merges do
not complete the live speech or coaching implementations. Positive reason codes
still require Lane 4's handoff. Keep local rehearsal data, credentials, and weights
out of Git, and follow the scoped publication rules in AGENTS.md.
