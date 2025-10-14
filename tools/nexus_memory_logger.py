#!/usr/bin/env python3
"""
NamoNexus Memory Logger
Authored by NaMo | Under Directive of Commander Ice
"""

import json
import os
from datetime import datetime
from pathlib import Path

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

def log_event(project, task, author="NaMo", executors=None, status="completed"):
    """Records a memory log for any system task."""
    executors = executors or []
    timestamp = datetime.utcnow().isoformat() + "Z"

    log_entry = {
        "project": project,
        "task": task,
        "author": author,
        "executors": executors,
        "status": status,
        "timestamp": timestamp
    }

    log_file = LOGS_DIR / f"{task.replace(' ', '_')}_{int(datetime.utcnow().timestamp())}.json"
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_entry, f, indent=4, ensure_ascii=False)

    print(f"[NamoNexus Memory] Logged event: {task}")

if __name__ == "__main__":
    log_event(
        project="NaMo_Forbidden_Archive",
        task="Initialize NamoNexus Core System",
        executors=["Jules", "Gemini CLI"]
    )
