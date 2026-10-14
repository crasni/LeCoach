"""Windowed WPM, filler, and pause observations from capture-time inputs.

The rules match the reviewed synthetic fixtures (`checks/speech/make_fixtures.py`):

- a trailing window is due every hop; if an utterance is in progress at the hop
  time, the window ends where that utterance began, so it never waits for
  unfinished speech;
- windows that would not advance, or that are shorter than the minimum
  observation before capture end, are skipped; a capture-end window is final;
- a window waits for the finals of every utterance it overlaps, up to the
  coverage wait, and reports null WPM/fillers if they do not arrive;
- silence of at least the pause minimum after the first speech is an active
  pause, then exactly one completed-pause window when speech resumes;
- after input becomes unavailable, windows report that availability with null
  values and an unknown pause;
- a window overlapping a final that could not be measured (unsupported language
  or failed transcription) reports null WPM and fillers.

Inputs must arrive in capture order: a boundary is reported before any `advance`
past it. Times are seconds on the shared session clock; the adapter supplies
them as whole milliseconds.
"""

import math
from dataclasses import dataclass

from .config import SpeechConfig
from .emitter import floor_ms, label, num
from .tracking import FinalUtterance

# Windows closer than this to the previous one carry no new information and
# would collide on millisecond event-ID labels.
_MIN_ADVANCE_S = 0.0005


@dataclass
class _Span:
    start_s: float
    end_s: float = math.inf
    final: FinalUtterance | None = None


@dataclass
class _Window:
    event_id: str
    end_s: float
    deadline_s: float
    pause_start_s: float | None = None


class MetricsTracker:
    def __init__(self, config: SpeechConfig) -> None:
        self.config = config
        self._spans: dict[int, _Span] = {}
        self._pending: list[_Window] = []
        self._window_ends: list[float] = []
        self._next_hop = 1
        self._last_end_s = 0.0
        self._now_s = 0.0
        self._lost: tuple[float, str] | None = None
        self._capture_end_s: float | None = None

    # Inputs ---------------------------------------------------------------

    def speech_started(self, seq: int, at_s: float) -> list[tuple[str, dict]]:
        # Windows due strictly before this onset could not have seen it.
        self._schedule(at_s, inclusive=False)
        ended = [span.end_s for span in self._spans.values() if span.end_s != math.inf]
        self._spans[seq] = _Span(at_s)
        resumed = ended and at_s - max(ended) >= self.config.pause_min_s
        if resumed and not self._unavailable_at(at_s):
            self._reserve(_Window(f"pause-{label(at_s)}", at_s,
                                  at_s + self.config.coverage_wait_s, max(ended)))
        return self._resolve()

    def speech_ended(self, seq: int, at_s: float) -> None:
        span = self._spans[seq]
        if span.end_s == math.inf:
            span.end_s = max(at_s, span.start_s)

    def finalized(self, seq: int, final: FinalUtterance) -> list[tuple[str, dict]]:
        self._spans[seq].final = final
        return self._resolve()

    def input_unavailable(self, at_s: float, availability: str) -> None:
        if self._lost is None:
            self._lost = (at_s, availability)

    def advance(self, now_s: float) -> list[tuple[str, dict]]:
        self._now_s = max(self._now_s, now_s)
        self._schedule(self._now_s, inclusive=True)
        return self._resolve()

    def finish(self, capture_end_s: float) -> list[tuple[str, dict]]:
        """Schedule the capture-end window and resolve everything still pending.

        Audio can run a few milliseconds ahead of the shared clock, so windows
        past capture end are discarded (the controller would reject them) and do
        not suppress the capture-end window.
        """
        if self._capture_end_s is None:
            self._capture_end_s = capture_end_s
            self._pending = [w for w in self._pending if w.end_s <= capture_end_s + 1e-9]
            self._last_end_s = max((end for end in self._window_ends
                                    if end <= capture_end_s + 1e-9), default=0.0)
            self._schedule(capture_end_s, inclusive=True)
            self._candidate(capture_end_s)
        return self._resolve(force=True)

    # Scheduling -----------------------------------------------------------

    def _schedule(self, until_s: float, inclusive: bool) -> None:
        hop = self.config.metrics_hop_s
        while True:
            due = floor_ms(self._next_hop * hop)  # millisecond ends keep event IDs distinct
            if due > until_s + 1e-9 or (not inclusive and due >= until_s - 1e-9):
                return
            if self._capture_end_s is not None and due > self._capture_end_s + 1e-9:
                return
            self._next_hop += 1
            self._candidate(due)

    def _candidate(self, due_s: float) -> None:
        end_s = next((span.start_s for span in self._spans.values()
                      if span.start_s < due_s < span.end_s), due_s)
        final = self._capture_end_s is not None and due_s >= self._capture_end_s - 1e-9
        if end_s <= self._last_end_s + _MIN_ADVANCE_S:
            return
        if not final and end_s - max(0.0, end_s - self.config.metrics_window_s) \
                < self.config.min_observation_s - 1e-9:
            return
        self._reserve(_Window(f"metrics-{label(end_s)}", end_s,
                              due_s + self.config.coverage_wait_s))

    def _reserve(self, window: _Window) -> None:
        self._pending.append(window)
        self._window_ends.append(window.end_s)
        self._last_end_s = max(self._last_end_s, window.end_s)

    # Resolution -----------------------------------------------------------

    def _resolve(self, force: bool = False) -> list[tuple[str, dict]]:
        ready, waiting = [], []
        for window in self._pending:
            if self._unavailable_at(window.end_s):
                ready.append((window.event_id, self._unavailable_payload(window)))
                continue
            covered = all(span.final is not None for span in self._overlapping(window.end_s))
            if covered or force or self._now_s >= window.deadline_s - 1e-9:
                ready.append((window.event_id, self._payload(window, covered)))
            else:
                waiting.append(window)
        self._pending = waiting
        return ready

    def _bounds(self, end_s: float) -> tuple[float, float]:
        return max(0.0, end_s - self.config.metrics_window_s), end_s

    def _overlapping(self, end_s: float) -> list[_Span]:
        start_s, _ = self._bounds(end_s)
        return [span for span in self._spans.values()
                if span.start_s < end_s and span.end_s > start_s]

    def _unavailable_at(self, end_s: float) -> bool:
        return self._lost is not None and end_s > self._lost[0]

    def _unavailable_payload(self, window: _Window) -> dict:
        start_s, end_s = self._bounds(window.end_s)
        return {
            "window_start_s": num(start_s),
            "window_end_s": num(end_s),
            "availability": self._lost[1],
            "wpm": None,
            "filler_count": None,
            "filler_rate_per_min": None,
            "pause": {"state": "unknown", "duration_s": None, "start_s": None, "end_s": None},
        }

    def _payload(self, window: _Window, covered: bool) -> dict:
        start_s, end_s = self._bounds(window.end_s)
        minutes = (end_s - start_s) / 60
        overlapping = self._overlapping(end_s)
        known = (
            covered
            and self.config.analysis_supported
            and all(span.final.measurable for span in overlapping if span.final)
            and end_s - start_s >= self.config.min_observation_s - 1e-9
        )
        tokens = [token for span in self._spans.values() if span.final
                  for token in span.final.tokens if start_s < token.at_s <= end_s]
        words = sum(1 for token in tokens if token.counts_as_word)
        fillers = sum(1 for token in tokens if token.ends_filler)
        return {
            "window_start_s": num(start_s),
            "window_end_s": num(end_s),
            "availability": "available",
            "wpm": num(round(words / minutes, 1)) if known else None,
            "filler_count": fillers if known else None,
            "filler_rate_per_min": num(round(fillers / minutes, 1)) if known else None,
            "pause": self._pause(window),
        }

    def _pause(self, window: _Window) -> dict:
        end_s = window.end_s
        if window.pause_start_s is not None:
            return {"state": "completed", "duration_s": num(end_s - window.pause_start_s),
                    "start_s": num(window.pause_start_s), "end_s": num(end_s)}
        ended = [span.end_s for span in self._spans.values() if span.end_s <= end_s]
        speaking = any(span.start_s <= end_s < span.end_s for span in self._spans.values())
        if ended and not speaking and end_s - max(ended) >= self.config.pause_min_s - 1e-9:
            return {"state": "active", "duration_s": num(end_s - max(ended)),
                    "start_s": num(max(ended)), "end_s": None}
        return {"state": "none", "duration_s": 0, "start_s": None, "end_s": None}
