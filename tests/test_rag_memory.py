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
    with patch("core.rag_memory_system.OpenAI") as mock_openai_cls:
        mock_openai_cls.return_value = MagicMock()
        from core.rag_memory_system import NaMoInfiniteMemory

        mem = NaMoInfiniteMemory(dataset_path=str(tmp_path) if tmp_path else "nonexistent_path")
    return mem


# ===========================================================================
# retrieve_context
# ===========================================================================

class TestRetrieveContext:
    def test_returns_string_when_no_files(self, tmp_path):
        mem = _make_memory(tmp_path)
        result = mem.retrieve_context("test query")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_loads_data_on_first_call(self, tmp_path):
        mem = _make_memory(tmp_path)
        assert mem.is_loaded is False
        mem.retrieve_context("anything")
        # After retrieve_context, ingest_data() is called which sets fallback memories
        assert len(mem.memories) > 0

    def test_uses_loaded_memories_for_fallback(self, tmp_path):
        mem = _make_memory(tmp_path)
        mem.memories = ["fragment A", "fragment B", "fragment C"]
        mem.is_loaded = True
        result = mem.retrieve_context("test")
        assert result in ["fragment A", "fragment B", "fragment C"]

    def test_fallback_when_no_vector_index(self, tmp_path):
        mem = _make_memory(tmp_path)
        mem.memories = ["test memory"]
        mem.is_loaded = True
        mem._faiss_index = None
        result = mem.retrieve_context("query")
        assert result == "test memory"

    def test_returns_ellipsis_when_memories_empty(self, tmp_path):
        mem = _make_memory(tmp_path)
        mem.is_loaded = True
        mem.memories = []
        result = mem.retrieve_context("query")
        assert result == "..."


# ===========================================================================
# ingest_data
# ===========================================================================

class TestIngestData:
    def test_ingest_no_files_sets_fallback_memories(self, tmp_path):
        mem = _make_memory(tmp_path)
        mem.ingest_data()
        assert len(mem.memories) > 0

    def test_ingest_with_txt_files(self, tmp_path):
        # Create a sample text file in the dataset path
        txt_file = tmp_path / "sample.txt"
        txt_file.write_text("This is a sample story for testing.\n" * 20)
        mem = _make_memory(tmp_path)
        mem.ingest_data()
        assert len(mem.memories) > 0

    def test_ingest_sets_is_loaded_when_files_found(self, tmp_path):
        txt_file = tmp_path / "data.txt"
        txt_file.write_text("content " * 50)
        mem = _make_memory(tmp_path)
        mem.ingest_data()
        assert mem.is_loaded is True


# ===========================================================================
# _vector_search
# ===========================================================================

class TestVectorSearch:
    def test_returns_none_when_no_index(self, tmp_path):
        mem = _make_memory(tmp_path)
        assert mem._vector_search("test") is None

    def test_returns_none_when_embed_fails(self, tmp_path):
        mem = _make_memory(tmp_path)
        mem._faiss_index = MagicMock()
        mem._faiss_meta = [{"file": "test.txt", "chunk_id": 0, "snippet": "hello"}]
        # Make _embed_with_retry raise
        with patch.object(mem, "_embed_with_retry", side_effect=Exception("embed error")):
            result = mem._vector_search("query")
        assert result is None
