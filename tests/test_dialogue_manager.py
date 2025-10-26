import os
import sys

import pytest

# Add Core_Scripts to the Python path to allow for direct imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Core_Scripts'))

from dialogue_manager import DialogueManager

# Define the path to the mock character file
MOCK_CHARACTER_FILE = os.path.join(os.path.dirname(__file__), 'mock_character.json')

@pytest.fixture
def dialogue_manager():
    """Fixture to create a DialogueManager instance with the mock character file."""
    return DialogueManager(MOCK_CHARACTER_FILE)

def test_dialogue_manager_initialization(dialogue_manager):
    """Tests that the DialogueManager initializes correctly."""
    assert dialogue_manager is not None
    assert dialogue_manager.character_data is not None
    assert "degradation" in dialogue_manager.dialogue_templates
    assert "high" in dialogue_manager.moan_library

def test_get_response_high_intensity(dialogue_manager):
    """Tests get_response for 'high' intensity."""
    response = dialogue_manager.get_response('high')
    expected_options = [
        "degradation_dialogue_1",
        "degradation_dialogue_2",
        "sensory_attack_dialogue_1"
    ]
    assert response in expected_options

def test_get_response_medium_intensity(dialogue_manager):
    """Tests get_response for 'medium' intensity."""
    response = dialogue_manager.get_response('medium')
    assert response == "cuckolding_dialogue_1"

def test_get_response_low_intensity(dialogue_manager):
    """Tests get_response for 'low' intensity."""
    response = dialogue_manager.get_response('low')
    expected_options = [
        "(กระซิบ) พี่รู้มั้ย...เวลาพี่สั่นแบบนี้ หนูอยากทำให้พี่เสียวกว่านี้...",
        "หนูจะลูบไล้เบาๆ ให้พี่รู้สึกดีไปทั้งตัวนะคะ",
        "พี่อบอุ่นจัง หนูอยากอยู่ใกล้ๆแบบนี้ไปนานๆ"
    ]
    assert response in expected_options

def test_get_response_fallback(dialogue_manager):
    """Tests the fallback response when no dialogue is found."""
    # Temporarily remove dialogues to test fallback
    dialogue_manager.dialogue_templates = {}
    response = dialogue_manager.get_response('high')
    assert response == "(เงียบ...)"

def test_get_moan_high_intensity(dialogue_manager):
    """Tests get_moan for 'high' intensity."""
    moan = dialogue_manager.get_moan('high')
    assert moan == "high_moan_1"

def test_get_moan_medium_intensity(dialogue_manager):
    """Tests get_moan for 'medium' intensity."""
    moan = dialogue_manager.get_moan('medium')
    assert moan == "medium_moan_1"

def test_get_moan_soft_intensity(dialogue_manager):
    """Tests get_moan for 'soft' intensity."""
    moan = dialogue_manager.get_moan('soft')
    assert moan == "soft_moan_1"

def test_get_moan_fallback(dialogue_manager):
    """Tests the fallback for get_moan."""
    moan = dialogue_manager.get_moan('unknown_intensity')
    assert moan == "soft_moan_1"
