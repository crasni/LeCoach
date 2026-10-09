# Speech adapter (AUD-01)

`lecoach.speech` turns microphone audio into v0 `speech.transcript`, `speech.metrics`, and speech `signal.status` events behind the INT-01 `CaptureAdapter` seam. [ARCHITECTURE.md](../../../docs/ARCHITECTURE.md) owns the event contract. The [speech checks README](../../../checks/speech/README.md) owns the v0 speech rules: windows, coverage, pauses, and null versus zero. [STATUS.md](../../../docs/STATUS.md) records what has been verified. The plan is the OpenSpec change [`aud-01-live-speech-adapter`](../../../openspec/changes/aud-01-live-speech-adapter/).

**Current state.** The model-free core and the adapter lifecycle are implemented and tested with scripted seams. The production microphone source, voice activity detection, and faster-whisper transcriber do not exist yet. They wait for the [issue #6](https://github.com/crasni/LeCoach/issues/6) decisions and the optional `speech` dependency group (task group 4 of the change). Nothing in this package has captured real audio or run a model.

## Layout

| Module | Responsibility |
| --- | --- |
| `config.py` | `SpeechConfig`, the one place for analysis and model settings |
| `text.py` | English tokenizer and filler lexicon; a parity test keeps it equal to `checks/speech/speech_text.py` |
| `tracking.py` | Utterance revisions: monotonic partials, one final, empty-final retraction |
| `metrics.py` | Windows, coverage, pauses, and null rules, matching the fixture generator |
| `emitter.py` | v0 envelopes, stable event IDs, and millisecond capture times |
| `pipeline.py` | Single-threaded composition of the three above; each call returns the events to emit |
| `seams.py` | `AudioSource`, `Segmenter`, and `Transcriber` protocols, and microphone errors |
| `adapter.py` | `SpeechAdapter`: lifecycle, worker threads, degraded mode, and release |

Importing `lecoach.speech` loads no optional package. Production seams must import `sounddevice`, `numpy`, or `faster_whisper` lazily, inside their own modules.

## Seams

- **`AudioSource`**
  - `open(on_audio, on_error)` starts streaming mono float frames at `sample_rate`. `on_audio` runs on the device thread; the adapter only queues the frames.
  - `open` raises `MicrophonePermissionDenied`, `MicrophoneNotFound`, or another `MicrophoneError` when the device cannot start. It runs on the event loop inside the startup bound, so it must return promptly.
  - A device lost mid-session is reported with `on_error(MicrophoneLost())`.
  - `close()` is idempotent and must tolerate a failed `open`. After any `open` attempt, the adapter calls it exactly once.
- **`Segmenter`** (voice activity detection)
  - `process(samples, first_frame)` returns `Boundary("start" | "end", frame)` with absolute frame indexes. A start may lie up to `lookback_s` before the current chunk.
  - `flush(end_frame)` closes an open segment at capture end, device loss, or overflow.
  - It splits segments longer than `max_utterance_s`, ideally at a quiet frame. As a backstop, the adapter ends any segment that reaches that length at the current audio and starts a new one there.
- **`Transcriber`**
  - Loaded once per process and shared by sessions. `ready` is true once the model can run.
  - `transcribe(samples, sample_rate, final)` returns `Transcription(text, words, language)`. Word times are relative to the segment audio. Empty text means no speech and retracts any partial.
  - It runs on the transcription thread, may take seconds, and must never download weights.

## Compose a live session

```python
from lecoach.contracts.interfaces import Components
from lecoach.runtime.session import SessionManager
from lecoach.speech import SpeechAdapter, SpeechConfig

speech_config = SpeechConfig()
transcriber = load_transcriber(speech_config)  # once, at application startup (group 4)


def factory(session_config):
    adapter = SpeechAdapter(speech_config, open_source(speech_config),
                            new_segmenter(speech_config), transcriber)
    return Components(speech=adapter)  # plus the vision, engagement, and logging parts


manager = SessionManager(factory)
```

- Load and warm up the transcriber at application startup, not in the factory. `SessionManager` calls the factory once per session, and `start` must finish within `startup_timeout_s` (5 s by default).
- If the transcriber is missing or not `ready`, the session still starts and speech reports `speech_model_unavailable`.
- Create the source and segmenter per session; they hold device and stream state.
- `load_transcriber`, `open_source`, and `new_segmenter` are placeholders for the group 4 implementations. `tests/test_speech_adapter.py` composes `SessionManager` the same way with scripted seams.

## Configuration

`SpeechConfig` is a strict model. Defaults are the issue #6 proposal and remain demo heuristics until the team records a decision.

| Field | Default | Meaning |
| --- | --- | --- |
| `language` | `en` | Analysis language. WPM and filler rules exist for English only. |
| `metrics_window_s` | 10.0 | Trailing window length |
| `metrics_hop_s` | 1.0 | Interval between windows (the fixtures use 5 s) |
| `min_observation_s` | 5.0 | Shorter periodic windows are skipped; shorter pause and capture-end windows report null WPM and fillers |
| `pause_min_s` | 1.0 | Shortest silence reported as a pause |
| `coverage_wait_s` | 3.0 | How long a window waits for the finals of overlapping speech before reporting null |
| `max_utterance_s` | 8.0 | The segmenter splits longer segments |
| `partial_interval_s` | 1.0 | Re-transcribe a growing segment this often for live partials; 0 disables partials |
| `sample_rate` | 16000 | Capture rate in Hz |
| `model`, `device`, `compute_type`, `model_dir` | `base.en`, `cpu`, `int8`, `models` | Transcriber settings for group 4 |

`SpeechAdapter` also takes these options:

- `max_backlog_chunks` (200): queued audio chunks allowed before overflow;
- `idle_tick_s` (0.1 s): how often degraded mode checks the clock for due windows;
- `lookback_s` (1.0 s): audio kept before the current chunk for a segment start.

## Capture time

- A sample's capture time is the clock reading at `start` plus the samples delivered before it divided by the sample rate, floored to the millisecond. Transcription delay never changes a timestamp.
- On the event loop, times are capped at the shared clock, so a fast audio clock cannot stamp the future. After `stop_capture`, they are capped at the capture end.
- Audio after the capture end is discarded, and an utterance in progress ends there.

## Failure reasons

| Reason | Availability | When |
| --- | --- | --- |
| `speech_model_unavailable` | `error` | The transcriber is missing or not ready at start; the microphone is not opened |
| `microphone_permission_denied` | `unavailable` | `open` raised `MicrophonePermissionDenied` |
| `microphone_not_found` | `unavailable` | `open` raised `MicrophoneNotFound`, or no source or segmenter is configured |
| `microphone_unavailable` | `unavailable` | `open` raised another `MicrophoneError` |
| `microphone_disconnected` | `error` | The source reported `MicrophoneLost`; the utterance in progress ends at that time |
| `audio_queue_overflow` | `error` | Segmentation fell more than `max_backlog_chunks` behind; the utterance in progress ends at the last processed audio |
| `transcription_failed` | `error` | The model raised; later finals are empty, and windows overlapping them report null |
| `speech_segmentation_failed` | `error` | The segmenter raised; the utterance in progress ends with an empty final |

In each case the adapter releases the microphone and emits one status, at the capture time where analysis stopped. Later windows report that availability with null values and an `unknown` pause, and the session continues for other inputs. Any other exception from `start` propagates. The controller then reports `adapter_start_failed`, and speech emits nothing further.

## Stop, drain, and release

- `stop_capture(capture_end_s)` cuts queued audio at the capture end and closes the microphone.
- `drain()` waits for segmentation and transcription to finish, then emits the remaining windows, including the final window at capture end.
- If the controller's shared stop/drain bound (2 s by default) expires first, it cancels drain. The adapter emits nothing more, and the controller lists speech in `incomplete_sources`.
- Both calls are idempotent. The microphone is closed exactly once, including after cancellation. The worker threads are daemons; each exits after its current model call.
- Audio and transcripts stay in memory. The adapter writes no files.

## Limitations

- It is not live yet: there is no production source, segmenter, or transcriber. Latency, drain time, and accuracy are unmeasured on CPU and on UGen300 (AUD-02).
- Analysis is English only. Other languages get transcripts and pauses, with null WPM and fillers.
- Whisper may omit fillers, so filler counts can be undercounts until AUD-02 measures recall.
- Degraded mode does not recover: after a failure, speech stays unavailable until the session ends.
- Windows start at session time 0, so the few milliseconds before the stream opens count as analyzed silence.
- Audio clock drift is capped at the shared clock but not corrected; AUD-02 measures it.
- One transcription thread serves partials and finals, so a long final delays the next partial.

## Check it

From the repository root:

```sh
uv run pytest -q tests/test_speech_config.py tests/test_speech_text.py \
  tests/test_speech_tracking.py tests/test_speech_pipeline.py tests/test_speech_adapter.py
uv run pytest -q
uv run ruff check src scripts tests examples
python3 checks/speech/check_speech.py
python3 checks/speech/make_fixtures.py --check
```

- The pipeline tests replay the fixture scenarios and compare the metric payloads with the committed fixtures.
- The adapter tests run the real worker threads and session controller with scripted seams. They pass every recorded stream through `checks/speech/check_speech.py`.
