"""Integration-owned local CPU composition through the subsystem public seams."""

import logging

from lespeech.coaching.feedback import TemplateFeedbackGenerator
from lespeech.coaching.recorder import InMemorySessionRecorder
from lespeech.contracts.interfaces import Components, SessionConfig
from lespeech.engagement import DEFAULT_RULES, RuleConfig, RuleEngine
from lespeech.engagement.compose import replay_with_engine
from lespeech.speech import SpeechConfig
from lespeech.speech.local import build_local_adapter as build_speech_adapter
from lespeech.speech.whisper import warm_up
from lespeech.vision.local_backend import build_local_adapter as build_vision_adapter
from lespeech.vision.local_backend import prewarm

log = logging.getLogger(__name__)


def prepare_live_factory(
    speech_config: SpeechConfig | None = None,
    rules: RuleConfig | None = None,
):
    """Prepare models before serving; acquire devices only when a session starts.

    Missing speech runtime/model preparation leaves speech unavailable without
    preventing a vision session. No weights are downloaded and no data is saved.
    Fixture sessions retain the existing computed-audience/authored-coach replay.
    """
    speech_config = speech_config or SpeechConfig()
    rules = rules or DEFAULT_RULES
    try:
        transcriber = warm_up(speech_config)
    except Exception as error:
        log.warning("Speech model preparation unavailable: %s", error)
        transcriber = None
    # Preparing this first adapter also loads the shared Silero model before the
    # API event loop. Later adapters reuse model weights, with fresh VAD state.
    prepared_speech = build_speech_adapter(speech_config, transcriber=transcriber)
    prewarm()
    replay = replay_with_engine(rules)

    def factory(config: SessionConfig) -> Components:
        nonlocal prepared_speech
        if config.mode == "fixture":
            return replay(config)
        speech = prepared_speech
        prepared_speech = None
        if speech is None:
            speech = build_speech_adapter(speech_config, transcriber=transcriber)
        return Components(
            speech=speech,
            vision=build_vision_adapter(),
            engagement=RuleEngine(rules),
            recorder=InMemorySessionRecorder(),
            feedback=TemplateFeedbackGenerator(
                stale_after_s={
                    "speech": rules.speech_stale_s,
                    "vision": rules.vision_stale_s,
                }
            ),
        )

    factory.live_integrated = True
    return factory
