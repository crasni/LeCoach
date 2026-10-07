"""Test-only components. These are not production speech, audience or coaching logic."""

import asyncio

from lecoach.contracts import CompletedSession, Feedback, parse_event


def event(session_id="test-session", event_id="metric", timestamp=1.0, **changes):
    value = {
        "schema_version": 0,
        "session_id": session_id,
        "event_id": event_id,
        "source": "speech",
        "type": "speech.metrics",
        "timestamp_s": timestamp,
        "payload": {
            "window_start_s": 0.0,
            "window_end_s": timestamp,
            "availability": "available",
            "wpm": 144.0,
            "filler_count": 0,
            "filler_rate_per_min": 0.0,
            "pause": {"state": "none", "duration_s": 0.0, "start_s": None, "end_s": None},
        },
    }
    return parse_event({**value, **changes})


class Capture:
    def __init__(self, fail=False, pending=False, delayed_start=False, flush=False):
        self.fail = fail
        self.pending = pending
        self.delayed_start = delayed_start
        self.flush = flush
        self.starts = 0
        self.stops = 0
        self.released = False
        self.cancelled = False
        self.context = None

    async def start(self, context):
        self.starts += 1
        self.context = context
        if self.fail:
            raise RuntimeError("synthetic device failure")
        if self.delayed_start:
            try:
                await asyncio.Event().wait()
            finally:
                self.released = True

    async def stop_capture(self, capture_end_s):
        self.stops += 1
        self.released = True
        self.capture_end_s = capture_end_s

    async def drain(self):
        if self.pending:
            try:
                await asyncio.Event().wait()
            finally:
                self.cancelled = True
        if self.flush:
            self.context.emit(event(self.context.session_id, "drained-final", self.capture_end_s))

    def preview_jpeg(self):
        return None


class Recorder:
    def __init__(self):
        self.events = []
        self.completed = None

    def start(self, context):
        self.context = context

    def on_event(self, event):
        self.events.append(event)

    def complete(self, duration_s, incomplete_sources):
        self.completed = CompletedSession(
            session_id=self.context.session_id,
            duration_s=duration_s,
            incomplete_sources=incomplete_sources,
            events=sorted(self.events, key=lambda e: (e.timestamp_s, e.event_id)),
        )
        return self.completed


class Generator:
    async def generate(self, session):
        return Feedback(
            session_id=session.session_id,
            duration_s=session.duration_s,
            moments=[],
            limitations=["Synthetic test components only."],
        )
