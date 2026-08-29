"""VPS Control Room CLI Tool for NRE Sovereign Edition.

Allows operators to inspect status, trigger backups, run security audits,
and test task routing directly via SSH / CLI.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from core.control_room import ControlRoomManager


def main() -> None:
    parser = argparse.ArgumentParser(description="NRE VPS Control Room Manager CLI")
    parser.add_argument(
        "action",
        choices=["status", "backup", "audit", "registry", "route", "analyze"],
        help="Action to perform",
    )
    parser.add_argument(
        "--text",
        type=str,
        default="",
        help="Input text for routing test or topic for architecture analysis",
    )
    parser.add_argument(
        "--engine",
        type=str,
        default=None,
        help="Explicit engine requested (when action=route)",
    )

    args = parser.parse_args()
    mgr = ControlRoomManager(base_dir=root_dir)

    if args.action == "status":
        res = mgr.get_full_status()
    elif args.action == "backup":
        res = mgr.backup.trigger_backup()
    elif args.action == "audit":
        res = mgr.auditor.run_audit()
    elif args.action == "registry":
        res = mgr.registry.get_summary()
    elif args.action == "route":
        res = mgr.router.route(user_input=args.text, requested_engine=args.engine)
    elif args.action == "analyze":
        res = mgr.analyzer.analyze(topic=args.text or "General System Architecture")

    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
