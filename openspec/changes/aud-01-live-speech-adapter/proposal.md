# Proposal

## Why

The audience can only react to real delivery if the rehearsal microphone produces timestamped transcripts and pace, filler, and pause observations locally. AUD-01 delivers that live speech producer. The INT-01 scaffold and executable v0 contracts are on main (PR #4), and the synthetic speech preparation and checks are merged (PR #3). The producer can now target the published `CaptureAdapter` seam. Analysis language, speech configuration defaults, and speech dependencies are still open in issue #6.

## What Changes

- Add a live speech adapter in `src/lecoach/speech/` that implements `start` / `stop_capture` / `drain` for local microphone capture against `SessionContext`.
- Segment captured audio with voice activity detection. Transcribe each segment locally with Whisper word timestamps, and publish canonical `speech.transcript` partial revisions and finals.
- Compute `speech.metrics` (WPM, fillers, pauses) from finalized words, following the rules proven by `checks/speech/`: null versus zero, finalized coverage, and one event per completed pause. Parameters come from a speech configuration object.
- Report device and model failures as `signal.status`, with unavailable metrics. Release the microphone on stop, failure, and cancellation. Drain pending speech within the session's stop bound.
- Keep the issue #6 decisions configurable until they are resolved:
  - analysis language;
  - timing defaults: window, hop, minimum observation, pause minimum, coverage wait, maximum utterance length;
  - the optional speech dependency group requested from integration.
- Test without models or devices: injected synthetic audio and transcriber fakes. Recorded live output is checked with `checks/speech/check_speech.py --stream`.
- Out of scope for this change:
  - engagement rules and thresholds (Lane 4);
  - recording and feedback (Lane 5);
  - composing the adapter into the live application factory (integration);
  - UGen300 acceleration and AUD-02 latency/filler measurement;
  - Mandarin analysis.

## Capabilities

### New Capabilities

- `speech-capture`: Local microphone capture behind the session adapter seam. Covers startup and shutdown ordering, capture-time mapping onto the shared clock, input availability reporting, resource release, and local-only processing.
- `speech-observations`: Canonical transcript revisions and speech metrics produced from local transcription. Covers revision freezing, finalized-word metrics, null versus zero, coverage, pause reporting, and unsupported language handling.

### Modified Capabilities

None. The change uses the v0 event shapes and session lifecycle from INT-01 without changing them.

## Impact

- **Code:** new modules under `src/lecoach/speech/` and speech tests under `tests/`. No change to `src/lecoach/contracts/` unless integration places the speech configuration there (issue #6).
- **Dependencies:** an optional `speech` group (`faster-whisper`, `sounddevice`, `numpy`) added by integration. Core setup and the default test suite stay model-free and device-free.
- **Runtime:**
  - Model weights download once into the ignored `models/` directory, and inference runs locally.
  - No audio or transcript is persisted by default.
  - Model loading happens before session start, so the 5 s startup bound and the 2 s stop/drain bound are not spent on downloads.
- **Coordination:**
  - Issue #6 decides language, defaults, and dependencies.
  - Integration composes `Components(speech=...)` for live mode.
  - Issue #13 records ownership, status, and acceptance; STATUS.md keeps dated evidence.
