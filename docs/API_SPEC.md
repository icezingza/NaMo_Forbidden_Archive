# API Spec

## NaMo Omega API (`server.py`)

### GET `/`
Response:
```json
{
  "status": "NaMo is Horny & Online",
  "engine": "Omega",
  "sin": "[Innocent Soul] บาปสะสม: 0 | ปลดล็อก: "
}
```

### POST `/chat`
Request:
```json
{
  "text": "สวัสดี",
  "session_id": "optional-session-id"
}
```

Response:
```json
{
  "response": "NaMo: ...",
  "session_id": "generated-or-provided",
  "media": {
    "image": "https://host/media/visual/...",
    "audio": "https://host/media/audio/...",
    "tts": "https://host/media/audio/generated/..."
  },
  "status": {
    "arousal": "50% (MAX)",
    "sin_status": "[Corrupted Master] ...",
    "active_personas": ["NaMo"]
  }
}
```

### POST `/v1/chat`
Headers:
```
X-API-Key: optional-api-key
```

Request:
```json
{
  "text": "สวัสดี",
  "session_id": "optional-session-id"
}
```

Response:
```json
{
  "response": "NaMo: ...",
  "session_id": "generated-or-provided",
  "media": {
    "image": "https://host/media/visual/...",
    "audio": "https://host/media/audio/...",
    "tts": "https://host/media/audio/generated/..."
  },
  "status": {
    "arousal": "50% (MAX)",
    "sin_status": "[Corrupted Master] ...",
    "active_personas": ["NaMo"]
  },
  "plan": "public"
}
```

Media hosting:
- Visual files: `GET /media/visual/{path}`
- Audio files: `GET /media/audio/{path}`

Notes:
- `media` URLs may be absolute if `PUBLIC_BASE_URL` is set, otherwise they are derived from the request base URL.
- Configure `CORS_ALLOW_ORIGINS` if a separate web client needs cross-origin access.
- Optional API keys can be configured via `NAMO_API_KEYS` (comma-separated `key:plan` pairs).
- Default plan is `NAMO_API_DEFAULT_PLAN` when no key is provided or when the key list is empty.
- Usage events can be logged with `NAMO_USAGE_LOG_PATH` (JSONL).

### GET `/v1/health`
Response:
```json
{
  "status": "ok",
  "engine": "Omega"
}
```

## Memory Service (`memory_service.py`)

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
  "emotion_context": {
    "sentiment_score": 0.2,
    "emotion_type": "neutral",
    "intensity": 3
  },
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
