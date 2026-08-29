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
        boost, directive = (
            lorebook.get_emotional_residue_directive(outcome) if outcome else (0.0, "")
        )
        print(f"\nInput: '{text}' -> Outcome Detected: '{outcome}' (Tension Boost: +{boost})")
        print(f"Directive Generated:\n{directive}")

    print("\n--- Testing Multi-Sensory Injection Engine (5D Atmospheric Immersion) ---")
    sensory_dir = lorebook.get_sensory_directive(environment="bedroom", tension_meter=85.0)
    print(f"Sensory Directive (Tension: 85.0/100):\n{sensory_dir}")

    print("\n--- Testing 'Push-Pull' Denial Teasing Mechanic ---")
    rushed_prompt = "เอาเลย ด่วนๆ ยัดเข้ามาใน ท่าหมา เลย"
    for turn_denial_count in [0, 1, 2]:
        print(
            f"\nTurn {turn_denial_count + 1} Rushed Input (Denial Counter: {turn_denial_count}): '{rushed_prompt}'"
        )
        injected = lorebook.inject_context(
            rushed_prompt, tension_meter=75.0, denial_counter=turn_denial_count
        )
        print(f"Injected Directive:\n{injected}")

    print("\n--- Testing Group 1: Deep Psychological Systems ---")
    # 1. Non-linear Tension Curve & Breaking Point (>85)
    print("\n1. Breaking Point (>85% Tension):")
    breaking_dir = lorebook.inject_context("จับฉันใน ท่าหมา แบบช้าๆ สิ", tension_meter=88.0)
    print(f"Breaking Point Context:\n{breaking_dir}")

    # 2. Safeword Protocol
    print("\n2. Safeword Protocol Triggered:")
    is_safe, safe_dir = lorebook.check_safeword("พอแล้ว หยุดก่อนนะ")
    print(f"Safeword Detected: {is_safe} -> Directive:\n{safe_dir}")

    # 3. Memory Anchors Flashback
    print("\n3. Memory Anchor Flashback Triggered:")
    anchors = [
        {"term": "กลิ่นสบู่", "memory_text": "กลิ่นสบู่ที่ติดผิวกายหลังคืนฝนตกชุ่มฉ่ำในอดีต"}
    ]
    flashback_dir = lorebook.check_memory_anchors("จำได้ไหม กลิ่นสบู่ คืนนั้น...", anchors)
    print(f"Flashback Directive:\n{flashback_dir}")

    print("\n--- Testing Group 3: Advanced Game Mechanics ---")
    print("\n1. Tease & Deny Streak Engine:")
    streak = 0
    for i in range(4):
        is_surrender, tease_dir, streak = lorebook.evaluate_tease_and_deny(streak, "เอาเลย สิ")
        print(
            f"Turn {i+1} (Streak: {streak}) -> Surrender Moment: {is_surrender}\nDirective: {tease_dir}\n"
        )

    print("\n2. 3-Phase Realistic Push-Pull Dynamics:")
    for phase in ["resistance", "negotiation", "surrender"]:
        phase_dir = lorebook.get_push_pull_phase_directive(phase)
        print(f"Phase '{phase.upper()}':\n{phase_dir}\n")

    print("\n--- Testing Group 4: Memory & Continuity ---")
    print("\n1. Erotic Memory Palace RAG Contextual Recall:")
    memories = [{"summary": "ฉากแนบชิดใต้แสงไฟสลัวในห้องนอน คืนที่มีเสียงฝนตกกระทบกระจกหน้าต่าง"}]
    palace_dir = lorebook.check_erotic_memory_palace(
        "จำคืนนั้นได้ไหม ที่เรานอนฟังเสียงฝนด้วยกัน", memories
    )
    print(f"Memory Palace Directive:\n{palace_dir}")

    print("\n2. Attachment Style Evolution Directives:")
    for style in ["anxious", "avoidant", "secure", "disorganized"]:
        style_dir = lorebook.get_attachment_style_directive(style)
        print(f"Style '{style.upper()}':\n{style_dir}\n")

    print("\n--- Testing Beat-Aware Retrieval & Tension Threshold Filtering ---")
    beat_inj = lorebook.inject_context(
        "จับฉันใน ท่าหมา แบบช้าๆ สิ",
        tension_meter=65.0,
        current_beat="escalation",
    )
    print(f"Beat-Aware Injected Context (Beat: ESCALATION | Tension: 65.0):\n{beat_inj}")


if __name__ == "__main__":
    main()
