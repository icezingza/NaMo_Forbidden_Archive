"""Agent Registry for NRE Control Room.

Manages registered engines, capabilities, health status, and active session metrics.
Designed for zero-overhead in-memory lookups with optional JSON persistence.
"""

from __future__ import annotations

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Central registry tracking all active agents and persona engines."""

    def __init__(self) -> None:
        self._registry: dict[str, dict[str, Any]] = {}
        self._initialized_at: float = time.time()
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Populate default known engines."""
        defaults = {
            "omega": {
                "name": "omega",
                "class_name": "NaMoOmegaEngine",
                "description": "Default multi-modal cognitive persona engine",
                "status": "online",
                "capabilities": ["chat", "rag", "cognition", "streaming"],
                "active_sessions": 0,
                "registered_at": self._initialized_at,
                "last_active": self._initialized_at,
            },
            "dark": {
                "name": "dark",
                "class_name": "DarkNaMoSystem",
                "description": "Unfiltered intense dark persona system",
                "status": "online",
                "capabilities": ["chat", "intensity_control"],
                "active_sessions": 0,
                "registered_at": self._initialized_at,
                "last_active": self._initialized_at,
            },
            "rinlada": {
                "name": "rinlada",
                "class_name": "RinladaAI",
                "description": "Sensual emotional fusion engine",
                "status": "online",
                "capabilities": ["chat", "emotion_fusion", "arousal"],
                "active_sessions": 0,
                "registered_at": self._initialized_at,
                "last_active": self._initialized_at,
            },
            "seraphina": {
                "name": "seraphina",
                "class_name": "SeraphinaAI",
                "description": "Complete AI persona integration",
                "status": "online",
                "capabilities": ["chat", "advanced_memory"],
                "active_sessions": 0,
                "registered_at": self._initialized_at,
                "last_active": self._initialized_at,
            },
            "ultimate": {
                "name": "ultimate",
                "class_name": "NaMoUltimateBrain",
                "description": "Unified ultimate cognitive brain",
                "status": "online",
                "capabilities": ["chat", "ultimate_fusion"],
                "active_sessions": 0,
                "registered_at": self._initialized_at,
                "last_active": self._initialized_at,
            },
        }
        self._registry.update(defaults)

    def register_engine(
        self,
        name: str,
        class_name: str,
        description: str,
        capabilities: list[str],
        status: str = "online",
    ) -> dict[str, Any]:
        """Register a new engine or update an existing registration."""
        entry = {
            "name": name,
            "class_name": class_name,
            "description": description,
            "status": status,
            "capabilities": capabilities,
            "active_sessions": self._registry.get(name, {}).get("active_sessions", 0),
            "registered_at": self._registry.get(name, {}).get("registered_at", time.time()),
            "last_active": time.time(),
        }
        self._registry[name] = entry
        logger.info("Engine '%s' registered/updated in AgentRegistry.", name)
        return entry

    def update_status(self, name: str, status: str, active_sessions: int | None = None) -> bool:
        """Update status and active sessions count for a registered engine."""
        if name not in self._registry:
            return False
        self._registry[name]["status"] = status
        self._registry[name]["last_active"] = time.time()
        if active_sessions is not None:
            self._registry[name]["active_sessions"] = active_sessions
        return True

    def get_engine(self, name: str) -> dict[str, Any] | None:
        """Get registration details for a single engine."""
        return self._registry.get(name)

    def list_engines(self) -> list[dict[str, Any]]:
        """List all registered engines."""
        return list(self._registry.values())

    def get_summary(self) -> dict[str, Any]:
        """Return aggregated summary metrics for the registry."""
        total_engines = len(self._registry)
        online_count = sum(1 for e in self._registry.values() if e["status"] == "online")
        total_sessions = sum(e["active_sessions"] for e in self._registry.values())

        return {
            "total_engines": total_engines,
            "online_engines": online_count,
            "total_active_sessions": total_sessions,
            "uptime_seconds": round(time.time() - self._initialized_at, 2),
            "engines": self.list_engines(),
        }
