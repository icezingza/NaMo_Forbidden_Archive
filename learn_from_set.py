import json
import os
import shutil
import time
import zipfile
from typing import List, Tuple

import faiss
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

ZIP_PATH = "learning_set/set.zip"
VECTOR_DIR = "vector_db"
os.makedirs(VECTOR_DIR, exist_ok=True)
DB_PATH = os.path.join(VECTOR_DIR, "knowledge.index")
META_PATH = os.path.join(VECTOR_DIR, "meta.json")
MODEL = "text-embedding-3-large"
load_dotenv()
client = OpenAI()

extract_dir = os.path.join(VECTOR_DIR, "extracted")
os.makedirs(extract_dir, exist_ok=True)

CHUNK_SIZE = 800
CHUNK_OVERLAP = 200

if not os.path.exists(ZIP_PATH):
    print("⚠️ กรุณาวางไฟล์ set.zip ใน learning_set ก่อนรันสคริปต์นี้")
    exit()

# Step 1: Clean old extracts and unzip fresh files
if os.path.exists(extract_dir):
    shutil.rmtree(extract_dir)
os.makedirs(extract_dir, exist_ok=True)

with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
    zip_ref.extractall(extract_dir)

def chunk_text(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Split text into overlapping chunks to keep embeddings small and focused."""
    if not text:
        return []
    chunks: List[str] = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(text_length, start + chunk_size)
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def embed_with_retry(text: str, attempts: int = 3, delay: float = 1.0) -> List[float]:
    """Create embeddings with basic retry/backoff."""
    for attempt in range(1, attempts + 1):
        try:
            return client.embeddings.create(model=MODEL, input=text).data[0].embedding
        except Exception as e:
            if attempt == attempts:
                raise
            wait = delay * attempt
            print(f"[Retry] embedding failed (attempt {attempt}/{attempts}): {e} -> retrying in {wait}s")
            time.sleep(wait)
    return []


# Step 2: Read all files and prepare chunks
docs: List[Tuple[str, str]] = []  # (chunk_text, filename)
metadata: List[dict] = []

for root, _, files in os.walk(extract_dir):
    for f in files:
        p = os.path.join(root, f)
        try:
            text = open(p, encoding="utf-8").read()
        except Exception:
            try:
                text = open(p, encoding="latin1").read()
            except Exception as e:
                print(f"[skip] อ่านไฟล์ {p} ไม่ได้: {e}")
                continue

        chunks = chunk_text(text, CHUNK_SIZE, CHUNK_OVERLAP)
        for idx, chunk in enumerate(chunks):
            docs.append((chunk, f))
            metadata.append(
                {
                    "file": f,
                    "chunk_id": idx,
                    "snippet": chunk[:160],
                    "path": os.path.relpath(p, start=extract_dir),
                }
            )

if not docs:
    print("⚠️ ไม่พบข้อมูลสำหรับฝัง (ไม่มีไฟล์หรือไฟล์ว่าง)")
    exit()

# Step 3: Create embeddings
embeddings = []
for i, (doc, fname) in enumerate(docs, 1):
    print(f"Embedding {i}/{len(docs)}: {fname}")
    emb = embed_with_retry(doc)
    embeddings.append(emb)
embeddings = np.array(embeddings).astype("float32")

# Step 4: Build FAISS index
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)
faiss.write_index(index, DB_PATH)

# Step 5: Save metadata
json.dump(metadata, open(META_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

print(f"✅ Dark Knowledge base created with {len(docs)} chunks from {len(set(m['file'] for m in metadata))} files.")
