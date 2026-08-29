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
