"""Cron Planner and Task Scheduler for NRE Control Room.

Provides non-blocking async background scheduling for periodic tasks (backups, audits, memory flushes).
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from typing import Any

logger = logging.getLogger(__name__)


class CronPlanner:
    """Async background task scheduler."""

    def __init__(self) -> None:
        self._tasks: dict[str, dict[str, Any]] = {}
        self._running: bool = False
        self._loop_task: asyncio.Task | None = None

    def register_task(
        self,
        name: str,
        interval_seconds: int,
        coro_func: Callable[[], Awaitable[Any]],
    ) -> None:
        """Register a scheduled periodic task."""
        self._tasks[name] = {
            "name": name,
            "interval_seconds": interval_seconds,
            "coro_func": coro_func,
            "last_run": 0.0,
            "run_count": 0,
            "status": "idle",
        }
        logger.info("Registered background task '%s' (interval=%ds)", name, interval_seconds)

    async def start(self) -> None:
        """Start the background scheduler loop."""
        if self._running:
            return
        self._running = True
        self._loop_task = asyncio.create_task(self._scheduler_loop())
        logger.info("CronPlanner scheduler loop started.")

    async def stop(self) -> None:
        """Stop the scheduler loop gracefully."""
        self._running = False
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass
            self._loop_task = None
        logger.info("CronPlanner scheduler loop stopped.")

    async def _scheduler_loop(self) -> None:
        """Background loop checking and executing tasks."""
        while self._running:
            now = time.time()
            for task_meta in self._tasks.values():
                if now - task_meta["last_run"] >= task_meta["interval_seconds"]:
                    task_meta["status"] = "running"
                    try:
                        await task_meta["coro_func"]()
                        task_meta["run_count"] += 1
                        task_meta["last_run"] = time.time()
                        task_meta["status"] = "success"
                    except Exception as err:
                        task_meta["status"] = f"failed: {err}"
                        logger.error("Error executing task '%s': %s", task_meta["name"], err)
            await asyncio.sleep(5)

    def list_tasks(self) -> list[dict[str, Any]]:
        """List metadata for all scheduled tasks."""
        return [
            {
                "name": meta["name"],
                "interval_seconds": meta["interval_seconds"],
                "last_run": meta["last_run"],
                "run_count": meta["run_count"],
                "status": meta["status"],
            }
            for meta in self._tasks.values()
        ]
