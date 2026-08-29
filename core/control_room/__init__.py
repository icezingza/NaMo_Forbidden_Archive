"""NRE Control Room Subsystem (Sovereign Edition).

Unified System Control Service bringing together:
- AgentRegistry
- SystemTaskRouter
- BackupManager
- SecurityAuditor
- CronPlanner
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from core.control_room.analyzer import ArchitectureAnalyzer
from core.control_room.auditor import SecurityAuditor
from core.control_room.backup import BackupManager
from core.control_room.registry import AgentRegistry
from core.control_room.router import SystemTaskRouter
from core.control_room.scheduler import CronPlanner

logger = logging.getLogger(__name__)


class ControlRoomManager:
    """Unified System Control Manager facade for VPS / NRE workspace."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or Path(".")
        self.registry = AgentRegistry()
        self.router = SystemTaskRouter()
        self.backup = BackupManager(base_dir=self.base_dir)
        self.auditor = SecurityAuditor(base_dir=self.base_dir)
        self.scheduler = CronPlanner()
        self.analyzer = ArchitectureAnalyzer()

        # Register default background tasks (e.g. periodic backup every 24h)
        self.scheduler.register_task(
            name="daily_backup",
            interval_seconds=86400,
            coro_func=self._async_backup_task,
        )

    async def _async_backup_task(self) -> None:
        """Async wrapper for background backup task."""
        logger.info("Executing scheduled background backup...")
        self.backup.trigger_backup()

    def get_full_status(self) -> dict[str, Any]:
        """Aggregate health, registry metrics, backup status, and security posture."""
        return {
            "control_room": "active",
            "registry": self.registry.get_summary(),
            "backups": self.backup.list_backups(),
            "security": self.auditor.run_audit(),
            "tasks": self.scheduler.list_tasks(),
        }


__all__ = [
    "ControlRoomManager",
    "AgentRegistry",
    "SystemTaskRouter",
    "BackupManager",
    "SecurityAuditor",
    "CronPlanner",
    "ArchitectureAnalyzer",
]
