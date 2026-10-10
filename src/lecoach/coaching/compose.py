"""Optional synthetic composition for integration-owner review; no default API change."""

from lecoach.contracts.interfaces import Components, SessionConfig
from lecoach.engagement import DEFAULT_RULES, RuleConfig, RuleEngine
from lecoach.runtime.session import SessionConflict

from .feedback import TemplateFeedbackGenerator
from .recorder import InMemorySessionRecorder


def replay_with_coaching(rules: RuleConfig | None = None):
    config = rules or DEFAULT_RULES

    def factory(session_config: SessionConfig) -> Components:
        if session_config.mode == "live":
            raise SessionConflict("live_not_integrated: synthetic coaching composition only")
        return Components(
            engagement=RuleEngine(config),
            recorder=InMemorySessionRecorder(),
            feedback=TemplateFeedbackGenerator(
                stale_after_s={
                    "speech": config.speech_stale_s,
                    "vision": config.vision_stale_s,
                }
            ),
        )

    factory.live_integrated = False
    return factory
