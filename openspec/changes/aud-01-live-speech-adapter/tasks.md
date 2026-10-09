# Tasks

Groups 1–3 are model-free and device-free, and can proceed while issue #6 is open. Group 4 starts only after issue #6 records the language and default decisions and integration adds the optional speech dependency group. [Issue #13](https://github.com/crasni/LeCoach/issues/13) owns status, blockers, remaining work, and acceptance; this checklist is a work breakdown. Publication follows [AGENTS.md](../../../AGENTS.md#scoped-autonomous-branch-publication).

## 1. Configuration and text rules

- [x] 1.1 Add a strict `SpeechConfig` in `src/lecoach/speech/config.py`. Defaults come from the issue #6 proposal (`en`, window 10 s, hop 1 s, minimum observation 5 s, pause minimum 1 s, coverage wait 3 s, maximum utterance 8 s), and the model, device, sample-rate, and partial-interval fields are documented. Verify that `tests/test_speech_config.py` covers defaults and rejects non-positive values and a hop longer than the window.
- [x] 1.2 Move the English tokenizer and filler lexicon into `src/lecoach/speech/text.py`. Verify that a parity test gives identical word and filler counts with `checks/speech/speech_text.py` for every fixture transcript and the existing tokenizer test sentences.

## 2. Model-free transcript and metrics tracking

- [x] 2.1 Implement utterance tracking from segment and transcription results:
  - monotonic partial revisions;
  - a single final per utterance;
  - empty-final retraction;
  - non-overlapping finals.

  Verify with unit tests for a corrected partial, a retracted hallucination, and no revision after a final.
- [x] 2.2 Implement metrics tracking:
  - trailing window and hop;
  - a window ends at the start of an in-progress utterance;
  - non-advancing and short windows are skipped;
  - minimum observation and coverage wait;
  - active and completed pauses after the first speech;
  - a final window at capture end;
  - unsupported-language and unavailable-input nulls.

  Verify that a parity test replays the `checks/speech/make_fixtures.py` scenarios and reproduces the committed fixture metric payloads.
- [x] 2.3 Implement the event emitter with v0 envelopes and stable IDs (`u<n>-r<revision>`, `metrics-<end>`, `pause-<end>`, `speech-status-<n>`). Verify that every emitted event passes `parse_event`, and that replayed tracker streams pass `checks/speech/check_speech.py --stream`.

## 3. Adapter lifecycle with injected seams

- [x] 3.1 Define `AudioSource`, segmenter, and `Transcriber` protocols, with scripted test doubles under `tests/`. Verify that `lecoach.speech` imports and the default `uv run pytest -q` passes without `faster-whisper`, `sounddevice`, or `numpy` installed.
- [x] 3.2 Implement `SpeechAdapter.start` / `stop_capture` / `drain`:
  - capture time from sample offsets on the shared clock;
  - a voice-activity worker thread and a transcription worker thread;
  - emission through `call_soon_threadsafe`.

  Verify with fake-source tests that observations carry capture times, start returns within the startup bound, and nothing is emitted after capture end.
- [x] 3.3 Implement degraded mode and release:
  - specific `signal.status` reasons for permission denial, missing or lost device, unavailable model, and audio queue overflow;
  - null windows while unavailable;
  - idempotent, cancellation-safe cleanup.

  Verify with `SessionController` tests for each failure, a single microphone release on repeated stop or cancelled drain, and speech listed as incomplete when drain exceeds the bound.
- [x] 3.4 Document the adapter seams, configuration, failure reasons, and limitations in `src/lecoach/speech/README.md`. Verify that the documented test and check commands run as written.

## 4. Production microphone and local transcription

- [ ] 4.1 Apply the issue #6 decisions to `SpeechConfig` defaults and the speech README. Verify that the configuration tests and documentation state the decided language and values, and link the issue.
- [ ] 4.2 Implement the PortAudio microphone source with the integration-added optional `speech` group. Verify that a smoke test skips cleanly when the group is absent, and that a manual check on the development host captures audio and reports a denied or missing device as a status.
- [ ] 4.3 Implement the process-wide model provider, the faster-whisper transcriber with word timestamps and bundled voice activity detection, and `python -m lecoach.speech.model --download` into the ignored `models/` directory. Verify that a smoke test on generated silence produces no speech segments or an empty final, and that `start` performs no download.
- [ ] 4.4 Run a live microphone rehearsal on the development host and export the speech stream to the ignored `sessions/` directory. Verify that `checks/speech/check_speech.py --stream` passes, and record the host, model, configuration, and observed limitations in STATUS.

## 5. Integration handoff

- [ ] 5.1 Provide the live composition instructions for `Components(speech=SpeechAdapter(...))`, including model warm-up before session start. Verify that a test composes `SessionManager` with the adapter and scripted sources, and receives speech events end to end.
- [ ] 5.2 Update Issue #13 and the dated STATUS evidence with commands, results, and limitations: fixture versus live, CPU only, and the filler undercount risk. Verify that every claim matches the latest check output.
- [ ] 5.3 Prepare reviewable commits authored by the owner and publish them to `agent/audio-streaming` under the AGENTS.md scoped publication policy. Open a scoped PR that refs #13, and record it on Issue #13.

## Workflow follow-up

- AUD-02 (latency, drain timing, filler recall, model size) is a separate change after a live rehearsal works.
- Archive this change with the archive workflow only after review and merge; verify the resulting main `speech-capture` and `speech-observations` specs.
