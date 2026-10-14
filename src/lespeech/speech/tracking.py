"""Canonical utterance revisions from segment boundaries and transcriptions."""

from dataclasses import dataclass

from .emitter import num
from .text import TimedToken


@dataclass(frozen=True)
class FinalUtterance:
    utterance_id: str
    start_s: float
    end_s: float
    text: str
    tokens: tuple[TimedToken, ...]
    measurable: bool


@dataclass
class _Utterance:
    utterance_id: str
    start_s: float
    end_s: float | None = None
    revision: int = -1
    partial_text: str | None = None
    partial_end_s: float = 0.0
    final: FinalUtterance | None = None


class UtteranceTracker:
    """One utterance per voice-activity segment: monotonic partials, one final.

    Segments arrive in capture order, so a start never precedes the previous
    segment's end; finals therefore never overlap.
    """

    def __init__(self) -> None:
        self._utterances: dict[int, _Utterance] = {}
        self._last_end_s = 0.0

    def get(self, seq: int) -> _Utterance:
        return self._utterances[seq]

    def start(self, seq: int, at_s: float) -> None:
        if seq in self._utterances:
            raise ValueError(f"utterance u{seq} already started")
        self._utterances[seq] = _Utterance(f"u{seq}", max(at_s, self._last_end_s))

    def end(self, seq: int, at_s: float) -> None:
        utterance = self._utterances[seq]
        if utterance.end_s is None:
            utterance.end_s = max(at_s, utterance.start_s)
            self._last_end_s = max(self._last_end_s, utterance.end_s)

    def partial(self, seq: int, text: str, covered_end_s: float) -> dict | None:
        """Return a new partial revision, or None for stale, empty, or repeated text."""
        utterance = self._utterances.get(seq)
        text = text.strip()
        if utterance is None or utterance.final is not None or not text:
            return None
        if text == utterance.partial_text:
            return None
        end_s = max(covered_end_s, utterance.start_s, utterance.partial_end_s)
        utterance.revision += 1
        utterance.partial_text, utterance.partial_end_s = text, end_s
        return {
            "utterance_id": utterance.utterance_id,
            "revision": utterance.revision,
            "is_final": False,
            "start_s": num(utterance.start_s),
            "end_s": num(end_s),
            "text": text,
        }

    def final(
        self, seq: int, text: str, tokens: list[TimedToken], measurable: bool
    ) -> tuple[dict, FinalUtterance]:
        """Freeze the utterance. Empty text retracts any displayed partial."""
        utterance = self._utterances[seq]
        if utterance.final is not None:
            raise ValueError(f"{utterance.utterance_id} is already final")
        if utterance.end_s is None:
            raise ValueError(f"{utterance.utterance_id} has not ended")
        text = text.strip()
        utterance.revision += 1
        utterance.final = FinalUtterance(
            utterance.utterance_id, utterance.start_s, utterance.end_s, text,
            tuple(tokens) if text else (), measurable,
        )
        payload = {
            "utterance_id": utterance.utterance_id,
            "revision": utterance.revision,
            "is_final": True,
            "start_s": num(utterance.start_s),
            "end_s": num(utterance.end_s),
            "text": text,
        }
        return payload, utterance.final
