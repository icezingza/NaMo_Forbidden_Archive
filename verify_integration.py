import os

from core.rag_chunker import MicroChunker

VECTOR_DIR = "vector_db"
DB_PATH = os.path.join(VECTOR_DIR, "knowledge.index")
MODEL = "text-embedding-3-large"


def test_chunker_rules():
    chunker = MicroChunker(max_tokens=150, overlap_tokens=20)

    words = ["dhamma"] * 300
    sample_text = " ".join(words)

    chunks = chunker.split_text(sample_text)
    print(f"Total chunks generated: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        token_count = chunker.count_tokens(chunk)
        print(f"Chunk {i+1} length: {token_count} tokens")
        assert (
            100 <= token_count <= 150
        ), f"Chunk {i+1} has {token_count} tokens (violates 100-150 range)"

    print("Verification passed!")


if __name__ == "__main__":
    test_chunker_rules()
