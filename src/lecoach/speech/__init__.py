"""Speech adapter implementation slot; owned by the audio lane.

Model-free core: configuration, text rules, utterance and metrics tracking, and
the session adapter. Production microphone and transcription seams import their
optional dependencies lazily, so this package imports without them.
"""

from .adapter import SpeechAdapter
from .config import SpeechConfig
from .seams import (
    AudioSource,
    Boundary,
    MicrophoneError,
    MicrophoneLost,
    MicrophoneNoSignal,
    MicrophoneNotFound,
    MicrophonePermissionDenied,
    Segmenter,
    Transcriber,
    Transcription,
    Word,
)

__all__ = [
    "AudioSource",
    "Boundary",
    "MicrophoneError",
    "MicrophoneLost",
    "MicrophoneNoSignal",
    "MicrophoneNotFound",
    "MicrophonePermissionDenied",
    "Segmenter",
    "SpeechAdapter",
    "SpeechConfig",
    "Transcriber",
    "Transcription",
    "Word",
]
