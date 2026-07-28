import asyncio
import json
import os
from pathlib import Path

import numpy as np
from openai import AsyncOpenAI

# Gate faiss import behind NAMO_RAG_ENABLED to prevent Windows hangs during initialization
faiss = None
if os.getenv("NAMO_RAG_ENABLED") == "1":
    try:
        import faiss
    except Exception as exc:
        print(f"[Memory System]: Failed to import faiss: {exc}")
        faiss = None


class NaMoInfiniteMemory:
    """
    ระบบความจำนิรันดร์ NRE v5.0.0: Micro-chunking & Semantic Search
    รองรับการค้นหาที่แม่นยำสูงด้วยขนาดย่อย 100-150 tokens
    """

    def __init__(self, dataset_path: str | Path = "learning_set"):
        self.dataset_path = Path(dataset_path)
        self.vector_db = Path("vector_db")
        self.meta_path = self.vector_db / "meta.json"
        self.index_path = self.vector_db / "knowledge.index"
        self._faiss_index = None
        self._faiss_meta: list[dict] = []
        self.client = AsyncOpenAI()
        self.is_loaded = False
        self._load_lock = asyncio.Lock()

        self.SEARCH_THRESHOLD = 0.45  # Distance threshold สำหรับ FAISS

    def ingest_data(self) -> None:
        """Load the pre-built FAISS artifacts without generating fallback content."""
        self._load_vector_index()
        self.is_loaded = True

    def _load_vector_index(self) -> None:
        """โหลด FAISS index และ metadata"""
        self._faiss_index = None
        self._faiss_meta = []

        if faiss is None:
            print(
                "[Memory System]: FAISS RAG is disabled (NAMO_RAG_ENABLED != 1). Skipping index load."
            )
            return

        if not self.meta_path.exists() or not self.index_path.exists():
            print("[Memory System]: vector index or metadata is missing; retrieval unavailable.")
            return

        try:
            with self.meta_path.open(encoding="utf-8") as metadata_file:
                metadata = json.load(metadata_file)
            if not isinstance(metadata, list):
                raise ValueError("FAISS metadata must be a JSON array")

            index = faiss.read_index(str(self.index_path))
            if index.ntotal != len(metadata):
                raise ValueError(
                    f"FAISS index/metadata size mismatch: {index.ntotal} != {len(metadata)}"
                )

            self._faiss_meta = metadata
            self._faiss_index = index
            print(f"[Memory System]: โหลด vector_db สำเร็จ ({len(self._faiss_meta)} chunks)")
        except (OSError, ValueError, json.JSONDecodeError, RuntimeError) as exc:
            self._faiss_index = None
            self._faiss_meta = []
            print(f"[Memory System]: โหลด vector_db ไม่ได้: {exc}")

    async def _embed_with_retry(self, text: str, attempts: int = 3, delay: float = 1.0):
        """Async embedding generation with retry logic"""
        for attempt in range(1, attempts + 1):
            try:
                response = await self.client.embeddings.create(
                    model="text-embedding-3-large", input=text
                )
                return response.data[0].embedding
            except Exception as e:
                if attempt == attempts:
                    raise
                wait = delay * attempt
                print(
                    f"[Memory System]: retry embed {attempt}/{attempts} failed ({e}) -> wait {wait}s"
                )
                await asyncio.sleep(wait)

    async def _vector_search(self, user_input: str) -> str | None:
        """Async semantic search จาก vector_db"""
        if self._faiss_index is None or not self._faiss_meta:
            return None
        try:
            q_emb = await self._embed_with_retry(user_input)
        except Exception as e:
            print(f"[Memory System]: vector search fallback (embed error: {e})")
            return None

        q_emb = np.array([q_emb]).astype("float32")
        distances, indices = await asyncio.to_thread(self._faiss_index.search, q_emb, 1)

        # ตรวจสอบ threshold เพื่อความแม่นยำ
        if distances[0][0] > self.SEARCH_THRESHOLD:
            print(
                f"[Memory System]: Search result ignored (distance {distances[0][0]:.4f} > threshold)"
            )
            return None

        best_idx = int(indices[0][0])
        if 0 <= best_idx < len(self._faiss_meta):
            hit = self._faiss_meta[best_idx]
            snippet = hit.get("snippet", "")
            return f"{hit.get('file')}#{hit.get('chunk_id')}: {snippet}"
        return None

    async def retrieve_context(self, user_input: str) -> str | None:
        """Return the best semantic hit, or ``None`` when retrieval is unavailable."""
        if not self.is_loaded:
            async with self._load_lock:
                if not self.is_loaded:
                    await asyncio.to_thread(self.ingest_data)

        return await self._vector_search(user_input)
