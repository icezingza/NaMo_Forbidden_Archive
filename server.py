import asyncio
import json
import time
import uuid
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime

import requests
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import settings
from core.base_persona import BasePersonaEngine
from core.dark_system import DarkNaMoSystem
from core.namo_omega_engine import NaMoOmegaEngine
from core.namo_ultimate_engine import NaMoUltimateBrain
from rinlada_fusion import RinladaAI
from seraphina_ai_complete import SeraphinaAI


# ---------------------------------------------------------------------------
# Rate limiter — sliding-window, keyed by client IP
# ---------------------------------------------------------------------------
class _RateLimiter:
    def __init__(self, max_calls: int, period_seconds: float) -> None:
        self._max = max_calls
        self._period = period_seconds
        self._buckets: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        self._buckets[key] = [t for t in self._buckets[key] if now - t < self._period]
        if len(self._buckets[key]) >= self._max:
            return False
        self._buckets[key].append(now)
        return True


# ---------------------------------------------------------------------------
# Session TTL — track last-active timestamp and evict stale sessions
# ---------------------------------------------------------------------------
_session_timestamps: dict[str, float] = {}


def _touch_session(session_id: str) -> None:
    _session_timestamps[session_id] = time.time()


def cleanup_expired_sessions(ttl_seconds: float | None = None) -> int:
    """Remove sessions older than ttl_seconds from all loaded engines.

    Returns the number of sessions evicted.
    """
    effective_ttl = ttl_seconds if ttl_seconds is not None else float(settings.session_ttl_seconds)
    now = time.time()
    expired = [sid for sid, ts in list(_session_timestamps.items()) if now - ts > effective_ttl]
    for sid in expired:
        _session_timestamps.pop(sid, None)
        for inst in _EngineRegistry._instances.values():
            for attr in _STATE_ATTRS:
                store = getattr(inst, attr, None)
                if isinstance(store, dict):
                    store.pop(sid, None)
    return len(expired)


async def _session_cleanup_loop() -> None:
    while True:
        await asyncio.sleep(settings.session_ttl_seconds)
        cleanup_expired_sessions()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    task = asyncio.create_task(_session_cleanup_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(title="NaMo Forbidden Archive v9.0 (Omega Sensory)", lifespan=lifespan)

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


# ---------------------------------------------------------------------------
# Engine Registry — lazy-loads persona engines on first request
# ---------------------------------------------------------------------------
class _EngineRegistry:
    """Lazy singleton registry for all persona engines."""

    _constructors: dict[str, type] = {}
    _instances: dict[str, BasePersonaEngine] = {}

    @classmethod
    def register(cls, name: str, engine_cls: type) -> None:
        cls._constructors[name] = engine_cls

    @classmethod
    def get(cls, name: str) -> BasePersonaEngine:
        if name not in cls._constructors:
            raise HTTPException(
                status_code=400,
                detail=f"unknown_engine '{name}'. available: {cls.available()}",
            )
        if name not in cls._instances:
            print(f"[EngineRegistry]: loading '{name}'...")
            cls._instances[name] = cls._constructors[name]()
        return cls._instances[name]

    @classmethod
    def available(cls) -> list[str]:
        return list(cls._constructors.keys())


# Register engines — omega loads immediately; others are lazy
_EngineRegistry.register("omega", NaMoOmegaEngine)
_EngineRegistry.register("rinlada", RinladaAI)
_EngineRegistry.register("seraphina", SeraphinaAI)
_EngineRegistry.register("dark", DarkNaMoSystem)
_EngineRegistry.register("ultimate", NaMoUltimateBrain)

# Pre-load default engine at startup
print("[System]: Awakening NaMo Omega...")
engine = _EngineRegistry.get(settings.default_engine)

# Rate limiter instance — initialized from settings
_rate_limiter = _RateLimiter(
    max_calls=settings.rate_limit_calls,
    period_seconds=float(settings.rate_limit_period),
)


class ChatInput(BaseModel):
    text: str
    session_id: str | None = None
    engine: str | None = None  # override engine per request; default from settings


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


def _store_memory_if_enabled(
    session_id: str, user_text: str, response_text: str, system_status: dict | None = None
) -> None:
    if not settings.memory_logging:
        return
    memory_url = settings.memory_api_url
    if not memory_url:
        return
    payload = {
        "content": f"user: {user_text}\nassistant: {response_text}",
        "type": "contextual",
        "session_id": session_id,
        "sin_stats": system_status,
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


def _get_base_url(request: Request) -> str:
    base_url = settings.public_base_url
    return _normalize_base_url(base_url if base_url else str(request.base_url))


def _resolve_engine_from_payload(payload: ChatInput) -> BasePersonaEngine:
    name = payload.engine or settings.default_engine
    return _EngineRegistry.get(name)


@app.post("/chat")
async def chat_with_namo(payload: ChatInput, request: Request):
    active_engine = _resolve_engine_from_payload(payload)
    session_id = payload.session_id or str(uuid.uuid4())
    _touch_session(session_id)
    result = active_engine.process_input(payload.text, session_id=session_id)

    media = _normalize_media(result["media_trigger"], _get_base_url(request))
    _store_memory_if_enabled(session_id, payload.text, result["text"], result["system_status"])

    return {
        "response": result["text"],
        "session_id": session_id,
        "media": media,
        "status": result["system_status"],
        "engine": active_engine.__class__.__name__,
    }


@app.post("/v1/chat")
async def chat_with_namo_v1(
    payload: ChatInput,
    request: Request,
    x_api_key: str | None = Header(default=None),
):
    client_ip = request.client.host if request.client else "unknown"
    if not _rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="rate_limit_exceeded")

    plan, allowed = _resolve_plan(x_api_key)
    if not allowed and settings.namo_api_keys:
        raise HTTPException(status_code=401, detail="invalid_api_key")

    active_engine = _resolve_engine_from_payload(payload)
    session_id = payload.session_id or str(uuid.uuid4())
    _touch_session(session_id)
    result = active_engine.process_input(payload.text, session_id=session_id)

    media = _normalize_media(result["media_trigger"], _get_base_url(request))
    _store_memory_if_enabled(session_id, payload.text, result["text"], result["system_status"])
    _log_usage(
        {
            "endpoint": "/v1/chat",
            "session_id": session_id,
            "plan": plan,
            "engine": active_engine.__class__.__name__,
            "text_length": len(payload.text),
        }
    )

    return {
        "response": result["text"],
        "session_id": session_id,
        "media": media,
        "status": result["system_status"],
        "plan": plan,
        "engine": active_engine.__class__.__name__,
    }


@app.post("/v1/chat/stream")
async def chat_stream(
    payload: ChatInput,
    request: Request,
    x_api_key: str | None = Header(default=None),
):
    client_ip = request.client.host if request.client else "unknown"
    if not _rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="rate_limit_exceeded")

    plan, allowed = _resolve_plan(x_api_key)
    if not allowed and settings.namo_api_keys:
        raise HTTPException(status_code=401, detail="invalid_api_key")

    active_engine = _resolve_engine_from_payload(payload)
    session_id = payload.session_id or str(uuid.uuid4())
    _touch_session(session_id)
    engine_name = active_engine.__class__.__name__

    queue: asyncio.Queue[str | None] = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def _produce() -> None:
        full_text: list[str] = []
        try:
            for chunk in active_engine.stream_input(payload.text, session_id=session_id):
                full_text.append(chunk)
                data = json.dumps(
                    {"chunk": chunk, "session_id": session_id, "plan": plan, "engine": engine_name},
                    ensure_ascii=False,
                )
                loop.call_soon_threadsafe(queue.put_nowait, f"data: {data}\n\n")
        except Exception as exc:
            err = json.dumps({"error": str(exc)}, ensure_ascii=False)
            loop.call_soon_threadsafe(queue.put_nowait, f"data: {err}\n\n")
        finally:
            assembled = "".join(full_text)
            _store_memory_if_enabled(session_id, payload.text, assembled)
            _log_usage(
                {
                    "endpoint": "/v1/chat/stream",
                    "session_id": session_id,
                    "plan": plan,
                    "engine": engine_name,
                    "text_length": len(payload.text),
                }
            )
            loop.call_soon_threadsafe(queue.put_nowait, None)  # sentinel

    async def _event_stream():
        loop.run_in_executor(None, _produce)
        while True:
            item = await queue.get()
            if item is None:
                done_msg = json.dumps(
                    {"done": True, "session_id": session_id, "engine": engine_name}
                )  # noqa: E501
                yield f"data: {done_msg}\n\n"
                break
            yield item

    return StreamingResponse(_event_stream(), media_type="text/event-stream")


@app.get("/v1/engines")
def list_engines():
    """List all registered persona engines."""
    return {"engines": _EngineRegistry.available(), "default": settings.default_engine}


@app.get("/v1/health")
def health_check():
    return {"status": "ok", "engine": settings.default_engine}


@app.get("/v1/status")
def engine_status():
    """Status of all loaded engines."""
    return {
        name: _EngineRegistry._instances[name].get_status() for name in _EngineRegistry._instances
    }


def _assert_admin(secret: str | None) -> None:
    """Raise 403 if ADMIN_SECRET is configured and the header does not match."""
    if settings.admin_secret and secret != settings.admin_secret:
        raise HTTPException(status_code=403, detail="forbidden")


_STATE_ATTRS = ("_session_states", "_session_arousal", "_session_intensity", "session_history")


def _collect_session_keys(eng_instance: BasePersonaEngine) -> list[str]:
    """Return all known session IDs tracked by an engine instance."""
    keys: set[str] = set()
    for attr in _STATE_ATTRS:
        store = getattr(eng_instance, attr, None)
        if isinstance(store, dict):
            keys.update(store.keys())
    return sorted(keys)


@app.get("/v1/admin/sessions")
def list_sessions(x_admin_secret: str | None = Header(default=None)):
    """List active sessions for all loaded engines.

    Protected by X-Admin-Secret header (requires ADMIN_SECRET env var).
    When ADMIN_SECRET is not set, the endpoint is open (dev mode).
    """
    _assert_admin(x_admin_secret)
    return {
        "sessions": {
            name: _collect_session_keys(inst) for name, inst in _EngineRegistry._instances.items()
        }
    }


@app.delete("/v1/admin/sessions/{session_id}")
def clear_session(
    session_id: str,
    x_admin_secret: str | None = Header(default=None),
):
    """Purge a session from all loaded engines.

    Removes the session from every per-session state store
    (_session_states, _session_arousal, _session_intensity, session_history).
    Returns which engines actually had data for that session.
    """
    _assert_admin(x_admin_secret)
    cleared: dict[str, bool] = {}
    for name, inst in _EngineRegistry._instances.items():
        removed = False
        for attr in _STATE_ATTRS:
            store = getattr(inst, attr, None)
            if isinstance(store, dict) and session_id in store:
                del store[session_id]
                removed = True
        cleared[name] = removed
    return {"session_id": session_id, "cleared_from": cleared}


@app.get("/")
def root():
    return {
        "status": "NaMo is Online",
        "default_engine": settings.default_engine,
        "available_engines": _EngineRegistry.available(),
    }
