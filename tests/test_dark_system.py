"""Tests for core/dark_system.py — DarkNaMoSystem coverage."""

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_engine():
    """Return DarkNaMoSystem with EmotionAdapter and MemoryAdapter mocked."""
    mock_emotion = MagicMock()
    mock_emotion.analyze_emotion.return_value = {"primary_emotion": "neutral", "intensity": 0.3}
    mock_memory = MagicMock()

    with (
        patch("core.dark_system.EmotionAdapter", return_value=mock_emotion),
        patch("core.dark_system.MemoryAdapter", return_value=mock_memory),
    ):
        from core.dark_system import DarkNaMoSystem

        engine = DarkNaMoSystem()
    engine.emotion_adapter = mock_emotion
    engine.memory_adapter = mock_memory
    return engine


# ===========================================================================
# process_input — standard paths
# ===========================================================================

class TestDarkNaMoProcessInput:
    def setup_method(self):
        self.engine = _make_engine()

    def test_returns_required_keys(self):
        result = self.engine.process_input("สวัสดี", session_id="s1")
        assert "text" in result
        assert "media_trigger" in result
        assert "system_status" in result

    def test_media_trigger_keys(self):
        result = self.engine.process_input("hello", session_id="s1")
        assert set(result["media_trigger"].keys()) == {"image", "audio", "tts"}

    def test_system_status_has_intensity(self):
        result = self.engine.process_input("hello", session_id="s1")
        assert "intensity" in result["system_status"]

    def test_high_intensity_emotion_increments_session(self):
        self.engine.emotion_adapter.analyze_emotion.return_value = {
            "primary_emotion": "lust",
            "intensity": 0.9,
        }
        before = self.engine._get_intensity("intense-session")
        self.engine.process_input("เร้าใจมาก", session_id="intense-session")
        after = self.engine._get_intensity("intense-session")
        assert after > before

    def test_none_session_uses_default(self):
        result = self.engine.process_input("hi", session_id=None)
        assert result["text"]

    def test_memory_logged_on_normal_input(self):
        self.engine.process_input("normal", session_id="mem-test")
        self.engine.memory_adapter.store_interaction.assert_called()


# ===========================================================================
# safe word
# ===========================================================================

class TestDarkNaMoSafeWord:
    def setup_method(self):
        self.engine = _make_engine()

    def test_safe_word_resets_intensity(self):
        self.engine._set_intensity("sw-session", 8)
        self.engine.process_input("อภัย", session_id="sw-session")
        assert self.engine._get_intensity("sw-session") == 1

    def test_safe_word_returns_aftercare_text(self):
        result = self.engine.process_input("อภัยนะ", session_id="sw-session")
        assert len(result["text"]) > 0

    def test_safe_word_logs_to_memory(self):
        self.engine.process_input("อภัย", session_id="sw-log")
        self.engine.memory_adapter.store_interaction.assert_called()


# ===========================================================================
# get_status
# ===========================================================================

class TestDarkNaMoGetStatus:
    def setup_method(self):
        self.engine = _make_engine()

    def test_get_status_engine_name(self):
        assert self.engine.get_status()["engine"] == "DarkNaMoSystem"

    def test_get_status_online(self):
        assert self.engine.get_status()["status"] == "online"

    def test_get_status_no_sessions(self):
        status = self.engine.get_status()
        assert status["active_sessions"] == 0
        assert status["avg_intensity"] == self.engine._default_intensity

    def test_get_status_with_sessions(self):
        self.engine._set_intensity("a", 7)
        self.engine._set_intensity("b", 3)
        status = self.engine.get_status()
        assert status["active_sessions"] == 2
        assert status["avg_intensity"] == 5  # (7+3)//2


# ===========================================================================
# _build_system_prompt (previously had bug: self.intensity)
# ===========================================================================

class TestDarkNaMoBuildSystemPrompt:
    def test_prompt_contains_context(self):
        engine = _make_engine()
        prompt = engine._build_system_prompt("testing")
        assert "testing" in prompt

    def test_prompt_contains_protocol_version(self):
        engine = _make_engine()
        prompt = engine._build_system_prompt("ctx")
        assert "3.0" in prompt or "Metaphysical" in prompt

    def test_prompt_does_not_raise(self):
        # Previously raised AttributeError due to self.intensity
        engine = _make_engine()
        result = engine._build_system_prompt("any context")
        assert isinstance(result, str)
