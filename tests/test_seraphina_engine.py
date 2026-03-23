"""Tests for seraphina_ai_complete.py — SeraphinaAI process_input (no TF required)."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_engine():
    from seraphina_ai_complete import SeraphinaAI

    return SeraphinaAI()


# ===========================================================================
# process_input contract
# ===========================================================================

class TestSeraphinaProcessInput:
    def setup_method(self):
        self.engine = _make_engine()

    def test_returns_required_keys(self):
        result = self.engine.process_input("Hello", session_id="s1")
        assert "text" in result
        assert "media_trigger" in result
        assert "system_status" in result

    def test_text_is_non_empty_string(self):
        result = self.engine.process_input("test", session_id="s1")
        assert isinstance(result["text"], str)
        assert len(result["text"]) > 0

    def test_media_trigger_keys(self):
        result = self.engine.process_input("test", session_id="s1")
        media = result["media_trigger"]
        assert "image" in media
        assert "audio" in media
        assert "tts" in media

    def test_system_status_has_detected_emotion(self):
        result = self.engine.process_input("hello", session_id="s1")
        assert "detected_emotion" in result["system_status"]

    def test_system_status_has_strategy(self):
        result = self.engine.process_input("hello", session_id="s1")
        assert "strategy" in result["system_status"]

    def test_multiple_calls_succeed(self):
        for i in range(3):
            result = self.engine.process_input(f"message {i}", session_id="multi")
            assert "text" in result

    def test_none_session_id_is_handled(self):
        result = self.engine.process_input("hi", session_id=None)
        assert result["text"]


# ===========================================================================
# get_status
# ===========================================================================

class TestSeraphinaGetStatus:
    def setup_method(self):
        self.engine = _make_engine()

    def test_get_status_returns_engine_name(self):
        status = self.engine.get_status()
        assert status["engine"] == "SeraphinaAI"

    def test_get_status_online(self):
        status = self.engine.get_status()
        assert status["status"] == "online"

    def test_get_status_has_persona(self):
        status = self.engine.get_status()
        assert "persona" in status
        assert "Seraphina" in status["persona"]

    def test_get_status_has_emotion_from_cognitive(self):
        status = self.engine.get_status()
        assert "emotion" in status


# ===========================================================================
# _build_system_prompt
# ===========================================================================

class TestSeraphinaBuildSystemPrompt:
    def test_prompt_contains_name(self):
        engine = _make_engine()
        prompt = engine._build_system_prompt("flirting")
        assert "Seraphina" in prompt

    def test_prompt_contains_context(self):
        engine = _make_engine()
        prompt = engine._build_system_prompt("conflict")
        assert "conflict" in prompt
