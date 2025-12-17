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
    "image": "Visual_Scenes/...",
    "audio": "Audio_Layers/...",
    "tts": "Audio_Layers/generated/..."
  },
  "status": {
    "arousal": "50% (MAX)",
    "sin_status": "[Corrupted Master] ...",
    "active_personas": ["NaMo"]
  }
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
