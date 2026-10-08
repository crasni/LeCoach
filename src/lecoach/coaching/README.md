# In-memory session recording

`InMemorySessionRecorder` implements the published recorder protocol in
`lecoach.contracts.interfaces`; event and completed-session types come from
`lecoach.contracts`. No shared contract or application composition is changed.

The integration owner can inject a fresh recorder per session with
`Components(recorder=InMemorySessionRecorder())`. The existing controller starts
the subscriber before capture, delivers lifecycle and normalized observations,
and calls `complete(duration_s, incomplete_sources)` after producers drain.
The returned canonical `CompletedSession` is suitable for the future feedback
generator and timeline consumer. Recording alone leaves feedback unavailable.

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

Moment selection and template feedback still require LIVE-01's actual
transition/reason evidence, particularly positive reasons. They are not supplied
by this recorder. Lane 1 owns default API composition; this implementation is
injected through the existing seam for verification, not enabled globally here.
