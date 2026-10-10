# Session recording and deterministic coaching

`InMemorySessionRecorder` implements the published recorder protocol in
`lecoach.contracts.interfaces`; event and completed-session types come from
`lecoach.contracts`. No shared contract or application composition is changed.

The integration owner can inject a fresh recorder per session with
`Components(recorder=InMemorySessionRecorder())`. The existing controller starts
the subscriber before capture, delivers lifecycle and normalized observations,
and calls `complete(duration_s, incomplete_sources)` after producers drain.
The returned canonical `CompletedSession` supplies the feedback generator and
timeline consumer. Recording alone leaves feedback unavailable. The recorder
was published and merged in [PR #5](https://github.com/crasni/LeCoach/pull/5).

The recorder preserves speech, vision, audience, status and lifecycle events,
including original capture times, transcript revisions and evidence IDs. It
deduplicates identical retries, rejects changed payloads under the same event ID,
and orders the completed timeline by capture time and event ID. Foreign sessions,
post-completion callbacks, post-stop audience changes and observations captured
after stop are ignored. Final transcripts captured before stop remain eligible
during drain. Lifecycle order and completion metadata must match.

Retention is volatile: only one active or completed timeline is kept by this
instance, replaced at the next `start` or released when the instance is discarded.
It does not retain the context/clock or run its own clock. Returned snapshots are
deep copies; callers own their retention and must release them when replacing a
session. Raw audio, video and camera previews are not accepted by the normalized
event schema. No files, models, credentials, or network connections are created.
There is no automatic durable session storage or development export.

From the repository root with the pinned project environment:

```sh
uv run python checks/coaching/record_replay.py
uv run pytest -q tests/test_coaching.py
```

The replay command feeds the actual recorder through the shared controller and
compares all nine existing synthetic cases (ten sessions) with the retained-event
oracles. Controller tests additionally cover live-mode lifecycle with fake
adapters, drain timeout and cancellation, immediate stop, and a recorder reused
across sessions. These checks establish consumer behavior with synthetic data;
they do not establish actual microphone/camera capture or inference performance.

## Feedback generator

`TemplateFeedbackGenerator(stale_after_s={"speech": ..., "vision": ...})` implements
`await generate(CompletedSession) -> Feedback`. Composition supplies freshness
limits from the engine's public `RuleConfig`; this consumer adds no engagement
thresholds, clock, shared contract or audience engine. See the canonical
[architecture](../../../docs/ARCHITECTURE.md) and
[engine handoff](../engagement/README.md) for reason semantics.

The selector consumes recorded negative transitions (`CONFUSED` / `BORED`) and
supported `ENGAGED` transitions. `INTERESTED` alone is insufficient for a strength.
Templates describe the published pace, filler, active-pause and approximate-facing
reasons with plain observations and one concrete practice action. Pace/pause/filler
values remain approximate; normalized facing scores and implementation terms
stay out of user-facing advice. The underlying canonical evidence IDs remain
intact. Templates do not infer intent, emotion, eye contact or delivery quality
from unavailable inputs. Unknown reason
codes, missing references, future observations, wrong modalities, null values,
superseding outages and stale evidence are omitted with a limitation. The latest
cited observation and latest source observation must be fresh at the transition;
older cited windows may still document a sustained incident. These checks are
conservative over capture timestamps; the canonical completed log has no arrival
ordering for equal capture times. Only the engine's explicit citations become
moment evidence; no uncited frame is attached to a reaction retroactively.

An `available` status cannot restore observations from before an outage. Every
cited measurement and the newest source observation must end strictly after the
latest recorded `unavailable`/`error` status at that decision. Equal capture times
are conservatively rejected. A new post-outage window restores the source but
does not validate old citations. This matches the reviewed and merged LIVE-01 handoff in
[PR #29](https://github.com/crasni/LeCoach/pull/29).

Repeated causes within one continuous negative episode become one improvement.
Episodes end at a nonnegative transition. Identical measurement evidence cannot
be recycled across episodes as new advice. Candidates rank by cited-window span,
then earliest capture timestamp and reason code; at most three are selected.
The one strength prefers support from both modalities, then cited-window span,
earlier capture time and stable transition IDs. These ranking choices are demo
heuristics, not validated quality scores. Improvements anchor at the earliest
cited measurement's capture time; strengths at the latest cited measurement's
capture time. Evidence IDs include the direct metrics and audience transitions.
Moments and evidence are deterministically ordered by capture time. There is no
minimum quota: no usable evidence means no invented moments. Source availability
and drain timeout limitations accompany the feedback.

## Optional integration composition

`lecoach.coaching.compose.replay_with_coaching(rules=None)` returns a component
factory supplying the existing `RuleEngine`, sole `InMemorySessionRecorder` and
`TemplateFeedbackGenerator`. It can be injected into `replay_case` or
`create_app(factory)`; each session receives fresh components. Live requests
explicitly fail as unavailable in this replay-only factory. Integration has delivered
a separate public CPU live composition in `lecoach.runtime.live` (merged PR #23):
`lecoach serve --live` uses this generator and displays computed coaching after stop.
Plain `lecoach serve` and fixture sessions retain authored example coaching.

```sh
uv run python checks/coaching/feedback_replay.py
uv run python checks/coaching/feedback_replay.py --case weak_to_improved --show-feedback
uv run pytest -q tests/test_feedback.py
```

The computed-engine baseline is separate from the historical authored feedback
fixtures; it checks all nine synthetic cases / ten sessions. The API test verifies
that injected computed feedback reaches the existing endpoint and that live mode
is unavailable. No persistent rehearsal output is written. Final acceptance of
LIVE-01's evidence handoff ([issue #18](https://github.com/crasni/LeCoach/issues/18))
remains an owner acceptance gate under
[issue #20](https://github.com/crasni/LeCoach/issues/20). The #17 revert disposition
is accepted (no rollback; branch retained), and the live composition/UI is
delivered. These synthetic checks do not complete COACH-01 or validate live devices, models or hardware.

## Inspect a completed session locally

The independent checker reads one existing canonical `CompletedSession`, invokes
this generator, and prints the canonical `Feedback` or a text report with a
timeline. It does not open devices, run another engine, export transcripts, or
write files. Input can be a synthetic completed session now, or an authorized
live run later; the checker cannot infer or certify that provenance from v0 events.

```sh
uv run python checks/coaching/session_feedback.py sessions/run/completed.json --timeline
uv run python checks/coaching/session_feedback.py sessions/run/completed.json --rules sessions/run/rules.json --format json
uv run pytest -q tests/test_session_feedback.py
```

These examples require an existing record in ignored `sessions/` supplied by its
caller, not a new capture/export command. `--rules` reads the actual engine's
`RuleConfig` JSON; omit it only when that session used `DEFAULT_RULES`. Freshness
must match the run, including any custom speech/vision age. The command validates
lifecycle, session isolation, ordering and canonical evidence links. Invalid
input exits nonzero without echoing input values. Text timeline rows identify
event type/ID and audience reasons; transcript contents are deliberately omitted.
JSON output is exactly `Feedback`, without a competing report/event schema.

The controller already calls `generate(completed_session)` through the published
feedback protocol. Lane 1 supplies fresh recorder/generator instances together
with the same engine config in its composition; Lane 4 consumes `Feedback` and
the recorder's `CompletedSession.events` for the complete timeline, including
transitions missed during a browser disconnect. No HTTP endpoint or default/live
composition is added by this checker. See the dated [consumer handoff review](../../../checks/coaching/handoff-review.md).

## Advice wording and consumer review

Each card answers two questions: what was observed, and what to try once in the
next rehearsal. Engine classifications select the existing cards; this wording
adds no independent score, threshold, transcript analysis or audience state.
Facing is qualified with “appeared”; it does not imply eye contact. An active
pause duration is a lower bound, with intent explicitly unknown. Filler advice
is attributed to the transcript and does not claim measured recognition recall.
A camera-only strength makes no pace claim, and speech-only strengths make no
camera claim. Input gaps and unfinished processing remain limitations.

Examples below are from synthetic supported evidence, not live host measurements:

| Card | Observation | One practice action |
| --- | --- | --- |
| Fast passage | This passage was fast, at about 200–205 words per minute. | Repeat this passage more slowly, pausing after each key point. |
| Turned away | You appeared to stay turned away from the camera during this passage. | Deliver your next key sentence facing the camera, with your notes beside it. |
| Supported strength | Your pace stayed around 144 words per minute and you appeared to keep facing the camera. | Repeat your next key point at this pace while facing the camera. |

The UI receives the same `Feedback` fields and evidence IDs; it can present the
observation/action directly without exposing normalized facing scores. Existing
selector tests and separate computed baselines guard citation identity, capture
anchors, unsupported omissions, quotas, outages and repeated-session isolation.
Actual live advice quality still needs reviewer confirmation against sanitized
moment details supplied through #20/#11. The operator's passed functional batch
does not establish exact citations or instrumented accuracy/latency.
