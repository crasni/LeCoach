"""Executable v0 contracts. Semantics are defined in docs/ARCHITECTURE.md."""

from .events import EVENT_ADAPTER, CompletedSession, Event, Feedback, parse_event

__all__ = ["EVENT_ADAPTER", "CompletedSession", "Event", "Feedback", "parse_event"]
