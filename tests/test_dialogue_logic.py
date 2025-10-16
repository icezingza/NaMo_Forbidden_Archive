import pytest
import sys
import os
from unittest.mock import MagicMock
import requests

# Add Core_Scripts to the Python path to allow for direct imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'Core_Scripts'))

from dark_dialogue_engine import DarkDialogueEngine

def test_dialogue_is_fixed_and_does_not_parrot_user_input(mocker):
    """
    Tests that the dialogue engine with the fix applied does not return the user's input.
    It now simulates the corrected behavior where recall happens first and finds nothing.
    """
    # Arrange
    mock_post = mocker.patch('requests.post')

    user_input = "สวัสดีตอนเช้า"
    session_id = "test-session-fixed"

    # After the fix, the first call to /recall should find no memories,
    # as the new input hasn't been stored yet. So, it returns an empty list.
    mock_recall_response = MagicMock()
    mock_recall_response.status_code = 200
    mock_recall_response.json.return_value = [] # Simulate finding no memories

    # The second call to /store can be a simple success response
    mock_store_response = MagicMock()
    mock_store_response.status_code = 200

    # We set the side_effect to return different values for each call
    mock_post.side_effect = [mock_recall_response, mock_store_response]

    # Act
    engine = DarkDialogueEngine()
    result = engine.process_input(user_input, session_id)

    # Assert
    # The response should now be the default message for when no memory is found.
    expected_response = "(หนูยังไม่เคยเรียนรู้เรื่องนี้... สอนหนูหน่อยสิคะ)"
    assert result.get('response') == expected_response, f"The engine response was not the expected default message."

    # We still expect two calls to the memory service
    assert mock_post.call_count == 2

    # Verify the first call was to /recall
    recall_call_args, _ = mock_post.call_args_list[0]
    assert recall_call_args[0].endswith('/recall')

    # Verify the second call was to /store
    store_call_args, store_call_kwargs = mock_post.call_args_list[1]
    assert store_call_args[0].endswith('/store')
    assert store_call_kwargs['json']['content'] == user_input

def test_safe_word_trigger(mocker):
    """Tests that the safe word trigger returns the aftercare response."""
    # Arrange
    engine = DarkDialogueEngine()
    user_input = "I need to stop, อภัย."
    session_id = "test-session-safe-word"

    # Act
    result = engine.process_input(user_input, session_id)

    # Assert
    assert result.get('response') == "(ระบบ Aftercare ทำงาน...)"
    assert result.get('arousal_level') == 0

def test_successful_memory_recall(mocker):
    """Tests that a successful memory recall returns the recalled memory."""
    # Arrange
    mock_post = mocker.patch('requests.post')
    user_input = "Tell me a secret."
    session_id = "test-session-recall"

    mock_recall_response = MagicMock()
    mock_recall_response.status_code = 200
    mock_recall_response.json.return_value = [{'content': 'This is a recalled secret.'}]

    mock_store_response = MagicMock()
    mock_store_response.status_code = 200

    mock_post.side_effect = [mock_recall_response, mock_store_response]

    # Act
    engine = DarkDialogueEngine()
    result = engine.process_input(user_input, session_id)

    # Assert
    assert result.get('response') == 'This is a recalled secret.'
    assert mock_post.call_count == 2

def test_memory_recall_request_exception(mocker):
    """Tests that a RequestException during recall is handled gracefully."""
    # Arrange
    mock_post = mocker.patch('requests.post')
    mock_post.side_effect = requests.exceptions.RequestException("Connection error")

    user_input = "What happens if the memory is down?"
    session_id = "test-session-recall-error"

    # Act
    engine = DarkDialogueEngine()
    result = engine.process_input(user_input, session_id)

    # Assert
    assert result.get('response') == "(เกิดข้อผิดพลาดในการเชื่อมต่อกับแกนความทรงจำของหนู...)"
    # The recall fails, but the store is still attempted.
    assert mock_post.call_count == 2

def test_memory_store_request_exception(mocker):
    """Tests that a RequestException during store does not crash the engine."""
    # Arrange
    mock_post = mocker.patch('requests.post')
    user_input = "Storing this should fail."
    session_id = "test-session-store-error"

    mock_recall_response = MagicMock()
    mock_recall_response.status_code = 200
    mock_recall_response.json.return_value = []

    # The second call (store) will raise an exception
    mock_post.side_effect = [mock_recall_response, requests.exceptions.RequestException("Connection error")]

    # Act
    engine = DarkDialogueEngine()
    result = engine.process_input(user_input, session_id)

    # Assert
    # The response should be the default one since recall found nothing
    assert result.get('response') == "(หนูยังไม่เคยเรียนรู้เรื่องนี้... สอนหนูหน่อยสิคะ)"
    # Both recall and store should have been attempted
    assert mock_post.call_count == 2
