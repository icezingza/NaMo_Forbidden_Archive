"""Tests for rinlada_fusion.py — RinladaAI process_input (no TF required)."""

import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_engine(tmp_path):
    """Return a RinladaAI instance that writes soul state to tmp_path."""
    import rinlada_fusion as rf

    # Redirect STATE_PATH so tests don't pollute the repo root
    with patch.object(rf, "STATE_PATH", tmp_path / "Rinlada_Memory.json"):
        from rinlada_fusion import RinladaAI

        engine = RinladaAI()
    return engine


# ===========================================================================
# process_input contract
# ===========================================================================


class TestRinladaProcessInput:
    def test_returns_required_keys(self, tmp_path):
        engine = _make_engine(tmp_path)
        result = engine.process_input("สวัสดี", session_id="s1")
        assert "text" in result
        assert "media_trigger" in result
        assert "system_status" in result

    def test_text_is_non_empty_string(self, tmp_path):
        engine = _make_engine(tmp_path)
        result = engine.process_input("hello", session_id="s1")
        assert isinstance(result["text"], str)
        assert len(result["text"]) > 0

    def test_media_trigger_keys(self, tmp_path):
        engine = _make_engine(tmp_path)
        result = engine.process_input("test", session_id="s1")
        media = result["media_trigger"]
        assert "image" in media
        assert "audio" in media
        assert "tts" in media

    def test_system_status_has_arousal(self, tmp_path):
        engine = _make_engine(tmp_path)
        result = engine.process_input("test", session_id="s1")
        assert "arousal" in result["system_status"]

    def test_system_status_has_intent(self, tmp_path):
        engine = _make_engine(tmp_path)
        result = engine.process_input("test", session_id="s1")
        assert "intent" in result["system_status"]


# ===========================================================================
# Per-session arousal isolation
# ===========================================================================


class TestRinladaSessionIsolation:
    def test_two_sessions_independent(self, tmp_path):
        engine = _make_engine(tmp_path)
        # Call once each with different session IDs
        engine.process_input("hello", session_id="A")
        engine.process_input("hello", session_id="B")
        # Each session was seeded from the same initial soul arousal, so they
        # should be equal (not cross-contaminated)
        arousal_a = engine._get_session_arousal("A")
        arousal_b = engine._get_session_arousal("B")
        # After 1 call each they should have the same value (same gain)
        assert arousal_a == arousal_b

    def test_arousal_accumulates_within_session(self, tmp_path):
        engine = _make_engine(tmp_path)
        engine.process_input("hello", session_id="X")
        after_1 = engine._get_session_arousal("X")
        engine.process_input("hello", session_id="X")
        after_2 = engine._get_session_arousal("X")
        assert after_2 > after_1

    def test_default_session_key(self, tmp_path):
        engine = _make_engine(tmp_path)
        engine.process_input("hi", session_id=None)
        assert "default" in engine._session_arousal


# ===========================================================================
# get_status
# ===========================================================================


class TestRinladaGetStatus:
    def test_get_status_returns_engine_name(self, tmp_path):
        engine = _make_engine(tmp_path)
        status = engine.get_status()
        assert status["engine"] == "RinladaAI"

    def test_get_status_online(self, tmp_path):
        engine = _make_engine(tmp_path)
        status = engine.get_status()
        assert status["status"] == "online"

    def test_get_status_has_persona_name(self, tmp_path):
        engine = _make_engine(tmp_path)
        status = engine.get_status()
        assert "persona" in status
        assert len(status["persona"]) > 0


# ===========================================================================
# interact() — covers lines 214-239
# ===========================================================================


class TestRinladaInteract:
    def test_interact_command_intent(self, tmp_path, capsys):
        engine = _make_engine(tmp_path)
        engine.interact("สั่งมาเลย")  # triggers Command intent → Submit strategy
        captured = capsys.readouterr()
        assert "น้าริน" in captured.out or "ไอซ์" in captured.out

    def test_interact_lust_intent(self, tmp_path, capsys):
        engine = _make_engine(tmp_path)
        engine.interact("เย็ดกัน")  # triggers Lust intent → Tease strategy
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_interact_affection_intent(self, tmp_path, capsys):
        engine = _make_engine(tmp_path)
        engine.interact("รักน้ามาก")  # triggers Affection intent → Seduce strategy
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_interact_general_input(self, tmp_path, capsys):
        engine = _make_engine(tmp_path)
        engine.interact("ดีเลยนะ")  # general → Wait strategy
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_interact_evolution_message(self, tmp_path, capsys):
        engine = _make_engine(tmp_path)
        # Force consciousness near threshold so it evolves
        engine.soul.data["consciousness_level"] = 990
        engine.interact("สั่งมาเลย")  # gains 20 XP → 1010 → evolves
        captured = capsys.readouterr()
        assert "EVOLVED" in captured.out or engine.soul.data["cycle_count"] >= 1


# ===========================================================================
# _generate_response — all strategy branches
# ===========================================================================


class TestRinladaGenerateResponse:
    def test_submit_strategy(self, tmp_path):
        engine = _make_engine(tmp_path)
        analysis = {"intent": "Command", "dominance_score": 0.9}
        result = engine._generate_response("Submit", "test", analysis)
        assert isinstance(result, str) and len(result) > 0

    def test_tease_strategy(self, tmp_path):
        engine = _make_engine(tmp_path)
        analysis = {"intent": "Lust", "dominance_score": 0.7}
        result = engine._generate_response("Tease", "test", analysis)
        assert isinstance(result, str) and len(result) > 0

    def test_seduce_strategy(self, tmp_path):
        engine = _make_engine(tmp_path)
        analysis = {"intent": "Affection", "dominance_score": 0.3}
        result = engine._generate_response("Seduce", "test", analysis)
        assert isinstance(result, str) and len(result) > 0

    def test_wait_strategy(self, tmp_path):
        engine = _make_engine(tmp_path)
        analysis = {"intent": "General", "dominance_score": 0.5}
        result = engine._generate_response("Wait", "test", analysis)
        assert isinstance(result, str) and len(result) > 0


# ===========================================================================
# SoulMemory — update_experience evolution path
# ===========================================================================


class TestSoulMemoryEvolution:
    def test_evolution_resets_consciousness(self, tmp_path):
        import rinlada_fusion as rf

        with patch.object(rf, "STATE_PATH", tmp_path / "soul.json"):
            from rinlada_fusion import SoulMemory

            soul = SoulMemory()

        soul.data["consciousness_level"] = 990
        evolved = soul.update_experience(20)
        assert evolved is True
        assert soul.data["consciousness_level"] == 0  # resets to 0 on evolution

    def test_evolution_increments_cycle(self, tmp_path):
        import rinlada_fusion as rf

        with patch.object(rf, "STATE_PATH", tmp_path / "soul2.json"):
            from rinlada_fusion import SoulMemory

            soul = SoulMemory()

        soul.data["consciousness_level"] = 999
        soul.update_experience(10)
        assert soul.data["cycle_count"] == 1

    def test_no_evolution_below_threshold(self, tmp_path):
        import rinlada_fusion as rf

        with patch.object(rf, "STATE_PATH", tmp_path / "soul3.json"):
            from rinlada_fusion import SoulMemory

            soul = SoulMemory()

        soul.data["consciousness_level"] = 500
        evolved = soul.update_experience(10)
        assert evolved is False
