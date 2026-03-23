"""Tests for adapters/memory.py — local write and unified remote forwarding."""

import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture()
def local_adapter(tmp_path):
    """MemoryAdapter writing to a temp file with no remote configured."""
    db = str(tmp_path / "mem.json")
    with patch("adapters.memory.settings") as mock_settings:
        mock_settings.memory_api_url = None
        mock_settings.memory_api_key = None
        from adapters.memory import MemoryAdapter

        adapter = MemoryAdapter(db_file=db)
    return adapter, db


def test_store_creates_entry_in_local_json(local_adapter):
    adapter, db = local_adapter
    adapter.store_interaction(
        user_input="hello",
        response="world",
        session_id="test-session",
    )
    with open(db, encoding="utf-8") as f:
        history = json.load(f)
    assert len(history) == 1
    entry = history[0]
    assert entry["user"] == "hello"
    assert entry["bot"] == "world"
    assert entry["session_id"] == "test-session"
    assert "timestamp" in entry


def test_store_multiple_entries_append(local_adapter):
    adapter, db = local_adapter
    adapter.store_interaction("msg1", "resp1", session_id="s1")
    adapter.store_interaction("msg2", "resp2", session_id="s1")
    with open(db, encoding="utf-8") as f:
        history = json.load(f)
    assert len(history) == 2


def test_none_values_are_stripped(local_adapter):
    adapter, db = local_adapter
    adapter.store_interaction(
        "hi",
        "there",
        emotions=None,
        arousal_level=None,
        infection_status=None,
    )
    with open(db, encoding="utf-8") as f:
        entry = json.load(f)[0]
    assert "emotions" not in entry
    assert "arousal_level" not in entry


def test_get_last_conversation(local_adapter):
    adapter, _ = local_adapter
    assert adapter.get_last_conversation() is None
    adapter.store_interaction("first", "response1")
    adapter.store_interaction("second", "response2")
    last = adapter.get_last_conversation()
    assert last["user"] == "second"


def test_store_forwards_to_remote_when_configured(tmp_path):
    """When MEMORY_API_URL is set, store_interaction also posts to the remote."""
    db = str(tmp_path / "mem_remote.json")
    with patch("adapters.memory.settings") as mock_settings:
        mock_settings.memory_api_url = "http://memory.local/store"
        mock_settings.memory_api_key = "secret-key"
        from adapters.memory import MemoryAdapter

        adapter = MemoryAdapter(db_file=db)

    with patch("adapters.memory.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        adapter.store_interaction("user text", "bot reply", session_id="s2")

    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args
    assert call_kwargs.kwargs["json"]["session_id"] == "s2"
    assert "user text" in call_kwargs.kwargs["json"]["content"]
    assert call_kwargs.kwargs["headers"]["x-api-key"] == "secret-key"


def test_remote_failure_does_not_raise(tmp_path):
    """A remote forwarding failure is silently logged — does not raise."""
    import requests as _requests

    db = str(tmp_path / "mem_fail.json")
    with patch("adapters.memory.settings") as mock_settings:
        mock_settings.memory_api_url = "http://memory.local/store"
        mock_settings.memory_api_key = None
        from adapters.memory import MemoryAdapter

        adapter = MemoryAdapter(db_file=db)

    with patch(
        "adapters.memory.requests.post",
        side_effect=_requests.RequestException("timeout"),
    ):
        # Should not raise
        adapter.store_interaction("msg", "resp")
