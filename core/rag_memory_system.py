import asyncio
import glob
import json
import os
import random
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
        self.client = AsyncOpenAI()  # เปลี่ยนเป็น Async ตามมาตรฐาน NRE
        self.memories: list[str] = []
        self.is_loaded = False
        
        # Configuration สำหรับ Micro-chunking
        self.CHUNK_SIZE = 150  # tokens (approx)
        self.CHUNK_OVERLAP = 20
        self.SEARCH_THRESHOLD = 0.45  # Distance threshold สำหรับ FAISS

    def ingest_data(self):
        """อ่านไฟล์ .txt และ .htm ทั้งหมดในโฟลเดอร์ และทำ Micro-chunking"""
        print(f"[Memory System]: กำลังแสกนพื้นที่ {self.dataset_path} ...")

        extracted_dir = self.vector_db / "extracted"
        search_root = extracted_dir if extracted_dir.exists() else self.dataset_path

        txt_files = glob.glob(str(search_root / "**" / "*.txt"), recursive=True)
        htm_files = glob.glob(str(search_root / "**" / "*.htm"), recursive=True)
        all_files = txt_files + htm_files

        if not all_files:
            print("[Warning]: ไม่พบไฟล์นิยาย! กรุณาเช็ค path ว่าแตกไฟล์ zip หรือยัง")
            self.memories = ["การเย็ดที่เร่าร้อนคือศิลปะ...", "เสียงครางกระเส่าทำให้คลั่ง..."]
            self._load_vector_index()
            return

        print(f"[Memory System]: พบไฟล์นิยาย {len(all_files)} เรื่อง กำลังทำ Micro-chunking...")

        for file_path in all_files:
            try:
                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    # Micro-chunking strategy: 100-150 tokens overlap
                    # Simple char-based approximation for now, should be token-based in production
                    stride = self.CHUNK_SIZE - self.CHUNK_OVERLAP
                    chunks = [content[i : i + self.CHUNK_SIZE] for i in range(0, len(content), stride)]
                    self.memories.extend(chunks)
            except Exception as e:
                print(f"อ่านไฟล์ {file_path} ไม่ได้: {e}")

        self._load_vector_index()
        self.is_loaded = True
        print(f"[Memory System]: จดจำข้อมูลเสร็จสิ้น! มีคลังความรู้ {len(self.memories)} micro-fragments")

    def _load_vector_index(self):
        """โหลด FAISS index และ metadata"""
        if faiss is None:
            print("[Memory System]: FAISS RAG is disabled (NAMO_RAG_ENABLED != 1). Skipping index load.")
            return

        if self.meta_path.exists() and self.index_path.exists():
            try:
                self._faiss_meta = json.load(open(self.meta_path, encoding="utf-8"))
                self._faiss_index = faiss.read_index(str(self.index_path))
                print(f"[Memory System]: โหลด vector_db สำเร็จ ({len(self._faiss_meta)} chunks)")
            except Exception as e:
                print(f"[Memory System]: โหลด vector_db ไม่ได้: {e}")

    async def _embed_with_retry(self, text: str, attempts: int = 3, delay: float = 1.0):
        """Async embedding generation with retry logic"""
        for attempt in range(1, attempts + 1):
            try:
                response = await self.client.embeddings.create(
                    model="text-embedding-3-large", 
                    input=text
                )
                return response.data[0].embedding
            except Exception as e:
                if attempt == attempts:
                    raise
                wait = delay * attempt
                print(f"[Memory System]: retry embed {attempt}/{attempts} failed ({e}) -> wait {wait}s")
                await asyncio.sleep(wait)

    async def _vector_search(self, user_input: str) -> str | None:
        """Async semantic search จาก vector_db"""
        if not self._faiss_index or not self._faiss_meta:
            return None
        try:
            q_emb = await self._embed_with_retry(user_input)
        except Exception as e:
            print(f"[Memory System]: vector search fallback (embed error: {e})")
            return None

        q_emb = np.array([q_emb]).astype("float32")
        distances, indices = self._faiss_index.search(q_emb, 1)
        
        # ตรวจสอบ threshold เพื่อความแม่นยำ
        if distances[0][0] > self.SEARCH_THRESHOLD:
            print(f"[Memory System]: Search result ignored (distance {distances[0][0]:.4f} > threshold)")
            return None

        best_idx = int(indices[0][0])
        if 0 <= best_idx < len(self._faiss_meta):
            hit = self._faiss_meta[best_idx]
            snippet = hit.get("snippet", "")
            return f"{hit.get('file')}#{hit.get('chunk_id')}: {snippet}"
        return None

    async def retrieve_context(self, user_input: str) -> str:
        """Async context retrieval"""
        if not self.is_loaded:
            # Sync call for initial ingestion is acceptable during init or first run
            # but ideally should be pre-loaded
            self.ingest_data()

        vector_hit = await self._vector_search(user_input)
        if vector_hit:
            return vector_hit

        # Fallback: สุ่มฉากที่น่าสนใจมา 1 ฉาก
        if self.memories:
            return random.choice(self.memories)
        return "..."
