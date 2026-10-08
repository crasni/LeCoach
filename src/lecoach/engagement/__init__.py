"""Sole engagement-engine implementation slot; owned by the realtime lane."""

from .config import DEFAULT_RULES, RuleConfig
from .engine import RuleEngine

__all__ = ["DEFAULT_RULES", "RuleConfig", "RuleEngine"]
