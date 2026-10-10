# LeCoach architecture and shared contracts

This file is the canonical interface reference for all five roles. [GUIDE.md](../GUIDE.md) defines product scope; [GitHub Issues](https://github.com/crasni/LeCoach/issues?q=is%3Aissue+label%3Acoordination) assign work and own live acceptance. INT-01 implements the MVP v0 shapes below, is merged through PR #4, and is accepted by the maintainer with the remaining peer-review/downstream signoff gate waived. Current implementation evidence lives in [STATUS.md](STATUS.md). Model choices remain with the producer owners. The [OpenSpec implementation checklist](../openspec/changes/archive/2026-10-09-int-01-local-integration-scaffold/tasks.md) records execution order.

## INT-01 implementation decisions and handoff

### Current language and validation policy — 2026-10-09

English is the product/rehearsal and speech-analysis baseline. The maintainer
canceled the unaccepted Mandarin/zh-TW delta; existing v0 English units, tokenizer,
filler rules and consumer semantics remain unchanged. Unsupported measurements
remain null/unknown. [#6](https://github.com/crasni/LeCoach/issues/6) records the
speech-owned configuration and optional dependency handoff; no new shared schema
or engine rule is introduced.

Stage I live acceptance targets the confirmed ordinary demo computer using local
CPU inference. UGen300 is unavailable before qualification and remains a later
Stage II validation milestone. Lucas is the likely operator; actual host and
recording arrangements remain unconfirmed. Clocks, lifecycle and evidence rules
below are unchanged.

Python 3.12.14 with uv hosts the controller, in-process event bus, and local FastAPI API. React/TypeScript with Vite renders outputs. Core lockfiles exclude model/capture packages; request modality dependency additions through integration. One backend process runs on `127.0.0.1:8000`; development Vite runs on loopback port 5173 with an API/WebSocket proxy. The backend can serve the built frontend for the demo. No remote inference or media service is used.

The executable event models live in `src/lecoach/contracts/events.py`; protocols/configuration live in `contracts/interfaces.py`. The root `contracts/schema.json` and `frontend/src/generated/contracts.ts` are generated artifacts. This document owns semantics; Python models implement them. Update both together and regenerate rather than editing TypeScript separately.

| Location | Boundary |
| --- | --- |
| `src/lecoach/runtime/` | Shared clocks, controller, FIFO subscriptions, synthetic fixture playback. |
| `src/lecoach/api/` | Local HTTP/WebSocket transport and composition. |
| `src/lecoach/speech/`, `src/lecoach/vision/` | Producer implementation slots; no capture/model implementation in INT-01. |
| `src/lecoach/engagement/`, `src/lecoach/coaching/` | Sole engine and recorder/generator implementation slots, for their assigned owners. |
| `frontend/src/` | Integration inspection shell; Lane 4 replaces it with the rehearsal experience. |
| `checks/coaching/` | Unchanged, locally reviewed Lane 5 synthetic cases from PR #1. |

Inject `Components` into `SessionManager(factory)` to compose live implementations. `SessionContext` supplies `session_id`, the same `clock.now()` in seconds, synchronous `emit(event)`, and `SessionConfig`. Model work must run outside the API event loop; marshal worker-thread emissions back onto that loop. Synchronous subscriber callbacks must finish promptly; the bus drains reentrant emissions FIFO so supporting source events reach every subscriber before resulting audience events.

The capture adapter protocol is `await start(context)`, `await stop_capture(capture_end_s)`, `await drain()`. `start` completes after capture is initialized, not after the rehearsal finishes. `stop_capture` stops acquisition; `drain` flushes observations captured at or before the supplied end. Implement both idempotently and release resources in cancellation-safe cleanup. The vision adapter additionally provides `preview_jpeg() -> bytes | None`; the local volatile preview uses only the latest JPEG, capped at 512 kB and five frames/s by default. The browser does not open a second camera stream.

The engine protocol is `start(context)`, `on_event(event)`, `stop()`. The recorder protocol is `start(context)`, `on_event(event)`, `complete(duration_s, incomplete_sources) -> CompletedSession`. The generator protocol is `await generate(completed_session) -> Feedback`. No default live engine, logger, or coaching generator is implemented by integration. The proposed P0 recorder keeps active/completed data in memory until next session/application exit; explicit development exports use ignored `sessions/`. Producer owners must not enable raw recording by default.

`SessionConfig.mode` and every transport snapshot explicitly distinguish `fixture` and `live`. `output_provenance` distinguishes authored fixture outputs from computed live outputs without changing the v0 event envelope. Default live composition is unavailable until the subsystem handoffs. Configuration defaults are centralized: startup timeout 5 s, shared stop/drain timeout 2 s, feedback timeout 5 s, browser queue 128 events, replay speed 5×. These are integration bounds, not engagement thresholds or measured inference latencies. Pace/language and audience rule defaults remain Lane 4's handoff.

The controller validates event type/source, finite values, capture windows and null observations, deduplicates stable event IDs, rejects foreign/closed sessions, and freezes transcript display after a final revision. Its hash index and latest display state are not a second full recorder. The sole recorder must preserve the required timeline/revision evidence and validate feedback evidence links.

Local API: `GET /api/health`, `GET /api/fixtures`, `POST /api/sessions` (prepare, no capture), `WS /api/sessions/{id}/events` (subscribe), `POST /api/sessions/{id}/start`, `POST /api/sessions/{id}/stop`, `GET /api/sessions/{id}`, `GET /api/sessions/{id}/feedback`, and `GET /api/sessions/{id}/preview`. Connect the event stream before starting. WebSocket wrappers are `{kind: "snapshot", snapshot: ...}` or `{kind: "event", event: ...}`; they do not add event types. Allowed browser origins are local ports 8000 and 5173. New sessions release the previous session's retained display state; old IDs become unavailable. Start/stop retries do not reopen capture.

Browser delivery uses bounded queues independent of inference/recording. Overflow closes that connection with code 1013, requiring an explicit snapshot resynchronization. Reconnection supplies current phase, input status, transcript and latest audience state without restarting acquisition. Input status follows capture time; a status event wins a metric timestamp tie, and later degraded windows retain the current specific failure until an available observation shows recovery. Full completed timelines come from the actual recorder when integrated. Fixture feedback is served only when authored playback completes; stopping early reports feedback unavailable.

Fixture arrays remain in delivery order, including late events; the fake clock advances monotonically to the maximum observed delivery time. A test-only explicit schedule can delay delivery beyond capture times. The headless replay command exposes a delivery trace and authored feedback, not a production CompletedSession. A consumer factory can replace authored engagement/feedback with real engine/recorder/generator outputs through the same replay seam. Positive reason codes and measured live behavior still need the assigned owners' handoffs.

## Ownership and flow

```text
Session controller (role 1)
  ├─ microphone → local speech adapter (role 2) ─┐
  └─ webcam → local vision adapter (role 3) ─────┤
                                               ↓
                                  engagement engine (role 4)
                                    ├─ audience UI (role 4)
                                    └─ session logger (role 5)
                                              ↓
                                     feedback (role 5)
```

The logger also subscribes to normalized speech, vision, and lifecycle events so feedback can show supporting observations. Role 4 owns the **single** engagement engine. Role 5 selects moments from that engine's recorded output and evidence; it must not calculate a second competing live state. Role 1 reviews shared-interface changes and integration. Models emit normalized data through adapters rather than importing UI or coaching internals.

Raw microphone and camera input, inference, transcript, and session processing stay local. Do not introduce a cloud inference fallback. Hardware acceleration belongs behind adapters; no UGen300 compatibility or measured speed is claimed until validated on the actual target.

## Common event envelope and clock

All events use this envelope; `payload` varies by type:

```ts
type Event = {
  schema_version: 0;
  session_id: string;
  event_id: string;
  source: "session" | "speech" | "vision" | "engagement";
  type: string;
  timestamp_s: number;
  payload: object;
};
```

`event_id` is unique within a session and stable on retry. Consumers deduplicate by `(session_id, event_id)`. Use finite numbers, JSON `null` for unknown values, and no `NaN`, implicit zero defaults, or epoch timestamps in signal fields. Ignore events from other sessions.

The session controller creates one monotonic clock at start. `timestamp_s` means seconds elapsed from that start, **at capture or observation**, not when inference finishes. Every adapter receives the same `session_id` and clock. Audio sample offsets are mapped from the capture start against this clock; video frames are stamped on capture with it. Worker/process adapters receive an explicit clock-offset mapping from the controller. They must not start independent zero-based clocks. Windowed metrics use their capture window end as `timestamp_s` and include `window_start_s` and `window_end_s`.

Inference may deliver events late or out of order. The logger preserves their capture times and can separately record `received_at_s` using the shared clock to measure lag. The live engine must not let an older observation overwrite a newer one, and must reject stale observations using capture age. Final feedback orders events by capture time; equal timestamps use event ID as a stable tie-breaker. Late events arriving during drain can inform feedback, but do not retrospectively change audience reactions already shown.

## Session lifecycle

Proposed integration seams, expressible as functions or local event callbacks:

```ts
startSession(config): SessionContext; // session_id, shared clock, emit(event)
speech.start(context): Promise<void>;
vision.start(context): Promise<void>;
engagement.start(context, ruleConfig): void;
stopSession(session_id): Promise<void>; // stop capture, flush producers, complete log
feedback.generate(completedSession): Feedback;
```

Role 1 implements the controller; each owner implements their corresponding seam. Start the logger and subscribers before capture. Emit `session.started` with timestamp `0`. Adapter failures emit `signal.status`; unavailable input must leave the other pipeline usable.

At stop, emit `session.stopping` with capture end time, stop microphone/camera acquisition, then drain final transcript and pending metrics with a configurable bounded timeout. Stop live engagement updates. Emit `session.completed` after producers are drained or timed out; its timestamp is the capture end time, with payload `{ "duration_s": 90, "incomplete_sources": [] }`. Timed-out sources go in that list. The logger closes the session before feedback generation. No new capture-timestamped observations may be later than capture end; callbacks after completion are ignored. Partial startup failure and repeated stop calls must release devices safely.

`signal.status` uses source `speech` or `vision` and payload:

```json
{"availability":"unavailable","reason":"camera_permission_denied"}
```

Availability is `available`, `unavailable`, or `error`; reasons describe device/model conditions and appear as clear UI notices. Signal absence is not evidence of poor delivery. No audio/video is persisted by default; logger storage format and retention must be documented when implemented.

## Speech contract — role 2

`speech.transcript`:

```json
{
  "schema_version": 0,
  "session_id": "demo-001",
  "event_id": "speech-18",
  "source": "speech",
  "type": "speech.transcript",
  "timestamp_s": 12.4,
  "payload": {
    "utterance_id": "u-4",
    "revision": 2,
    "is_final": true,
    "start_s": 10.2,
    "end_s": 12.4,
    "text": "Our results are ready."
  }
}
```

An utterance retains its ID as partial text is revised. `revision` increases; a final replaces the current partial and freezes that utterance. Consumers ignore old revisions and duplicate finals. UI can display partials, but WPM, filler counts, and feedback count final utterances once. Audio chunks that overlap must be reconciled inside the speech adapter before emitting canonical utterances; consumers must not stitch model chunks. A final includes capture start/end. Partial end time reflects the latest captured audio covered by the partial, not processing completion.

`speech.metrics` payload:

```json
{
  "window_start_s": 2.4,
  "window_end_s": 12.4,
  "availability": "available",
  "wpm": 144,
  "filler_count": 1,
  "filler_rate_per_min": 6,
  "pause": {"state":"none","duration_s":0,"start_s":null,"end_s":null}
}
```

- `wpm`: finalized token count attributed to the window, divided by window duration in minutes. Use word capture times when available; otherwise consistently assign words to utterance end and document that coarse estimate. Denominator includes silence. Window length and minimum observation time are configured centrally; insufficient finalized text coverage or unsupported language/tokenization yields `null`, not a misleading zero. Record the tokenizer, language, and approximation in implementation docs.
- `filler_count`: integer count from finalized text in the same window, using a documented language-specific lexicon. `filler_rate_per_min` divides that count by window duration in minutes. Unknown or unsupported detection is `null`. Do not count every partial revision again.
- Pause state is `none`, `active`, `completed`, or `unknown`. `active` has a capture start and elapsed duration with `end_s: null`; `completed` has capture start/end and their difference. Emit each completed pause once with its own event ID. Unknown capture/detection yields `duration_s: null`. Silence cannot by itself establish that a pause was intentional, that speech was unclear, or that content was confusing.

WPM and fillers are approximate observations, not scores. Document analysis language and limits before choosing pace rules. Do not imply one WPM band is appropriate for all languages or presentations.

## Vision contract — role 3

`vision.metrics` payload:

```json
{
  "window_start_s": 11.4,
  "window_end_s": 12.4,
  "availability": "available",
  "person_present": true,
  "pose_available": true,
  "facing_score": 0.8,
  "activity_score": 0.35
}
```

`facing_score` and `activity_score` are finite values in `[0, 1]` or `null`. Facing estimates head/body orientation toward the camera; it does not measure eye contact or emotion. Activity estimates observed gesture/movement over the window, normalized by visible body scale and elapsed time where possible; the adapter documents its mapping. More movement is not automatically better.

`person_present` and `pose_available` are booleans or `null` if detection cannot decide. For no detected person, occlusion, unsupported pose, or an unavailable camera, affected derived scores are `null`. Low movement alone is not grounds for a negative reaction. Pose/keypoint internals can stay in the adapter; add shared keypoints only if a consuming feature needs them. No fabricated gaze, confidence, attention, or emotion fields.

## Engagement contract — role 4

The exact state names are `ENGAGED`, `NEUTRAL`, `CONFUSED`, `BORED`, and `INTERESTED`. These represent simulated audience reactions, not measured human emotions or clinically meaningful speaker judgments.

`engagement.state` payload:

```json
{
  "state": "CONFUSED",
  "previous_state": "NEUTRAL",
  "reasons": [
    {"code":"pace_high","source_event_ids":["speech-19"]},
    {"code":"facing_away_sustained","source_event_ids":["vision-22"]}
  ],
  "usable_sources": ["speech","vision"]
}
```

The event timestamp is the current shared clock time when the audience decision is emitted; referenced source events retain their original capture times. Emit a starting `NEUTRAL` state and subsequent state transitions. The UI renders these events without implementing its own rules. Each reason points to stored evidence; omit unknown/stale signals rather than assigning negative contributions. With no usable sources, return to `NEUTRAL` with an empty reason list and show input availability separately. With one usable source, evaluate only rules whose required evidence remains available.

Use a small explicit rule configuration: pace bands, filler threshold, silence duration, facing threshold/duration, per-source stale age, smoothing duration, and transition dwell/hysteresis. Speech staleness must accommodate the chosen metric window and measured inference delay; video uses its own age limit. Declare every default and unit in one implementation configuration file. Require sustained evidence before transitions and a recovery threshold/dwell to prevent flicker. Keep rules deterministic for a given event stream and configuration.

LIVE-01 reason codes (proposed by Lane 4, pending integration review). Negative: `pace_high` and `fillers_frequent` (→ `CONFUSED`); `pace_low`, `silence_prolonged` and `facing_away_sustained` (→ `BORED`). Positive, cited by `INTERESTED`/`ENGAGED`: `pace_steady` (speech) and `facing_audience` (vision). Each cites the speech or vision metric events that supported it. Negative states cite every currently active negative rule; a transition to `NEUTRAL` has no reasons. The rules, defaults and units are documented in `src/lecoach/engagement/README.md` and `config.py`.

Thresholds are demo heuristics to tune using recorded fixtures, **not scientifically validated measures**. Use `INTERESTED` for configured recovery/positive observations, `ENGAGED` for sustained positive observations, and negative states only for explicit supported rules. Avoid unsupported labels such as "unconfident" or "bad eye contact." Completed short pauses may contribute to a positive transition only with contextual evidence; prolonged silence may trigger a rule only when audio capture and silence detection are known to work.

## Timeline and feedback — role 5

Logger input is the shared event stream. Preserve event IDs, source times, and evidence links. Feedback returns at most one supported strong moment and two or three supported improvement moments. Each moment has:

```ts
type Moment = {
  timestamp_s: number;
  kind: "strength" | "improvement";
  observation: string;
  suggestion: string;
  evidence_event_ids: string[];
};
```

The controller hands the logger's completed session to feedback; the UI consumes the returned summary and the original event list for its timeline:

```ts
type CompletedSession = {
  session_id: string;
  duration_s: number;
  events: Event[];
  incomplete_sources: ("speech" | "vision")[];
};
type Feedback = {
  session_id: string;
  duration_s: number;
  moments: Moment[];
  limitations: string[];
};
```

Empty or unsupported sessions return an empty `moments` array and plain-language `limitations`. A summary never contains another engagement score or an independently computed live audience state.

Select sustained transitions and supporting measurements, deduplicate adjacent incidents, and use capture timestamps for explanations. Feedback must not invent a strength or fill a quota if evidence is insufficient. Explain approximate observations in plain language and give a concrete action. An unavailable camera, startup window, or stale transcript is an input limitation, not an improvement moment. P0 uses templates; optional local LLM feedback follows a working end-to-end P0.

## Integration fixtures and change control

Role 1 supplies a deterministic fake session clock and a replayable JSON event fixture; replay advances to the fixture times rather than reading wall time. Roles 2 and 3 can deliver fixture producers before model integration, letting roles 4 and 5 work independently. Fixture mode is explicitly labeled in the demo; it must not masquerade as live inference.

Minimum integration scenarios: weak delivery → sustained improved delivery → stop and feedback; unavailable camera with valid speech; no usable signals; delayed/out-of-order events; partial transcript revisions and duplicate finals; stop with a pending final transcript. Verify the same replay produces the same audience transitions and that missing signals never produce negative feedback. Verify devices are released and the log completes after stop.

Change this file before changing a producer/consumer boundary. Role 1 coordinates affected owners, fixture updates, and compatibility. Keep v0 intentionally small; choose transport/framework only once in integration and record the decision here. Do not create another contract or source of truth inside a role-specific document.
