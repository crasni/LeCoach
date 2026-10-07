"""Small, strict JSON contracts shared by every producer and consumer."""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator, model_validator

Seconds = Annotated[float, Field(strict=True, ge=0, allow_inf_nan=False)]
Score = Annotated[float, Field(strict=True, ge=0, le=1, allow_inf_nan=False)]
Text = Annotated[str, Field(strict=True, min_length=1, pattern=r"\S")]
Count = Annotated[int, Field(strict=True, ge=0)]
Modality = Literal["speech", "vision"]
Availability = Literal["available", "unavailable", "error"]
AudienceState = Literal["ENGAGED", "NEUTRAL", "CONFUSED", "BORED", "INTERESTED"]


class Model(BaseModel):
    model_config = ConfigDict(
        extra="forbid", strict=True, allow_inf_nan=False, frozen=True, revalidate_instances="always"
    )


class EmptyPayload(Model):
    pass


class CompletionPayload(Model):
    duration_s: Seconds
    incomplete_sources: list[Modality]

    @model_validator(mode="after")
    def unique_sources(self) -> Self:
        if len(self.incomplete_sources) != len(set(self.incomplete_sources)):
            raise ValueError("incomplete_sources must be unique")
        return self


class StatusPayload(Model):
    availability: Availability
    reason: Text


class TranscriptPayload(Model):
    utterance_id: Text
    revision: Count
    is_final: bool
    start_s: Seconds
    end_s: Seconds
    text: str

    @model_validator(mode="after")
    def ordered_interval(self) -> Self:
        if self.start_s > self.end_s:
            raise ValueError("transcript start must precede end")
        return self


class Pause(Model):
    state: Literal["none", "active", "completed", "unknown"]
    duration_s: Seconds | None
    start_s: Seconds | None
    end_s: Seconds | None

    @model_validator(mode="after")
    def consistent_pause(self) -> Self:
        if self.state == "unknown":
            if self.duration_s is not None:
                raise ValueError("unknown pause duration must be null")
        elif self.state == "none":
            if (self.duration_s, self.start_s, self.end_s) != (0, None, None):
                raise ValueError("no pause requires zero duration and null bounds")
        elif self.state == "active":
            if self.start_s is None or self.duration_s is None or self.end_s is not None:
                raise ValueError("active pause requires start/duration and null end")
        elif (
            self.start_s is None
            or self.end_s is None
            or self.duration_s is None
            or self.end_s < self.start_s
            or abs(self.duration_s - (self.end_s - self.start_s)) > 1e-6
        ):
            raise ValueError("completed pause requires ordered bounds and matching duration")
        return self


class Window(Model):
    window_start_s: Seconds
    window_end_s: Seconds
    availability: Availability

    @model_validator(mode="after")
    def ordered_window(self) -> Self:
        if self.window_start_s > self.window_end_s:
            raise ValueError("window start must precede end")
        return self


class SpeechMetricsPayload(Window):
    wpm: Seconds | None
    filler_count: Count | None
    filler_rate_per_min: Seconds | None
    pause: Pause


class VisionMetricsPayload(Window):
    person_present: bool | None
    pose_available: bool | None
    facing_score: Score | None
    activity_score: Score | None

    @model_validator(mode="after")
    def absent_pose_is_unknown(self) -> Self:
        if (
            self.availability != "available"
            or self.person_present is not True
            or self.pose_available is not True
        ):
            if self.facing_score is not None or self.activity_score is not None:
                raise ValueError("unavailable person/pose must have null derived scores")
        return self


class Reason(Model):
    code: Text
    source_event_ids: Annotated[list[Text], Field(min_length=1)]


class EngagementPayload(Model):
    state: AudienceState
    previous_state: AudienceState
    reasons: list[Reason]
    usable_sources: list[Modality]

    @model_validator(mode="after")
    def consistent_evidence(self) -> Self:
        if len(self.usable_sources) != len(set(self.usable_sources)):
            raise ValueError("usable_sources must be unique")
        if not self.usable_sources and (self.state != "NEUTRAL" or self.reasons):
            raise ValueError("no usable sources requires NEUTRAL without reasons")
        return self


class Envelope(Model):
    schema_version: Literal[0]
    session_id: Text
    event_id: Text
    timestamp_s: Seconds

    @field_validator("schema_version", mode="before")
    @classmethod
    def integer_version(cls, value):
        if type(value) is not int or value != 0:
            raise ValueError("schema_version must be integer 0")
        return value

    @model_validator(mode="after")
    def observation_time(self) -> Self:
        payload = getattr(self, "payload", None)
        if isinstance(payload, Window) and self.timestamp_s != payload.window_end_s:
            raise ValueError("metric timestamp must equal capture window end")
        if isinstance(payload, TranscriptPayload) and self.timestamp_s != payload.end_s:
            raise ValueError("transcript timestamp must equal capture end")
        if isinstance(payload, CompletionPayload) and self.timestamp_s != payload.duration_s:
            raise ValueError("completion timestamp must equal duration")
        if getattr(self, "type", None) == "session.started" and self.timestamp_s != 0:
            raise ValueError("session starts at zero")
        return self


class StartedEvent(Envelope):
    source: Literal["session"]
    type: Literal["session.started"]
    payload: EmptyPayload


class StoppingEvent(Envelope):
    source: Literal["session"]
    type: Literal["session.stopping"]
    payload: EmptyPayload


class CompletedEvent(Envelope):
    source: Literal["session"]
    type: Literal["session.completed"]
    payload: CompletionPayload


class StatusEvent(Envelope):
    source: Modality
    type: Literal["signal.status"]
    payload: StatusPayload


class TranscriptEvent(Envelope):
    source: Literal["speech"]
    type: Literal["speech.transcript"]
    payload: TranscriptPayload


class SpeechMetricsEvent(Envelope):
    source: Literal["speech"]
    type: Literal["speech.metrics"]
    payload: SpeechMetricsPayload


class VisionMetricsEvent(Envelope):
    source: Literal["vision"]
    type: Literal["vision.metrics"]
    payload: VisionMetricsPayload


class EngagementEvent(Envelope):
    source: Literal["engagement"]
    type: Literal["engagement.state"]
    payload: EngagementPayload


Event = Annotated[
    StartedEvent
    | StoppingEvent
    | CompletedEvent
    | StatusEvent
    | TranscriptEvent
    | SpeechMetricsEvent
    | VisionMetricsEvent
    | EngagementEvent,
    Field(discriminator="type"),
]
EVENT_ADAPTER = TypeAdapter(Event)


def parse_event(value: object) -> Event:
    return EVENT_ADAPTER.validate_python(value)


class Moment(Model):
    timestamp_s: Seconds
    kind: Literal["strength", "improvement"]
    observation: Text
    suggestion: Text
    evidence_event_ids: Annotated[list[Text], Field(min_length=1)]

    @model_validator(mode="after")
    def unique_evidence(self) -> Self:
        if len(self.evidence_event_ids) != len(set(self.evidence_event_ids)):
            raise ValueError("moment evidence IDs must be unique")
        return self


class CompletedSession(CompletionPayload):
    session_id: Text
    events: list[Event]

    @model_validator(mode="after")
    def isolated_timeline(self) -> Self:
        keys = [(e.timestamp_s, e.event_id) for e in self.events]
        if keys != sorted(keys) or len({e.event_id for e in self.events}) != len(keys):
            raise ValueError("timeline must be sorted and deduplicated")
        if any(
            e.session_id != self.session_id or e.timestamp_s > self.duration_s for e in self.events
        ):
            raise ValueError("timeline includes foreign session or post-capture event")
        completed = [e for e in self.events if e.type == "session.completed"]
        started = [e for e in self.events if e.type == "session.started"]
        stopping = [e for e in self.events if e.type == "session.stopping"]
        if len(started) != 1 or len(stopping) != 1 or stopping[0].timestamp_s != self.duration_s:
            raise ValueError("timeline requires matching start and stop lifecycle events")
        if (
            len(completed) != 1
            or completed[0].payload.duration_s != self.duration_s
            or completed[0].payload.incomplete_sources != self.incomplete_sources
        ):
            raise ValueError("timeline requires one matching completion")
        return self


class Feedback(Model):
    session_id: Text
    duration_s: Seconds
    moments: Annotated[list[Moment], Field(max_length=4)]
    limitations: list[Text]

    @model_validator(mode="after")
    def evidence_bounds(self) -> Self:
        if (
            sum(m.kind == "strength" for m in self.moments) > 1
            or sum(m.kind == "improvement" for m in self.moments) > 3
        ):
            raise ValueError("feedback allows at most one strength and three improvements")
        if any(m.timestamp_s > self.duration_s for m in self.moments):
            raise ValueError("moment is after capture end")
        return self


def validate_feedback(feedback: Feedback, session: CompletedSession) -> Feedback:
    """Validate identity and evidence links, without choosing or inventing moments."""
    feedback = Feedback.model_validate(feedback)
    if feedback.session_id != session.session_id or feedback.duration_s != session.duration_s:
        raise ValueError("feedback identity/duration mismatch")
    events = {event.event_id: event for event in session.events}
    for moment in feedback.moments:
        if any(event_id not in events for event_id in moment.evidence_event_ids):
            raise ValueError("feedback has dangling evidence")
        if any(
            events[event_id].type
            in ("signal.status", "session.started", "session.stopping", "session.completed")
            for event_id in moment.evidence_event_ids
        ):
            raise ValueError("input limitations cannot become coaching evidence")
    return feedback
