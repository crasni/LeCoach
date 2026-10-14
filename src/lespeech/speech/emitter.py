"""Canonical v0 speech event envelopes with stable, session-unique IDs."""

import math


def floor_ms(value: float) -> float:
    """The latest whole millisecond not after `value`.

    Capture times are quantized down, so rounding never stamps an observation
    after the moment it describes or after the controller's capture end.
    """
    millis = math.floor(value * 1000 + 1e-6)  # tolerate float noise at exact milliseconds
    return millis / 1000 if millis / 1000 <= value else (millis - 1) / 1000


def num(value: float) -> float | int:
    """Millisecond capture precision; integral values stay integers."""
    value = round(value, 3)
    return int(value) if value == int(value) else value


def label(value: float) -> str:
    return str(num(value))


class EventFactory:
    """Builds `u<n>-r<revision>`, `metrics-<end>`, `pause-<end>`, `speech-status-<n>`."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self._statuses = 0

    def _event(self, event_id: str, kind: str, timestamp_s: float, payload: dict) -> dict:
        return {
            "schema_version": 0,
            "session_id": self.session_id,
            "event_id": event_id,
            "source": "speech",
            "type": kind,
            "timestamp_s": timestamp_s,
            "payload": payload,
        }

    def transcript(self, payload: dict) -> dict:
        event_id = f"{payload['utterance_id']}-r{payload['revision']}"
        return self._event(event_id, "speech.transcript", payload["end_s"], payload)

    def metrics(self, event_id: str, payload: dict) -> dict:
        return self._event(event_id, "speech.metrics", payload["window_end_s"], payload)

    def status(self, at_s: float, availability: str, reason: str) -> dict:
        self._statuses += 1
        return self._event(f"speech-status-{self._statuses}", "signal.status", num(at_s),
                           {"availability": availability, "reason": reason})
