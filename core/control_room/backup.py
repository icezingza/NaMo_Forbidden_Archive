"""Backup Manager for NRE Control Room.

Executes deterministic timestamped backups of state files, memory stores, and vector indexes.
Supports rotation retention policy to keep disk usage controlled.
"""

from __future__ import annotations

import logging
import os
import time
import zipfile
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class BackupManager:
    """Manages system state backups and rotation retention policies."""

    def __init__(
        self,
        base_dir: Path | None = None,
        backup_dir: Path | None = None,
        max_backups: int = 10,
    ) -> None:
        self.base_dir = base_dir or Path(".")
        self.backup_dir = backup_dir or (self.base_dir / "backups")
        self.max_backups = max_backups
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def trigger_backup(self) -> dict[str, Any]:
        """Execute a full state backup archive.

        Returns metadata summary of the created backup.
        """
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        archive_name = f"namo_backup_{timestamp}.zip"
        archive_path = self.backup_dir / archive_name

        targets = [
            self.base_dir / "vector_db",
            self.base_dir / "memory_history.json",
            self.base_dir / "memory_protocol.json",
            self.base_dir / "namo_state.json",
            self.base_dir / "chat_profile.json",
            self.base_dir / "Rinlada_Memory.json",
            self.base_dir / "system.yaml",
        ]

        included_files = []
        start_time = time.time()

        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for target in targets:
                if not target.exists():
                    continue

                if target.is_file():
                    arcname = target.name
                    zipf.write(target, arcname=arcname)
                    included_files.append(arcname)
                elif target.is_dir():
                    for root, _, files in os.walk(target):
                        for file in files:
                            full_path = Path(root) / file
                            arcname = full_path.relative_to(self.base_dir)
                            zipf.write(full_path, arcname=str(arcname))
                            included_files.append(str(arcname))

        file_size = archive_path.stat().st_size
        duration = round(time.time() - start_time, 3)

        # Enforce retention policy
        self._rotate_backups()

        summary = {
            "status": "success",
            "archive_name": archive_name,
            "archive_path": str(archive_path.resolve()),
            "size_bytes": file_size,
            "file_count": len(included_files),
            "duration_seconds": duration,
            "timestamp": timestamp,
        }
        logger.info("Backup created successfully: %s (%d bytes)", archive_name, file_size)
        return summary

    def _rotate_backups(self) -> None:
        """Delete oldest backups if total exceeds max_backups."""
        backups = sorted(
            [f for f in self.backup_dir.glob("namo_backup_*.zip") if f.is_file()],
            key=lambda x: x.stat().st_mtime,
        )

        while len(backups) > self.max_backups:
            oldest = backups.pop(0)
            try:
                oldest.unlink()
                logger.info("Removed old backup due to retention policy: %s", oldest.name)
            except Exception as err:
                logger.warning("Failed to delete old backup %s: %s", oldest.name, err)

    def list_backups(self) -> list[dict[str, Any]]:
        """List all existing backup archives with metadata."""
        backups = sorted(
            [f for f in self.backup_dir.glob("namo_backup_*.zip") if f.is_file()],
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )

        return [
            {
                "name": b.name,
                "path": str(b.resolve()),
                "size_bytes": b.stat().st_size,
                "created_at": time.ctime(b.stat().st_mtime),
            }
            for b in backups
        ]
