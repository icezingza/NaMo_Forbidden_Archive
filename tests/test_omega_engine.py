"""Tests for core/namo_omega_engine.py — no LLM / no network required."""

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Ensure LLM is disabled for all tests in this module
os.environ.setdefault("NAMO_LLM_ENABLED", "0")


# ---------------------------------------------------------------------------
# Helpers: import with LLM + RAG disabled
# ---------------------------------------------------------------------------

def _make_engine():
    """Return a NaMoOmegaEngine with LLM and RAG mocked out."""
    with (
        patch("core.namo_omega_engine.TTSAdapter") as mock_tts_cls,
        patch("core.namo_omega_engine.NaMoOmegaEngine._resolve_llm_enabled", return_value=False),
    ):
        mock_tts_cls.return_value = MagicMock(_client=None, synthesize=MagicMock(return_value=None))
        from core.namo_omega_engine import NaMoOmegaEngine

        engine = NaMoOmegaEngine()
    return engine


# ===========================================================================
# SinSystem
# ===========================================================================

class TestSinSystem:
    def setup_method(self):
        from core.namo_omega_engine import SinSystem

        self.sin = SinSystem()

    def test_initial_state(self):
        assert self.sin.sin_points == 0
        assert self.sin.rank == "Innocent Soul"
        assert self.sin.unlocked_fetishes == []

    def test_commit_sin_accumulates(self):
        self.sin.commit_sin(3)
        assert self.sin.sin_points == 300

    def test_commit_sin_updates_rank_corrupted(self):
        self.sin.commit_sin(11)  # 1100 points → Corrupted Master
        assert self.sin.rank == "Corrupted Master"
        assert "Sensory Overload" in self.sin.unlocked_fetishes

    def test_commit_sin_updates_rank_dark_lord(self):
        self.sin.commit_sin(51)  # 5100 points → Dark Lord
        assert self.sin.rank == "Dark Lord"
        assert "Mindbreak" in self.sin.unlocked_fetishes

    def test_get_status_contains_rank(self):
        status = self.sin.get_status()
        assert "Innocent Soul" in status

    def test_get_status_contains_points(self):
        self.sin.commit_sin(5)
        status = self.sin.get_status()
        assert "500" in status


# ===========================================================================
# SensoryOverloadManager
# ===========================================================================

class TestSensoryOverloadManager:
    def setup_method(self):
        from core.namo_omega_engine import SensoryOverloadManager

        self.mgr = SensoryOverloadManager()

    def test_low_arousal_no_trigger(self):
        result = self.mgr.trigger_sensation(10, "hello")
        assert result["image"] is None
        assert result["audio"] is None

    def test_medium_arousal_triggers_omega(self):
        result = self.mgr.trigger_sensation(60, "test")
        assert result["image"] is not None
        assert "omega" in result["image"].lower() or "NaMo" in result["image"]
        assert result["audio"] is not None

    def test_high_arousal_triggers_mindbreak(self):
        result = self.mgr.trigger_sensation(100, "normal")
        assert result["image"] is not None
        assert "mindbreak" in result["image"].lower() or "Mindbreak" in result["image"]

    def test_mindbreak_context_triggers_even_at_low_arousal(self):
        result = self.mgr.trigger_sensation(5, "mindbreak scenario")
        assert result["image"] is not None

    def test_whisper_context_sets_audio(self):
        result = self.mgr.trigger_sensation(10, "กระซิบบอกฉันหน่อย")
        assert result["audio"] is not None


# ===========================================================================
# PersonaOrchestrator
# ===========================================================================

class TestPersonaOrchestrator:
    def setup_method(self):
        from core.namo_omega_engine import PersonaOrchestrator

        self.orc = PersonaOrchestrator()

    def test_initial_active_personas(self):
        assert self.orc.active_personas == ["NaMo"]

    def test_summon_new_persona(self):
        msg = self.orc.summon_persona("Sister")
        assert "Sister" in self.orc.active_personas
        assert "Sister" in msg

    def test_summon_duplicate_is_noop(self):
        self.orc.summon_persona("Sister")
        msg = self.orc.summon_persona("Sister")
        assert msg == ""
        assert self.orc.active_personas.count("Sister") == 1

    def test_summon_unknown_persona(self):
        msg = self.orc.summon_persona("Ghost")
        assert msg == ""

    def test_generate_dialogue_includes_namo(self):
        result = self.orc.generate_dialogue("test", "Innocent Soul")
        assert "NaMo" in result

    def test_generate_dialogue_with_sister(self):
        self.orc.summon_persona("Sister")
        result = self.orc.generate_dialogue("test", "Innocent Soul")
        assert "Sister" in result


# ===========================================================================
# NaMoOmegaEngine — process_input (no LLM)
# ===========================================================================

class TestNaMoOmegaEngineProcessInput:
    def setup_method(self):
        self.engine = _make_engine()

    def test_returns_required_keys(self):
        result = self.engine.process_input("สวัสดี", session_id="s1")
        assert "text" in result
        assert "media_trigger" in result
        assert "system_status" in result

    def test_system_status_keys(self):
        result = self.engine.process_input("hello", session_id="s1")
        status = result["system_status"]
        assert "arousal" in status
        assert "sin_status" in status
        assert "active_personas" in status

    def test_sin_trigger_raises_arousal(self):
        result = self.engine.process_input("เย็ด", session_id="sin-test")
        status = result["system_status"]
        # arousal is returned as e.g. "10%"
        arousal_val = int(status["arousal"].rstrip("%"))
        assert arousal_val > 0

    def test_sister_summon_keyword(self):
        self.engine.process_input("เรียกน้องมาเล่นด้วย", session_id="persona-test")
        state = self.engine._get_session_state("persona-test")
        # "เรียกน้อง" triggers persona summon
        assert "Sister" in state["personas"].active_personas

    def test_per_session_isolation(self):
        self.engine.process_input("เย็ด", session_id="session-A")
        self.engine.process_input("สวัสดี", session_id="session-B")
        state_a = self.engine._get_session_state("session-A")
        state_b = self.engine._get_session_state("session-B")
        assert state_a["arousal"] > state_b["arousal"]

    def test_media_trigger_keys(self):
        result = self.engine.process_input("hi", session_id="media-test")
        media = result["media_trigger"]
        assert "image" in media
        assert "audio" in media

    def test_default_session_used_when_none(self):
        self.engine.process_input("เย็ด", session_id=None)
        self.engine.process_input("เย็ด", session_id=None)
        # Both should accumulate in same "default" session
        state = self.engine._get_session_state(None)
        assert state["arousal"] >= 20  # 10 + 10


# ===========================================================================
# NaMoOmegaEngine — history management
# ===========================================================================

class TestNaMoOmegaEngineHistory:
    def setup_method(self):
        self.engine = _make_engine()
        self.engine.llm_memory_turns = 2  # keep last 4 messages (2*2)

    def test_history_appended_after_process_input(self):
        self.engine.process_input("hello", session_id="h1")
        history = self.engine._get_history("h1")
        assert len(history) == 2  # user + assistant

    def test_history_trimmed_when_exceeds_max(self):
        for i in range(5):
            self.engine._append_history("trim-test", "user", f"msg{i}")
            self.engine._append_history("trim-test", "assistant", f"resp{i}")
        history = self.engine._get_history("trim-test")
        assert len(history) == 4  # max_items = max(2, 2*2) = 4


# ===========================================================================
# NaMoOmegaEngine — stream_input fallback (no LLM)
# ===========================================================================

class TestNaMoOmegaEngineStream:
    def setup_method(self):
        self.engine = _make_engine()

    def test_stream_yields_text_when_no_llm(self):
        chunks = list(self.engine.stream_input("สวัสดี", session_id="stream-test"))
        assert len(chunks) >= 1
        assert all(isinstance(c, str) for c in chunks)

    def test_stream_content_non_empty(self):
        chunks = list(self.engine.stream_input("test", session_id="stream-test2"))
        combined = "".join(chunks)
        assert len(combined) > 0


# ===========================================================================
# NaMoOmegaEngine — get_status
# ===========================================================================

class TestNaMoOmegaEngineStatus:
    def setup_method(self):
        self.engine = _make_engine()

    def test_get_status_returns_engine_name(self):
        status = self.engine.get_status()
        assert status["engine"] == "NaMoOmegaEngine"

    def test_get_status_online(self):
        status = self.engine.get_status()
        assert status["status"] == "online"

    def test_get_status_session_count(self):
        self.engine.process_input("hi", session_id="s1")
        self.engine.process_input("hi", session_id="s2")
        status = self.engine.get_status()
        assert status["active_sessions"] >= 2

    def test_get_status_llm_disabled(self):
        status = self.engine.get_status()
        assert status["llm_enabled"] is False

    def test_get_status_has_emotion_from_cognitive(self):
        status = self.engine.get_status()
        assert "emotion" in status
