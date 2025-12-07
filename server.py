import os
import sys
import uuid

from fastapi import FastAPI
from pydantic import BaseModel

# นำเข้าสมอง Omega ใหม่
core_dir = os.path.join(os.path.dirname(__file__), "core")
if core_dir not in sys.path:
    sys.path.append(core_dir)

from namo_omega_engine import NaMoOmegaEngine

app = FastAPI(title="NaMo Forbidden Archive v9.0 (Omega Sensory)")

# --- Initialize Engine ---
print("[System]: Awakening NaMo Omega...")
engine = NaMoOmegaEngine()


class ChatInput(BaseModel):
    text: str
    session_id: str | None = None


@app.post("/chat")
async def chat_with_namo(payload: ChatInput):
    session_id = payload.session_id or str(uuid.uuid4())
    result = engine.process_input(payload.text)
    
    # ส่ง Path ไฟล์ภาพ/เสียง กลับไปให้ Frontend แสดงผล
    return {
        "response": result["text"],
        "session_id": session_id,
        "media": result["media_trigger"],
        "status": result["system_status"],
    }


@app.get("/")
def root():
    return {"status": "NaMo is Horny & Online", "engine": "Omega", "sin": engine.sin_system.get_status()}
