#!/usr/bin/env python3
"""
Senior Python Script to update core/lorebooks/Sex_Positions_Kinks_SlowBurn_TH_v10.json:
1. Strip trailing/leading spaces from string arrays (key, keysRaw, keywordsRaw, keysecondary).
2. Add 'beat' field ("tease", "resistance", "escalation", "resolution", "recovery").
3. Add 'tension_threshold' field ([min, max]).
4. Overwrite original JSON file and report summary.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def strip_spaces(value):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    elif isinstance(value, str):
        return value.strip()
    return value


def determine_beat_and_tension(entry: dict) -> tuple[str, list[int]]:
    comment = str(entry.get("comment", "")).lower()
    content = str(entry.get("content", "")).lower()
    entry_id = entry.get("id", 0)

    # 1. Recovery
    if entry_id in (54, 55) or "aftercare" in comment or "aftermath" in comment or "หลังฉาก" in content or "นอนกอด" in content:
        return "recovery", [0, 40]

    # 2. Resolution (Orgasm / Climax / Cum / Creampie)
    if (
        entry_id in (52, 53)
        or "orgasm" in comment
        or "creampie" in comment
        or "cum" in comment
        or "เสร็จ" in content
        or "หลั่ง" in content
        or "จุดสุดยอด" in content
    ):
        return "resolution", [80, 100]

    # 3. Resistance / Tease
    if "resistance" in comment or "tease" in comment or "เล่นตัว" in content or "ต่อรอง" in content or "ปฏิเสธ" in content or "ชะลอ" in content:
        return "resistance", [20, 60]

    if "kiss" in comment or "foreplay" in comment or "touch" in comment or "ลูบไล้" in content or "สัมผัส" in content:
        return "tease", [10, 50]

    # 4. Escalation (Default for positions & kinks)
    return "escalation", [40, 85]


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    json_path = Path("core/lorebooks/Sex_Positions_Kinks_SlowBurn_TH_v10.json")
    if not json_path.exists():
        print(f"❌ File not found: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    updated_count = 0

    for entry in data:
        updated = False

        # 1. Strip trailing/leading spaces from string fields and arrays
        for field in ["key", "keysRaw", "keywordsRaw", "keysecondary"]:
            if field in entry:
                cleaned = strip_spaces(entry[field])
                if cleaned != entry[field]:
                    entry[field] = cleaned
                    updated = True

        # 2. Add 'beat' field
        beat, tension_range = determine_beat_and_tension(entry)
        entry["beat"] = beat
        entry["tension_threshold"] = tension_range
        updated_count += 1

    # Overwrite original file
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Updated {updated_count} entries in {json_path}")

    # Summary by Beat
    beat_counts = {}
    for entry in data:
        b = entry["beat"]
        beat_counts[b] = beat_counts.get(b, 0) + 1

    print("\n📊 Summary by Beat Classification:")
    for b, count in beat_counts.items():
        print(f"  - {b}: {count} entries")


if __name__ == "__main__":
    main()
