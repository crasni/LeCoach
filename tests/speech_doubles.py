"""Scripted speech seams for tests: no audio devices, models, or optional packages."""

import threading

from lecoach.speech.seams import Boundary, MicrophoneLost, Transcription, Word

RATE = 16_000


class ScriptedSource:
    """Delivers silent frames on demand; a scripted segmenter decides where speech is."""

    sample_rate = RATE

    def __init__(self, fail: Exception | None = None):
        self.fail = fail
        self.opened = self.closed = self.delivered = 0
        self.on_audio = self.on_error = None

    def open(self, on_audio, on_error):
        self.opened += 1
        if self.fail:
            raise self.fail
        self.on_audio, self.on_error = on_audio, on_error

    def close(self):
        self.closed += 1

    def push(self, until_s: float, chunk_s: float = 0.1):
        """Deliver frames from the current position up to `until_s` of audio."""
        target, step = round(until_s * RATE), round(chunk_s * RATE)
        while self.delivered < target:
            count = min(step, target - self.delivered)
            self.on_audio([0.0] * count)
            self.delivered += count

    def lose(self):
        self.on_error(MicrophoneLost())


class ScriptedSegmenter:
    """Speech intervals in seconds of audio; `gate` blocks processing until set."""

    def __init__(self, intervals, gate: threading.Event | None = None):
        self.boundaries = sorted(
            [Boundary("start", round(start * RATE)) for start, _ in intervals]
            + [Boundary("end", round(end * RATE)) for _, end in intervals],
            key=lambda boundary: (boundary.frame, boundary.kind == "start"))
        self.gate = gate
        self.open = False
        self.calls = 0

    def process(self, samples, first_frame):
        self.calls += 1
        if self.gate is not None:
            self.gate.wait(5)
        last = first_frame + len(samples)
        found = [b for b in self.boundaries if first_frame <= b.frame < last]
        for boundary in found:
            self.open = boundary.kind == "start"
        return found

    def flush(self, end_frame):
        if self.open:
            self.open = False
            return [Boundary("end", end_frame)]
        return []


class ScriptedTranscriber:
    """One scripted final per segment, in order, with evenly spread word times.

    Partials return the first word. `fail_on` raises on that final (0-based);
    `gate` blocks every call until set.
    """

    def __init__(self, finals, ready=True, fail_on: int | None = None,
                 gate: threading.Event | None = None):
        self.finals, self._ready, self.fail_on, self.gate = list(finals), ready, fail_on, gate
        self.calls = self.final_calls = 0
        self.thread_names = set()

    @property
    def ready(self):
        return self._ready

    def transcribe(self, samples, sample_rate, final):
        self.calls += 1
        self.thread_names.add(threading.current_thread().name)
        if self.gate is not None:
            self.gate.wait(5)
        text = self.finals[min(self.final_calls, len(self.finals) - 1)] if self.finals else ""
        if not final:
            return Transcription(text.split()[0] if text else "")
        index, self.final_calls = self.final_calls, self.final_calls + 1
        if index == self.fail_on:
            raise RuntimeError("synthetic model failure")
        pieces = [f" {word}" for word in text.split()]
        step = len(samples) / sample_rate / max(len(pieces), 1)
        return Transcription(text, tuple(Word(piece, n * step, (n + 1) * step)
                                         for n, piece in enumerate(pieces)))
