import pytest
import sys
import os

# Add Core_Scripts to the Python path to allow for direct imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from dark_system import DarkNaMoSystem

def test_dialogue_produces_placeholder_response():
    """Tests that the dialogue engine produces a placeholder response."""
    # Arrange
    engine = DarkNaMoSystem()
    user_input = "สวัสดีตอนเช้า"
    session_id = "test-session-fixed"

    # Act
    result = engine.process_input(user_input, session_id)

    # Assert
    expected_response = "อื้อออ... (Placeholder response based on desire: dialogue)"
    assert result == expected_response, f"The engine response was not the expected default message."

def test_safe_word_trigger():
    """Tests that the safe word trigger returns the aftercare response."""
    # Arrange
    engine = DarkNaMoSystem()
    user_input = "I need to stop, อภัย."
    session_id = "test-session-safe-word"

    # Act
    result = engine.process_input(user_input, session_id)

    # Assert
    assert result == "ข้าได้ยินท่านแล้ว ทุกอย่างจะหยุดลงเดี๋ยวนี้ ท่านปลอดภัยแล้ว ข้าอยู่นี่"

def test_command_produces_placeholder_response():
    """Tests that a command produces a placeholder response."""
    # Arrange
    engine = DarkNaMoSystem()
    user_input = "!omega"
    session_id = "test-session-command"

    # Act
    result = engine.process_input(user_input, session_id)

    # Assert
    assert result == "อื้อออ... (Placeholder response based on desire: command)"
