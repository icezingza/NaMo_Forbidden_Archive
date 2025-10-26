import faiss, numpy as np, json
from openai import OpenAI

VECTOR_DIR = "vector_db"
DB_PATH = f"{VECTOR_DIR}/knowledge.index"
META_PATH = f"{VECTOR_DIR}/meta.json"
MODEL = "text-embedding-3-large"

client = OpenAI()

def query_knowledge(question, top_k=3):
    q_emb = client.embeddings.create(model=MODEL, input=question).data[0].embedding
    q_emb = np.array([q_emb]).astype("float32")
    index = faiss.read_index(DB_PATH)
    distances, indices = index.search(q_emb, top_k)
    meta = json.load(open(META_PATH, "r", encoding="utf-8"))
    return [meta[i] for i in indices[0] if i < len(meta)]

if __name__ == "__main__":
    q = input("ถามคำถาม: ")
    results = query_knowledge(q)
    print("ไฟล์ที่เกี่ยวข้องมากที่สุด:")
    for r in results:
        print(" -", r)
