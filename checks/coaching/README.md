# COACH-01 synthetic acceptance cases

For the COACH-02 English narration draft, scenario procedure and timing/evidence
handoff, see [demo preparation](demo/README.md). It uses the computed coaching
checks below; final live-demo acceptance stays with the assigned Issues.

These are Lane 5 acceptance artifacts prepared before INT-01 and LIVE-01.
Every event, transcript, transition, and feedback example is hand-authored and
synthetic. No microphone, camera, inference model, or accelerator was used.
The original consistency utility does not implement a recorder, session controller,
engagement engine, fake clock, or feedback generator. INT-01 has since published
Python contracts and the approved application layout. The actual recorder can now
be checked separately using the continuation command below.

[ARCHITECTURE.md](../../docs/ARCHITECTURE.md) remains the contract authority.
`fixtures/*.json` are arrays of those events in **delivery order**. Array order
models late delivery without changing capture timestamps or adding event fields.
`expectations.json` is a test oracle: it lists the events a completed log should
retain and gives illustrative `Feedback` objects. Its surrounding metadata is
test-only and is not another application/session contract.

## Run the preparation checks

From the repository root, using Python 3.10+ and its standard library:

```sh
python3 checks/coaching/check_cases.py
python3 -m unittest discover -s checks/coaching -p 'test_*.py' -v
```

The first command checks the synthetic input and manually written expectations.
The second checks that the acceptance utility rejects representative faulty
outputs. Passing them establishes **test artifact consistency**, not completed
COACH-01 functionality or live inference.

## Check the actual recorder

With the pinned project environment, run:

```sh
uv run python checks/coaching/record_replay.py
uv run pytest -q tests/test_coaching.py
```

`record_replay.py` injects the production `InMemorySessionRecorder` into the
published fixture/controller seam and checks its completed timelines against
all ten session oracles. The controller still receives authored audience events;
no live engine or feedback generator is injected. The command writes no session
files. See [recorder behavior and retention](../../src/lecoach/coaching/README.md).

## Cases and expected behavior

| Case | Expected coaching | Recorder/feedback acceptance target |
| --- | --- | --- |
| `weak_to_improved` | Two improvements and one supported strength | Preserve direct measurements and authored audience transitions; explain using capture times |
| `camera_unavailable` | One speech improvement, no strength, camera limitation | Missing camera must not become negative delivery feedback or fill an insight quota |
| `no_usable_signals` | No moments; input limitation | Unavailable microphone and camera are not poor delivery |
| `empty_session` | No moments; insufficient-evidence limitation | Start and stop at zero duration without fabricated insights |
| `insufficient_window` | No moments; insufficient-window limitation | Preserve null startup metrics; do not reinterpret them as zero WPM |
| `late_final_and_duplicates` | No moments without supported audience evidence | Keep final arriving during drain, deduplicate retries, preserve partial history, exclude foreign session and post-completion callback |
| `drain_timeout` | No moments; incomplete-speech limitation | Preserve `incomplete_sources`; ignore callback delivered after completion |
| `repeated_sessions` | Separate summaries with no supported moments | Reused event IDs and zero-based clocks stay scoped to each session; discard old-session callback |
| `adjacent_incidents` | One improvement, no strength | Two transitions citing the same incident do not create duplicate advice |

The historical authored positive transitions in `weak_to_improved` deliberately
have empty reason lists: positive codes were not named when they were authored.
The illustrative
strength cites an authored `ENGAGED` state and direct speech/facing observations;
it does not assert which rule caused that state. Lane 4 has since published
`pace_steady` and `facing_audience` in merged PR #7; final evidence acceptance
is tracked in issue #18. This historical example is not the computed-engine
acceptance baseline. Only the originally documented
`pace_high` and `facing_away_sustained` examples are used for negative reasons.
Numeric observations are synthetic demo examples, not validated thresholds.
Head/body facing is approximate; the feedback does not claim eye tracking,
emotion detection, or inferred confidence. The adjacent-transition case tests
coaching deduplication; it cannot establish that the live engine smooths correctly.

## Check computed engine and coaching output

```sh
uv run python checks/coaching/feedback_replay.py
uv run python checks/coaching/feedback_replay.py --case weak_to_improved --show-feedback
uv run pytest -q tests/test_feedback.py
```

This optional composition runs the production engine, recorder and template
generator through the published replay seam. `engine_expectations.json` contains
test-only assertions hand-derived from the merged engine's transition timing and
reason citations. It defines no new session/event shape. The checker validates
canonical completed sessions and feedback references before comparing anchors.
All nine cases / ten sessions run without devices or persistent output. Tests also
exercise the existing API with this factory injected; the default app is unchanged.

For `weak_to_improved`, computed transitions occur at 0, 20, 30, 35 and 40 seconds.
The feedback anchors at direct capture observations: pace improvement 10 seconds,
approximate-facing improvement 25 seconds, and strength 40 seconds. The strength
uses `vision-35`, as cited by the engine; `vision-40` arrived after that reaction.
Repeated `pace_high` references at 20 and 30 seconds produce one improvement.
Final engine/evidence acceptance and any revert disposition remain integration
dependencies; this is a proposed consumer baseline for review.

## Check historical authored outputs

After Lane 1 confirms the contracts and Lane 4 provides transitions, use the
application's actual recorder and feedback generator to consume a selected case.
Export each consumer's results as a JSON array containing its canonical
`CompletedSession` or `Feedback` objects; this array is only a CLI batch wrapper.
Keep exports under ignored `sessions/` rather than committing rehearsal data.
For example, after the application has produced those files:

```sh
python3 checks/coaching/check_cases.py --case weak_to_improved \
  --completed sessions/coach-completed.json --feedback sessions/coach-feedback.json
```

The utility compares a completed timeline with the manually listed retained
events, including order, original payloads, session identity, duration, and
incomplete sources. Feedback checks compare the selected moment kinds, capture
timestamps, and minimum evidence anchors. Wording may differ; every observation
and suggestion must be nonempty, and limitations must be present when required.
These assertions exercise the chosen cases, not every permissible feedback
selection. Review and update the hand-authored expectations with the integrator
when the implementation handoff changes a case; do not change production rules
merely to match example wording.

Human review must still verify that observations accurately describe evidence,
suggestions are useful, missing-source limitations are specific, and moment
selection is appropriate. This utility cannot validate natural-language truth,
live latency, producer timeout duration, transcription accuracy, language-specific
pace bands, audience smoothing, device release, or local privacy behavior.

## Integration handoff

Lane 1 has published executable event types, lifecycle subscription/stop boundaries,
the shared clock, fixture replay entry point, and application layout through PR #4.
The in-memory recorder uses those seams and was merged in PR #5. Lane 4's merged
PR #7 supplies reason vocabulary, positive evidence and computed deterioration/
recovery examples, with final acceptance pending issue #18. No shared interface
revision is introduced here.

The recorder, selector, templates and optional replay composition are implemented
in `src/lecoach/coaching/`; they use the existing `Event`,
`CompletedSession`, `Feedback`, and `Moment` contracts. The UI remains Lane 4's
responsibility. Durable storage, live integration, and the COACH-02 demo evidence
are still pending; P1 LLM feedback/questions/TTS remain gated by integrated P0.

These files contain only synthetic data and stay local when checks run. The
utility has no network access or recording behavior and creates no persistent
session output. Tests use temporary synthetic JSON files that are cleaned up.
