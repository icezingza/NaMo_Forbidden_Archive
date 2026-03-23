# API Spec

## NaMo Omega API (`server.py`)

### GET `/`
Response:
```json
{
  "status": "NaMo is Online",
  "default_engine": "omega",
  "available_engines": ["omega", "rinlada", "seraphina", "dark", "ultimate"]
}
```

---

### POST `/chat`
Request:
```json
{
  "text": "สวัสดี",
  "session_id": "optional-session-id",
  "engine": "omega"
}
```
`engine` — optional; selects the persona engine for this request.
Defaults to `DEFAULT_ENGINE` env var (default `omega`).

Response:
```json
{
  "response": "NaMo: ...",
  "session_id": "generated-or-provided",
  "engine": "NaMoOmegaEngine",
  "media": {
    "image": "https://host/media/visual/...",
    "audio": "https://host/media/audio/...",
    "tts": "https://host/media/audio/tts/<uuid>.mp3"
  },
  "status": {
    "arousal": "50%",
    "sin_status": "[Corrupted Master] ...",
    "active_personas": ["NaMo"]
  }
}
```

---

### POST `/v1/chat`
Headers:
```
X-API-Key: optional-api-key
```

Request:
```json
{
  "text": "สวัสดี",
  "session_id": "optional-session-id",
  "engine": "omega"
}
```

Response:
```json
{
  "response": "NaMo: ...",
  "session_id": "generated-or-provided",
  "engine": "NaMoOmegaEngine",
  "media": {
    "image": "https://host/media/visual/...",
    "audio": "https://host/media/audio/...",
    "tts": "https://host/media/audio/tts/<uuid>.mp3"
  },
  "status": {
    "arousal": "50%",
    "sin_status": "[Corrupted Master] ...",
    "active_personas": ["NaMo"]
  },
  "plan": "public"
}
```

---

### POST `/v1/chat/stream`
Server-Sent Events endpoint.  Same request shape as `/v1/chat`.

Each event:
```
data: {"chunk": "<text token>", "session_id": "...", "plan": "...", "engine": "..."}
```
Final event:
```
data: {"done": true, "session_id": "...", "engine": "..."}
```

---

### GET `/v1/engines`
Lists all registered persona engines.

Response:
```json
{
  "engines": ["omega", "rinlada", "seraphina", "dark", "ultimate"],
  "default": "omega"
}
```

---

### GET `/v1/health`
Response:
```json
{
  "status": "ok",
  "engine": "omega"
}
```

---

### GET `/v1/status`
Returns status of all currently loaded engines (engines are loaded lazily —
only engines that have received at least one request appear here).

Response:
```json
{
  "omega": {
    "engine": "NaMoOmegaEngine",
    "status": "online",
    "active_sessions": 3,
    "llm_enabled": false,
    "rag_memory": false,
    "tts_online": false
  }
}
```

---

### GET `/v1/admin/sessions`
Lists active session IDs across all loaded engines.

Headers:
```
X-Admin-Secret: <ADMIN_SECRET>   # required if ADMIN_SECRET is set
```

Response:
```json
{
  "sessions": {
    "omega": ["session-abc", "session-xyz"],
    "dark": ["session-abc"]
  }
}
```

---

### DELETE `/v1/admin/sessions/{session_id}`
Purges a session from all loaded engines (clears in-memory state).

Headers:
```
X-Admin-Secret: <ADMIN_SECRET>   # required if ADMIN_SECRET is set
```

Response:
```json
{
  "session_id": "session-abc",
  "cleared_from": {
    "omega": true,
    "dark": true,
    "rinlada": false
  }
}
```

---

Media hosting:
- Visual files: `GET /media/visual/{path}`
- Audio files: `GET /media/audio/{path}`
- TTS files:   `GET /media/audio/tts/{uuid}.mp3`

Notes:
- `media` URLs are absolute when `PUBLIC_BASE_URL` is set, otherwise derived from the request base URL.
- `engine` field in request body selects the persona. All engines share the same session namespace.
- Configure `CORS_ALLOW_ORIGINS` if a separate web client needs cross-origin access.
- Optional API keys: `NAMO_API_KEYS` (comma-separated `key:plan` pairs).
- Default plan: `NAMO_API_DEFAULT_PLAN` when no key is provided or key list is empty.
- Usage events: `NAMO_USAGE_LOG_PATH` (JSONL).

---

## Memory Service (`memory_service.py`)

Standalone service (port 8081). `MemoryAdapter` in `adapters/memory.py` auto-forwards
writes to this service when `MEMORY_API_URL` is configured.

### POST `/store`
Request:
```json
{
  "content": "hello",
  "type": "contextual",
  "session_id": "session-123",
  "emotion_context": {
    "sentiment_score": 0.2,
    "emotion_type": "neutral",
    "intensity": 3
  },
  "dharma_tags": ["metta"]
}
```

Response:
```json
{
  "content": "hello",
  "type": "contextual",
  "session_id": "session-123",
  "emotion_context": {"sentiment_score": 0.2, "emotion_type": "neutral", "intensity": 3},
  "dharma_tags": ["metta"],
  "id": "mem_1730000000_0",
  "created_at": "2025-01-01T00:00:00"
}
```

### POST `/recall`
Request:
```json
{
  "query": "anything",
  "limit": 10
}
```

Response:
```json
[
  {
    "content": "previous",
    "type": "contextual",
    "session_id": "session-123",
    "emotion_context": null,
    "dharma_tags": null,
    "id": "mem_1730000000_0",
    "created_at": "2025-01-01T00:00:00"
  }
]
```

### GET `/health`
Response:
```json
{
  "status": "ok",
  "memory_records": 10
}
```
