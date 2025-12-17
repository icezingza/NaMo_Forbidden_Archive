import os
import uuid

import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from dotenv import load_dotenv

from core.namo_omega_engine import NaMoOmegaEngine

load_dotenv()

app = FastAPI(title="NaMo Forbidden Archive v9.0 (Omega Sensory)")

# --- CORS + Static Media ---
cors_origins_raw = os.getenv("CORS_ALLOW_ORIGINS", "*")
cors_origins = [o.strip() for o in cors_origins_raw.split(",") if o.strip()] or ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media/visual", StaticFiles(directory="Visual_Scenes", check_dir=False), name="visual")
app.mount("/media/audio", StaticFiles(directory="Audio_Layers", check_dir=False), name="audio")

# --- Initialize Engine ---
print("[System]: Awakening NaMo Omega...")
engine = NaMoOmegaEngine()


class ChatInput(BaseModel):
    text: str
    session_id: str | None = None


def _normalize_base_url(value: str) -> str:
    return value.rstrip("/")


def _resolve_media_url(path: str | None, base_url: str) -> str | None:
    if not path:
        return None
    if path.startswith("http://") or path.startswith("https://"):
        return path
    normalized = path.replace("\\", "/")
    if normalized.startswith("/"):
        return f"{base_url}{normalized}"
    if normalized.startswith("Visual_Scenes/"):
        rel = normalized[len("Visual_Scenes/") :]
        return f"{base_url}/media/visual/{rel}"
    if normalized.startswith("Audio_Layers/"):
        rel = normalized[len("Audio_Layers/") :]
        return f"{base_url}/media/audio/{rel}"
    return f"{base_url}/{normalized}"


def _normalize_media(media: dict, base_url: str) -> dict:
    if not media:
        return {}
    return {k: _resolve_media_url(v, base_url) for k, v in media.items()}


def _store_memory_if_enabled(session_id: str, user_text: str, response_text: str) -> None:
    if os.getenv("MEMORY_LOGGING", "0") != "1":
        return
    memory_url = os.getenv("MEMORY_API_URL")
    if not memory_url:
        return
    payload = {
        "content": f"user: {user_text}\nassistant: {response_text}",
        "type": "contextual",
        "session_id": session_id,
    }
    headers = {}
    memory_key = os.getenv("MEMORY_API_KEY")
    if memory_key:
        headers["x-api-key"] = memory_key
    try:
        requests.post(memory_url, json=payload, headers=headers, timeout=2)
    except requests.RequestException as exc:
        print(f"[MemoryLog]: Failed to store memory: {exc}")


@app.post("/chat")
async def chat_with_namo(payload: ChatInput, request: Request):
    session_id = payload.session_id or str(uuid.uuid4())
    result = engine.process_input(payload.text)

    base_url = os.getenv("PUBLIC_BASE_URL")
    if base_url:
        base_url = _normalize_base_url(base_url)
    else:
        base_url = _normalize_base_url(str(request.base_url))
    media = _normalize_media(result["media_trigger"], base_url)
    _store_memory_if_enabled(session_id, payload.text, result["text"])

    # ส่ง Path ไฟล์ภาพ/เสียง กลับไปให้ Frontend แสดงผล
    return {
        "response": result["text"],
        "session_id": session_id,
        "media": media,
        "status": result["system_status"],
    }


@app.get("/")
def root():
    return {"status": "NaMo is Horny & Online", "engine": "Omega", "sin": engine.sin_system.get_status()}
