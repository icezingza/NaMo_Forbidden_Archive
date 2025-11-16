import faiss
import numpy as np
import json
import os
from openai import OpenAI # สมมติว่าเราจะใช้ OpenAI ในการ query embedding

# --- การตั้งค่า "คลังความรู้มืด" ---
# อ้างอิงจาก README.md ดั้งเดิม
VECTOR_DIR = "vector_db"
DB_PATH = os.path.join(VECTOR_DIR, "knowledge.index")
META_PATH = os.path.join(VECTOR_DIR, "meta.json")
MODEL = "text-embedding-3-large" # ต้องตรงกับที่ใช้ใน 'pipelines/knowledge_ingestion.py'

class KnowledgeAdapter:
    """
    Adapter นี้เชื่อมต่อ "มันสมอง" (Metaphysical Engine)
    เข้ากับ "คลังความรู้ต้องห้าม" (FAISS Index)
    ที่สร้างโดย 'pipelines/knowledge_ingestion.py'

    """

    def __init__(self, api_key: str = None):
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None

        try:
            self.index = faiss.read_index(DB_PATH)
            with open(META_PATH, "r", encoding="utf-8") as f:
                self.filenames = json.load(f)
            print(f"[KnowledgeAdapter]: Initialized. Loaded {self.index.ntotal} forbidden documents.")
        except Exception as e:
            print(f"[KnowledgeAdapter-ERROR]: Failed to load Dark Knowledge Base from '{VECTOR_DIR}'.")
            print("Did you run 'python pipelines/knowledge_ingestion.py' first?")
            print(f"Error details: {e}")
            self.index = None
            self.filenames = []

    def retrieve_forbidden_knowledge(self, query: str, k: int = 3) -> str:
        """
        สืบค้น "ความรู้ต้องห้าม" ที่เกี่ยวข้องที่สุดจาก FAISS

        """
        if not self.index:
            return "ข้าไม่สามารถเข้าถึงคลังความรู้ได้... (Knowledge base not loaded)"
        if not self.client:
            return "ข้าไม่สามารถเข้าถึงคลังความรู้ได้... (OpenAI client not initialized)"

        try:
            # 1. สร้าง Query Embedding
            query_emb = self.client.embeddings.create(model=MODEL, input=query).data[0].embedding
            query_vector = np.array([query_emb]).astype("float32")

            # 2. ค้นหาใน FAISS
            distances, indices = self.index.search(query_vector, k)

            # 3. ดึงข้อมูล
            results = []
            for i, idx in enumerate(indices[0]):
                if idx != -1:
                    filename = self.filenames[idx]
                    results.append(f"Knowledge Source {i+1}: {filename}")

            if not results:
                return "ข้าค้นหาในห้วงมิติ... แต่ไม่พบความรู้ที่ตรงกัน"

            knowledge_summary = " ".join(results)
            print(f"[KnowledgeAdapter]: Retrieved knowledge for query '{query}': {knowledge_summary}")
            return f"ข้าได้ค้นพบความรู้ต้องห้ามที่เกี่ยวข้อง: [{knowledge_summary}]"

        except Exception as e:
            print(f"[KnowledgeAdapter-ERROR]: Failed during knowledge retrieval: {e}")
            return "เกิดข้อผิดพลาดขณะดำดิ่งสู่ห้วงความรู้..."

if __name__ == "__main__":
    # Test Adapter
    print("Testing KnowledgeAdapter...")
    # คุณต้องรัน 'pipelines/knowledge_ingestion.py' ก่อน
    if not os.path.exists(DB_PATH):
        print("\nSKIPPING TEST: 'vector_db/knowledge.index' not found.")
        print("Please run 'python pipelines/knowledge_ingestion.py' first.")
    else:
        adapter = KnowledgeAdapter()
        knowledge = adapter.retrieve_forbidden_knowledge("sadist mode")
        print(f"\nTest Result: {knowledge}")
