"""Backward-compatible import surface for the manifest-aware lorebook runtime."""
from core.slowburn_lorebook_runtime import (
    DEFAULT_LOREBOOK_PATH,
    DEFAULT_PROMPT_PATH,
    POSITION_MAP,
    SlowBurnLorebook,
)

__all__ = ["DEFAULT_LOREBOOK_PATH", "DEFAULT_PROMPT_PATH", "POSITION_MAP", "SlowBurnLorebook"]
