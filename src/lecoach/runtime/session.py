"""One session controller; logging and audience rules are injected consumers."""

import asyncio
import hashlib
from collections.abc import Callable
from uuid import uuid4

from lecoach.contracts import CompletedSession, Event, Feedback, parse_event
from lecoach.contracts.events import TranscriptEvent, validate_feedback
from lecoach.contracts.interfaces import (
    Components,
    SessionConfig,
    SessionContext,
    SessionSnapshot,
)

from .bus import EventBus
from .clock import Clock, FakeClock, MonotonicClock


class SessionConflict(ValueError):
    pass


class SessionController:
    def __init__(
        self,
        config: SessionConfig,
        components: Components | None = None,
        session_id: str | None = None,
        clock: Clock | None = None,
    ) -> None:
        self.config = config
        self.components = components or Components()
        self.session_id = session_id or str(uuid4())
        self.clock = clock or (FakeClock() if config.mode == "fixture" else MonotonicClock())
        self.bus = EventBus()
        self.context = SessionContext(self.session_id, self.clock, self.emit, config)
        self.phase = "prepared"
        self.capture_end_s: float | None = None
        self.incomplete_sources: list[str] = []
        self.feedback: Feedback | None = None
        self.feedback_status = "pending"
        self.error: str | None = None
        self.latest: dict[str, Event] = {}
        self.transcript: dict[str, TranscriptEvent] = {}
        self.input_status = {
            name: {"availability": "unavailable", "reason": "not_started"}
            for name in ("speech", "vision")
        }
        self._seen: dict[str, str] = {}
        self._input_status_time: dict[str, float] = {}
        self._start_task: asyncio.Task | None = None
        self._stop_task: asyncio.Task | None = None
        self._adapter_starts: list[asyncio.Task] = []
        self.playback: asyncio.Task | None = None
        self._consumer_unsubscribers: list[Callable[[], None]] = []
        self._consumer_failed = False
        self.bus.subscribe(self._display)

    def snapshot(self) -> SessionSnapshot:
        return SessionSnapshot(
            session_id=self.session_id,
            mode=self.config.mode,
            phase=self.phase,
            elapsed_s=self.capture_end_s
            if self.capture_end_s is not None
            else (self.clock.now() if self.phase != "prepared" else 0.0),
            duration_s=self.capture_end_s,
            incomplete_sources=self.incomplete_sources,
            input_status=self.input_status,
            latest_events=self.latest,
            transcript=sorted(self.transcript.values(), key=lambda e: e.payload.start_s),
            feedback_status=self.feedback_status,
            output_provenance="hand_authored"
            if self.config.mode == "fixture"
            and not (self.components.engagement or self.components.feedback)
            else "computed",
            error=self.error,
        )

    def _display(self, event: Event) -> None:
        key = f"signal.status:{event.source}" if event.type == "signal.status" else event.type
        previous = self.latest.get(key)
        if previous is None or event.timestamp_s >= previous.timestamp_s:
            self.latest[key] = event
            if event.type in ("signal.status", "speech.metrics", "vision.metrics"):
                status = self.latest.get(f"signal.status:{event.source}")
                status_wins_tie = (
                    event.type != "signal.status"
                    and status is not None
                    and status.timestamp_s == event.timestamp_s
                )
                if (
                    event.timestamp_s >= self._input_status_time.get(event.source, -1.0)
                    and not status_wins_tie
                ):
                    self._input_status_time[event.source] = event.timestamp_s
                    if event.type == "signal.status":
                        self.input_status[event.source] = event.payload.model_dump()
                    else:
                        # Degraded metric windows add no device/model diagnosis.
                        # Keep the current explicit failure until recovery; an old
                        # status must not reappear after a newer available window.
                        keep_failure = (
                            event.payload.availability != "available"
                            and status is not None
                            and status.payload.availability != "available"
                            and self.input_status[event.source] == status.payload.model_dump()
                        )
                        if not keep_failure:
                            self.input_status[event.source] = {
                                "availability": event.payload.availability,
                                "reason": "observation_available"
                                if event.payload.availability == "available"
                                else "observation_unavailable",
                            }
        if isinstance(event, TranscriptEvent):
            current = self.transcript.get(event.payload.utterance_id)
            if current is None or (
                not current.payload.is_final and event.payload.revision > current.payload.revision
            ):
                self.transcript[event.payload.utterance_id] = event

    def emit(self, value: Event | dict) -> bool:
        event = parse_event(value)
        if event.source == "session":
            raise ValueError("lifecycle events belong to the controller")
        return self._accept(event)

    def _accept(self, event: Event) -> bool:
        if event.session_id != self.session_id or self.phase not in ("running", "stopping"):
            return False
        if self.capture_end_s is not None and event.timestamp_s > self.capture_end_s:
            return False
        if self.phase == "stopping" and event.source == "engagement":
            return False
        digest = hashlib.sha256(event.model_dump_json().encode()).hexdigest()
        if event.event_id in self._seen:
            if self._seen[event.event_id] != digest:
                raise ValueError("retry changed a stable event ID")
            return False
        self._seen[event.event_id] = digest
        try:
            self.bus.publish(event)
        except Exception:
            self._consumer_failed = True
            self.error = "consumer_failed"
            for unsubscribe in self._consumer_unsubscribers:
                unsubscribe()
            self._consumer_unsubscribers.clear()
            asyncio.create_task(self.stop())
            raise
        return True

    def _lifecycle(self, kind: str, timestamp: float, payload: dict) -> None:
        self._accept(
            parse_event(
                {
                    "schema_version": 0,
                    "session_id": self.session_id,
                    "event_id": f"session:{kind.rsplit('.', 1)[-1]}",
                    "source": "session",
                    "type": kind,
                    "timestamp_s": timestamp,
                    "payload": payload,
                }
            )
        )

    def _status(self, source: str, reason: str) -> None:
        self.emit(
            {
                "schema_version": 0,
                "session_id": self.session_id,
                "event_id": f"status:{source}:{uuid4()}",
                "source": source,
                "type": "signal.status",
                "timestamp_s": min(self.clock.now(), self.capture_end_s)
                if self.capture_end_s is not None
                else self.clock.now(),
                "payload": {"availability": "unavailable", "reason": reason},
            }
        )

    async def start(self, fixture_started: Event | None = None) -> SessionSnapshot:
        if self.phase in ("stopping", "completed"):
            raise SessionConflict("session has already stopped")
        if self._start_task is None:
            self._start_task = asyncio.create_task(self._start(fixture_started))
        await asyncio.shield(self._start_task)
        return self.snapshot()

    async def _start(self, fixture_started: Event | None) -> None:
        self.clock.reset()
        self.phase = "running"
        recorder = self.components.recorder
        engine = self.components.engagement
        try:
            if recorder:
                recorder.start(self.context)
                self._consumer_unsubscribers.append(self.bus.subscribe(recorder.on_event))
            if engine:

                def consume_signal(event: Event) -> None:
                    if event.source in ("speech", "vision"):
                        engine.on_event(event)

                self._consumer_unsubscribers.append(self.bus.subscribe(consume_signal))
            if fixture_started:
                self._accept(fixture_started)
            else:
                self._lifecycle("session.started", 0.0, {})
            if engine:
                engine.start(self.context)
            if self.config.mode == "live":
                self._adapter_starts = [
                    asyncio.create_task(self._start_adapter(name, adapter))
                    for name, adapter in self._adapters()
                ]
                await asyncio.gather(*self._adapter_starts)
        except asyncio.CancelledError:
            raise
        except Exception:
            self.error = self.error or "session_start_failed"
            await self.stop()
            raise

    def _adapters(self) -> list[tuple[str, object]]:
        return [("speech", self.components.speech), ("vision", self.components.vision)]

    async def _start_adapter(self, name: str, adapter) -> None:
        if adapter is None:
            self._status(name, "adapter_not_integrated")
            return
        try:
            await asyncio.wait_for(adapter.start(self.context), self.config.startup_timeout_s)
        except Exception:
            self._status(name, "adapter_start_failed")
            try:
                await asyncio.wait_for(
                    adapter.stop_capture(self.clock.now()), self.config.drain_timeout_s
                )
            except Exception:
                self.error = "adapter_cleanup_failed"

    async def stop(self) -> SessionSnapshot:
        if self.phase == "completed":
            if self._stop_task:
                await asyncio.shield(self._stop_task)
            return self.snapshot()
        if self.phase == "prepared":
            await self.start()
        if self._stop_task is None:
            self._stop_task = asyncio.create_task(self._stop())
        await asyncio.shield(self._stop_task)
        return self.snapshot()

    async def _stop(self) -> None:
        self.capture_end_s = self.clock.now()
        self.phase = "stopping"
        current = asyncio.current_task()
        if self.playback is not None and self.playback is not current:
            self.playback.cancel()
            await asyncio.gather(self.playback, return_exceptions=True)
        self._lifecycle("session.stopping", self.capture_end_s, {})
        if self.components.engagement:
            try:
                self.components.engagement.stop()
            except Exception:
                self.error = "engine_stop_failed"
        for task in self._adapter_starts:
            if not task.done():
                task.cancel()
        await asyncio.gather(*self._adapter_starts, return_exceptions=True)
        deadline = asyncio.get_running_loop().time() + self.config.drain_timeout_s

        async def bounded(operation: str, adapters: list[tuple[str, object]]) -> set[str]:
            async def run(adapter) -> bool:
                try:
                    if operation == "stop_capture":
                        await adapter.stop_capture(self.capture_end_s)
                    else:
                        await adapter.drain()
                    return True
                except Exception:
                    return False

            tasks = {
                asyncio.create_task(run(adapter)): name
                for name, adapter in adapters
                if adapter is not None
            }
            if not tasks:
                return set()
            done, pending = await asyncio.wait(
                tasks, timeout=max(0.0, deadline - asyncio.get_running_loop().time())
            )
            failed = {tasks[t] for t in pending} | {tasks[t] for t in done if not t.result()}
            for task in pending:
                task.cancel()
            # Adapters release resources in cancellation-safe finally blocks.
            await asyncio.gather(*pending, return_exceptions=True)
            return failed

        failed = await bounded("stop_capture", self._adapters())
        failed |= await bounded(
            "drain", [(name, adapter) for name, adapter in self._adapters() if name not in failed]
        )
        self.incomplete_sources = sorted(failed)
        self._lifecycle(
            "session.completed",
            self.capture_end_s,
            {
                "duration_s": self.capture_end_s,
                "incomplete_sources": self.incomplete_sources,
            },
        )
        self.phase = "completed"
        await self._complete_consumers()

    async def _complete_consumers(self) -> None:
        self.feedback_status = "pending"
        try:
            if self.components.recorder and not self._consumer_failed:
                completed = CompletedSession.model_validate(
                    self.components.recorder.complete(self.capture_end_s, self.incomplete_sources)
                )
                if (
                    completed.session_id != self.session_id
                    or completed.duration_s != self.capture_end_s
                    or completed.incomplete_sources != self.incomplete_sources
                ):
                    raise ValueError("recorder completion metadata mismatch")
                if self.components.feedback:
                    feedback = await asyncio.wait_for(
                        self.components.feedback.generate(completed),
                        self.config.feedback_timeout_s,
                    )
                    self.feedback = validate_feedback(feedback, completed)
                    self.feedback_status = "ready"
        except Exception:
            self.feedback = None
            self.error = "feedback_unavailable"
        finally:
            if self.feedback_status != "ready":
                self.feedback_status = "unavailable"
            for unsubscribe in self._consumer_unsubscribers:
                unsubscribe()
            self._consumer_unsubscribers.clear()

    def accept_authored(self, value: Event | dict) -> bool:
        """Trusted fixture seam; live producers cannot emit authored lifecycle events."""
        if self.config.mode != "fixture":
            raise ValueError("authored input requires fixture mode")
        event = parse_event(value)
        if event.session_id != self.session_id or self.phase == "completed":
            return False
        if event.type == "session.started":
            raise ValueError("use start() before fixture playback")
        if event.type == "session.stopping":
            if self.phase != "running":
                return False
            self.capture_end_s = event.timestamp_s
            self.phase = "stopping"
            if self.components.engagement:
                self.components.engagement.stop()
        if event.type == "session.completed":
            if self.phase != "stopping" or event.timestamp_s != self.capture_end_s:
                raise ValueError("authored completion must match capture end")
        accepted = self._accept(event)
        if accepted and event.type == "session.completed":
            self.incomplete_sources = event.payload.incomplete_sources
            self.phase = "completed"
        return accepted


class SessionManager:
    def __init__(self, factory: Callable[[SessionConfig], Components] | None = None) -> None:
        self.factory = factory
        self.current: SessionController | None = None

    def create(self, config: SessionConfig, **kwargs) -> SessionController:
        if self.current and (
            self.current.phase != "completed" or self.current.feedback_status == "pending"
        ):
            raise SessionConflict("stop the current session before creating another")
        if config.mode == "live" and self.factory is None:
            raise SessionConflict(
                "live_not_integrated: use synthetic replay until producer handoff"
            )
        components = self.factory(config) if self.factory else Components()
        self.current = SessionController(config, components, **kwargs)
        return self.current

    def get(self, session_id: str) -> SessionController:
        if self.current is None or self.current.session_id != session_id:
            raise KeyError(session_id)
        return self.current

    async def shutdown(self) -> None:
        if self.current:
            if self.current.phase != "completed":
                await self.current.stop()
            elif self.current._stop_task:
                await asyncio.shield(self.current._stop_task)
            elif self.current.playback:
                await asyncio.shield(self.current.playback)
