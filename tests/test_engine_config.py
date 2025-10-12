import sys
import os
import pytest

# Add Core_Scripts to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Core_Scripts'))

from dark_dialogue_engine import DarkDialogueEngine

def test_dark_dialogue_engine_custom_config():
    """
    Tests if the DarkDialogueEngine can be initialized with custom configuration.
    """
    custom_safe_word = "test_safe_word"
    custom_memory_url = "http://test-url:1234"

    engine = DarkDialogueEngine(safe_word=custom_safe_word, memory_service_url=custom_memory_url)

    assert engine.safe_word == custom_safe_word
    assert engine.memory_service_url == custom_memory_url
