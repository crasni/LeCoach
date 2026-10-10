# Speech adapter (AUD-01)

`lecoach.speech` turns microphone audio into v0 `speech.transcript`, `speech.metrics`, and speech `signal.status` events behind the INT-01 `CaptureAdapter` seam. [ARCHITECTURE.md](../../../docs/ARCHITECTURE.md) owns the event contract. The [speech checks README](../../../checks/speech/README.md) owns the v0 speech rules: windows, coverage, pauses, and null versus zero. [Issue #13](https://github.com/crasni/LeCoach/issues/13) owns status and acceptance. The plan is the OpenSpec change [`aud-01-live-speech-adapter`](../../../openspec/changes/aud-01-live-speech-adapter/).

**Current state.**
- The model-free core and the adapter lifecycle are merged (PR #26).
- The production pieces are implemented: the PortAudio microphone, streaming Silero voice activity detection, a shared faster-whisper transcriber, model preparation commands, a WAV replay source, and a guided probe.
- They were checked with the real packages and synthesized English speech (espeak-ng) on a Linux container that has **no microphone**.
- No real microphone capture has been verified yet; that live rehearsal is the remaining acceptance in #13.

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
| `adapter.py` | `SpeechAdapter`: lifecycle, worker threads, degraded mode, release, and emission delays |
| `sources.py` | `PortAudioSource` (microphone) and `WavFileSource` (real-time replay of a recording) |
| `vad.py` | `SpeechGate` (segment decisions) and `SileroSegmenter` (streaming Silero probabilities) |
| `whisper.py` | `WhisperTranscriber`, the process-wide model provider, and `warm_up` |
| `model.py` | `python -m lecoach.speech.model --download / --check` |
| `local.py` | `build_local_adapter()`: one production adapter per session |
| `probe.py` | `python -m lecoach.speech.probe`: guided live check and measurements |

Importing `lecoach.speech` or any module above loads no optional package. `sounddevice`, `numpy`, `faster_whisper`, and `onnxruntime` are imported only when a source opens, a segmenter is built, or a model loads.

## Set up a computer

1. Install the integration-owned `speech` dependency group: `uv sync --frozen --group speech`. The group comes from PR #23 (#6); until that merges, it exists only on `agent/integration`.
2. On Debian/Ubuntu, install PortAudio for `sounddevice`: `sudo apt-get install libportaudio2`. The macOS and Windows wheels bundle it.
3. Prepare the model once, outside any session:

   ```sh
   uv run --group speech python -m lecoach.speech.model --download   # about 145 MB into models/
   uv run --group speech python -m lecoach.speech.model --check      # load time, silent run
   ```

4. Check the microphone with the guided probe below. The operating system may ask for microphone permission on the first run.

## Seams and production implementations

- **`AudioSource`:** `PortAudioSource`.
  - `open(on_audio, on_error)` streams mono float32 at `sample_rate` (16 kHz), in 32 ms blocks on PortAudio's thread. If the device cannot capture at 16 kHz, it captures at the device's default rate and resamples (linear interpolation).
  - `open` raises `MicrophoneNotFound`, `MicrophonePermissionDenied`, or another `MicrophoneError`. It runs on the event loop inside the startup bound, so it must return promptly.
  - While running, these are reported through `on_error`:
    - a stream that stops by itself, or delivers no audio for 2 s: `MicrophoneLost`;
    - exact digital silence for the first 2 s: `MicrophoneNoSignal`. macOS delivers zeros when microphone access is denied.
  - `close()` aborts and closes the stream; it is idempotent.
  - `WavFileSource` replays a 16-bit PCM WAV in real time through the same seam.
- **`Segmenter`:** `SileroSegmenter` uses the Silero model bundled with faster-whisper, at 16 kHz in 512-sample (32 ms) frames.
  - Model state and frame context carry across chunks, so streaming gives exactly the whole-file probabilities.
  - `SpeechGate` decides the segments:
    - speech starts at probability ≥ 0.5, padded back 0.1 s;
    - it ends 0.1 s after the first of 0.5 s of frames below 0.35;
    - a segment about to reach `max_utterance_s` is split at its quietest frame in the last 2 s.
  - The adapter also ends any segment that reaches `max_utterance_s`, as a backstop for other segmenters.
- **`Transcriber`:** `WhisperTranscriber`, one preloaded model per process with one call at a time.
  - Partials decode with beam 1 and text only. Finals decode with beam 5 and word timestamps.
  - Decoding is greedy at temperature 0, with no carried context.
  - Segments the model scores with `no_speech_prob ≥ 0.6` are dropped: on silence, `base.en` otherwise transcribed "You". An empty result is an empty final, which retracts any partial.
  - It never downloads: `load_transcriber` reads `models/faster-whisper-<model>` with `local_files_only=True`.

## Compose a live session

```python
from lecoach.contracts.interfaces import Components
from lecoach.speech import SpeechConfig
from lecoach.speech.local import build_local_adapter
from lecoach.speech.whisper import warm_up

warm_up(SpeechConfig())  # once at application startup: load the model, run it once


def factory(session_config):
    if session_config.mode == "live":
        return Components(speech=build_local_adapter(), ...)  # one adapter per session
```

- Load the model at application startup, never in the factory or in `start`. A cold load took 14.7 s once in testing; the 5 s startup bound is for opening the microphone.
- `build_local_adapter()` never raises for missing parts. The adapter starts and reports the matching status instead:
  - no prepared model or runtime: `speech_model_unavailable`;
  - no Silero runtime: `speech_vad_unavailable`;
  - no PortAudio: `microphone_unavailable`;
  - no input device: `microphone_not_found`.
- Each adapter instance is single-use. `SessionManager` calls the factory once per session; `tests/test_speech_adapter.py` composes it that way with scripted seams.
- `adapter.delays` keeps, per emitted event, the shared clock at emission minus the event's capture time, for AUD-02 measurement.

## Guided live check

```sh
uv run --group speech python -m lecoach.speech.probe --list-devices
uv run --group speech python -m lecoach.speech.probe --out sessions/speech-probe.json
uv run --group speech python -m lecoach.speech.probe --wav take.wav --out sessions/replay.json
python3 checks/speech/check_speech.py --stream sessions/speech-probe.json --summary
```

The probe runs the production adapter through the real session controller.
- **Prompts:** it guides the speaker through normal pace, fast speech, deliberate fillers, 10 s of silence, and a stop while still speaking (about 70 s).
- **Live output:** it prints finals, windows, and statuses as they arrive.
- **Report:**
  - model load and session start time;
  - final delay after speech ends, and window delay after the window ends;
  - stop-and-drain time and incomplete sources;
  - per-part WPM, fillers, and pauses.
- **Saved files:** `--out` saves the event stream for `check_speech.py` and a `.summary.json`. Both contain transcripts, so keep them in the ignored `sessions/` directory. No audio is written.
- **Options:** `--device` selects an input by index or name. `--drain-timeout` changes the stop bound (default 2 s, like the app).

## Configuration

`SpeechConfig` is a strict model. Its defaults are the English Stage I baseline accepted in [issue #6](https://github.com/crasni/LeCoach/issues/6), and remain demo heuristics until AUD-02 recordings tune them.

| Field | Default | Meaning |
| --- | --- | --- |
| `language` | `en` | Analysis language. WPM and filler rules exist for English only. |
| `metrics_window_s` | 10.0 | Trailing window length |
| `metrics_hop_s` | 1.0 | Interval between windows (the fixtures use 5 s) |
| `min_observation_s` | 5.0 | Shorter periodic windows are skipped; shorter pause and capture-end windows report null WPM and fillers |
| `pause_min_s` | 1.0 | Shortest silence reported as a pause |
| `coverage_wait_s` | 3.0 | How long a window waits for the finals of overlapping speech before reporting null |
| `max_utterance_s` | 8.0 | Longest segment before a split |
| `partial_interval_s` | 1.0 | Re-transcribe a growing segment this often for live partials; 0 disables partials |
| `sample_rate` | 16000 | Analysis rate in Hz |
| `model`, `device`, `compute_type` | `base.en`, `cpu`, `int8` | Transcriber settings |
| `model_dir` | `models` | Where prepared models live; any relative or absolute path |

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
| `speech_vad_unavailable` | `error` | No segmenter (the Silero runtime is missing) |
| `microphone_permission_denied` | `unavailable` | The device reported a permission error when opening |
| `microphone_not_found` | `unavailable` | No input device, or no source is configured |
| `microphone_unavailable` | `unavailable` | Another device error, or PortAudio or the speech group is missing |
| `microphone_no_signal` | `unavailable` | The first 2 s were exact digital silence: access denied (macOS) or a muted device |
| `microphone_disconnected` | `error` | The stream stopped or stalled for 2 s; the utterance in progress ends at that time |
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

## Observed with synthesized speech (not microphone evidence)

These figures come from a Linux container with 4 CPUs, `base.en`/int8, and the speech group from PR #23. The input was a 27 s espeak-ng English talk replayed in real time with `--wav`.
- **Accuracy:** 4 accurate finals, and the shared checker passes.
- **Filler recall:** "Umm" was kept as a filler, but "uh" was dropped.
- **Delays:** finals arrived 2.5 s median and 3.4 s max after each sentence ended; windows arrived 0.36 s median after their end.
- **Model:** a warm model loaded in about 1 s, the first cold load took 14.7 s, and a final transcription took 1.4 s for 7 s of audio.

Real voices, rooms, microphones, and the demo computer will differ; AUD-02 (#14) measures them.

## Limitations

- **Live evidence:** no real microphone capture or recognition quality has been verified yet. Only the missing-device path ran against real PortAudio.
- **Language:** analysis is English only. Other languages get transcripts and pauses, with null WPM and fillers.
- **Fillers:** Whisper drops some fillers ("uh" above), so filler counts are likely undercounts until AUD-02 measures recall.
- **Permission detection:** detecting denied access through digital silence is a heuristic. A device that opens but stays near-silent without exact zeros is treated as quiet speech.
- **Recovery:** degraded mode does not recover; after a failure, speech stays unavailable until the session ends.
- **Timing:**
  - Final delays on a slow CPU can approach the 3 s coverage wait. Windows then report null instead of an undercount.
  - A final still running at stop can exceed the 2 s drain bound.
  - A long final delays the next partial, because one transcription thread serves both.
- **Clock:** windows start at session time 0, so the few milliseconds before the stream opens count as analyzed silence. Audio clock drift is capped at the shared clock but not corrected.

## Check it

From the repository root, in the core environment:

```sh
uv run pytest -q tests/test_speech_config.py tests/test_speech_text.py tests/test_speech_tracking.py \
  tests/test_speech_pipeline.py tests/test_speech_adapter.py tests/test_speech_production.py
uv run pytest -q
uv run ruff check src scripts tests examples
python3 checks/speech/check_speech.py
python3 checks/speech/make_fixtures.py --check
```

With the speech group, a prepared model, and optionally `espeak-ng` for the synthesized end-to-end test:

```sh
LECOACH_SPEECH_MODEL_DIR=models uv run --group speech pytest -q tests/test_speech_runtime.py
```

- The pipeline tests replay the fixture scenarios and compare the metric payloads with the committed fixtures.
- The adapter tests run the real worker threads and session controller with scripted seams. They pass every recorded stream through `checks/speech/check_speech.py`.
- The production tests cover segment decisions, error mapping, transcript filtering, model loading, and degraded composition without optional packages.
- The runtime tests check the following against the real packages:
  - Silero streaming against whole-file processing;
  - PortAudio handling, through a fake device module;
  - Whisper on silence and on synthesized English;
  - a synthesized talk through the full adapter and session controller.
