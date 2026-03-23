"""Unit tests for the three cognitive-stack modules.

Covers:
- EmotionEngine  : update, momentum, decay, snapshot, to_prose, dominant
- CognitiveStream: perceive, reflect, to_monologue, clear, thought types
- LearningEngine : observe, adapt_traits, get_preferences, persistence
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.cognitive_stream import CognitiveStream, Thought
from core.emotion_engine import EmotionEngine, EmotionVector
from core.learning_engine import LearningEngine

# ─────────────────────────────────────────────────────────────
# EmotionEngine
# ─────────────────────────────────────────────────────────────


class TestEmotionVector:
    def test_clamp_keeps_values_in_range(self):
        vec = EmotionVector(joy=2.0, arousal=-1.0, desire=1.5)
        vec.clamp()
        assert 0.0 <= vec.joy <= 1.0
        assert 0.0 <= vec.arousal <= 1.0
        assert 0.0 <= vec.desire <= 1.0

    def test_dominant_returns_string_and_float(self):
        vec = EmotionVector(joy=0.5, arousal=0.3, trust=0.5, anger=0.9, desire=0.0)
        name, intensity = vec.dominant()
        assert name == "anger"
        assert isinstance(intensity, float)

    def test_to_prose_returns_non_empty_string(self):
        vec = EmotionVector(joy=0.9, arousal=0.8, desire=0.7)
        prose = vec.to_prose()
        assert isinstance(prose, str)
        assert len(prose) > 0

    def test_to_prose_neutral_state(self):
        vec = EmotionVector(joy=0.5, arousal=0.3, trust=0.5, anger=0.0, desire=0.0)
        prose = vec.to_prose()
        assert isinstance(prose, str)


class TestEmotionEngine:
    def test_initial_state_matches_baseline(self):
        engine = EmotionEngine()
        snap = engine.snapshot()
        assert "joy" in snap
        assert "prose" in snap
        assert "dominant" in snap

    def test_lust_trigger_raises_desire_and_arousal(self):
        engine = EmotionEngine()
        before_desire = engine.current.desire
        before_arousal = engine.current.arousal
        engine.update("lust", intensity=0.8)
        assert engine.current.desire > before_desire
        assert engine.current.arousal > before_arousal

    def test_affection_trigger_raises_joy_and_trust(self):
        engine = EmotionEngine()
        engine.update("affection", intensity=0.7)
        assert engine.current.joy > EmotionEngine.BASELINE.joy
        assert engine.current.trust >= EmotionEngine.BASELINE.trust

    def test_rejection_trigger_lowers_joy(self):
        engine = EmotionEngine()
        engine.update("rejection", intensity=0.9)
        assert engine.current.joy < EmotionEngine.BASELINE.joy

    def test_decay_moves_values_toward_baseline(self):
        engine = EmotionEngine()
        engine.current.anger = 0.9  # force high anger
        engine.decay()
        assert engine.current.anger < 0.9

    def test_momentum_prevents_instant_jump(self):
        """Two sequential triggers should produce a smaller change than a
        single large trigger because momentum builds gradually."""
        engine_single = EmotionEngine()
        engine_single.update("lust", intensity=1.0)
        high_desire = engine_single.current.desire

        engine_gradual = EmotionEngine()
        engine_gradual.update("lust", intensity=0.2)
        engine_gradual.update("lust", intensity=0.2)
        gradual_desire = engine_gradual.current.desire

        # gradual build-up is strictly less than a single full blast
        assert gradual_desire < high_desire

    def test_snapshot_keys_are_complete(self):
        engine = EmotionEngine()
        snap = engine.snapshot()
        for key in (
            "joy",
            "arousal",
            "trust",
            "anger",
            "desire",
            "dominant",
            "dominant_intensity",
            "prose",
        ):
            assert key in snap

    def test_values_stay_clamped_after_many_updates(self):
        engine = EmotionEngine()
        for _ in range(20):
            engine.update("lust", intensity=1.0)
        snap = engine.snapshot()
        for key in ("joy", "arousal", "trust", "anger", "desire"):
            assert 0.0 <= snap[key] <= 1.0


# ─────────────────────────────────────────────────────────────
# CognitiveStream
# ─────────────────────────────────────────────────────────────


class TestCognitiveStream:
    def _emotion(self, **kwargs) -> EmotionVector:
        return EmotionVector(
            **{"joy": 0.5, "arousal": 0.3, "trust": 0.5, "anger": 0.0, "desire": 0.0, **kwargs}
        )

    def test_perceive_returns_list_of_thoughts(self):
        stream = CognitiveStream()
        emotion = self._emotion()
        thoughts = stream.perceive("ฉันรักคุณ", emotion, memories=[])
        assert isinstance(thoughts, list)
        for t in thoughts:
            assert isinstance(t, Thought)
            assert isinstance(t.content, str)
            assert 0.0 <= t.intensity <= 1.0

    def test_affection_keyword_produces_impulse(self):
        stream = CognitiveStream()
        emotion = self._emotion(joy=0.8)
        thoughts = stream.perceive("ฉันรักและชอบคุณมาก", emotion, memories=[])
        types = [t.thought_type for t in thoughts]
        assert "impulse" in types

    def test_lust_keyword_produces_desire_thought(self):
        stream = CognitiveStream()
        emotion = self._emotion(desire=0.7, arousal=0.7)
        thoughts = stream.perceive("เย็ดกันเถอะ", emotion, memories=[])
        types = [t.thought_type for t in thoughts]
        assert any(tp in types for tp in ("impulse", "desire"))

    def test_conflict_surfaces_when_desire_high_trust_low(self):
        stream = CognitiveStream()
        emotion = self._emotion(desire=0.8, trust=0.2)
        thoughts = stream.perceive("บอกอะไรหน่อย", emotion, memories=[])
        types = [t.thought_type for t in thoughts]
        assert "conflict" in types

    def test_memory_produces_memory_thought(self):
        stream = CognitiveStream()
        emotion = self._emotion(trust=0.7)
        memories = [{"text": "ไอซ์บอกว่ารักน้าริน", "importance": 0.8}]
        thoughts = stream.perceive("อะไรนะ", emotion, memories=memories)
        types = [t.thought_type for t in thoughts]
        assert "memory" in types

    def test_reflect_returns_thought_or_none(self):
        stream = CognitiveStream()
        emotion = self._emotion(joy=0.1)
        result = stream.reflect(emotion)
        assert result is None or isinstance(result, Thought)

    def test_reflect_returns_thought_for_sad_emotion(self):
        stream = CognitiveStream()
        emotion = self._emotion(joy=0.1)
        result = stream.reflect(emotion)
        assert result is not None
        assert result.thought_type == "reflection"

    def test_to_monologue_returns_string(self):
        stream = CognitiveStream()
        emotion = self._emotion(joy=0.8)
        stream.perceive("ฉันรักคุณ", emotion, memories=[])
        monologue = stream.to_monologue()
        assert isinstance(monologue, str)

    def test_to_monologue_empty_when_no_thoughts(self):
        stream = CognitiveStream()
        assert stream.to_monologue() == ""

    def test_clear_empties_queue(self):
        stream = CognitiveStream()
        emotion = self._emotion(desire=0.8)
        stream.perceive("เย็ด", emotion, memories=[])
        stream.clear()
        assert stream.to_monologue() == ""

    def test_queue_respects_max_size(self):
        stream = CognitiveStream()
        emotion = self._emotion(desire=0.9)
        for _ in range(20):
            stream.perceive("รักรักรักรัก", emotion, memories=[])
        assert len(stream.thought_queue) <= stream.MAX_QUEUE


# ─────────────────────────────────────────────────────────────
# LearningEngine
# ─────────────────────────────────────────────────────────────


class TestLearningEngine:
    @pytest.fixture()
    def tmp_engine(self, tmp_path):
        return LearningEngine(save_path=tmp_path / "test_learned.json")

    def _snapshot(self, dominant="neutral", arousal=0.3):
        return {"dominant": dominant, "arousal": arousal, "prose": ""}

    def test_observe_increments_pattern_count(self, tmp_engine):
        tmp_engine.observe("ฉันรักคุณ", "affection", self._snapshot("joy"))
        tmp_engine.observe("ฉันรักคุณ", "affection", self._snapshot("joy"))
        key = "affection_joy"
        assert key in tmp_engine.patterns
        assert tmp_engine.patterns[key].count == 2

    def test_observe_updates_topic_affinity(self, tmp_engine):
        tmp_engine.observe("ฉันรักคุณ คิดถึง", "affection", self._snapshot())
        assert tmp_engine.topic_affinity.get("romance", 0) > 0

    def test_adapt_traits_returns_dict_with_required_keys(self, tmp_engine):
        for _ in range(5):
            tmp_engine.observe("สั่ง!", "Command", self._snapshot("anger", 0.8))
        traits = tmp_engine.adapt_traits()
        for key in ("boldness", "playfulness", "vulnerability", "expressiveness"):
            assert key in traits
            assert 0.0 <= traits[key] <= 1.0

    def test_adapt_traits_boldness_rises_with_commands(self, tmp_engine):
        for _ in range(10):
            tmp_engine.observe("ก้ม! ทำตาม!", "Command", self._snapshot("anger", 0.9))
        traits = tmp_engine.adapt_traits()
        assert traits["boldness"] > 0.5

    def test_get_preferences_returns_expected_keys(self, tmp_engine):
        tmp_engine.observe("สวัสดี", "neutral", self._snapshot())
        prefs = tmp_engine.get_preferences()
        for key in ("frequent_words", "preferred_topics", "trait_evolution", "total_interactions"):
            assert key in prefs

    def test_persist_and_reload(self, tmp_path):
        path = tmp_path / "learn.json"
        engine1 = LearningEngine(save_path=path)
        for _ in range(10):  # triggers a save (SAVE_INTERVAL=10)
            engine1.observe("รัก", "affection", self._snapshot("joy"))
        engine1.topic_affinity["romance"] = 0.77
        engine1._maybe_save()

        engine2 = LearningEngine(save_path=path)
        assert engine2.topic_affinity.get("romance", 0) > 0

    def test_pattern_pruning_keeps_size_bounded(self, tmp_engine):
        for i in range(tmp_engine.MAX_PATTERNS + 20):
            tmp_engine.observe(f"input {i}", f"intent_{i}", self._snapshot())
        # Force prune check
        tmp_engine._prune_patterns()
        assert len(tmp_engine.patterns) <= tmp_engine.MAX_PATTERNS

    def test_no_crash_on_missing_save_file(self, tmp_path):
        engine = LearningEngine(save_path=tmp_path / "nonexistent.json")
        assert engine._observation_count == 0
