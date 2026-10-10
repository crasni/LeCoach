"""Sole recorder/generator implementation slot; owned by the coaching lane."""

from .feedback import TemplateFeedbackGenerator
from .recorder import InMemorySessionRecorder

__all__ = ["InMemorySessionRecorder", "TemplateFeedbackGenerator"]
