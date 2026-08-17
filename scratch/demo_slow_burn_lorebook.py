import json
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath("."))

def run_lorebook_demo():
    print("=" * 70)
    print("  🔥 DEMO: SLOW-BURN THAI EROTIC SKILL & LOREBOOK IN ACTION 🔥")
    print("=" * 70)

    lorebook_path = Path(".agents/skills/slow-burn-thai-erotic/references/lorebook-positions.json")
    with open(lorebook_path, encoding="utf-8") as f:
        lorebook = json.load(f)

    print(f"Total Lorebook Entries Loaded: {len(lorebook)}\n")

    # Sample scenarios testing various positions and kinks
    scenarios = [
        {"name": "Scenario 1: Titjob (นมหนีบ/เย็ดนม)", "trigger": "เย็ดนม"},
        {"name": "Scenario 2: Blowjob (อมควย/โม๊ก)", "trigger": "อมควย"},
        {"name": "Scenario 3: Doggy Style (ท่าหมา)", "trigger": "doggy"},
        {"name": "Scenario 4: Cowgirl (ขี่บน)", "trigger": "cowgirl"},
        {"name": "Scenario 5: Dirty Talk (คุยเสียว/พูดหยาบ)", "trigger": "talk dirty"},
        {"name": "Scenario 6: Aftercare (กอด/ดูแลหลังฉาก)", "trigger": "aftercare"}
    ]

    for sc in scenarios:
        print(f"📌 {sc['name']}")
        trigger = sc['trigger']
        matched_entry = None

        for entry in lorebook:
            keys = entry.get("key", [])
            if any(trigger.lower() in k.lower() for k in keys):
                matched_entry = entry
                break

        if matched_entry:
            comment = matched_entry.get("comment", "")
            content = matched_entry.get("content", "")
            keys_str = ", ".join(matched_entry.get("key", [])[:5])
            print(f"   [Matched Entry] : {comment}")
            print(f"   [Trigger Keys]  : {keys_str}...")
            print(f"   [SlowBurn Prose]: \"{content[:150]}...\"\n")
        else:
            print(f"   [No Match Found]\n")

    print("=" * 70)
    print("  ✅ SKILL & LOREBOOK DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_lorebook_demo()
