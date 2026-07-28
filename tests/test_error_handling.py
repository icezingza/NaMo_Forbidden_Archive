"""Tests for structured, client-safe error handling (core.exceptions + server handlers)."""

import os
import sys
from unittest.mock import AsyncMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient

from core.exceptions import EngineError, NamoAPIError, error_payload
from server import app

client = TestClient(app)
# A client that returns the 500 response instead of re-raising, for the catch-all handler.
client_no_raise = TestClient(app, raise_server_exceptions=False)


# --- error_payload helper ---


def test_error_payload_omits_detail_when_none():
    assert error_payload("oops", "INTERNAL_ERROR") == {
        "success": False,
        "error": "oops",
        "error_code": "INTERNAL_ERROR",
    }


def test_error_payload_includes_detail_when_present():
    body = error_payload("oops", "ENGINE_ERROR", "trace-context")
    assert body["detail"] == "trace-context"
    assert body["success"] is False


def test_custom_exception_attributes():
    exc = EngineError("engine down", detail="stack")
    assert isinstance(exc, NamoAPIError)
    assert exc.status_code == 502
    assert exc.error_code == "ENGINE_ERROR"
    assert exc.message == "engine down"
    assert exc.detail == "stack"


# --- validation errors ---


def test_validation_error_returns_structured_shape():
    with patch("server.settings") as mock_settings:
        mock_settings.debug = False
        mock_settings.namo_api_keys = None
        mock_settings.namo_api_default_plan = "public"
        response = client.post("/chat", json={})  # missing required "text"
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "VALIDATION_ERROR"
    assert "detail" not in data  # hidden when not in debug


# --- custom NamoAPIError mapping ---


def test_namo_api_error_maps_to_status_and_code():
    with (
        patch("server.settings") as mock_settings,
        patch("server.engine.process_input", new=AsyncMock(side_effect=EngineError("engine down"))),
        patch("server._store_memory_if_enabled"),
    ):
        mock_settings.debug = False
        mock_settings.namo_api_keys = None
        mock_settings.namo_api_default_plan = "public"
        mock_settings.public_base_url = None
        mock_settings.default_engine = "omega"
        mock_settings.memory_logging = 0
        response = client.post("/chat", json={"text": "hi", "session_id": "err-engine"})
    assert response.status_code == 502
    data = response.json()
    assert data["error_code"] == "ENGINE_ERROR"
    assert data["success"] is False


# --- unexpected errors: no stack trace in production ---


def test_unhandled_exception_hides_detail_in_prod():
    with (
        patch("server.settings") as mock_settings,
        patch("server.engine.process_input", new=AsyncMock(side_effect=ValueError("boom"))),
        patch("server._store_memory_if_enabled"),
    ):
        mock_settings.debug = False
        mock_settings.namo_api_keys = None
        mock_settings.namo_api_default_plan = "public"
        mock_settings.public_base_url = None
        mock_settings.default_engine = "omega"
        mock_settings.memory_logging = 0
        response = client_no_raise.post("/chat", json={"text": "hi", "session_id": "err-500"})
    assert response.status_code == 500
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "INTERNAL_ERROR"
    assert "detail" not in data  # no stack trace leaked in production


def test_unhandled_exception_exposes_detail_in_debug():
    with (
        patch("server.settings") as mock_settings,
        patch("server.engine.process_input", new=AsyncMock(side_effect=ValueError("boom"))),
        patch("server._store_memory_if_enabled"),
    ):
        mock_settings.debug = True
        mock_settings.namo_api_keys = None
        mock_settings.namo_api_default_plan = "public"
        mock_settings.public_base_url = None
        mock_settings.default_engine = "omega"
        mock_settings.memory_logging = 0
        response = client_no_raise.post("/chat", json={"text": "hi", "session_id": "err-dbg"})
    assert response.status_code == 500
    data = response.json()
    assert "ValueError" in data["detail"]
