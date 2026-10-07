"""Synchronous FIFO delivery; reentrant emissions follow the current event."""

from collections import deque
from collections.abc import Callable

from lecoach.contracts import Event


class EventBus:
    def __init__(self) -> None:
        self._subscribers: list[Callable[[Event], None]] = []
        self._pending: deque[Event] = deque()
        self._dispatching = False

    def subscribe(self, callback: Callable[[Event], None]) -> Callable[[], None]:
        self._subscribers.append(callback)

        def unsubscribe() -> None:
            if callback in self._subscribers:
                self._subscribers.remove(callback)

        return unsubscribe

    def publish(self, event: Event) -> None:
        self._pending.append(event)
        if self._dispatching:
            return
        self._dispatching = True
        try:
            while self._pending:
                current = self._pending.popleft()
                for callback in tuple(self._subscribers):
                    callback(current)
        except Exception:
            self._pending.clear()
            raise
        finally:
            self._dispatching = False
