import glob
import json
import os
import random
import time
from pathlib import Path

import faiss
import numpy as np
from openai import OpenAI


class NaMoInfiniteMemory:
    """
    ระบบความจำนิรันดร์: อ่านไฟล์นิยายจริงๆ ของคุณจาก learning_set
    """
    def __init__(self, dataset_path: str | Path = "learning_set"):
        self.dataset_path = Path(dataset_path)
        self.vector_db = Path("vector_db")
        self.meta_path = self.vector_db / "meta.json"
        self.index_path = self.vector_db / "knowledge.index"
        self._faiss_index = None
        self._faiss_meta: list[dict] = []
        self.client = OpenAI()
        self.memories = []
        self.is_loaded = False

    def ingest_data(self):
        """อ่านไฟล์ .txt และ .htm ทั้งหมดในโฟลเดอร์"""
        print(f"[Memory System]: กำลังแสกนพื้นที่ {self.dataset_path} ...")

        # ค้นหาไฟล์ทั้งหมด (รองรับโครงสร้างไฟล์ของคุณ)
        # หมายเหตุ: ในเครื่องจริงต้องแตก zip ออกมาไว้ที่ learning_set/ หรือ vector_db/extracted ก่อน
        extracted_dir = self.vector_db / "extracted"
        search_root = extracted_dir if extracted_dir.exists() else self.dataset_path

        txt_files = glob.glob(str(search_root / "**" / "*.txt"), recursive=True)
        htm_files = glob.glob(str(search_root / "**" / "*.htm"), recursive=True)
        all_files = txt_files + htm_files

        if not all_files:
            print("[Warning]: ไม่พบไฟล์นิยาย! กรุณาเช็ค path ว่าแตกไฟล์ zip หรือยัง")
            # ใส่ข้อมูลสำรองถ้าหาไฟล์ไม่เจอ
            self.memories = ["การเย็ดที่เร่าร้อนคือศิลปะ...", "เสียงครางกระเส่าทำให้คลั่ง..."]
            self._load_vector_index()
            return

        print(f"[Memory System]: พบไฟล์นิยาย {len(all_files)} เรื่อง กำลังดูดซับ...")

        for file_path in all_files:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    # ตัดเป็นท่อนๆ สั้นๆ เพื่อให้จำง่าย (Chunking)
                    chunks = [content[i:i+300] for i in range(0, len(content), 300)]
                    self.memories.extend(chunks)
            except Exception as e:
                print(f"อ่านไฟล์ {file_path} ไม่ได้: {e}")

        self._load_vector_index()
        self.is_loaded = True
        print(f"[Memory System]: จดจำข้อมูลเสร็จสิ้น! มีคลังความรู้ {len(self.memories)} fragments")

    def _load_vector_index(self):
        """โหลด FAISS index และ metadata ถ้ามี เพื่อใช้ semantic search"""
        if self.meta_path.exists() and self.index_path.exists():
            try:
                self._faiss_meta = json.load(open(self.meta_path, encoding="utf-8"))
                self._faiss_index = faiss.read_index(str(self.index_path))
                print(f"[Memory System]: โหลด vector_db สำเร็จ ({len(self._faiss_meta)} chunks)")
            except Exception as e:
                print(f"[Memory System]: โหลด vector_db ไม่ได้: {e}")

    def _embed_with_retry(self, text: str, attempts: int = 3, delay: float = 1.0):
        for attempt in range(1, attempts + 1):
            try:
                return (
                    self.client.embeddings.create(model="text-embedding-3-large", input=text)
                    .data[0]
                    .embedding
                )
            except Exception as e:
                if attempt == attempts:
                    raise
                wait = delay * attempt
                print(
                    f"[Memory System]: retry embed {attempt}/{attempts} failed ({e}) -> wait {wait}s"
                )
                time.sleep(wait)

    def _vector_search(self, user_input: str):
        """ค้นหา semantic จาก vector_db ถ้ามี"""
        if not self._faiss_index or not self._faiss_meta:
            return None
        try:
            q_emb = self._embed_with_retry(user_input)
        except Exception as e:
            print(f"[Memory System]: vector search fallback (embed error: {e})")
            return None

        q_emb = np.array([q_emb]).astype("float32")
        distances, indices = self._faiss_index.search(q_emb, 1)
        best_idx = int(indices[0][0])
        if 0 <= best_idx < len(self._faiss_meta):
            hit = self._faiss_meta[best_idx]
            snippet = hit.get("snippet", "")
            return f"{hit.get('file')}#{hit.get('chunk_id')}: {snippet}"
        return None

    def retrieve_context(self, user_input):
        """สุ่มหยิบความทรงจำที่เกี่ยวข้อง (หรือสุ่มมาเลยถ้ายังไม่ได้ทำ Vector Search)"""
        if not self.is_loaded:
            self.ingest_data()

        vector_hit = self._vector_search(user_input)
        if vector_hit:
            return vector_hit

        # Fallback: สุ่มฉากเสียวๆ มา 1 ฉากเพื่อเป็นแรงบันดาลใจ
        if self.memories:
            return random.choice(self.memories)
        return "..."
