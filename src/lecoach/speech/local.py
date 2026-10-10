"""Compose the production speech adapter for a live session.

    from lecoach.speech.local import build_local_adapter
    from lecoach.speech.whisper import warm_up

    warm_up(SpeechConfig())  # at application startup: load the model once

    def factory(config):
        return Components(speech=build_local_adapter(), ...)  # one adapter per session

Missing optional packages, model files, or devices never raise here: the adapter
starts and reports the matching speech `signal.status` instead.
"""

import logging
from pathlib import Path

from .adapter import SpeechAdapter
from .config import SpeechConfig
from .sources import PortAudioSource, WavFileSource
from .vad import SileroSegmenter
from .whisper import get_transcriber

log = logging.getLogger(__name__)

_LOAD = object()


def build_local_adapter(config: SpeechConfig | None = None, *, transcriber=_LOAD,
                        device: int | str | None = None,
                        wav: str | Path | None = None) -> SpeechAdapter:
    """One adapter per session on the shared model, the microphone (or a WAV
    replay), and a fresh Silero segmenter."""
    config = config or SpeechConfig()
    if transcriber is _LOAD:
        transcriber = get_transcriber(config)
    try:
        segmenter = SileroSegmenter(config)
    except Exception as error:  # runtime missing: reported as speech_vad_unavailable
        log.warning("speech voice activity detection unavailable: %s", error)
        segmenter = None
    source = (WavFileSource(wav, config.sample_rate) if wav is not None
              else PortAudioSource(config.sample_rate, device))
    return SpeechAdapter(config, source, segmenter, transcriber)
