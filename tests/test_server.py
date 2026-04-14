import os
import sys
from unittest.mock import MagicMock, patch

# Ensure project root is on sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient

# We need to import the app from server.py
from server import (
    _log_usage,
    _normalize_base_url,
    _normalize_media,
    _parse_api_key_map,
    _RateLimiter,
    _resolve_plan,
    _store_memory_if_enabled,
    _touch_session,
    app,
    cleanup_expired_sessions,
)

# Create a client for testing
client = TestClient(app)


def test_root_endpoint():
    """Tests the root (/) endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "NaMo is Online"
    assert "default_engine" in data
    assert "available_engines" in data


def test_health_check_endpoint():
    """Tests the health check (/v1/health) endpoint."""
    response = client.get("/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "engine" in response.json()


def test_list_engines_endpoint():
    """Tests the /v1/engines endpoint lists all registered engines."""
    response = client.get("/v1/engines")
    assert response.status_code == 200
    data = response.json()
    assert "engines" in data
    assert "omega" in data["engines"]
    assert "rinlada" in data["engines"]
    assert "seraphina" in data["engines"]
    assert "dark" in data["engines"]
    assert "ultimate" in data["engines"]


def test_parse_api_key_map():
    """Tests the _parse_api_key_map helper function."""
    # Test with None and empty string
    assert _parse_api_key_map(None) == {}
    assert _parse_api_key_map("") == {}
    assert _parse_api_key_map("  ,  ") == {}

    # Test with a single key (defaults to 'standard')
    assert _parse_api_key_map("key1") == {"key1": "standard"}

    # Test with a single key and a plan
    assert _parse_api_key_map("key1:premium") == {"key1": "premium"}

    # Test with a key and an empty plan (defaults to 'standard')
    assert _parse_api_key_map("key1:") == {"key1": "standard"}

    # Test with multiple keys
    raw_string = "key1:premium, key2, key3:pro , key4:  "
    expected = {
        "key1": "premium",
        "key2": "standard",
        "key3": "pro",
        "key4": "standard",
    }
    assert _parse_api_key_map(raw_string) == expected


@patch("server.settings")
def test_resolve_plan_no_keys_configured(mock_settings):
    """Tests _resolve_plan when no API keys are configured in settings."""
    mock_settings.namo_api_keys = None
    mock_settings.namo_api_default_plan = "free"

    # No key provided, should be allowed with default plan
    assert _resolve_plan(None) == ("free", True)

    # A key is provided, but since none are configured, it's still allowed
    assert _resolve_plan("some-key") == ("free", True)


@patch("server.settings")
def test_resolve_plan_with_keys_configured(mock_settings):
    """Tests _resolve_plan when API keys are configured."""
    mock_settings.namo_api_keys = "key-pro:pro, key-std:standard"
    mock_settings.namo_api_default_plan = "public"

    # Case 1: No API key provided -> Not allowed, returns default plan
    assert _resolve_plan(None) == ("public", False)

    # Case 2: Invalid API key provided -> Not allowed, returns default plan
    assert _resolve_plan("invalid-key") == ("public", False)

    # Case 3: Valid 'pro' key provided -> Allowed, returns 'pro' plan
    assert _resolve_plan("key-pro") == ("pro", True)

    # Case 4: Valid 'standard' key provided -> Allowed, returns 'standard' plan
    assert _resolve_plan("key-std") == ("standard", True)


def test_normalize_media_helpers():
    """Tests the media URL normalization helper functions."""
    base_url = "http://localhost:8000"

    # Test _normalize_base_url
    assert _normalize_base_url("http://test.com/") == "http://test.com"
    assert _normalize_base_url("http://test.com") == "http://test.com"

    # Test _normalize_media
    media_in = {
        "visual": "Visual_Scenes/scene1.jpg",
        "audio": "Audio_Layers/layer1.mp3",
        "external": "https://example.com/image.png",
        "absolute": "/media/visual/scene2.jpg",
        "none": None,
        "windows_path": "Visual_Scenes\\scene3.jpg",
    }

    expected_media_out = {
        "visual": "http://localhost:8000/media/visual/scene1.jpg",
        "audio": "http://localhost:8000/media/audio/layer1.mp3",
        "external": "https://example.com/image.png",
        "absolute": "http://localhost:8000/media/visual/scene2.jpg",
        "none": None,
        "windows_path": "http://localhost:8000/media/visual/scene3.jpg",
    }

    assert _normalize_media(media_in, base_url) == expected_media_out
    assert _normalize_media({}, base_url) == {}
    assert _normalize_media(None, base_url) == {}


@patch("server.engine.process_input")
@patch("server._store_memory_if_enabled")
@patch("server._log_usage")
@patch("server.settings")
def test_chat_v1_endpoint_success_with_key(
    mock_settings, mock_log_usage, mock_store_memory, mock_process_input
):  # noqa: E501
    """Tests a successful call to the /v1/chat endpoint with a valid API key."""
    # Arrange
    mock_settings.namo_api_keys = "my-secret-key:premium"
    mock_settings.namo_api_default_plan = "public"
    mock_settings.public_base_url = None
    mock_settings.default_engine = "omega"  # ensure engine routing works

    mock_process_input.return_value = {
        "text": "This is the response.",
        "media_trigger": {"visual": "Visual_Scenes/test.jpg"},
        "system_status": {"sin_level": 2},
    }

    payload = {"text": "Hello", "session_id": "test-session-123"}
    headers = {"x-api-key": "my-secret-key"}

    # Act
    response = client.post("/v1/chat", json=payload, headers=headers)

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert data["response"] == "This is the response."
    assert data["session_id"] == "test-session-123"
    assert data["plan"] == "premium"
    assert data["media"]["visual"].endswith("/media/visual/test.jpg")
    assert data["status"] == {"sin_level": 2}

    mock_process_input.assert_called_once_with("Hello", session_id="test-session-123")
    mock_store_memory.assert_called_once_with(
        "test-session-123", "Hello", "This is the response.", {"sin_level": 2}
    )
    mock_log_usage.assert_called_once()
    log_call_args = mock_log_usage.call_args[0][0]
    assert log_call_args["endpoint"] == "/v1/chat"
    assert log_call_args["session_id"] == "test-session-123"
    assert log_call_args["plan"] == "premium"


@patch("server.engine.process_input")
@patch("server._store_memory_if_enabled")
@patch("server.settings")
def test_legacy_chat_endpoint_success(mock_settings, mock_store_memory, mock_process_input):
    """Tests a successful call to the legacy /chat endpoint."""
    # Arrange
    mock_settings.public_base_url = "http://test.public.url"
    mock_settings.default_engine = "omega"  # ensure engine routing works

    mock_process_input.return_value = {
        "text": "Legacy response.",
        "media_trigger": {"audio": "Audio_Layers/legacy.mp3"},
        "system_status": {"sin_level": 0},
    }

    payload = {"text": "Legacy Hello", "session_id": "legacy-session-456"}

    # Act
    response = client.post("/chat", json=payload)

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert data["response"] == "Legacy response."
    assert data["session_id"] == "legacy-session-456"
    assert "plan" not in data
    assert data["media"]["audio"] == "http://test.public.url/media/audio/legacy.mp3"
    assert data["status"] == {"sin_level": 0}

    mock_process_input.assert_called_once_with("Legacy Hello", session_id="legacy-session-456")
    mock_store_memory.assert_called_once_with(
        "legacy-session-456", "Legacy Hello", "Legacy response.", {"sin_level": 0}
    )


# ---------------------------------------------------------------------------
# Admin session management
# ---------------------------------------------------------------------------


def test_list_sessions_no_auth_required_when_no_admin_secret():
    """GET /v1/admin/sessions returns 200 when ADMIN_SECRET is not set."""
    with patch("server.settings") as mock_settings:
        mock_settings.admin_secret = None
        response = client.get("/v1/admin/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data


def test_list_sessions_returns_403_with_wrong_secret():
    """GET /v1/admin/sessions returns 403 when ADMIN_SECRET is set and header is wrong."""
    with patch("server.settings") as mock_settings:
        mock_settings.admin_secret = "correct-secret"
        response = client.get("/v1/admin/sessions", headers={"x-admin-secret": "wrong"})
    assert response.status_code == 403


def test_clear_session_removes_from_engine():
    """DELETE /v1/admin/sessions/{id} clears session data from loaded engines."""
    # Inject a fake session directly into the omega engine's session_states
    from server import _EngineRegistry

    eng = _EngineRegistry._instances.get("omega")
    if eng is None:
        return  # engine not loaded in this test run

    test_sid = "admin-test-session-xyz"
    if hasattr(eng, "_session_states"):
        eng._session_states[test_sid] = {"arousal": 5, "sin_system": None, "personas": None}
    if hasattr(eng, "session_history"):
        eng.session_history[test_sid] = []

    with patch("server.settings") as mock_settings:
        mock_settings.admin_secret = None  # no auth required
        response = client.delete(f"/v1/admin/sessions/{test_sid}")

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == test_sid
    assert "cleared_from" in data

    # Session should be gone from the engine
    if hasattr(eng, "_session_states"):
        assert test_sid not in eng._session_states
    if hasattr(eng, "session_history"):
        assert test_sid not in eng.session_history


# ---------------------------------------------------------------------------
# _store_memory_if_enabled
# ---------------------------------------------------------------------------


@patch("server.settings")
def test_store_memory_disabled_when_flag_off(mock_settings):
    mock_settings.memory_logging = 0
    with patch("server.requests.post") as mock_post:
        _store_memory_if_enabled("s1", "hi", "hello", None)
    mock_post.assert_not_called()


@patch("server.settings")
def test_store_memory_disabled_when_no_url(mock_settings):
    mock_settings.memory_logging = 1
    mock_settings.memory_api_url = None
    with patch("server.requests.post") as mock_post:
        _store_memory_if_enabled("s1", "hi", "hello", None)
    mock_post.assert_not_called()


@patch("server.settings")
def test_store_memory_posts_when_configured(mock_settings):
    mock_settings.memory_logging = 1
    mock_settings.memory_api_url = "http://memory.local/store"
    mock_settings.memory_api_key = "secret"
    with patch("server.requests.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=200)
        _store_memory_if_enabled("s1", "user text", "bot reply", {"stat": 1})
    mock_post.assert_called_once()
    payload = mock_post.call_args.kwargs["json"]
    assert "user text" in payload["content"]
    assert "bot reply" in payload["content"]
    assert payload["session_id"] == "s1"
    assert mock_post.call_args.kwargs["headers"]["x-api-key"] == "secret"


@patch("server.settings")
def test_store_memory_exception_silent(mock_settings):
    import requests as _req

    mock_settings.memory_logging = 1
    mock_settings.memory_api_url = "http://memory.local/store"
    mock_settings.memory_api_key = None
    with patch("server.requests.post", side_effect=_req.RequestException("timeout")):
        _store_memory_if_enabled("s1", "hi", "bye", None)  # should not raise


# ---------------------------------------------------------------------------
# _log_usage
# ---------------------------------------------------------------------------


def test_log_usage_writes_to_file(tmp_path):
    log_path = str(tmp_path / "usage.jsonl")
    with patch("server.settings") as mock_settings:
        mock_settings.namo_usage_log_path = log_path
        _log_usage({"endpoint": "/v1/chat", "session_id": "s1", "plan": "pro"})

    import json as _json

    with open(log_path) as f:
        line = _json.loads(f.read().strip())
    assert line["endpoint"] == "/v1/chat"
    assert "timestamp" in line


def test_log_usage_no_path_is_noop():
    with patch("server.settings") as mock_settings:
        mock_settings.namo_usage_log_path = None
        _log_usage({"endpoint": "/v1/chat"})  # should not raise


def test_log_usage_oserror_is_silenced(tmp_path):
    with patch("server.settings") as mock_settings:
        mock_settings.namo_usage_log_path = "/nonexistent/path/usage.jsonl"
        _log_usage({"endpoint": "/v1/chat"})  # should not raise


# ---------------------------------------------------------------------------
# Session TTL — cleanup_expired_sessions
# ---------------------------------------------------------------------------


def test_cleanup_expired_sessions_removes_stale(monkeypatch):
    import server

    # Inject a fake old session
    server._session_timestamps["stale-session"] = 0.0  # epoch = always expired
    removed = cleanup_expired_sessions(ttl_seconds=1.0)
    assert removed >= 1
    assert "stale-session" not in server._session_timestamps


def test_cleanup_keeps_fresh_sessions(monkeypatch):
    import time as _time

    import server

    sid = "fresh-session-xyz"
    server._session_timestamps[sid] = _time.time()  # just now
    cleanup_expired_sessions(ttl_seconds=3600.0)
    assert sid in server._session_timestamps
    # cleanup
    server._session_timestamps.pop(sid, None)


def test_touch_session_records_timestamp():
    import time as _time

    import server

    before = _time.time()
    _touch_session("ts-test-session")
    after = _time.time()
    ts = server._session_timestamps.get("ts-test-session", 0)
    assert before <= ts <= after
    server._session_timestamps.pop("ts-test-session", None)


# ---------------------------------------------------------------------------
# Rate limiter (_RateLimiter)
# ---------------------------------------------------------------------------


def test_rate_limiter_allows_within_limit():
    limiter = _RateLimiter(max_calls=5, period_seconds=60)
    for _ in range(5):
        assert limiter.is_allowed("ip-1") is True


def test_rate_limiter_blocks_when_exceeded():
    limiter = _RateLimiter(max_calls=3, period_seconds=60)
    for _ in range(3):
        limiter.is_allowed("ip-2")
    assert limiter.is_allowed("ip-2") is False


def test_rate_limiter_resets_after_period():
    import time as _time

    limiter = _RateLimiter(max_calls=2, period_seconds=0.05)
    limiter.is_allowed("ip-3")
    limiter.is_allowed("ip-3")
    assert limiter.is_allowed("ip-3") is False
    _time.sleep(0.1)
    assert limiter.is_allowed("ip-3") is True


def test_rate_limiter_different_keys_independent():
    limiter = _RateLimiter(max_calls=1, period_seconds=60)
    assert limiter.is_allowed("ip-A") is True
    assert limiter.is_allowed("ip-A") is False
    assert limiter.is_allowed("ip-B") is True  # different key, not affected


# ---------------------------------------------------------------------------
# /v1/chat/stream endpoint
# ---------------------------------------------------------------------------


@patch("server.settings")
def test_stream_endpoint_returns_sse(mock_settings):
    mock_settings.namo_api_keys = None
    mock_settings.namo_api_default_plan = "public"
    mock_settings.public_base_url = None
    mock_settings.default_engine = "omega"
    mock_settings.rate_limit_calls = 1000
    mock_settings.rate_limit_period = 60
    mock_settings.memory_logging = 0
    mock_settings.namo_usage_log_path = None

    with patch("server._rate_limiter") as mock_rl:
        mock_rl.is_allowed.return_value = True
        with patch("server.engine.stream_input") as mock_stream:
            mock_stream.return_value = iter(["สวัสดี", "ค่ะ"])
            response = client.post(
                "/v1/chat/stream",
                json={"text": "hello", "session_id": "stream-test"},
            )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]


# ---------------------------------------------------------------------------
# /v1/status endpoint
# ---------------------------------------------------------------------------


def test_engine_status_endpoint():
    response = client.get("/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


# ---------------------------------------------------------------------------
# Per-request engine override
# ---------------------------------------------------------------------------


@patch("server.settings")
def test_chat_with_engine_override(mock_settings):
    mock_settings.namo_api_keys = None
    mock_settings.namo_api_default_plan = "public"
    mock_settings.public_base_url = None
    mock_settings.default_engine = "omega"
    mock_settings.memory_logging = 0

    with patch("server._store_memory_if_enabled"):
        response = client.post(
            "/chat",
            json={"text": "สวัสดี", "engine": "ultimate", "session_id": "override-test"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["engine"] == "NaMoUltimateBrain"
