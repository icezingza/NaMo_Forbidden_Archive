"""Tests for core/rag_memory_system.py — NaMoInfiniteMemory (mocked deps)."""

import os
import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_memory(tmp_path=None):
    """Return NaMoInfiniteMemory with OpenAI client mocked."""
    with patch("core.rag_memory_system.AsyncOpenAI") as mock_openai_cls:
        mock_openai_cls.return_value = MagicMock()
        from core.rag_memory_system import NaMoInfiniteMemory

        mem = NaMoInfiniteMemory(dataset_path=str(tmp_path) if tmp_path else "nonexistent_path")
    return mem


# ===========================================================================
# retrieve_context
# ===========================================================================


class TestRetrieveContext:
    async def test_returns_none_when_index_is_missing(self, tmp_path):
        mem = _make_memory(tmp_path)
        result = await mem.retrieve_context("test query")
        assert result is None

    async def test_initializes_once_on_first_call(self, tmp_path):
        mem = _make_memory(tmp_path)
        assert mem.is_loaded is False
        await mem.retrieve_context("anything")
        assert mem.is_loaded is True

    async def test_no_match_returns_none(self, tmp_path):
        mem = _make_memory(tmp_path)
        mem.is_loaded = True
        result = await mem.retrieve_context("test")
        assert result is None

    async def test_missing_vector_index_returns_none(self, tmp_path):
        mem = _make_memory(tmp_path)
        mem.is_loaded = True
        mem._faiss_index = None
        result = await mem.retrieve_context("query")
        assert result is None


# ===========================================================================
# ingest_data
# ===========================================================================


class TestIngestData:
    def test_ingest_missing_index_is_deterministic(self, tmp_path):
        mem = _make_memory(tmp_path)
        mem.ingest_data()
        assert mem.is_loaded is True
        assert mem._faiss_index is None
        assert mem._faiss_meta == []


# ===========================================================================
# _vector_search
# ===========================================================================


class TestVectorSearch:
    async def test_returns_none_when_no_index(self, tmp_path):
        mem = _make_memory(tmp_path)
        assert await mem._vector_search("test") is None

    async def test_returns_none_when_embed_fails(self, tmp_path):
        mem = _make_memory(tmp_path)
        mem._faiss_index = MagicMock()
        mem._faiss_meta = [{"file": "test.txt", "chunk_id": 0, "snippet": "hello"}]
        # Make _embed_with_retry raise
        with patch.object(mem, "_embed_with_retry", side_effect=Exception("embed error")):
            result = await mem._vector_search("query")
        assert result is None
