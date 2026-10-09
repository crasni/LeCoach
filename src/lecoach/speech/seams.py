"""Device and model seams for the speech adapter.

Production implementations (PortAudio microphone, voice activity detection,
faster-whisper) live behind these protocols and import their optional
dependencies lazily. Tests use scripted implementations.
"""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Literal, Protocol


class MicrophoneError(RuntimeError):
    """Base class for capture failures reported as speech `signal.status`."""

    availability = "unavailable"
    reason = "microphone_unavailable"


class MicrophonePermissionDenied(MicrophoneError):
    reason = "microphone_permission_denied"


class MicrophoneNotFound(MicrophoneError):
    reason = "microphone_not_found"


class MicrophoneLost(MicrophoneError):
    availability = "error"
    reason = "microphone_disconnected"


@dataclass(frozen=True)
class Word:
    """A model word piece; times are seconds from the start of the segment audio."""

    text: str
    start_s: float
    end_s: float


@dataclass(frozen=True)
class Transcription:
    """Model output for one segment. Empty text means no speech was recognized."""

    text: str
    words: tuple[Word, ...] = ()
    language: str | None = None


@dataclass(frozen=True)
class Boundary:
    """A voice-activity boundary at an absolute frame index since capture start."""

    kind: Literal["start", "end"]
    frame: int


class AudioSource(Protocol):
    """Mono float32 microphone frames at `sample_rate`, delivered on a device thread."""

    sample_rate: int

    def open(
        self,
        on_audio: Callable[[Sequence[float]], None],
        on_error: Callable[[MicrophoneError], None],
    ) -> None:
        """Start streaming; raise MicrophoneError subclasses for denied/missing devices."""

    def close(self) -> None:
        """Stop streaming and release the device. Must be idempotent."""


class Segmenter(Protocol):
    """Voice activity detection; splits segments longer than the maximum utterance."""

    def process(self, samples: Sequence[float], first_frame: int) -> list[Boundary]: ...

    def flush(self, end_frame: int) -> list[Boundary]:
        """Close any open segment at `end_frame` (capture end or device loss)."""


class Transcriber(Protocol):
    """A preloaded local speech-to-text model shared across sessions."""

    @property
    def ready(self) -> bool: ...

    def transcribe(self, samples: Sequence[float], sample_rate: int, final: bool) -> Transcription:
        """Transcribe one segment's audio; finals include word timestamps."""
