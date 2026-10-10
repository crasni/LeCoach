"""Local faster-whisper transcription and the process-wide model provider.

The model loads once per process from the ignored `models/` directory, never
during a session and never from the network; `python -m lecoach.speech.model
--download` prepares it. `faster_whisper` and `numpy` come from the optional
`speech` dependency group and are imported when a model loads or runs.
"""

import logging
import threading
from array import array
from pathlib import Path

from .config import SpeechConfig
from .seams import Transcription, Word

log = logging.getLogger(__name__)

WHISPER_RATE = 16_000
# Segments the model itself scores as probably non-speech are dropped: on noise
# or silence, Whisper otherwise invents short text such as "You".
NO_SPEECH_DROP = 0.6


class ModelUnavailable(RuntimeError):
    """The speech runtime or the prepared model is missing or failed to load."""


def model_path(config: SpeechConfig) -> Path:
    return Path(config.model_dir) / f"faster-whisper-{config.model}"


def to_transcription(segments, language: str | None, *, words: bool) -> Transcription:
    """Join the speech segments' text; keep word timings for finals."""
    kept = [segment for segment in segments
            if segment.no_speech_prob < NO_SPEECH_DROP and segment.text.strip()]
    text = " ".join(segment.text.strip() for segment in kept)
    timed = tuple(Word(word.word, float(word.start), float(word.end))
                  for segment in kept for word in (segment.words or ())) if words else ()
    return Transcription(text, timed, language)


class WhisperTranscriber:
    """The `Transcriber` seam on one preloaded model; one call runs at a time."""

    def __init__(self, model, language: str = "en", *, initial_prompt: str | None = None) -> None:
        self._model = model
        self.language = language
        self.initial_prompt = initial_prompt
        self._lock = threading.Lock()

    @property
    def ready(self) -> bool:
        return self._model is not None

    def transcribe(self, samples, sample_rate: int, final: bool) -> Transcription:
        import numpy as np

        if isinstance(samples, array):
            audio = np.frombuffer(samples, dtype=np.float32)
        else:
            audio = np.asarray(samples, dtype=np.float32)
        if sample_rate != WHISPER_RATE:
            positions = np.arange(int(len(audio) * WHISPER_RATE / sample_rate))
            audio = np.interp(positions * sample_rate / WHISPER_RATE, np.arange(len(audio)),
                              audio).astype(np.float32)
        with self._lock:
            segments, info = self._model.transcribe(
                audio, language=self.language, beam_size=5 if final else 1, temperature=0.0,
                word_timestamps=final, vad_filter=False, condition_on_previous_text=False,
                initial_prompt=self.initial_prompt)
            segments = list(segments)  # decoding happens while iterating
        return to_transcription(segments, info.language, words=final)


_TRANSCRIBERS: dict[tuple, WhisperTranscriber] = {}
_LOCK = threading.Lock()


def load_transcriber(config: SpeechConfig) -> WhisperTranscriber:
    """Load the configured model once per process from `models/`; never download."""
    path = model_path(config)
    key = (str(path), config.device, config.compute_type, config.language)
    with _LOCK:
        if key in _TRANSCRIBERS:
            return _TRANSCRIBERS[key]
        if not (path / "model.bin").is_file():
            raise ModelUnavailable(
                f"no model in {path}; run: python -m lecoach.speech.model --download")
        try:
            from faster_whisper import WhisperModel

            model = WhisperModel(str(path), device=config.device,
                                 compute_type=config.compute_type, local_files_only=True)
        except Exception as error:
            raise ModelUnavailable(f"cannot load {path}: {error}") from error
        transcriber = _TRANSCRIBERS[key] = WhisperTranscriber(model, config.language)
        return transcriber


def get_transcriber(config: SpeechConfig) -> WhisperTranscriber | None:
    """`load_transcriber` for composition: None (logged) when the model is missing.

    The adapter then reports `speech_model_unavailable` instead of failing start.
    """
    try:
        return load_transcriber(config)
    except ModelUnavailable as error:
        log.warning("speech model unavailable: %s", error)
        return None


def warm_up(config: SpeechConfig) -> WhisperTranscriber:
    """Load the model and run one silent transcription, so the first session is not slow."""
    transcriber = load_transcriber(config)
    transcriber.transcribe(array("f", bytes(4 * WHISPER_RATE)), WHISPER_RATE, final=True)
    return transcriber
