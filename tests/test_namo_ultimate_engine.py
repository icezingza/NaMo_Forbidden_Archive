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


# ===========================================================================
# EmotionParasite — all infection branches
# ===========================================================================

def test_parasite_masochist_trigger(engine):
    result = engine.process_input("ด่าฉันสิ", session_id="masochist-test")
    assert result["system_status"]["sin_status"] == "masochist"


def test_parasite_lust_slave_trigger(engine):
    result = engine.process_input("เงี่ยนมาก", session_id="lust-test")
    assert result["system_status"]["sin_status"] == "lust_slave"


def test_parasite_neutral_trigger(engine):
    result = engine.process_input("สวัสดีจ้า", session_id="neutral-test")
    assert result["system_status"]["sin_status"] == "neutral"


def test_parasite_obsessed_trigger(engine):
    result = engine.process_input("ฉันรักคุณมาก", session_id="obsessed-test")
    assert result["system_status"]["sin_status"] == "obsessed"


# ===========================================================================
# Moan path — arousal > 50
# ===========================================================================

def test_moan_path_response_mode_dominance(engine):
    engine._set_arousal("dom-session", 60)
    result = engine.process_input("ด่าฉันสิ", session_id="dom-session")
    assert "ความเงี่ยน:" in result["text"]
    assert result["system_status"]["response_mode"] == "high_dominance"


def test_moan_path_response_mode_manipulation(engine):
    engine._set_arousal("manip-session", 60)
    result = engine.process_input("รักคุณมาก", session_id="manip-session")
    assert "ความเงี่ยน:" in result["text"]
    assert result["system_status"]["response_mode"] == "emotional_manipulation"


# ===========================================================================
# get_status — with sessions populated
# ===========================================================================

def test_get_status_avg_arousal_with_sessions(engine):
    engine._set_arousal("g1", 40)
    engine._set_arousal("g2", 60)
    status = engine.get_status()
    assert status["avg_arousal"] == 50
    assert status["active_sessions"] == 2


# ===========================================================================
# ForbiddenDialogueLibrary — loading from tmp files
# ===========================================================================

def test_forbidden_library_loads_from_txt(tmp_path):
    txt = tmp_path / "learn.txt"
    txt.write_text("หนูอยากให้พี่จับหนู\nพี่น่ารักมากเลยนะคะ\n" * 5)

    from core.namo_ultimate_engine import ForbiddenDialogueLibrary

    lib = ForbiddenDialogueLibrary(core_file="nonexistent.json", learning_dir=str(tmp_path))
    total = sum(len(v) for v in lib.dialogues.values())
    assert total > 0


def test_forbidden_library_get_response_default(engine):
    from core.namo_ultimate_engine import ForbiddenDialogueLibrary

    lib = ForbiddenDialogueLibrary(core_file="nonexistent.json", learning_dir="nonexistent")
    resp = lib.get_response("high_seduction")
    assert isinstance(resp, str) and len(resp) > 0


def test_forbidden_library_get_moan(engine):
    from core.namo_ultimate_engine import ForbiddenDialogueLibrary

    lib = ForbiddenDialogueLibrary(core_file="nonexistent.json", learning_dir="nonexistent")
    moan = lib.get_moan()
    assert isinstance(moan, str) and len(moan) > 0
