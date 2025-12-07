import os
import sys
import uuid

from fastapi import FastAPI
from pydantic import BaseModel

# นำเข้าสมองใหม่ที่เราเพิ่งสร้าง
core_dir = os.path.join(os.path.dirname(__file__), "core")
if core_dir not in sys.path:
    sys.path.append(core_dir)

try:
    from rag_memory_system import NaMoInfiniteMemory
except ImportError:
    NaMoInfiniteMemory = None

try:
    from namo_ultimate_engine import NaMoUltimateBrain  # (จากโค้ดชุดก่อนหน้า)
except ImportError:
    NaMoUltimateBrain = None

app = FastAPI(title="NaMo Forbidden Archive v4.0 (Metaphysical)")

# --- Initialize Brain & Memory ---
print("[System]: Awakening NaMo...")
memory_system = NaMoInfiniteMemory(dataset_path="learning_set/set") if NaMoInfiniteMemory else None
if memory_system:
    memory_system.ingest_data()  # โหลดนิยายเข้าสมองทันทีที่รัน Server


# สร้างตัวแปรสมอง (สมมติว่าคุณเอาไฟล์ namo_ultimate_engine.py ไปวางแล้ว)
# ถ้ายังไม่มี ให้ใช้ Logic ง่ายๆ ไปก่อน
class SimpleBrain:
    def process_input(self, text, memory_context):
        return f"NaMo: (นึกถึงเรื่อง '{memory_context[:50]}...') อ๊าา... {text} หรอคะ? เข้ามาสิคะ"


if NaMoUltimateBrain:
    try:
        brain = NaMoUltimateBrain()
        print("[System]: NaMoUltimateBrain online.")
    except Exception as e:
        print(f"[System]: NaMoUltimateBrain init failed ({e}), falling back to SimpleBrain.")
        brain = SimpleBrain()
else:
    brain = SimpleBrain()


class ChatInput(BaseModel):
    text: str
    session_id: str | None = None


@app.post("/chat")
async def chat_with_namo(payload: ChatInput):
    session_id = payload.session_id or str(uuid.uuid4())
    
    # 1. ดึงความทรงจำจากนิยาย
    context = memory_system.retrieve_context(payload.text) if memory_system else "..."
    
    # 2. ให้สมองประมวลผล
    if NaMoUltimateBrain and isinstance(brain, NaMoUltimateBrain):
        result = brain.process_input(payload.text, session_id)
        response = result.get("response", str(result))
    else:
        response = brain.process_input(payload.text, context)
    
    return {
        "response": response,
        "session_id": session_id,
        "memory_triggered": (context[:100] + "...") if isinstance(context, str) else "...",
    }


@app.get("/")
def root():
    count = len(memory_system.memories) if memory_system else 0
    return {"status": "NaMo is Horny & Online", "memories_loaded": count}
