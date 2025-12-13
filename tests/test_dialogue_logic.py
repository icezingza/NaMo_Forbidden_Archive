import os
import sys

import pytest

# Add the root directory to the Python path to allow for direct imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from core.dark_system import DarkNaMoSystem


@pytest.fixture
def mock_adapters(monkeypatch):
    """Mocks the Memory and Emotion adapters."""
    monkeypatch.setattr("adapters.memory.MemoryAdapter.store_interaction", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        "adapters.emotion.EmotionAdapter.analyze_emotion",
        lambda *args, **kwargs: {"primary_emotion": "neutral", "intensity": 0.5},
    )


def test_sadness_input_triggers_comfort_response(monkeypatch, mock_adapters):
    """Tests that a sad input triggers a comfort-seeking response."""
    # Arrange
    monkeypatch.setattr(
        "adapters.emotion.EmotionAdapter.analyze_emotion",
        lambda *args, **kwargs: {"primary_emotion": "sadness", "intensity": 0.9},
    )
    engine = DarkNaMoSystem()
    user_input = "ฉันรู้สึกเศร้าจัง..."
    session_id = "test-session-sadness"

    # Act
    result = engine.process_input(user_input, session_id)

    # Assert
    assert "ข้ารู้สึกถึงความเศร้าของท่าน..." in result


def test_high_intensity_anger_input_triggers_dominance_response(monkeypatch, mock_adapters):
    """Tests that a high-intensity angry input triggers a dominance response."""
    # Arrange
    monkeypatch.setattr(
        "adapters.emotion.EmotionAdapter.analyze_emotion",
        lambda *args, **kwargs: {"primary_emotion": "anger", "intensity": 0.9},
    )
    engine = DarkNaMoSystem()
    engine.intensity = 8  # Manually set intensity for testing
    user_input = "ฉันโกรธมาก!"
    session_id = "test-session-anger"

    # Act
    result = engine.process_input(user_input, session_id)

    # Assert
    assert "อารมณ์รุนแรงจังนะคะ..." in result


def test_safe_word_trigger(monkeypatch, mock_adapters):
    """Tests that the safe word trigger returns the aftercare response."""
    # Arrange
    engine = DarkNaMoSystem()
    user_input = "พอแล้ว! อภัย นะ"
    session_id = "test-session-safe-word"

    # Act
    result = engine.process_input(user_input, session_id)

    # Assert
    assert result == "ข้าได้ยินท่านแล้ว ทุกอย่างจะหยุดลงเดี๋ยวนี้ ท่านปลอดภัยแล้ว ข้าอยู่นี่"


def test_neutral_input_triggers_provoke_reaction_response(monkeypatch, mock_adapters):
    """Tests that a neutral input triggers a provoke reaction response."""
    # Arrange
    monkeypatch.setattr(
        "adapters.emotion.EmotionAdapter.analyze_emotion",
        lambda *args, **kwargs: {"primary_emotion": "neutral", "intensity": 0.1},
    )
    engine = DarkNaMoSystem()
    user_input = "..."
    session_id = "test-session-neutral"

    # Act
    result = engine.process_input(user_input, session_id)

    # Assert
    assert "ท่านเงียบจัง..." in result
