"""Test script for Slow-Burn Lorebook Injector."""

from __future__ import annotations

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir))

from core.slowburn_lorebook import SlowBurnLorebook


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("Loading Slow-Burn Lorebook (v10)...")
    lorebook = SlowBurnLorebook("core/lorebooks/Sex_Positions_Kinks_SlowBurn_TH_v10.json")

    test_cases = [
        ("จับฉันใน ท่าหมา แบบช้าๆ สิ", 20.0),  # Low Tension (20)
        ("จับฉันใน ท่าหมา แบบช้าๆ สิ", 50.0),  # Mid Tension (50)
        ("จับฉันใน ท่าหมา แบบช้าๆ สิ", 85.0),  # High Tension (85)
        ("เธอเดินเข้ามาใกล้ แล้วกระซิบว่า อยากให้ฉัน โม๊ก ให้ไหม", 85.0),  # Blowjob High
        ("สวัสดีครับ วันนี้อากาศดีจัง", 50.0),  # No trigger
    ]

    for i, (text, tension) in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: '{text}' (Tension: {tension}/100) ---")
        injected = lorebook.inject_context(text, tension_meter=tension)

        if injected:
            print("✅ Detected Keyword Match! Injected Context:")
            print(injected)
        else:
            print("⚠️ No lorebook keywords triggered.")

    print("\n--- Testing Emotional Residue & Aftercare Continuity ---")
    residue_samples = [
        "ทนไว้ก่อนนะ ยังไม่ให้เสร็จตอนนี้ ห้ามกลั้นหายใจ",  # Edging / Unfulfilled
        "ขอกอดหน่อยนะ นอนกอดกันนิ่งๆ",  # Aftercare
    ]
    for text in residue_samples:
        outcome = lorebook.detect_scene_outcome(text)
        boost, directive = lorebook.get_emotional_residue_directive(outcome) if outcome else (0.0, "")
        print(f"\nInput: '{text}' -> Outcome Detected: '{outcome}' (Tension Boost: +{boost})")
        print(f"Directive Generated:\n{directive}")


if __name__ == "__main__":
    main()
