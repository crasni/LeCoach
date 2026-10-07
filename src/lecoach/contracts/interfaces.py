"""Public implementation seams. Subsystems import contracts, not each other."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, Protocol

from pydantic import Field

from lecoach.runtime.clock import Clock

from .events import CompletedSession, Event, Feedback, Model, Seconds, Text


class SessionConfig(Model):
    mode: Literal["fixture", "live"] = "fixture"
    fixture_case: Text = "weak_to_improved"
    replay_speed: float = Field(default=5.0, strict=True, gt=0, le=100, allow_inf_nan=False)
    startup_timeout_s: float = Field(default=5.0, strict=True, gt=0, le=60)
    drain_timeout_s: float = Field(default=2.0, strict=True, gt=0, le=60)
    feedback_timeout_s: float = Field(default=5.0, strict=True, gt=0, le=60)


class RuntimeSettings(Model):
    client_queue_size: int = Field(default=128, strict=True, ge=1, le=10000)
    preview_interval_s: float = Field(default=0.2, strict=True, gt=0, le=10)
    preview_max_bytes: int = Field(default=512_000, strict=True, ge=1)


@dataclass(frozen=True)
class SessionContext:
    session_id: str
    clock: Clock
    emit: Callable[[Event | dict], bool]
    config: SessionConfig


class CaptureAdapter(Protocol):
    async def start(self, context: SessionContext) -> None: ...
    async def stop_capture(self, capture_end_s: float) -> None: ...
    async def drain(self) -> None: ...


class VisionAdapter(CaptureAdapter, Protocol):
    def preview_jpeg(self) -> bytes | None: ...


class EngagementEngine(Protocol):
    def start(self, context: SessionContext) -> None: ...
    def on_event(self, event: Event) -> None: ...
    def stop(self) -> None: ...


class SessionRecorder(Protocol):
    def start(self, context: SessionContext) -> None: ...
    def on_event(self, event: Event) -> None: ...
    def complete(self, duration_s: float, incomplete_sources: list[str]) -> CompletedSession: ...


class FeedbackGenerator(Protocol):
    async def generate(self, session: CompletedSession) -> Feedback: ...


@dataclass
class Components:
    speech: CaptureAdapter | None = None
    vision: VisionAdapter | None = None
    engagement: EngagementEngine | None = None
    recorder: SessionRecorder | None = None
    feedback: FeedbackGenerator | None = None


class SessionSnapshot(Model):
    session_id: Text
    mode: Literal["fixture", "live"]
    phase: Literal["prepared", "running", "stopping", "completed"]
    elapsed_s: Seconds
    duration_s: Seconds | None
    incomplete_sources: list[Literal["speech", "vision"]]
    input_status: dict[str, dict[str, str]]
    latest_events: dict[str, Event]
    transcript: list[Event]
    feedback_status: Literal["pending", "ready", "unavailable"]
    output_provenance: Literal["hand_authored", "computed"]
    error: str | None
