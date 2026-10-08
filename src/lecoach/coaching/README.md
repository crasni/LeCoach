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
reasons with actual cited numbers and a practical action. They do not infer intent,
emotion, eye contact or delivery quality from unavailable inputs. Unknown reason
codes, missing references, future observations, wrong modalities, null values,
superseding outages and stale evidence are omitted with a limitation. The latest
cited observation and latest source observation must be fresh at the transition;
older cited windows may still document a sustained incident. These checks are
conservative over capture timestamps; the canonical completed log has no arrival
ordering for equal capture times. Only the engine's explicit citations become
moment evidence; no uncited frame is attached to a reaction retroactively.

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
explicitly fail as unavailable. Default app/CLI composition is unchanged and still
needs integration-owner review before enabling computed coaching globally.

```sh
uv run python checks/coaching/feedback_replay.py
uv run python checks/coaching/feedback_replay.py --case weak_to_improved --show-feedback
uv run pytest -q tests/test_feedback.py
```

The computed-engine baseline is separate from the historical authored feedback
fixtures; it checks all nine synthetic cases / ten sessions. The API test verifies
that injected computed feedback reaches the existing endpoint and that live mode
is unavailable. No persistent rehearsal output is written. Final acceptance of
LIVE-01's evidence handoff ([issue #18](https://github.com/crasni/LeCoach/issues/18)),
including the pending revert disposition, and default composition/UI handoff remain
pending under [issue #20](https://github.com/crasni/LeCoach/issues/20). These synthetic
checks do not complete COACH-01 or validate live devices, models or hardware.
