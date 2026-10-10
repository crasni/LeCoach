"""Single-threaded speech logic: utterances, metrics, and event envelopes.

The adapter feeds capture-time inputs from its worker threads through the event
loop; tests feed them directly. Every method returns v0 event dicts to emit.
"""

from .config import SpeechConfig
from .emitter import EventFactory
from .metrics import MetricsTracker
from .seams import Transcription
from .text import even_tokens, timed_tokens
from .tracking import UtteranceTracker


class SpeechPipeline:
    def __init__(self, session_id: str, config: SpeechConfig) -> None:
        self.config = config
        self.events = EventFactory(session_id)
        self.utterances = UtteranceTracker()
        self.metrics = MetricsTracker(config)

    def _windows(self, windows: list[tuple[str, dict]]) -> list[dict]:
        return [self.events.metrics(event_id, payload) for event_id, payload in windows]

    def speech_started(self, seq: int, at_s: float) -> list[dict]:
        self.utterances.start(seq, at_s)
        return self._windows(self.metrics.speech_started(seq, self.utterances.get(seq).start_s))

    def speech_ended(self, seq: int, at_s: float) -> list[dict]:
        self.utterances.end(seq, at_s)
        self.metrics.speech_ended(seq, self.utterances.get(seq).end_s)
        return []

    def partial(self, seq: int, text: str, covered_end_s: float) -> list[dict]:
        payload = self.utterances.partial(seq, text, covered_end_s)
        return [self.events.transcript(payload)] if payload else []

    def finalized(
        self, seq: int, transcription: Transcription, measurable: bool = True
    ) -> list[dict]:
        """Freeze an utterance. `measurable=False` marks a final whose words are
        unknown (failed transcription), so overlapping windows report null."""
        utterance = self.utterances.get(seq)
        start_s, end_s = utterance.start_s, utterance.end_s
        words = [(word.text, start_s + word.end_s) for word in transcription.words]
        tokens = (timed_tokens(words, start_s, end_s) if words
                  else even_tokens(transcription.text, start_s, end_s))
        measurable = (measurable and self.config.analysis_supported
                      and transcription.language in (None, self.config.language))
        payload, final = self.utterances.final(seq, transcription.text, tokens, measurable)
        return [self.events.transcript(payload)] + self._windows(
            self.metrics.finalized(seq, final))

    def unavailable(self, at_s: float, availability: str, reason: str) -> list[dict]:
        self.metrics.input_unavailable(at_s, availability)
        return [self.events.status(at_s, availability, reason)] + self._windows(
            self.metrics.advance(at_s))

    def advance(self, now_s: float) -> list[dict]:
        return self._windows(self.metrics.advance(now_s))

    def finish(self, capture_end_s: float) -> list[dict]:
        return self._windows(self.metrics.finish(capture_end_s))
