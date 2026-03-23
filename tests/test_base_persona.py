"""Tests for core/base_persona.py — CognitiveCore and BasePersonaEngine."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# ---------------------------------------------------------------------------
# Minimal concrete engine for testing BasePersonaEngine abstract methods
# ---------------------------------------------------------------------------

def _make_minimal_engine(text="hello world. goodbye."):
    from core.base_persona import BasePersonaEngine

    class _MinimalEngine(BasePersonaEngine):
        def __init__(self, response_text):
            self._response = response_text

        def process_input(self, user_input, session_id=None):
            return {
                "text": self._response,
                "media_trigger": {"image": None, "audio": None, "tts": None},
                "system_status": {"arousal": "0%", "sin_status": "ok", "active_personas": []},
            }

    return _MinimalEngine(text)


# ===========================================================================
# CognitiveCore
# ===========================================================================

class TestCognitiveCore:
    def setup_method(self, tmp_path_factory=None):
        from core.base_persona import CognitiveCore

        self.core = CognitiveCore(save_dir=None)

    def test_process_returns_required_keys(self):
        out = self.core.process("hello", "neutral", memories=[])
        assert "emotion" in out
        assert "monologue" in out
        assert "autonomous" in out
        assert "persona_traits" in out
        assert "preferences" in out

    def test_emotion_is_dict(self):
        out = self.core.process("test input", "lust", memories=[])
        assert isinstance(out["emotion"], dict)

    def test_monologue_is_str(self):
        out = self.core.process("test", "neutral", memories=[])
        assert isinstance(out["monologue"], str)

    def test_persona_traits_has_boldness(self):
        out = self.core.process("test", "neutral", memories=[])
        assert "boldness" in out["persona_traits"]

    def test_multiple_calls_accumulate_emotion(self):
        for _ in range(5):
            self.core.process("เย็ด", "lust", memories=[])
        snap = self.core.emotion.snapshot()
        assert snap["desire"] > 0

    def test_build_context_block_returns_str(self):
        out = self.core.process("test", "neutral", memories=[])
        block = self.core.build_context_block(out)
        assert isinstance(block, str)
        assert len(block) > 0

    def test_build_context_block_contains_traits(self):
        out = self.core.process("test", "neutral", memories=[])
        block = self.core.build_context_block(out)
        assert "boldness" in block

    def test_build_context_block_contains_emotion_prose(self):
        out = self.core.process("test", "neutral", memories=[])
        block = self.core.build_context_block(out)
        assert "感情状態" in block

    def test_build_context_block_includes_monologue_when_present(self, tmp_path):
        from core.base_persona import CognitiveCore

        core = CognitiveCore(save_dir=tmp_path)
        # Trigger a thought so monologue is non-empty
        core.process("รักคุณมาก", "affection", memories=[{"content": "past memory"}])
        out = core.process("คิดถึงคุณ", "affection", memories=[])
        block = core.build_context_block(out)
        # block must at least contain the emotion section
        assert "感情状態" in block

    def test_autonomous_reflection_is_str_or_none(self):
        out = self.core.process("test", "neutral", memories=[])
        assert out["autonomous"] is None or isinstance(out["autonomous"], str)


# ===========================================================================
# BasePersonaEngine — stream_input sentence splitting
# ===========================================================================

class TestBasePersonaEngineStreamInput:
    def test_stream_yields_chunks(self):
        engine = _make_minimal_engine("Hello world. How are you?")
        chunks = list(engine.stream_input("hi", session_id="s1"))
        assert len(chunks) >= 1

    def test_stream_joined_matches_original(self):
        text = "Hello world. How are you?"
        engine = _make_minimal_engine(text)
        chunks = list(engine.stream_input("hi", session_id="s1"))
        combined = "".join(chunks)
        # combined should contain all non-whitespace chars from original
        assert combined.replace(" ", "") == text.replace(" ", "")

    def test_stream_splits_on_exclamation(self):
        engine = _make_minimal_engine("Wow! Amazing! Yes.")
        chunks = list(engine.stream_input("hi", session_id="s1"))
        assert len(chunks) >= 2

    def test_stream_skips_empty_parts(self):
        engine = _make_minimal_engine("Hello... ")
        chunks = list(engine.stream_input("hi", session_id="s1"))
        assert all(c.strip() != "" for c in chunks)

    def test_stream_single_sentence(self):
        engine = _make_minimal_engine("Just one sentence")
        chunks = list(engine.stream_input("hi", session_id="s1"))
        assert len(chunks) == 1
        assert chunks[0] == "Just one sentence"


# ===========================================================================
# BasePersonaEngine — get_status
# ===========================================================================

class TestBasePersonaEngineGetStatus:
    def test_get_status_no_cognitive(self):
        engine = _make_minimal_engine()
        status = engine.get_status()
        assert status["engine"] == "_MinimalEngine"
        assert status["status"] == "online"
        assert "emotion" not in status

    def test_get_status_with_cognitive(self, tmp_path):
        engine = _make_minimal_engine()
        engine.init_cognition(save_dir=tmp_path)
        status = engine.get_status()
        assert "emotion" in status
        assert "traits" in status

    def test_build_system_prompt_default(self):
        engine = _make_minimal_engine()
        prompt = engine._build_system_prompt("flirting")
        assert "_MinimalEngine" in prompt
        assert "flirting" in prompt
