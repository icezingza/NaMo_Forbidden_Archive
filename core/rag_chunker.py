"""Micro-Chunker Strategy for Dhamma / Abhidhamma and Persona RAG.

Enforces 100-150 token max micro-chunks with a 20-token overlap, preserving sentence boundaries
(Thai & English) to prevent embedding smearing and guarantee high semantic precision.
"""

from __future__ import annotations

import re


class MicroChunker:
    """Sentence-aware micro-chunking engine for RAG pipelines."""

    def __init__(
        self,
        max_tokens: int = 150,
        overlap_tokens: int = 20,
        chars_per_token: float = 3.5,
    ) -> None:
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        self.chars_per_token = chars_per_token

        self.max_chars = int(max_tokens * chars_per_token)
        self.overlap_chars = int(overlap_tokens * chars_per_token)

    def chunk_text(self, text: str) -> list[str]:
        """Split text into overlapping micro-chunks respecting sentence boundaries.

        Args:
            text: Input document string.

        Returns:
            List of micro-chunk strings (100-150 tokens max each).
        """
        if not text or not text.strip():
            return []

        # 1. Split into sentence units (Thai & English sentence delimiters)
        sentences = re.split(r"(?<=[.!?…\n])\s*|(?<=ๆ)\s+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return []

        chunks: list[str] = []
        current_chunk: list[str] = []
        current_len = 0

        for sentence in sentences:
            sentence_len = len(sentence)

            # If a single sentence exceeds max_chars, split it cleanly
            if sentence_len > self.max_chars:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_len = 0
                
                # Hard chunk long sentence
                sub_start = 0
                while sub_start < sentence_len:
                    sub_end = min(sentence_len, sub_start + self.max_chars)
                    chunks.append(sentence[sub_start:sub_end])
                    sub_start += self.max_chars - self.overlap_chars
                continue

            if current_len + sentence_len > self.max_chars:
                chunk_str = " ".join(current_chunk)
                chunks.append(chunk_str)

                # Overlap: keep tail sentences fitting overlap_chars
                overlap_sentences: list[str] = []
                overlap_len = 0
                for prev_sent in reversed(current_chunk):
                    if overlap_len + len(prev_sent) <= self.overlap_chars:
                        overlap_sentences.insert(0, prev_sent)
                        overlap_len += len(prev_sent)
                    else:
                        break

                current_chunk = overlap_sentences + [sentence]
                current_len = sum(len(s) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_len += sentence_len

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks
