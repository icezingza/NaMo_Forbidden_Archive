# Developer Quickstart

## Setup
```bash
cp .env.example .env          # fill in API keys as needed
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run Services
```bash
# API server (port 8000)
make run
# or: uvicorn server:app --host 0.0.0.0 --port 8000 --reload

# Memory service (port 8081, optional)
uvicorn memory_service:app --host 0.0.0.0 --port 8081 --reload

# Web client
cd web && python -m http.server 5173
```

## Basic Chat
```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-key" \
  -d '{"text":"สวัสดี","session_id":"demo"}'
```

## Select Engine per Request
```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"text":"สวัสดี","engine":"rinlada","session_id":"demo"}'
```

Available engines: `omega` (default), `rinlada`, `seraphina`, `dark`, `ultimate`.
List at runtime: `GET /v1/engines`

## Streaming (SSE)
```bash
curl -N -X POST http://localhost:8000/v1/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"text":"สวัสดี","session_id":"demo"}'
```

## API Keys (optional)
Set in `.env`:
```
NAMO_API_KEYS=key1:public,key2:creator
NAMO_API_DEFAULT_PLAN=public
NAMO_USAGE_LOG_PATH=usage_events.jsonl
```

When `NAMO_API_KEYS` is empty, the API is open (dev mode).

## Admin Session Management
Requires `ADMIN_SECRET` env var.

```bash
# List active sessions
curl http://localhost:8000/v1/admin/sessions \
  -H "X-Admin-Secret: your-secret"

# Clear a session from all engines
curl -X DELETE http://localhost:8000/v1/admin/sessions/demo \
  -H "X-Admin-Secret: your-secret"
```

## Media URLs
- Visual: `/media/visual/{path}`
- Audio: `/media/audio/{path}`
- TTS (generated): `/media/audio/tts/{uuid}.mp3`

Set `PUBLIC_BASE_URL` in `.env` to get absolute URLs in API responses.

## Common Make Commands
```bash
make setup       # install dependencies
make run         # start dev server
make test        # pytest -q
make lint        # ruff check
make format      # black check
make precommit   # lint + format + test
make audit       # pip-audit + bandit security scan
```

## Adding a New Engine
1. Create engine class in `core/`, inherit `BasePersonaEngine`
2. Implement `process_input(user_input, session_id)` — return the standard shape
3. Register in `server.py`: `_EngineRegistry.register("name", MyEngine)`
4. Add tests under `tests/`
