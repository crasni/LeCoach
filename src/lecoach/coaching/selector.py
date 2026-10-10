"""Select evidence-linked moments from recorded audience output, without new rules."""

import math
from bisect import bisect_right
from collections.abc import Mapping
from dataclasses import dataclass, field

from lecoach.contracts import CompletedSession, Event
from lecoach.contracts.events import EngagementEvent, Moment, Reason

from . import templates


@dataclass
class Candidate:
    codes: set[str]
    metrics: dict[str, Event] = field(default_factory=dict)
    transitions: dict[str, EngagementEvent] = field(default_factory=dict)

    @property
    def span_s(self) -> float:
        return max(e.payload.window_end_s for e in self.metrics.values()) - min(
            e.payload.window_start_s for e in self.metrics.values()
        )

    def moment(self, kind: str) -> Moment:
        measurements = sorted(self.metrics.values(), key=lambda e: (e.timestamp_s, e.event_id))
        if kind == "strength":
            observation, suggestion = templates.strength(self.codes, measurements)
            timestamp = max(e.timestamp_s for e in measurements)
        else:
            observation, suggestion = templates.improvement(next(iter(self.codes)), measurements)
            timestamp = min(e.timestamp_s for e in measurements)
        evidence = sorted(
            [*self.metrics.values(), *self.transitions.values()],
            key=lambda e: (e.timestamp_s, e.event_id),
        )
        return Moment(
            timestamp_s=timestamp,
            kind=kind,
            observation=observation,
            suggestion=suggestion,
            evidence_event_ids=[e.event_id for e in evidence],
        )


class EvidenceIndex:
    def __init__(self, session: CompletedSession, stale_after_s: Mapping[str, float]):
        if set(stale_after_s) != {"speech", "vision"} or any(
            type(age) not in (int, float) or not math.isfinite(age) or age <= 0
            for age in stale_after_s.values()
        ):
            raise ValueError("provide finite positive speech/vision freshness limits")
        self.limits = dict(stale_after_s)
        self.events = {e.event_id: e for e in session.events}
        self.metrics = {source: [] for source in self.limits}
        self.statuses = {source: [] for source in self.limits}
        for event in session.events:
            if event.type in ("speech.metrics", "vision.metrics"):
                self.metrics[event.source].append(event)
            elif event.type == "signal.status":
                self.statuses[event.source].append(event)
        self.outages = {
            source: [e for e in history if e.payload.availability != "available"]
            for source, history in self.statuses.items()
        }
        self.times = {
            (kind, source): [e.timestamp_s for e in history[source]]
            for kind, history in (
                ("metrics", self.metrics),
                ("status", self.statuses),
                ("outage", self.outages),
            )
            for source in self.limits
        }

    def latest(self, source: str, kind: str, at: float) -> Event | None:
        history = {"metrics": self.metrics, "status": self.statuses, "outage": self.outages}[kind]
        position = bisect_right(self.times[kind, source], at) - 1
        return history[source][position] if position >= 0 else None

    def support(self, transition: EngagementEvent, reason: Reason) -> list[Event] | None:
        code = reason.code
        if code not in templates.REASON_SOURCES:
            return None
        source = templates.REASON_SOURCES[code]
        if source not in transition.payload.usable_sources:
            return None
        observations = []
        for event_id in dict.fromkeys(reason.source_event_ids):
            event = self.events.get(event_id)
            if (
                event is None
                or event.timestamp_s > transition.timestamp_s
                or not templates.usable_measurement(code, event)
            ):
                return None
            observations.append(event)
        newest = self.latest(source, "metrics", transition.timestamp_s)
        if newest is None or not templates.usable_measurement(code, newest):
            return None
        # Historical windows may prove a sustained run; its latest cited window
        # and the latest observed source must still be fresh at the decision.
        if any(
            transition.timestamp_s - timestamp > self.limits[source]
            for timestamp in (newest.timestamp_s, max(e.timestamp_s for e in observations))
        ):
            return None
        # An available status cannot revive pre-outage observations. A new
        # observation restores the source, but cannot make old citations usable.
        outage = self.latest(source, "outage", transition.timestamp_s)
        if outage is not None and any(
            event.timestamp_s <= outage.timestamp_s for event in [newest, *observations]
        ):
            return None
        return observations


def select_moments(
    session: CompletedSession, stale_after_s: Mapping[str, float]
) -> tuple[list[Moment], bool]:
    index = EvidenceIndex(session, stale_after_s)
    improvements: dict[tuple[int, str], Candidate] = {}
    strengths: list[Candidate] = []
    episode = 0
    in_negative_episode = False
    omitted = False
    for event in session.events:
        if event.type != "engagement.state":
            continue
        negative = event.payload.state in ("CONFUSED", "BORED")
        if negative and not in_negative_episode:
            episode += 1
        in_negative_episode = negative
        if not negative and event.payload.state != "ENGAGED":
            continue  # INTERESTED alone does not establish a sustained strength.
        positive_candidate = Candidate(set())
        if not event.payload.reasons:
            omitted = True
        for reason in event.payload.reasons:
            is_positive = reason.code in templates.POSITIVE_CODES
            observations = index.support(event, reason)
            if observations is None or negative == is_positive:
                omitted = True
                continue
            if negative:
                # Every repetition of a cause in one continuous negative episode
                # contributes evidence to one insight, not another quota slot.
                candidate = improvements.setdefault(
                    (episode, reason.code), Candidate({reason.code})
                )
            else:
                candidate = positive_candidate
                candidate.codes.add(reason.code)
            candidate.metrics.update((e.event_id, e) for e in observations)
            candidate.transitions[event.event_id] = event
        if positive_candidate.metrics:
            strengths.append(positive_candidate)

    ranked = sorted(
        improvements.values(),
        key=lambda c: (-c.span_s, min(e.timestamp_s for e in c.metrics.values()), sorted(c.codes)),
    )
    selected = []
    used: dict[str, set[str]] = {}
    for candidate in ranked:
        code = next(iter(candidate.codes))
        ids = set(candidate.metrics)
        if ids <= used.get(code, set()):
            continue  # A later episode cannot recycle identical evidence as new advice.
        used.setdefault(code, set()).update(ids)
        selected.append(candidate.moment("improvement"))
        if len(selected) == 3:
            break
    if strengths:
        strongest = min(
            strengths,
            key=lambda c: (
                -len({e.source for e in c.metrics.values()}),
                -c.span_s,
                max(e.timestamp_s for e in c.metrics.values()),
                sorted(c.transitions),
            ),
        )
        selected.append(strongest.moment("strength"))
    return sorted(selected, key=lambda m: (m.timestamp_s, m.kind, m.evidence_event_ids)), omitted
