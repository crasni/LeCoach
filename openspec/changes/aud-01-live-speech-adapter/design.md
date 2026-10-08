# Design

## Context

See [proposal.md](proposal.md#why) for motivation and [the specs](specs/) for required behavior. The design is shaped by these facts on main (`ebdf421`):

- **Adapter seam.** `CaptureAdapter` (`src/lecoach/contracts/interfaces.py`) exposes `async start(context)`, `async stop_capture(capture_end_s)`, and `async drain()`.
- **Startup.** The controller (`src/lecoach/runtime/session.py`) bounds each adapter's start by `startup_timeout_s` (5 s). A start that fails or times out gets a generic `adapter_start_failed` status, and the controller then calls `stop_capture`.
- **Shutdown.** `stop_capture` and `drain` share one `drain_timeout_s` budget (2 s). Adapters that time out are cancelled and listed in `incomplete_sources`.
- **Emission.** `SessionContext.emit` is synchronous. It validates and publishes on the controller's event loop, and drops events after capture end or completion. ARCHITECTURE requires worker threads to marshal emissions back onto that loop.
- **Per-session components.** `SessionManager` calls the integration factory once per session, so per-session objects must not own expensive model state.
- **Fixed v0 shapes.** `checks/speech/` already proves the transcript, metrics, and pause semantics with fixtures and a producer checker (37 tests).
- **Dependencies.** The core lockfile excludes model and capture packages; additions go through integration.

## Goals / Non-Goals

**Goals:**
- Keep every decision-dependent value in one speech configuration, so issue #6 outcomes are configuration edits.
- Make the transcript and metrics logic model-free, deterministic, and testable with a fake clock and synthetic word timings.
- Keep devices and models behind narrow seams, so tests run without them and a UGen300 transcriber can replace the CPU one later.

**Non-Goals:**
- Choosing engagement thresholds.
- Editing the shared session controller, event schema, application factory, or root manifests.
- Streaming partial-word agreement algorithms.
- Speaker diarization.
- Audio recording or export features.

## Decisions

### Pipeline of small injected stages

`SpeechAdapter` composes five stages:

```
AudioSource → Segmenter (voice activity) → Transcriber → UtteranceTracker → MetricsTracker
```

- An emitter stamps envelopes and stable IDs. IDs follow the fixtures' `u<n>-r<revision>`, `metrics-<end>`, `pause-<end>`, and `speech-status-<n>`.
- `AudioSource` and `Transcriber` are protocols. Production uses a PortAudio microphone source and a faster-whisper transcriber; tests use scripted sources and fake transcribers.
- **Alternative rejected:** an all-in-one streaming library such as whisper_streaming or WhisperLive. It adds heavy dependencies, its revision semantics differ from the v0 contract, and it is hard to test without models.

### Capture time from sample offsets

At stream start, the adapter records the shared clock value and the frame counter. A sample's capture time is that value plus elapsed frames divided by the sample rate. Segment boundaries, word times (segment start plus model word offset), and window ends all derive from this mapping.

- **Alternative rejected:** wall-clock time in the audio callback. It adds callback jitter and would stamp observations with processing time rather than capture time.
- Drift between the audio clock and the monotonic clock is negligible for rehearsal-length sessions; AUD-02 measures it.

### Threads and emission

The PortAudio callback copies frames into a bounded queue. One worker thread runs voice activity detection, transcription, and tracking.

- Each event is handed to the controller with `loop.call_soon_threadsafe(context.emit, event)`, using the loop captured in `start`. The worker never calls `emit` directly.
- Queue overflow drops the oldest audio, raises an error status, and ends the affected utterance. Blocking the audio callback would lose audio anyway.
- **Alternative rejected:** asyncio-only processing. Model inference is CPU-bound and would stall the API loop.

### Process-wide model provider

A shared provider loads the Whisper model once per process, at composition time or through an explicit warm-up. `start` only opens the microphone and starts the worker. If the model is missing or failed to load, `start` emits `signal.status` error `speech_model_unavailable` and continues in unavailable mode.

A small speech-owned module (`python -m lecoach.speech.model --download`) pre-downloads weights into the ignored `models/` directory. Downloads never happen during a session.

- **Alternative rejected:** loading per session. It exceeds the 5 s startup bound and repeats work, because the factory runs per session.

### Degraded mode reports instead of raising

For permission denial, a missing device, or an unavailable model, the adapter emits a speech `signal.status` with a specific reason. Then it keeps emitting non-available windows with null values until stop, which matches the `microphone_denied` and `microphone_lost` fixtures.

- Raising from `start` would replace the specific reason with the controller's generic `adapter_start_failed`.
- Unexpected exceptions still propagate, so the controller's bounded cleanup applies.

### Segmentation and partial revisions

- **Segments.** Voice activity detection uses the Silero model bundled with faster-whisper, at 16 kHz in 32 ms frames. A segment ends after a short hangover of trailing silence. A segment longer than `max_utterance_s` is split at its quietest recent frame.
- **Partials.** While a segment grows, it is re-transcribed every `partial_interval_s` to publish partial revisions (default 1.0 s; 0 disables partials). Finals come from one pass over the closed segment with word timestamps.
- **Hallucination guards.** The no-speech threshold and empty results produce an empty final, which retracts any partial.
- **Alternative rejected:** finals-only. The live transcript view (Lane 4) needs partials. The cost is bounded by the interval and can be disabled if AUD-02 shows CPU pressure.

### Metrics engine mirrors the fixture rules

`MetricsTracker` consumes segment boundaries and finalized words in capture time. It applies the rules already used to generate `checks/speech/fixtures`:

- trailing window and hop;
- a window ends where an in-progress utterance began;
- non-advancing windows are skipped;
- minimum observation;
- coverage wait for overlapping finals;
- active and completed pauses after the first speech;
- a final window at capture end.

A parity test replays the fixture scenario scripts through `MetricsTracker` and compares its metric payloads with the committed fixtures. Every emitted stream is also checked with `checks/speech/check_speech.py` and `parse_event`.

- **Alternative rejected:** re-deriving rules ad hoc. It risks drifting from the reviewed fixtures that Lanes 4 and 5 consume.

### Text rules move into the package

The English tokenizer and filler lexicon become production code in `lecoach.speech.text`. `checks/speech/speech_text.py` stays a standard-library copy, so the checker still runs without installing the package. A parity test compares both on a shared corpus.

- **Alternative rejected:** importing `checks/` from production code. Production should not depend on test utilities.

### Speech-owned configuration until issue #6 decides

`SpeechConfig`, a strict Pydantic model in `lecoach.speech.config`, holds:

- `language`, `metrics_window_s`, `metrics_hop_s`, `min_observation_s`, `pause_min_s`, `coverage_wait_s`, `max_utterance_s`;
- model name, device, and compute type;
- sample rate and `partial_interval_s`.

Defaults are the issue #6 proposal. The adapter takes the config in its constructor. If integration moves it into `contracts/interfaces.py`, only the import changes.

### Optional dependencies, lazy imports

`faster-whisper`, `sounddevice`, and `numpy` are imported only inside the production source and transcriber modules. Integration adds them as an optional `speech` group. The core install, default pytest run, and checks keep working without them; production-only smoke tests skip when they are missing.

## Risks / Trade-offs

- [CPU finalization of the last utterance may exceed the 2 s drain budget] → keep segments short with `max_utterance_s`, start with `base.en`, and transcribe on segment close rather than at stop. AUD-02 measures and may request a larger bound from integration.
- [Whisper may omit fillers] → document filler counts as possible undercounts, measure recall in AUD-02, and leave prompt or model alternatives to that evidence.
- [Partial re-transcription costs CPU] → make the interval configurable, allow finals-only, and measure in AUD-02.
- [PortAudio setup differs per OS] → report device errors as statuses, and document the Linux system library (`libportaudio2`) and permission prompts in setup instructions.
- [Model download size and time] → pre-download outside sessions, keep weights in ignored `models/`, and never download during `start`.
- [Audio queue overflow under load] → bounded queue, an error status, and utterance closure instead of silent gaps.
- [Fixture-rule parity could hide shared mistakes] → also validate with the independent checker and `parse_event`, and with recorded live sessions in AUD-02.

## Migration Plan

1. Land the model-free core with tests and parity checks: configuration, text rules, utterance and metrics trackers, emitter, adapter lifecycle with scripted sources, and degraded mode. No live composition yet.
2. After issue #6 decides language and defaults and integration adds the optional dependency group, add the production microphone source, model provider, and transcriber. Keep the fake-based tests.
3. Integration composes `Components(speech=SpeechAdapter(...))` in the live factory. Pushes and PRs follow AGENTS.md approval.
4. AUD-02 measures latency, drain timing, and filler recall on the development host.

Rollback: omit the speech adapter from the factory; live speech then reports `adapter_not_integrated`. No data migration is involved.

## Open Questions

- Final default values and analysis language (issue #6). They are configuration values, so the structure and tasks do not change.
- Whether `SpeechConfig` stays speech-owned or moves into `contracts/interfaces.py` (issue #6). This is an import move.
- Model size (`base.en` versus `small.en`) and whether `small.en` fits the drain budget, settled by AUD-02 measurements.
