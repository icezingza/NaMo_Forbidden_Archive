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

