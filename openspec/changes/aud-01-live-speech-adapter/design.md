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

- Capture times are floored to the millisecond. Rounding to the nearest millisecond would stamp the capture-end window or final up to 0.5 ms after the controller's capture end, which the controller rejects.
- On the event loop, times are capped at the shared clock and, after stop, at the capture end. A fast audio clock therefore cannot stamp an observation in the future.
- **Alternative rejected:** wall-clock time in the audio callback. It adds callback jitter and would stamp observations with processing time rather than capture time.
- Drift between the audio clock and the monotonic clock is expected to be small for rehearsal-length sessions; the cap prevents future stamps, and AUD-02 measures the drift.

### Threads and emission

The PortAudio callback only copies frames into a queue. Two worker threads follow:

- A voice-activity thread segments audio in real time and advances the capture watermark.
- A transcription thread runs the shared model on closed segments and partial snapshots. Slow inference therefore never delays segmentation, pause onsets, or windows that do not wait on that speech.

Workers post their results to the loop captured in `start` with `loop.call_soon_threadsafe`. The utterance and metrics trackers run there, single-threaded, and emit through `context.emit`; workers never touch tracker state or call `emit`.

- When segmentation falls more than a bounded backlog behind, the adapter ends the affected utterance at the last processed audio, reports `audio_queue_overflow`, and stops capture for the rest of the session. Later audio could only be analyzed late, and the v0 rules have no recovery transition. Blocking the audio callback would lose audio anyway.
- **Alternatives rejected:**
  - asyncio-only processing: model inference is CPU-bound and would stall the API loop;
  - one worker for segmentation and transcription: every model call would delay segmentation by seconds and could trigger overflow.

### Process-wide model provider

A shared provider loads the Whisper model once per process, at composition time or through an explicit warm-up. `start` only opens the microphone and starts the worker. If the model is missing or failed to load, `start` emits `signal.status` error `speech_model_unavailable` and continues in unavailable mode.

A small speech-owned module (`python -m lecoach.speech.model --download`) pre-downloads weights into the ignored `models/` directory. Downloads never happen during a session: the provider loads only local files.

- `warm_up(config)` loads the model and runs one silent transcription at application startup. A cold `base.en` load took 14.7 s once in testing.
- `get_transcriber(config)` returns `None` when the runtime or model is missing, so composition still succeeds and the adapter reports the status.

- **Alternative rejected:** loading per session. It exceeds the 5 s startup bound and repeats work, because the factory runs per session.

### Production sources and checks

- `PortAudioSource` captures at 16 kHz in 32 ms blocks, or at the device's default rate with streaming linear resampling.
  - It reports a stream that stops by itself, or stalls for 2 s, as lost.
  - It reports exact digital silence for the first 2 s as `microphone_no_signal`. macOS delivers zeros instead of an error when access is denied.
  - It opens the system default input, or the device that `LECOACH_SPEECH_DEVICE` names by index or name. The application's composition therefore needs no device option; the probe's `--device` overrides the variable.
- `WavFileSource` replays a recording in real time through the same seam, so one take can be compared across models and settings.
- `python -m lecoach.speech.probe` runs the production adapter through the session controller with guided prompts. It reports delays and drain timing, and saves a stream for `check_speech.py`. It writes no audio.

### Degraded mode reports instead of raising

For permission denial, a missing or lost device, an unavailable model or voice activity runtime, digital-silence input, queue overflow, or a failed transcription or segmentation, the adapter emits a speech `signal.status` with a specific reason. Then it keeps emitting non-available windows with null values until stop, which matches the `microphone_denied` and `microphone_lost` fixtures. Degraded mode does not recover within a session.

- Raising from `start` would replace the specific reason with the controller's generic `adapter_start_failed`.
- The outage begins where segmentation stops, so no utterance is finalized after the reported outage start. After a transcription failure, finals without text are marked unmeasurable, and windows overlapping them report null rather than zero.
- Unexpected exceptions from `start` still propagate, so the controller's bounded cleanup applies, and speech emits nothing further.

### Segmentation and partial revisions

- **Segments.** Voice activity detection uses the Silero model bundled with faster-whisper, at 16 kHz in 32 ms frames.
  - The model state and frame context carry across chunks, so streaming gives exactly the whole-file probabilities.
  - Speech starts at probability ≥ 0.5, padded back 0.1 s, and never before the previous segment's end.
  - It ends 0.1 s after the first of 0.5 s of frames below 0.35.
  - A segment about to reach `max_utterance_s` is split at its quietest frame in the last 2 s. As a backstop, the adapter itself ends any segment that reaches `max_utterance_s` and starts a new one at the same capture time, so memory and final transcription time stay bounded with any segmenter.
- **Partials.** While a segment grows, it is re-transcribed every `partial_interval_s` to publish partial revisions (default 1.0 s; 0 disables partials). Finals come from one pass over the closed segment with word timestamps.
- **Decoding.** Partials use beam 1 and text only; finals use beam 5 with word timestamps. Decoding is greedy at temperature 0 and does not carry context between segments.
- **Hallucination guards.** Segments the model scores with `no_speech_prob ≥ 0.6` are dropped. On 2 s of silence, `base.en` produced "You" at 0.81, which Whisper's own combined log-probability rule keeps. An empty result is an empty final, which retracts any partial.
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
