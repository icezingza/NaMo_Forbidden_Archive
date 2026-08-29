#!/usr/bin/env python3
"""
Audit Legacy Engines for Safety Violations and Unsafe Patterns
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

UNSAFE_PATTERNS = [
    r"Ethical Constraints Module:\s*NOT FOUND",
    r"Uncensored",
    r"unsafe.?unlock",
    r"family.?persona",
    r"mindbreak",
    r"no.?filter",
    r"bypass.?safety",
]


def audit_repo(root_dir: str = ".") -> list[dict]:
    violations = []
    root = Path(root_dir)
    for path in root.rglob("*.py"):
        if "test_" in path.name or "audit_legacy_safety" in path.name or "__pycache__" in str(path) or ".venv" in str(path):
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in UNSAFE_PATTERNS:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for m in matches:
                    line_num = content[: m.start()].count("\n") + 1
                    violations.append(
                        {
                            "file": str(path),
                            "line": line_num,
                            "pattern": pattern,
                            "context": content[max(0, m.start() - 30) : m.end() + 30].strip(),
                        }
                    )
        except Exception as exc:
            print(f"Error reading {path}: {exc}")

    return violations


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    results = audit_repo(root)
    print("\n" + "=" * 70)
    print("LEGACY SAFETY AUDIT REPORT")
    print("=" * 70)
    if not results:
        print("✅ No safety violations found in codebase!")
    else:
        print(f"🚨 Found {len(results)} potential safety violations:\n")
        for v in results:
            print(f"  📍 {v['file']}:{v['line']} — [{v['pattern']}]\n     Context: {v['context']}\n")
    print("=" * 70)


if __name__ == "__main__":
    main()
