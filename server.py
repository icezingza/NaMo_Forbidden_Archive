import json
import uuid
from datetime import datetime

import requests
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import settings
from core.namo_omega_engine import NaMoOmegaEngine

app = FastAPI(title="NaMo Forbidden Archive v9.0 (Omega Sensory)")

# --- CORS + Static Media ---
cors_origins = [o.strip() for o in settings.cors_allow_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/media/visual", StaticFiles(directory="Visual_Scenes", check_dir=False), name="visual")
app.mount("/media/audio", StaticFiles(directory="Audio_Layers", check_dir=False), name="audio")
app.mount("/ui", StaticFiles(directory="web", html=True, check_dir=False), name="ui")

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
    if not settings.memory_logging:
        return
    memory_url = settings.memory_api_url
    if not memory_url:
        return
    payload = {
        "content": f"user: {user_text}\nassistant: {response_text}",
        "type": "contextual",
        "session_id": session_id,
    }
    headers = {}
    memory_key = settings.memory_api_key
    if memory_key:
        headers["x-api-key"] = memory_key
    try:
        requests.post(memory_url, json=payload, headers=headers, timeout=2)
    except requests.RequestException as exc:
        print(f"[MemoryLog]: Failed to store memory: {exc}")

def _parse_api_key_map(raw: str | None) -> dict[str, str]:
    if not raw:
        return {}
    mapping: dict[str, str] = {}
    for entry in raw.split(","):
        item = entry.strip()
        if not item:
            continue
        if ":" in item:
            key, plan = item.split(":", 1)
            mapping[key.strip()] = plan.strip() or "standard"
        else:
            mapping[item] = "standard"
    return mapping


def _resolve_plan(api_key: str | None) -> tuple[str, bool]:
    mapping = _parse_api_key_map(settings.namo_api_keys)
    default_plan = settings.namo_api_default_plan
    if not mapping:
        return default_plan, True
    if not api_key:
        return default_plan, False
    if api_key in mapping:
        return mapping[api_key], True
    return default_plan, False


def _log_usage(event: dict) -> None:
    path = settings.namo_usage_log_path
    if not path:
        return
    payload = dict(event)
    payload["timestamp"] = datetime.utcnow().isoformat() + "Z"
    try:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except OSError as exc:
        print(f"[UsageLog]: Failed to write usage event: {exc}")


@app.post("/chat")
async def chat_with_namo(payload: ChatInput, request: Request):
    session_id = payload.session_id or str(uuid.uuid4())
    result = engine.process_input(payload.text, session_id=session_id)

    base_url = settings.public_base_url
    if base_url:  # Use configured public URL if available
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


@app.post("/v1/chat")
async def chat_with_namo_v1(
    payload: ChatInput,
    request: Request,
    x_api_key: str | None = Header(default=None),
):
    plan, allowed = _resolve_plan(x_api_key)
    if not allowed and settings.namo_api_keys:
        raise HTTPException(status_code=401, detail="invalid_api_key")
    session_id = payload.session_id or str(uuid.uuid4())
    result = engine.process_input(payload.text, session_id=session_id)

    base_url = settings.public_base_url
    if base_url:  # Use configured public URL if available
        base_url = _normalize_base_url(base_url)
    else:
        base_url = _normalize_base_url(str(request.base_url))
    media = _normalize_media(result["media_trigger"], base_url)
    _store_memory_if_enabled(session_id, payload.text, result["text"])
    _log_usage(
        {
            "endpoint": "/v1/chat",
            "session_id": session_id,
            "plan": plan,
            "text_length": len(payload.text),
        }
    )

    return {
        "response": result["text"],
        "session_id": session_id,
        "media": media,
        "status": result["system_status"],
        "plan": plan,
    }


@app.get("/v1/health")
def health_check():
    return {"status": "ok", "engine": "Omega"}


@app.get("/")
def root():
    return {"status": "NaMo is Horny & Online", "engine": "Omega", "sin": engine.sin_system.get_status()}
