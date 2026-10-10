# AUD-01 speech preparation: fixtures, checks, and proposed v0 rules

These are Lane 2 preparation artifacts. INT-01's scaffold is now available on main through PR #4; a live adapter and agreed analysis configuration remain pending. Every event is
synthetic. `make_fixtures.py` generates the fixtures from hand-written scenario
scripts; no microphone, audio file, speech model, or accelerator was used. This
directory has no speech adapter, session controller, replay clock, logger, or
engagement engine. Application language and directories remain Lane 1's
decision, and [ARCHITECTURE.md](../../docs/ARCHITECTURE.md) remains the
contract authority.

The model-free speech core in [`src/lecoach/speech/`](../../src/lecoach/speech/README.md)
implements these rules, and a parity test replays every scenario below through it.

`fixtures/*.json` are arrays of v0 events in **delivery order**, one event per
line. Each fixture is a complete session (`session.started` to
`session.completed`) carrying only speech and lifecycle events, so Lanes 4 and 5
can replay realistic speech input before the live adapter exists.
`expectations.json` is a hand-derived oracle of what a consumer should
reconstruct from each case. It is test-only metadata, not another contract.

## Run the checks

From the repository root, using Python 3.10+ and its standard library (tested
with 3.11, 3.12, and 3.13):

```sh
python3 checks/speech/check_speech.py
python3 -m unittest discover -s checks/speech -p 'test_*.py' -v
python3 checks/speech/make_fixtures.py --check
```

The first command checks every fixture against the speech contract checks and
its oracle. The default `uv run pytest -q` also includes these speech tests.
The second confirms that the checker rejects representative faulty
producer output. The third confirms that the committed fixtures match the
scenario scripts. Passing them establishes **test-artifact consistency**, not
working microphone capture, transcription, or latency.

## Cases

| Case | Exercises | Consumer expectation |
| --- | --- | --- |
| `steady_pace` | About 110-130 WPM, one hesitation, three sentence pauses, a partial corrected by its final | Count finals once; show the corrected text |
| `rapid_speech` | Pace rising from about 110 to 234 WPM with only short gaps | High-pace evidence without completed pauses |
| `filler_heavy` | 11 fillers in 37 words, about 24-29 fillers per minute | Filler evidence comes from finalized text only |
| `prolonged_silence` | A 10.8 s silence reported active while it grows, then completed | Silence is measured: WPM is 0, not null |
| `delivery_effects` | Model warm-up, stale partial after its final, identical retry, hallucinated partial retracted by an empty final, out-of-order pause metrics, final drained after stop | Ignore old revisions and retries; order by capture time; a null coverage window is unknown, not slow |
| `microphone_denied` | Permission denied at start | Unavailable input is not poor delivery |
| `microphone_lost` | Disconnect mid-utterance; the cut utterance is finalized | Keep earlier evidence; later windows are unknown |
| `silence_only` | Working capture, the speaker never starts | 0 WPM and no pause before the first speech |
| `unsupported_language` | Mandarin speech outside the v0 English rules | Transcripts and pauses only; WPM and fillers stay null |
| `repeated_sessions` | Two sessions reusing clocks, event IDs, and utterance IDs | Scope everything by `session_id` |

Numbers are demo examples, not validated pace or filler thresholds.

## Proposed v0 speech rules for review

The fixtures follow these rules, and `check_speech.py` enforces those visible in
an event stream. They choose details the contract leaves to the speech adapter.
Lane 1 owns the central configuration once INT-01 lands; Lane 4 owns the
thresholds applied to these observations.

- **Language and tokens.** Analysis language is English ([speech_text.py](speech_text.py)). A token is a run of letters or digits, with internal apostrophes, hyphens, or periods (`don't`, `real-time`, `3.5`). Bracketed annotations such as `[BLANK_AUDIO]` or `(applause)` are removed. For other languages, WPM and filler fields are null.
- **WPM.** Finalized tokens, excluding hesitations, attributed to the window by word end time, divided by the window length in minutes (silence included). The fixtures spread tokens evenly across each utterance; the adapter should use the model's word timestamps. Partial text never counts.
- **Fillers.** Hesitations (`um`, `uh`, `er`, `ah`, `hmm`, `mhm`, `eh`, including stretched spellings) count anywhere. `like`, `you know`, and `I mean` count only when punctuation sets them off as a whole clause, so "I like it" is not a filler. Fillers come from finalized text only.
- **Windows.** A 10 s trailing window is emitted every hop (5 s in the fixtures; 1-2 s is suggested live). The window ends at the hop time or, if someone is still speaking, where that utterance began, so metrics never wait for unfinished speech. Windows that would not advance, or that are shorter than 5 s, are skipped; a final window at the capture end is always reported during drain. The adapter waits up to 3 s for the finals of overlapping utterances; otherwise the window reports null for insufficient coverage.
- **Null versus zero.** Null means unknown: a window shorter than 5 s, a coverage timeout, an unsupported language, or unavailable input. `0` WPM means audio was captured and analyzed and nobody spoke.
- **Pauses.** A pause is silence of at least 1.0 s after the first speech. While it lasts, metrics report it as `active` with the elapsed time. When speech resumes, the adapter emits one extra `speech.metrics` event (`pause-<end>`) whose window ends at that moment, reporting the `completed` pause; no other event repeats it. Silence before the first speech is not a pause, and a pause still active at stop stays `active`. `unknown` is reserved for unavailable input.
- **Availability.** A permission or device failure emits a speech `signal.status`. Later metrics carry that availability with null values and an `unknown` pause. An utterance cut by a disconnect is finalized at the disconnect time.
- **Utterances.** An utterance is a voice-activity segment; the adapter should split segments longer than about 8 s. A partial's `end_s` is the latest audio it covers. A final freezes its utterance, finals never overlap, and an empty final retracts a hallucinated partial. Pending speech is finalized during drain.
- **Event IDs.** IDs are `u<n>-r<revision>`, `metrics-<window end>`, `pause-<pause end>`, and `speech-status-<n>`. Each is stable on retry.

## Check real adapter output later

After AUD-01 records a live session, export its speech and lifecycle events in
delivery order (a JSON array, or JSON Lines with a `.jsonl` suffix). Keep the
export under the ignored `sessions/` directory rather than committing rehearsal
data. Vision and engagement events in the same file are ignored. Pass agreed
values if the central configuration differs:

```sh
python3 checks/speech/check_speech.py --stream sessions/speech-events.jsonl --summary \
  --min-observation-s 5 --pause-min-s 1
```

The checker verifies envelopes, stable retries, lifecycle and capture-end
limits, and revision freezing. It confirms that finals do not overlap and that
pending speech is finalized. For every metric it checks:

- window and timestamp shape;
- null-versus-zero rules and availability during reported outages;
- coverage, so no window is counted before its overlapping utterances are final;
- WPM and filler bounds from the finals delivered before the metric;
- pause shape, placement, completeness, and single reporting.

`--summary` prints the reconstructed final transcript, totals, and pauses for
review.

It cannot judge transcription accuracy, word-timestamp quality, real voice
activity behavior, latency, device release, or privacy. Those need AUD-02
measurements on the development host.

These checks validate **producer** output. Lane 5's coaching fixtures
deliberately include post-completion callbacks and metrics-only speech windows
that consumers must tolerate, so this checker rejects them by design. In the
other direction, Lane 5's `check_event` from
[draft PR #1](https://github.com/crasni/LeCoach/pull/1) accepted all 214 events
in these fixtures.

## Implementation research for the live adapter

This is a proposed plan, not a measured or approved implementation:

- **Pipeline.** Microphone capture → voice activity detection (for example Silero VAD) → local Whisper transcription with word timestamps (for example faster-whisper on CPU with int8) → utterance reconciliation → the window and pause rules above → `emit(event)` with the shared session clock.
- **Hardware path.** The official SalesKit in `docs/` lists Whisper-Tiny, -Base, and -Small as supported on UGen300 (Hailo-10H) through the Hailo GenAI Model Zoo (PDF pages 7, 8, and 15). Using one of those sizes on CPU first keeps a later accelerator adapter behind the same seam. Nothing has been run or measured on UGen300.
- **Fillers.** Whisper often omits disfluencies such as "um" and "uh" ([discussion](https://huggingface.co/spaces/openai/whisper/discussions/30)), so filler counts may be undercounts. Prompting with fillers is reported to help inconsistently. [CrisperWhisper](https://github.com/nyrahealth/CrisperWhisper) targets verbatim transcription, but its weights use a non-commercial license and it is not on the UGen300 list. Filler recall must be measured in AUD-02 before the demo relies on it.
- **Hallucination.** Whisper can produce text such as "Thank you." on silence or noise. Gate transcription with voice activity detection and no-speech thresholds, and retract a hallucinated partial with an empty final (see `delivery_effects`).

## Open questions for review

1. **Pause events (Lane 1/4):** is an extra `speech.metrics` event per completed pause the agreed reading of "emit each completed pause once with its own event ID"?
2. **Leading silence (Lane 4):** pauses start after the first speech, and silence-only windows report 0 WPM with no pause. Does the audience need a separate "not started" signal?
3. **Null reasons (Lane 1/5):** consumers cannot tell why WPM is null (short window, coverage timeout, unsupported language). An optional reason field would be a contract change.
4. **Configuration (Lane 1):** where do window, hop, minimum observation, pause minimum, and coverage wait live, and with which values?
5. **Language (team):** is English-only analysis acceptable for the demo? Mandarin would need a characters-per-minute measure and its own filler list (for example 嗯, 呃, 那個, 就是).
6. **Model failure (Lane 1):** if capture works but the model fails to load, should the adapter emit `signal.status` error `speech_model_unavailable` and error-availability metrics?

## Integration-owner review

The preparation fixtures are compatible with the executable v0 event models:
all 214 events validate. Keep schema validation alongside this standalone semantic
checker; it does not exhaustively reproduce every strict model constraint.
Lifecycle-bearing streams must start with `session.started`, completion requires
stop, start/stop payloads are empty, and incomplete sources are unique speech/vision
modalities. Speech-only exports without lifecycle remain supported, but cannot
prove completion or drain behavior.

The extra completed-pause metric and measured leading silence with zero WPM are
compatible with the existing contract; they do not establish intentional pauses
or poor delivery. Null remains unknown without adding a reason field. Device/model
failure can use the existing `signal.status` error and unavailable metric shapes.
English tokenization and the proposed timing constants remain fixture assumptions,
not approved Mandarin/demo support or central live configuration. Coordinate those
choices before implementing the live adapter. No shared event shape was changed.

## Integration handoff

Lane 1 needs to confirm these rules or the agreed changes, the configuration
location, and the application layout, executable contract, and replay seam.
AUD-01 then implements the adapter in that layout and checks its recorded
output with `--stream`. Lane 4 can drive pace, filler, pause, and
unavailable-input reactions from these fixtures now; null is not zero, and
completed pauses arrive once. Lane 5 can use the transcripts, drain behavior,
and limitation cases. No shared contract, dependency manifest, or root
configuration is changed by these preparation artifacts.

The checks use no network, devices, or models, and create no persistent output;
tests write temporary synthetic files that are cleaned up.
