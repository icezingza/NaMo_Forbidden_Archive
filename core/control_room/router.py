"""System Task Router for NRE Control Room.

Fast, deterministic rule-based router that maps incoming requests to the optimal
persona engine or system action without LLM overhead.
"""

from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)


class SystemTaskRouter:
    """Deterministic intent and engine router."""

    def __init__(self) -> None:
        # Keyword patterns for deterministic engine selection
        self._patterns = [
            (re.compile(r"\b(dark|unfiltered|hardcore|sin|smut)\b", re.IGNORECASE), "dark"),
            (re.compile(r"\b(rinlada|sensual|arousal|fusion|erotic)\b", re.IGNORECASE), "rinlada"),
            (re.compile(r"\b(seraphina|complete|bot)\b", re.IGNORECASE), "seraphina"),
            (re.compile(r"\b(ultimate|brain|asi|supreme)\b", re.IGNORECASE), "ultimate"),
        ]

    def route(
        self,
        user_input: str,
        requested_engine: str | None = None,
        default_engine: str = "omega",
    ) -> dict[str, Any]:
        """Route input to target engine and determine routing metadata.

        Returns:
            {
                "target_engine": str,
                "confidence": float,
                "reasoning": str,
                "is_explicit_override": bool
            }
        """
        # 1. Explicit override takes precedence
        if requested_engine and requested_engine.strip():
            engine_clean = requested_engine.strip().lower()
            return {
                "target_engine": engine_clean,
                "confidence": 1.0,
                "reasoning": f"Explicit request engine='{engine_clean}'",
                "is_explicit_override": True,
            }

        # 2. Rule-based keyword matching
        for pattern, engine in self._patterns:
            if pattern.search(user_input):
                return {
                    "target_engine": engine,
                    "confidence": 0.95,
                    "reasoning": f"Matched pattern '{pattern.pattern}' -> {engine}",
                    "is_explicit_override": False,
                }

        # 3. Fallback to default engine
        return {
            "target_engine": default_engine,
            "confidence": 0.80,
            "reasoning": f"Default fallback -> {default_engine}",
            "is_explicit_override": False,
        }
