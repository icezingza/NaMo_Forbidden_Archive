import os
import sys
from unittest.mock import patch

# Ensure project root is on sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient

# We need to import the app from server.py
from server import _normalize_base_url, _normalize_media, _parse_api_key_map, _resolve_plan, app, engine

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
def test_chat_v1_endpoint_success_with_key(mock_settings, mock_log_usage, mock_store_memory, mock_process_input):
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