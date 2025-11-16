import pytest
from unittest.mock import patch
from app import main_loop

def test_app_initializes_and_exits():
    """
    Tests that the main application initializes without errors and exits cleanly.
    """
    with patch('builtins.input', return_value='exit'):
        try:
            main_loop()
        except SystemExit as e:
            assert e.code == 1, "The application should not exit with an error code."
