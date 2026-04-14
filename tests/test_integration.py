"""Integration tests: session lifecycle, multi-engine, cleanup, and input validation.

These tests exercise the full stack from server.py down to engine process_input().
All external services (OpenAI, ElevenLabs, emotion API) are either absent or mocked
so the suite runs fully offline.
"""

from __future__ import annotations

import sys
import time
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_chat_input(text: str = "สวัสดี", session_id: str | None = None, engine: str | None = None):
    from server import ChatInput

    return ChatInput(text=text, session_id=session_id, engine=engine)


# ---------------------------------------------------------------------------
# Phase 1: Input validation
# ---------------------------------------------------------------------------


class TestChatInputValidation:
    def test_valid_text_accepted(self):
        ci = _make_chat_input(text="hello")
        assert ci.text == "hello"

    def test_text_too_long_raises(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            _make_chat_input(text="x" * 4001)

    def test_text_at_limit_accepted(self):
        ci = _make_chat_input(text="x" * 4000)
        assert len(ci.text) == 4000

    def test_valid_session_id_accepted(self):
        sid = str(uuid.uuid4())
        ci = _make_chat_input(session_id=sid)
        assert ci.session_id == sid

    def test_session_id_alphanumeric_accepted(self):
        ci = _make_chat_input(session_id="test-session_123")
        assert ci.session_id == "test-session_123"

    def test_session_id_with_spaces_rejected(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            _make_chat_input(session_id="invalid session")

    def test_session_id_with_special_chars_rejected(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            _make_chat_input(session_id="../../etc/passwd")

    def test_session_id_too_long_rejected(self):
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            _make_chat_input(session_id="a" * 129)

    def test_none_session_id_accepted(self):
        ci = _make_chat_input(session_id=None)
        assert ci.session_id is None


# ---------------------------------------------------------------------------
# Phase 3: Unified session state (BasePersonaEngine interface)
# ---------------------------------------------------------------------------


class TestBasePersonaSessionInterface:
    def _make_engine(self):
        from core.namo_omega_engine import NaMoOmegaEngine

        return NaMoOmegaEngine()

    def test_collect_session_keys_empty_at_start(self):
        engine = self._make_engine()
        assert engine._collect_session_keys() == []

    def test_session_key_appears_after_process_input(self):
        engine = self._make_engine()
        sid = "test-integ-collect"
        engine.process_input("สวัสดี", session_id=sid)
        assert sid in engine._collect_session_keys()

    def test_evict_session_removes_state(self):
        engine = self._make_engine()
        sid = "test-integ-evict"
        engine.process_input("สวัสดี", session_id=sid)
        assert sid in engine._collect_session_keys()
        engine._evict_session(sid)
        assert sid not in engine._collect_session_keys()

    def test_evict_nonexistent_session_is_safe(self):
        engine = self._make_engine()
        # Must not raise
        engine._evict_session("ghost-session-xyz")

    def test_multiple_sessions_isolated(self):
        engine = self._make_engine()
        engine.process_input("สวัสดี", session_id="sess-a")
        engine.process_input("สวัสดี", session_id="sess-b")
        keys = engine._collect_session_keys()
        assert "sess-a" in keys
        assert "sess-b" in keys
        engine._evict_session("sess-a")
        assert "sess-a" not in engine._collect_session_keys()
        assert "sess-b" in engine._collect_session_keys()


# ---------------------------------------------------------------------------
# Phase 3: Session cleanup via server cleanup_expired_sessions
# ---------------------------------------------------------------------------


class TestSessionCleanup:
    def test_cleanup_removes_expired_sessions(self):
        from server import (
            _EngineRegistry,
            _session_timestamps,
            _touch_session,
            cleanup_expired_sessions,
        )

        sid = f"cleanup-{uuid.uuid4().hex[:8]}"
        engine = _EngineRegistry.get("omega")
        engine.process_input("สวัสดี", session_id=sid)
        _touch_session(sid)

        # Force expiry
        _session_timestamps[sid] = time.time() - 99999
        evicted = cleanup_expired_sessions(ttl_seconds=1)

        assert evicted >= 1
        assert sid not in engine._collect_session_keys()
        assert sid not in _session_timestamps

    def test_cleanup_does_not_remove_active_sessions(self):
        from server import (
            _EngineRegistry,
            _touch_session,
            cleanup_expired_sessions,
        )

        sid = f"active-{uuid.uuid4().hex[:8]}"
        engine = _EngineRegistry.get("omega")
        engine.process_input("สวัสดี", session_id=sid)
        _touch_session(sid)  # fresh timestamp

        cleanup_expired_sessions(ttl_seconds=9999)
        assert sid in engine._collect_session_keys()

        # Cleanup
        engine._evict_session(sid)


# ---------------------------------------------------------------------------
# Phase 1: All registered engines produce valid output
# ---------------------------------------------------------------------------


class TestAllEnginesProcessInput:
    """Smoke-test: every registered engine must handle a basic Thai message."""

    @pytest.mark.parametrize("engine_name", ["omega", "dark", "ultimate", "rinlada", "seraphina"])
    def test_engine_returns_standard_shape(self, engine_name):
        from server import _EngineRegistry

        engine = _EngineRegistry.get(engine_name)
        result = engine.process_input("สวัสดี", session_id=f"integ-{engine_name}")
        assert isinstance(result["text"], str)
        assert len(result["text"]) > 0
        # media_trigger must have image and audio keys (tts is optional/engine-specific)
        assert "image" in result["media_trigger"]
        assert "audio" in result["media_trigger"]
        # system_status must be a non-empty dict (keys vary per engine)
        assert isinstance(result["system_status"], dict)
        assert len(result["system_status"]) > 0

    # Engines that maintain per-session state dicts tracked by _collect_session_keys
    @pytest.mark.parametrize("engine_name", ["omega", "dark", "ultimate", "rinlada"])
    def test_stateful_engine_session_keys_tracked(self, engine_name):
        from server import _EngineRegistry

        engine = _EngineRegistry.get(engine_name)
        sid = f"track-{engine_name}"
        engine.process_input("test", session_id=sid)
        assert sid in engine._collect_session_keys()
        engine._evict_session(sid)
