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

    test_inputs = [
        "เธอเดินเข้ามาใกล้ แล้วกระซิบว่า อยากให้ฉัน โม๊ก ให้ไหม",  # Blowjob
        "จับฉันใน ท่าหมา แบบช้าๆ สิ",  # Doggy Slow / Deep
        "ฉันอยาก กอด เธอหลังเสร็จ",  # Aftercare
        "สวัสดีครับ วันนี้อากาศดีจัง",  # No trigger
    ]

    for i, text in enumerate(test_inputs, 1):
        print(f"\n--- Test Case {i}: '{text}' ---")
        injected = lorebook.inject_context(text)

        if injected:
            print("✅ Detected Keyword Match! Injected Context:")
            print(injected)
        else:
            print("⚠️ No lorebook keywords triggered.")


if __name__ == "__main__":
    main()
