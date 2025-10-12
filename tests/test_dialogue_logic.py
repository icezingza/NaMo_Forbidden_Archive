import pytest
import sys
import os
from unittest.mock import MagicMock

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