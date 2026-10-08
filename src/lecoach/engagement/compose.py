"""Composition helpers that hand the real engine to Lane 1's session seams."""

from lecoach.contracts.interfaces import Components, SessionConfig
from lecoach.runtime.session import SessionConflict

from .config import RuleConfig
from .engine import RuleEngine


def replay_with_engine(rules: RuleConfig | None = None):
    """Factory for synthetic replay whose audience is computed by the real engine.

    Authored audience events in the fixtures are skipped by the replay seam. Coaching
    stays authored until the recorder/generator handoff. Live capture is not composed
    here, so live sessions remain explicitly unavailable.
    """

    def factory(config: SessionConfig) -> Components:
        if config.mode == "live":
            raise SessionConflict(
                "live_not_integrated: use synthetic replay until producer handoff"
            )
        return Components(engagement=RuleEngine(rules))

    factory.live_integrated = False
    return factory
