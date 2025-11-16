import json
import os
import zipfile

import faiss
import numpy as np
from openai import OpenAI

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
    print("⚠️ กรุณาวางไฟล์ set.zip ใน learning_set ก่อนรันสคริปต์นี้")
    exit()

# Step 1: Extract files

with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
    zip_ref.extractall(extract_dir)

# Step 2: Read all files

docs, filenames = [], []
for root, _, files in os.walk(extract_dir):
    for f in files:
        p = os.path.join(root, f)
        try:
            text = open(p, encoding="utf-8").read()
        except Exception:
            text = open(p, encoding="latin1").read()
        docs.append(text)
        filenames.append(f)

# Step 3: Create embeddings

embeddings = []
for i, doc in enumerate(docs, 1):
    print(f"Embedding {i}/{len(docs)}: {filenames[i-1]}")
    emb = client.embeddings.create(model=MODEL, input=doc).data[0].embedding
    embeddings.append(emb)
embeddings = np.array(embeddings).astype("float32")

# Step 4: Build FAISS index

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)
faiss.write_index(index, DB_PATH)

# Step 5: Save metadata

json.dump(filenames, open(META_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print(f"✅ Dark Knowledge base created with {len(docs)} documents.")
