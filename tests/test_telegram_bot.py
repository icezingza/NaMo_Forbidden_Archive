import os
import sys
import unittest.mock
import pytest

def test_telegram_bot_loads_token_from_env():
    """
    Tests that the Telegram bot script loads the token from the environment variable.
    """
    with unittest.mock.patch.dict(os.environ, {"TELEGRAM_TOKEN": "fake-token"}):
        with unittest.mock.patch('telegram.ext.ApplicationBuilder'):
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Core_Scripts'))
            if 'namo_auto_AI_reply' in sys.modules:
                import importlib
                importlib.reload(sys.modules['namo_auto_AI_reply'])
                from namo_auto_AI_reply import TOKEN
            else:
                from namo_auto_AI_reply import TOKEN
            assert TOKEN == "fake-token"

def test_telegram_bot_raises_error_if_token_is_missing():
    """
    Tests that the script raises a ValueError if the TELEGRAM_TOKEN is not set.
    """
    with unittest.mock.patch.dict(os.environ, clear=True):
        with pytest.raises(ValueError, match="No TELEGRAM_TOKEN set for Telegram bot"):
            with unittest.mock.patch('telegram.ext.ApplicationBuilder'):
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Core_Scripts'))
                if 'namo_auto_AI_reply' in sys.modules:
                    import importlib
                    importlib.reload(sys.modules['namo_auto_AI_reply'])
                else:
                    import namo_auto_AI_reply
