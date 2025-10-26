import os, zipfile, json
from openai import OpenAI
import numpy as np, faiss

ZIP_PATH = "learning_set/set.zip"
VECTOR_DIR = "vector_db"
os.makedirs(VECTOR_DIR, exist_ok=True)
DB_PATH = os.path.join(VECTOR_DIR, "knowledge.index")
META_PATH = os.path.join(VECTOR_DIR, "meta.json")
MODEL = "text-embedding-3-large"
client = OpenAI()

extract_dir = os.path.join(VECTOR_DIR, "extracted")
os.makedirs(extract_dir, exist_ok=True)
if not os.path.exists(ZIP_PATH):
    print("⚠️ กรุณาวาง set.zip ใน learning_set ก่อนรันสคริปต์นี้")
    exit()

with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
    zip_ref.extractall(extract_dir)

docs, filenames = [], []
for root, _, files in os.walk(extract_dir):
    for f in files:
        p = os.path.join(root, f)
        try:
            text = open(p, "r", encoding="utf-8").read()
        except:
            text = open(p, "r", encoding="latin1").read()
        docs.append(text)
        filenames.append(f)

embeddings = []
for doc in docs:
    emb = client.embeddings.create(model=MODEL, input=doc).data[0].embedding
    embeddings.append(emb)
embeddings = np.array(embeddings).astype("float32")

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)
faiss.write_index(index, DB_PATH)
json.dump(filenames, open(META_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print(f"✅ Dark Knowledge base created with {len(docs)} documents.")
