"""Deterministic post-session templates over the sole engine's recorded evidence."""

from collections.abc import Mapping

from lecoach.contracts import CompletedSession, Feedback
from lecoach.contracts.events import validate_feedback

from .selector import EvidenceIndex, select_moments


class TemplateFeedbackGenerator:
    def __init__(self, *, stale_after_s: Mapping[str, float]) -> None:
        # Values are supplied by composition from the engine's public RuleConfig.
        # Coaching does not define another set of audience thresholds/defaults.
        self._stale_after_s = dict(stale_after_s)

    async def generate(self, session: CompletedSession) -> Feedback:
        session = CompletedSession.model_validate(session)
        moments, omitted = select_moments(session, self._stale_after_s)
        index = EvidenceIndex(session, self._stale_after_s)
        limitations = []
        for source, label in (("speech", "Speech"), ("vision", "Camera")):
            observations = index.metrics[source]
            usable = any(
                e.payload.availability == "available"
                and (
                    (
                        e.payload.wpm is not None
                        or e.payload.filler_rate_per_min is not None
                        or e.payload.pause.state in ("active", "completed")
                    )
                    if source == "speech"
                    else e.payload.person_present is True
                    and e.payload.pose_available is True
                    and e.payload.facing_score is not None
                )
                for e in observations
            )
            if not usable:
                limitations.append(
                    f"No usable {label.lower()} delivery observations were recorded."
                )
            elif any(e.payload.availability != "available" for e in index.statuses[source]) or any(
                e.payload.availability != "available"
                or (source == "vision" and e.payload.facing_score is None)
                for e in observations
            ):
                limitations.append(f"{label} input was unavailable for part of this session.")
            if source in session.incomplete_sources:
                limitations.append(f"{label} processing did not finish before the drain timeout.")
        if omitted:
            limitations.append(
                "Some audience changes lacked supported, usable evidence and were omitted."
            )
        if not moments:
            limitations.append(
                "There is not enough supported audience evidence to select coaching moments."
            )
        return validate_feedback(
            Feedback(
                session_id=session.session_id,
                duration_s=session.duration_s,
                moments=moments,
                limitations=limitations,
            ),
            session,
        )
