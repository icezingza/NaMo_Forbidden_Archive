import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath("."))

def build_vector_meta_from_lorebook():
    """
    Ingests Sex_Positions_Kinks_SlowBurn_TH_v10.json into the NaMo Vector DB metadata
    format (vector_db/meta.json) so NaMo's RAG system can query intimate position chunks.
    """
    print("[Ingest Lorebook]: Reading Slow-Burn Lorebook JSON...")
    lorebook_path = Path("slow-burn-thai-erotic-FULL/full-package/Sex_Positions_Kinks_SlowBurn_TH_v10.json")
    if not lorebook_path.exists():
        lorebook_path = Path(".agents/skills/slow-burn-thai-erotic/references/lorebook-positions.json")

    with open(lorebook_path, encoding="utf-8") as f:
        entries = json.load(f)

    print(f"[Ingest Lorebook]: Loaded {len(entries)} entries.")

    vector_db_dir = Path("vector_db")
    vector_db_dir.mkdir(exist_ok=True)
    meta_path = vector_db_dir / "meta.json"

    existing_meta = []
    if meta_path.exists():
        try:
            with open(meta_path, encoding="utf-8") as f:
                existing_meta = json.load(f)
        except Exception:
            existing_meta = []

    # Format lorebook entries as metadata chunks
    new_chunks = []
    for idx, entry in enumerate(entries):
        comment = entry.get("comment", f"Entry-{idx}")
        content = entry.get("content", "")
        keys = entry.get("key", [])
        chunk = {
            "chunk_id": f"lorebook_{entry.get('id', idx)}",
            "file": "lorebook-positions.json",
            "title": comment,
            "keys": keys,
            "snippet": f"[{comment}] (Triggers: {', '.join(keys[:5])}) {content}"
        }
        new_chunks.append(chunk)

    # Merge or write meta.json
    combined = existing_meta + [c for c in new_chunks if c["chunk_id"] not in [e.get("chunk_id") for e in existing_meta]]

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)

    print(f"[Ingest Lorebook]: Successfully wrote {len(combined)} chunks to {meta_path}")

if __name__ == "__main__":
    build_vector_meta_from_lorebook()
