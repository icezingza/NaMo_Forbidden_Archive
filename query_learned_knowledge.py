import json
import os
import time

import faiss
import numpy as np
from openai import OpenAI

VECTOR_DIR = "vector_db"
DB_PATH = f"{VECTOR_DIR}/knowledge.index"
META_PATH = f"{VECTOR_DIR}/meta.json"
MODEL = "text-embedding-3-large"
client = OpenAI()


def embed_with_retry(text: str, attempts: int = 3, delay: float = 1.0):
    for attempt in range(1, attempts + 1):
        try:
            return client.embeddings.create(model=MODEL, input=text).data[0].embedding
        except Exception as e:
            if attempt == attempts:
                raise
            wait = delay * attempt
            print(f"[Retry] embedding failed (attempt {attempt}/{attempts}): {e} -> retrying in {wait}s")
            time.sleep(wait)


def query_knowledge(question, top_k=3):
    if not os.path.exists(DB_PATH) or not os.path.exists(META_PATH):
        raise FileNotFoundError("ไม่พบฐานความรู้ใน vector_db/ โปรดรัน learn_from_set.py ก่อน")

    q_emb = embed_with_retry(question)
    q_emb = np.array([q_emb]).astype("float32")
    index = faiss.read_index(DB_PATH)
    distances, indices = index.search(q_emb, top_k)
    meta = json.load(open(META_PATH, encoding="utf-8"))
    results = []
    for i, dist in zip(indices[0], distances[0]):
        if i < len(meta):
            item = meta[i]
            item["score"] = float(dist)
            results.append(item)
    return results


if __name__ == "__main__":
    q = input("ถามคำถาม: ")
    results = query_knowledge(q)
    print("ไฟล์ที่เกี่ยวข้องมากที่สุด:")
    for r in results:
        print(f" - {r['file']}#{r['chunk_id']} :: {r['snippet']}")
