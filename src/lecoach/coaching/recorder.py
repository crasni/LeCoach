"""Volatile normalized-event recording through the published SessionRecorder seam."""

from typing import Literal

from lecoach.contracts import CompletedSession, Event, parse_event
from lecoach.contracts.events import CompletedEvent, CompletionPayload
from lecoach.contracts.interfaces import SessionContext


class InMemorySessionRecorder:
    """Keep one session in memory; replace retained data on the next start.

    Subscriber calls run on the controller's event loop. No private clock,
    inference, raw-media recording, disk writes, or network access is involved.
    Completed snapshots are independent copies so callers cannot alter evidence.
    """

    def __init__(self) -> None:
        self._session_id: str | None = None
        self._phase: Literal["idle", "prepared", "running", "stopping", "closed"] = "idle"
        self._events: dict[str, Event] = {}
        self._capture_end_s: float | None = None
        self._completion: CompletedEvent | None = None
        self._result: CompletedSession | None = None

    def start(self, context: SessionContext) -> None:
        if self._session_id is not None and self._result is None:
            raise RuntimeError("complete the current recording before starting another")
        self._session_id = context.session_id
        self._phase = "prepared"
        self._events = {}
        self._capture_end_s = None
        self._completion = None
        self._result = None

    def on_event(self, event: Event) -> None:
        if self._phase == "idle":
            raise RuntimeError("start the recorder before delivering events")
        if self._phase == "closed":
            return
        event = parse_event(event)
        if event.session_id != self._session_id:
            return
        previous = self._events.get(event.event_id)
        if previous is not None:
            if previous != event:
                raise ValueError("retry changed a stable event ID")
            return
        if event.type == "session.started":
            if self._phase != "prepared":
                raise ValueError("session.started must occur exactly once")
            self._phase = "running"
        elif self._phase == "prepared":
            raise ValueError("session.started must precede observations")
        elif event.type == "session.stopping":
            if self._phase != "running":
                raise ValueError("session.stopping must occur exactly once")
            self._capture_end_s = event.timestamp_s
            self._phase = "stopping"
        elif event.type == "session.completed":
            if self._phase != "stopping" or event.timestamp_s != self._capture_end_s:
                raise ValueError("completion must follow stop at the same capture end")
            self._completion = event.model_copy(deep=True)
            self._phase = "closed"
        elif self._capture_end_s is not None:
            if event.timestamp_s > self._capture_end_s or event.source == "engagement":
                return
        # Copy nested lists/payloads as well as the frozen outer model.
        self._events[event.event_id] = event.model_copy(deep=True)

    def complete(self, duration_s: float, incomplete_sources: list[str]) -> CompletedSession:
        metadata = CompletionPayload(duration_s=duration_s, incomplete_sources=incomplete_sources)
        if self._completion is None:
            raise RuntimeError("record session.completed before completing the log")
        if self._completion.payload != metadata:
            raise ValueError("completion metadata differs from the recorded lifecycle")
        if self._result is None:
            self._result = CompletedSession(
                session_id=self._session_id,
                duration_s=metadata.duration_s,
                incomplete_sources=metadata.incomplete_sources,
                events=sorted(self._events.values(), key=lambda e: (e.timestamp_s, e.event_id)),
            )
            # The completed snapshot is now the sole retained timeline.
            self._events = {}
        return self._result.model_copy(deep=True)
