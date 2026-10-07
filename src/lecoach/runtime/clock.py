import time
from typing import Protocol


class Clock(Protocol):
    def reset(self) -> None: ...
    def now(self) -> float: ...


class MonotonicClock:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._start = time.monotonic()

    def now(self) -> float:
        return time.monotonic() - self._start


class FakeClock:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self._time = 0.0

    def now(self) -> float:
        return self._time

    def advance_to(self, value: float) -> None:
        if not value >= self._time or not value < float("inf"):
            raise ValueError("fake time must be finite and cannot move backward")
        self._time = value
