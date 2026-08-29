"""Unit tests for MicroChunker RAG strategy."""

from __future__ import annotations

from core.rag_chunker import MicroChunker


def test_micro_chunker_basic():
    chunker = MicroChunker(max_tokens=50, overlap_tokens=10, chars_per_token=3.5)
    sample_text = (
        "NaMo Forbidden Archive is a cognitive AI system. "
        "It supports multi-modal emotion fusion and high precision memory. "
        "Dhamma and Abhidhamma texts require micro-chunking for precise semantic search. "
        "This prevents embedding smearing across large contexts."
    )
    chunks = chunker.chunk_text(sample_text)

    assert len(chunks) >= 1
    for chunk in chunks:
        # Check that no chunk drastically exceeds max_chars
        assert len(chunk) <= 250


def test_micro_chunker_empty():
    chunker = MicroChunker()
    assert chunker.chunk_text("") == []
    assert chunker.chunk_text("   ") == []


def test_micro_chunker_sentence_boundaries():
    chunker = MicroChunker(max_tokens=20, overlap_tokens=5, chars_per_token=3.0)
    text = "First sentence here. Second sentence here. Third sentence here."
    chunks = chunker.chunk_text(text)

    assert len(chunks) >= 2
    # Ensure sentence boundary punctuation is preserved
    assert "." in chunks[0]
