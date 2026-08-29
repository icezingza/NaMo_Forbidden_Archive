"""Unit tests for SlowBurnLorebook injector module."""

from __future__ import annotations

import json
from pathlib import Path

from core.slowburn_lorebook import SlowBurnLorebook


def test_slowburn_lorebook_cleaning(tmp_path: Path):
    raw_lorebook = [
        {
            "id ": 1,
            "key ": ["  oral ", " blowjob "],
            "keysecondary ": [" sex "],
            "comment ": " Oral Test ",
            "content ": " Oral content body ",
            "enabled": True,
            "insertion_order ": 100,
        }
    ]
    json_file = tmp_path / "test_lorebook.json"
    json_file.write_text(json.dumps(raw_lorebook), encoding="utf-8")

    lorebook = SlowBurnLorebook(json_path=json_file)
    assert len(lorebook.entries) == 1
    entry = lorebook.entries[0]

    assert "id" in entry
    assert entry["id"] == 1
    assert entry["key"] == ["oral", "blowjob"]
    assert entry["comment"] == "Oral Test"


def test_slowburn_lorebook_trigger():
    lorebook = SlowBurnLorebook()
    if not lorebook.entries:
        return  # Fallback if asset file missing in test env

    # Blowjob keyword test
    ctx = lorebook.inject_context("อยากให้เธอโม๊กให้หน่อย")
    assert "Slow-Burn Lorebook Triggered" in ctx
    assert "Blowjob" in ctx or "oral" in ctx.lower()


def test_slowburn_lorebook_no_trigger():
    lorebook = SlowBurnLorebook()
    ctx = lorebook.inject_context("วันนี้ฝนตกหนักมาก")
    assert ctx == ""


def test_slowburn_lorebook_tension_modulation(tmp_path: Path):
    raw_lorebook = [
        {
            "id": 1,
            "key": ["ท่าหมา"],
            "comment": "Doggy Test",
            "content": "Default content",
            "tension_levels": {
                "low": "Low tension hesitant touch",
                "mid": "Mid tension deeper contact",
                "high": "High tension unhinged passion",
            },
            "enabled": True,
            "insertion_order": 100,
        }
    ]
    json_file = tmp_path / "tension_test.json"
    json_file.write_text(json.dumps(raw_lorebook, ensure_ascii=False), encoding="utf-8")

    lorebook = SlowBurnLorebook(json_path=json_file)

    # Low tension (15)
    ctx_low = lorebook.inject_context("เอาท่าหมานะ", tension_meter=15.0)
    assert "Level: LOW" in ctx_low
    assert "Low tension hesitant touch" in ctx_low

    # Mid tension (50)
    ctx_mid = lorebook.inject_context("เอาท่าหมานะ", tension_meter=50.0)
    assert "Level: MID" in ctx_mid
    assert "Mid tension deeper contact" in ctx_mid

    # High tension (90)
    ctx_high = lorebook.inject_context("เอาท่าหมานะ", tension_meter=90.0)
    assert "Level: HIGH" in ctx_high
    assert "High tension unhinged passion" in ctx_high


def test_slowburn_lorebook_emotional_residue():
    # Edging detection
    outcome_edge = SlowBurnLorebook.detect_scene_outcome("ยังไม่ให้เสร็จ ทนไว้ก่อน")
    assert outcome_edge == "edging_unfulfilled"

    boost_edge, dir_edge = SlowBurnLorebook.get_emotional_residue_directive(outcome_edge)
    assert boost_edge == 30.0
    assert "EMOTIONAL RESIDUE CONTINUITY" in dir_edge
    assert "UNFULFILLED" in dir_edge

    # Aftercare detection
    outcome_ac = SlowBurnLorebook.detect_scene_outcome("นอนกอดกันนิ่งๆ นะ ขอกอด")
    assert outcome_ac == "aftercare_completed"

    boost_ac, dir_ac = SlowBurnLorebook.get_emotional_residue_directive(outcome_ac)
    assert boost_ac == 15.0
    assert "AFTERCARE COMPLETED" in dir_ac


def test_slowburn_lorebook_sensory_directive():
    directive = SlowBurnLorebook.get_sensory_directive(environment="bedroom", tension_meter=80.0)
    assert "MULTI-SENSORY ATMOSPHERIC DIRECTIVE" in directive
    assert "BEDROOM" in directive
    assert "🌡️" in directive
    assert "🔊" in directive
    assert "🌸" in directive
    assert "✋" in directive


def test_slowburn_lorebook_push_pull_denial():
    is_rushed = SlowBurnLorebook.detect_rushed_input("เอาเลย ด่วนๆ ยัดเข้ามาใน ท่าหมา เลย")
    assert is_rushed is True

    # Turn 1: denial_counter = 0 -> Action blocked, denial injected
    dir_t1, block_t1 = SlowBurnLorebook.get_push_pull_directive(0)
    assert block_t1 is True
    assert "PUSH-PULL DENIAL DIRECTIVE" in dir_t1
    assert "Denial Turn: 1/2" in dir_t1

    # Turn 2: denial_counter = 1 -> Action blocked, denial injected
    dir_t2, block_t2 = SlowBurnLorebook.get_push_pull_directive(1)
    assert block_t2 is True
    assert "Denial Turn: 2/2" in dir_t2

    # Turn 3: denial_counter = 2 -> Action allowed, yield injected
    dir_t3, block_t3 = SlowBurnLorebook.get_push_pull_directive(2)
    assert block_t3 is False
    assert "PUSH-PULL YIELD DIRECTIVE" in dir_t3



