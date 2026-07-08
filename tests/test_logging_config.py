"""Tests for config.setup_logging — no network or filesystem required."""

import logging
from unittest.mock import patch

from config import setup_logging


def test_debug_true_forces_debug_level():
    """In development (debug=True) the root level floor is DEBUG."""
    with patch("config.settings") as mock_settings:
        mock_settings.debug = True
        mock_settings.log_level = "INFO"
        setup_logging()
    assert logging.getLogger().level == logging.DEBUG


def test_honors_log_level_when_not_debug():
    """In production (debug=False) the configured log_level is honored."""
    with patch("config.settings") as mock_settings:
        mock_settings.debug = False
        mock_settings.log_level = "WARNING"
        setup_logging()
    assert logging.getLogger().level == logging.WARNING


def test_invalid_level_falls_back_to_info():
    """An unrecognized log_level falls back to INFO (not a crash)."""
    with patch("config.settings") as mock_settings:
        mock_settings.debug = False
        mock_settings.log_level = "NOT_A_LEVEL"
        setup_logging()
    assert logging.getLogger().level == logging.INFO


def test_explicit_level_override():
    """An explicit level argument overrides settings.log_level."""
    with patch("config.settings") as mock_settings:
        mock_settings.debug = False
        mock_settings.log_level = "INFO"
        setup_logging("ERROR")
    assert logging.getLogger().level == logging.ERROR
