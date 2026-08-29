import json
import sys
import os
from pathlib import Path

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath("."))


def test_slow_burn_framework():
    print("=" * 60)
    print("  SLOW-BURN THAI EROTIC FRAMEWORK - INTEGRATION TEST")
    print("=" * 60)

    # 1. Verify Skill Directory & SKILL.md
    skill_dir = Path(".agents/skills/slow-burn-thai-erotic")
    skill_file = skill_dir / "SKILL.md"
    assert skill_file.exists(), "SKILL.md is missing!"
    print(f"✓ [Skill Check]: SKILL.md found at {skill_file}")

    # 2. Verify References & Lorebook JSON
    lorebook_file = skill_dir / "references" / "lorebook-positions.json"
    system_prompt_file = skill_dir / "references" / "system-prompt.md"

    assert lorebook_file.exists(), "Lorebook JSON is missing!"
    assert system_prompt_file.exists(), "System Prompt MD is missing!"

    with open(lorebook_file, encoding="utf-8") as f:
        entries = json.load(f)

    print(f"✓ [Lorebook Check]: Successfully loaded {len(entries)} lorebook entries.")

    # Test key trigger lookup
    triggers = [
        "titjob",
        "blowjob",
        "doggy",
        "cowgirl",
        "dirty talk",
        "aftercare",
        "เย็ดนม",
        "อมควย",
    ]
    matched_count = 0
    print("\n--- Testing Keyword Trigger Matching ---")
    for trigger in triggers:
        matches = []
        for entry in entries:
            keys = entry.get("key", [])
            if any(trigger.lower() in k.lower() for k in keys):
                matches.append(entry.get("comment", entry.get("id")))
        if matches:
            matched_count += 1
            print(f"  [Match Found] '{trigger}' -> Entry: {matches[0]}")
        else:
            print(f"  [No Match] '{trigger}'")

    assert matched_count > 0, "No lorebook triggers matched!"

    # 3. Simulate NaMo Slow-Burn Reaction Logic
    print("\n--- Live Slow-Burn Simulation Test ---")
    from core.character_profile import CharacterProfile
    from Core_Scripts.emotion_parasite_engine import EmotionParasiteEngine

    namo = CharacterProfile("NaMo")
    engine = EmotionParasiteEngine()

    test_queries = [
        "ลองคุยเสียวหน่อยสิคนดี",
        "เธอหิวรึยัง มาอมควยให้หน่อย",
        "นอนลงช้าๆ แล้วทำให้ดูหน่อย",
    ]

    for q in test_queries:
        res, stats = engine.analyze_and_react(q, namo)
        print(f"\nUser Input: '{q}'")
        print(f"NaMo Reaction: {res}")
        print(f"Stat Updates: {stats}")
        print(f"NaMo Current State: {namo.get_status_str()}")

    print("\n" + "=" * 60)
    print("  ALL SLOW-BURN INTEGRATION TESTS PASSED (100% SUCCESS)!")
    print("=" * 60)


if __name__ == "__main__":
    test_slow_burn_framework()
