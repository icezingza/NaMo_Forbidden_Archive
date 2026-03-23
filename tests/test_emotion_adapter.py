"""Tests for adapters/emotion.py — EmotionAdapter with and without service."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest
import requests as _requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture()
def adapter():
    from adapters.emotion import EmotionAdapter

    return EmotionAdapter()


def test_analyze_emotion_success(adapter):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {"primary_emotion": "joy", "intensity": 0.9}

    with patch("adapters.emotion.requests.post", return_value=mock_resp) as mock_post:
        result = adapter.analyze_emotion("ดีใจมากเลย")

    mock_post.assert_called_once()
    assert result["primary_emotion"] == "joy"
    assert result["intensity"] == 0.9


def test_analyze_emotion_sends_correct_payload(adapter):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = {}

    with patch("adapters.emotion.requests.post", return_value=mock_resp) as mock_post:
        adapter.analyze_emotion("test text")

    call_kwargs = mock_post.call_args
    assert call_kwargs.kwargs["json"] == {"text": "test text"}
    assert call_kwargs.kwargs["timeout"] == 2


def test_analyze_emotion_request_exception_returns_fallback(adapter):
    with patch(
        "adapters.emotion.requests.post",
        side_effect=_requests.exceptions.RequestException("connection refused"),
    ):
        result = adapter.analyze_emotion("hello")

    assert result["primary_emotion"] == "unknown"
    assert result["intensity"] == 0
    assert "error" in result


def test_analyze_emotion_timeout_returns_fallback(adapter):
    with patch(
        "adapters.emotion.requests.post",
        side_effect=_requests.exceptions.Timeout("timed out"),
    ):
        result = adapter.analyze_emotion("slow")

    assert result["primary_emotion"] == "unknown"


def test_adapter_initializes_with_default_url():
    with patch.dict(os.environ, {}, clear=True):
        from importlib import reload

        import adapters.emotion

        reload(adapters.emotion)
        from adapters.emotion import EmotionAdapter

        a = EmotionAdapter()
    assert "8082" in a.api_url or "localhost" in a.api_url
