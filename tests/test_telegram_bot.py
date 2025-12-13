import importlib
import os
import sys
import types
import unittest.mock

import pytest

CORE_SCRIPTS_PATH = os.path.join(os.path.dirname(__file__), "..", "Core_Scripts")


def _inject_telegram_stub():
    """สร้างโมดูล telegram ปลอมเพื่อลด dependency ภายนอกระหว่างเทสต์"""
    telegram = types.ModuleType("telegram")
    ContextTypes = types.SimpleNamespace(DEFAULT_TYPE=object)

    class DummyFilter:
        def __init__(self, name):
            self.name = name

        def __and__(self, other):
            return self

        def __invert__(self):
            return self

    class DummyUpdate:
        def __init__(self):
            self.message = types.SimpleNamespace(text="", reply_text=lambda *args, **kwargs: None)

    dummy_filters = types.SimpleNamespace(TEXT=DummyFilter("TEXT"), COMMAND=DummyFilter("COMMAND"))

    telegram.ext = types.SimpleNamespace(
        ApplicationBuilder=lambda: types.SimpleNamespace(token=lambda *_: types.SimpleNamespace(build=lambda: types.SimpleNamespace(add_handler=lambda *_: None, run_polling=lambda: None))),
        CommandHandler=object,
        MessageHandler=lambda *args, **kwargs: None,
        filters=dummy_filters,
        ContextTypes=ContextTypes,
    )
    telegram.Update = DummyUpdate
    telegram.ContextTypes = ContextTypes
    telegram.filters = dummy_filters
    sys.modules["telegram"] = telegram
    sys.modules["telegram.ext"] = telegram.ext
    sys.modules["telegram.ext.filters"] = telegram.ext.filters
    return telegram


def _reload_module():
    sys.path.insert(0, CORE_SCRIPTS_PATH)
    if "namo_auto_AI_reply" in sys.modules:
        importlib.reload(sys.modules["namo_auto_AI_reply"])
    else:
        importlib.import_module("namo_auto_AI_reply")


def test_telegram_bot_loads_token_from_env():
    """Tests that the Telegram bot script loads the token from the environment."""
    _inject_telegram_stub()
    with unittest.mock.patch.dict(os.environ, {"TELEGRAM_TOKEN": "fake-token"}):
        _reload_module()
        from namo_auto_AI_reply import TOKEN

        assert TOKEN == "fake-token"


def test_telegram_bot_raises_error_if_token_is_missing():
    """Tests that the script raises a ValueError if the TELEGRAM_TOKEN is not set."""
    _inject_telegram_stub()
    with unittest.mock.patch.dict(os.environ, clear=True):
        with pytest.raises(ValueError, match="No TELEGRAM_TOKEN set for Telegram bot"):
            _reload_module()
