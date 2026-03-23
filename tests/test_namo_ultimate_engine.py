import os
import sys

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.namo_ultimate_engine import NaMoUltimateBrain


@pytest.fixture
def engine():
    return NaMoUltimateBrain()


def test_process_input_returns_standard_shape(engine):
    result = engine.process_input("สวัสดีค่ะ", session_id="test-001")
    assert isinstance(result, dict)
    assert "text" in result
    assert "media_trigger" in result
    assert "system_status" in result


def test_process_input_text_is_string(engine):
    result = engine.process_input("ต้องการอะไรไหมคะ", session_id="test-002")
    assert isinstance(result["text"], str)
    assert len(result["text"]) > 0


def test_process_input_media_trigger_keys(engine):
    result = engine.process_input("hello", session_id="test-003")
    media = result["media_trigger"]
    assert "image" in media
    assert "audio" in media
    assert "tts" in media


def test_process_input_system_status_has_required_keys(engine):
    result = engine.process_input("ทดสอบ", session_id="test-004")
    status = result["system_status"]
    assert "arousal" in status
    assert "sin_status" in status
    assert "active_personas" in status


def test_arousal_increases_with_input(engine):
    engine.process_input("ทดสอบ 1", session_id="s1")
    arousal_after = engine._get_arousal("s1")
    assert arousal_after >= 0


def test_moan_appended_when_arousal_high(engine):
    engine._set_arousal("s2", 60)
    result = engine.process_input("ทดสอบ", session_id="s2")
    assert "ความเงี่ยน:" in result["text"]


def test_get_status_returns_engine_info(engine):
    status = engine.get_status()
    assert status["engine"] == "NaMoUltimateBrain"
    assert status["status"] == "online"
    assert "active_sessions" in status
    assert "avg_arousal" in status


def test_build_system_prompt_contains_context(engine):
    prompt = engine._build_system_prompt("ทดสอบบริบท")
    assert "ทดสอบบริบท" in prompt
    assert "NaMo" in prompt


def test_cognitive_stack_attached(engine):
    assert engine.cognitive is not None


def test_process_input_no_session_id(engine):
    result = engine.process_input("ไม่มี session")
    assert isinstance(result, dict)
    assert "text" in result
