"""Replay reviewed, hand-authored cases without pretending to perform inference."""

import asyncio
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from lecoach.contracts import CompletedSession, Event, Feedback, parse_event
from lecoach.contracts.interfaces import Components, SessionConfig

from .clock import FakeClock
from .session import SessionController, SessionManager


def fixture_root() -> Path:
    checkout = Path(__file__).resolve().parents[3] / "checks" / "coaching"
    return (
        checkout
        if (checkout / "expectations.json").exists()
        else (Path(__file__).resolve().parents[1] / "fixture_data")
    )


@dataclass(frozen=True)
class FixtureCase:
    name: str
    description: str
    events: list[Event]
    authored_feedback: dict[str, Feedback]

    @property
    def session_ids(self) -> list[str]:
        return list(self.authored_feedback)


class FixtureRepository:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root or fixture_root()
        self._specs = json.loads((self.root / "expectations.json").read_text())

    def describe(self) -> list[dict]:
        return [
            {
                "name": name,
                "description": spec["description"],
                "session_count": len(spec["sessions"]),
            }
            for name, spec in self._specs.items()
        ]

    def load(self, name: str) -> FixtureCase:
        # Resolve only enumerated fixture names, never user-supplied paths.
        if name not in self._specs:
            raise ValueError("unknown_fixture_case")
        spec = self._specs[name]
        events = [
            parse_event(e)
            for e in json.loads((self.root / "fixtures" / f"{name}.json").read_text())
        ]
        index: dict[tuple[str, str], Event] = {}
        for event in events:
            key = (event.session_id, event.event_id)
            if key in index and index[key] != event:
                raise ValueError("fixture retry changed a stable ID")
            index[key] = event
        feedback = {}
        for oracle in spec["sessions"]:
            CompletedSession.model_validate(
                {
                    "session_id": oracle["session_id"],
                    "duration_s": oracle["duration_s"],
                    "incomplete_sources": oracle["incomplete_sources"],
                    "events": [
                        index[(oracle["session_id"], event_id)].model_dump()
                        for event_id in oracle["retained_event_ids"]
                    ],
                }
            )
            feedback[oracle["session_id"]] = Feedback.model_validate(oracle["feedback"])
        return FixtureCase(name, spec["description"], events, feedback)


def remap(event: Event, old_id: str, new_id: str) -> Event:
    if event.session_id != old_id:
        return event
    return parse_event({**event.model_dump(), "session_id": new_id})


async def finish_authored(controller: SessionController, authored: Feedback) -> None:
    await controller._complete_consumers()
    if controller.components.recorder is None and controller.components.feedback is None:
        controller.feedback = Feedback.model_validate(
            {
                **authored.model_dump(),
                "session_id": controller.session_id,
            }
        )
        controller.feedback_status = "ready"


async def play_browser(controller: SessionController, case: FixtureCase) -> None:
    """Paced transport demonstration; time itself remains deterministic fake time."""
    source_id = case.session_ids[0]
    clock = controller.clock
    assert isinstance(clock, FakeClock)
    try:
        for original in case.events:
            if original.type == "session.started":
                continue  # Controller already emitted the matching authored start.
            event = remap(original, source_id, controller.session_id)
            if event.session_id != controller.session_id:
                continue
            arrival_s = max(clock.now(), event.timestamp_s)
            await asyncio.sleep((arrival_s - clock.now()) / controller.config.replay_speed)
            clock.advance_to(arrival_s)
            if controller.components.engagement and event.source == "engagement":
                continue  # Real engine outputs replace authored audience transitions.
            controller.accept_authored(event)
            if event.type == "session.completed" and controller.phase == "completed":
                await finish_authored(controller, case.authored_feedback[source_id])
    except asyncio.CancelledError:
        raise
    except Exception:
        controller.error = "fixture_playback_failed"
        # Detach first so stop() does not wait for the task that requested it.
        controller.playback = None
        await controller.stop()


async def replay_case(
    case: FixtureCase,
    factory: Callable[[SessionConfig], Components] | None = None,
    delivery_schedule_s: list[float] | None = None,
    on_event: Callable[[Event], None] | None = None,
) -> dict:
    """Return a transport trace. This does not implement a production session logger."""
    if delivery_schedule_s is not None and len(delivery_schedule_s) != len(case.events):
        raise ValueError("delivery schedule must have one entry per input event")
    manager = SessionManager(factory)
    trace: list[dict] = []
    feedback: list[dict] = []
    unsubscribe: Callable[[], None] | None = None
    try:
        for index, event in enumerate(case.events):
            if event.type == "session.started":
                if unsubscribe:
                    unsubscribe()
                controller = manager.create(
                    SessionConfig(fixture_case=case.name), session_id=event.session_id
                )

                def receive(event: Event) -> None:
                    trace.append(event.model_dump())
                    if on_event:
                        on_event(event)

                unsubscribe = controller.bus.subscribe(receive)
                await controller.start(event)
                continue
            controller = manager.current
            if controller is None or event.session_id != controller.session_id:
                continue
            arrival_s = (
                event.timestamp_s if delivery_schedule_s is None else (delivery_schedule_s[index])
            )
            if arrival_s < event.timestamp_s:
                raise ValueError("delivery cannot precede capture")
            controller.clock.advance_to(max(controller.clock.now(), arrival_s))
            if controller.components.engagement and event.source == "engagement":
                continue
            accepted = controller.accept_authored(event)
            if accepted and event.type == "session.completed":
                await finish_authored(controller, case.authored_feedback[event.session_id])
                if controller.feedback:
                    feedback.append(controller.feedback.model_dump())
        return {
            "mode": "fixture",
            "case": case.name,
            "output_provenance": "computed_consumers" if factory else "hand_authored",
            "delivery_trace": trace,
            "feedback": feedback,
        }
    finally:
        if unsubscribe:
            unsubscribe()
        await manager.shutdown()
