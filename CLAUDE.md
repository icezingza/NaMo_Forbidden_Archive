# CLAUDE.md — NaMo Forbidden Archive

This file describes the codebase for AI assistants (Claude Code and similar tools).

---

## Project Overview

NaMo Forbidden Archive is an experimental Thai-language AI persona system. It exposes a character named "NaMo" through multiple interfaces: a CLI, a FastAPI REST server, and a static web client. The system includes memory persistence, optional LLM-backed responses (OpenAI), text-to-speech (ElevenLabs), a FAISS-based knowledge base, and an optional Telegram bot.

**Primary language:** Python 3.11+
**API framework:** FastAPI + uvicorn
**Content:** The codebase contains NSFW/adult roleplay content by design. Some modules simulate explicit dialogue for mature audiences.

---

## Repository Layout

```
.
├── app.py                    # CLI entry: DarkNaMoSystem (dark_system.py engine)
├── main.py                   # CLI entry: CharacterProfile + emotion_parasite_engine
├── server.py                 # FastAPI app — NaMoOmegaEngine REST API
├── memory_service.py         # Standalone memory microservice (FastAPI, port 8081)
├── config.py                 # Pydantic Settings (reads .env)
├── learn_from_set.py         # Builds FAISS vector DB from learning_set/set.zip
├── query_learned_knowledge.py# Query the FAISS knowledge base
├── arousal_detector.py       # Top-level script / standalone arousal analysis
├── dialogue_manager.py       # Top-level dialogue manager script
├── rinlada_fusion.py         # Rinlada persona fusion script
├── seraphina.py              # Seraphina persona script
├── seraphina_ai_complete.py  # Full Seraphina AI module
├── voice_chatbot.py          # Voice chatbot entry point
│
├── core/                     # Core engine modules
│   ├── namo_omega_engine.py  # NaMoOmegaEngine (primary engine for server.py)
│   ├── character_profile.py  # CharacterProfile class (used by main.py)
│   ├── dark_system.py        # DarkNaMoSystem (used by app.py)
│   ├── fusion_brain.py       # Fusion brain logic
│   ├── generative_brain.py   # Generative response brain
│   ├── metaphysical_engines.py # MetaphysicalDialogueEngine
│   ├── namo_ultimate_engine.py # Ultimate engine variant
│   └── rag_memory_system.py  # RAG-based memory retrieval
│
├── adapters/                 # IO adapters (thin wrappers around external services)
│   ├── emotion.py            # EmotionAdapter — calls optional external emotion API
│   ├── memory.py             # MemoryAdapter — reads/writes memory_history.json
│   └── tts.py                # TTSAdapter — ElevenLabs text-to-speech
│
├── Core_Scripts/             # Experimental / auxiliary scripts
│   ├── emotion_parasite_engine.py  # Emotion analysis + reaction
│   ├── dark_dialogue_engine.py
│   ├── forbidden_behavior_core.py
│   ├── namo_auto_AI_reply.py       # Telegram auto-reply bot
│   └── ...
│
├── tests/                    # pytest test suite
├── docs/                     # Architecture and API documentation
│   ├── ARCHITECTURE.md
│   ├── API_SPEC.md
│   ├── DEVELOPER_QUICKSTART.md
│   └── NamoNexus_Integration_Handbook.md
│
├── web/                      # Static web client (served at /ui)
│   ├── index.html
│   ├── app.js
│   └── styles.css
│
├── Audio_Layers/             # Static audio assets (served at /media/audio)
├── Visual_Scenes/            # Static image assets (served at /media/visual)
├── learning_set/             # Input ZIPs for FAISS knowledge base
├── tools/                    # Utility scripts (check_api.py, telegram_check.py)
│
├── Dockerfile                # Docker image for server.py
├── Dockerfile.memory         # Docker image for memory_service.py
├── requirements.txt          # Runtime dependencies
├── requirements-dev.txt      # Dev/test dependencies
├── pyproject.toml            # Build metadata
├── Makefile                  # Common developer tasks
├── pytest.ini                # pytest configuration
└── .pre-commit-config.yaml   # Pre-commit hooks
```

---

## Core Architecture

### Entry Points

| Entry point | Engine used | Interface |
|---|---|---|
| `app.py` | `core/dark_system.py` → `DarkNaMoSystem` | CLI |
| `main.py` | `core/character_profile.py` → `CharacterProfile` | CLI |
| `server.py` | `core/namo_omega_engine.py` → `NaMoOmegaEngine` | REST API |
| `memory_service.py` | standalone | REST API (port 8081) |

### NaMoOmegaEngine (primary engine)

Located in `core/namo_omega_engine.py`. Composed of:

- **`SinSystem`** — tracks cumulative "sin points" and unlocks content tiers
- **`SensoryOverloadManager`** — maps arousal level → static audio/image asset paths
- **`PersonaOrchestrator`** — manages multiple active personas (NaMo, Sister, Mother)
- **`NaMoOmegaEngine`** — orchestrates the above; optionally calls OpenAI for LLM responses

`process_input(user_input, session_id)` is the main method. It returns:
```python
{
    "text": str,
    "media_trigger": {"image": str|None, "audio": str|None, "tts": str|None},
    "system_status": {"arousal": str, "sin_status": str, "active_personas": list}
}
```

### Adapters

Adapters in `adapters/` wrap external I/O and should be easy to mock in tests:

- `MemoryAdapter` — reads/writes `memory_history.json`
- `EmotionAdapter` — HTTP call to `EMOTION_API_URL` (optional)
- `TTSAdapter` — calls ElevenLabs API if `ELEVENLABS_API_KEY` is set; no-ops otherwise

### Configuration (`config.py`)

All configuration is via environment variables (or a `.env` file). The `Settings` class uses `pydantic-settings` with `case_sensitive=False` and `extra="ignore"`.

Key settings:

| Env var | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required for LLM mode and knowledge base |
| `NAMO_LLM_ENABLED` | auto | Enable LLM responses (`1`/`0`; auto-detects from `OPENAI_API_KEY`) |
| `NAMO_LLM_MODEL` | `gpt-4o-mini` | OpenAI model |
| `NAMO_LLM_TEMPERATURE` | `0.85` | LLM temperature |
| `NAMO_LLM_MAX_TOKENS` | `240` | LLM max tokens |
| `NAMO_LLM_MEMORY_TURNS` | `6` | Conversation turns kept in context |
| `ELEVENLABS_API_KEY` | — | ElevenLabs TTS |
| `ELEVENLABS_VOICE_ID` | — | ElevenLabs voice ID |
| `TELEGRAM_TOKEN` | — | Telegram bot token |
| `EMOTION_API_URL` | `http://localhost:8082/analyze` | External emotion service |
| `PUBLIC_BASE_URL` | — | Absolute base URL for media links in API responses |
| `CORS_ALLOW_ORIGINS` | `*` | Comma-separated CORS origins |
| `MEMORY_LOGGING` | `0` | Set `1` to log to memory service |
| `MEMORY_API_URL` | — | Memory service URL |
| `MEMORY_API_KEY` | — | Memory service API key (sent as `x-api-key`) |
| `NAMO_API_KEYS` | — | Comma-separated `key:plan` pairs for `/v1/chat` |
| `NAMO_USAGE_LOG_PATH` | — | JSONL file path for usage logging |
| `SAFETY_FILTER_ENABLED` | `true` | Safety filter toggle |
| `NSFW_ALLOWED` | `false` | NSFW content toggle |

---

## REST API Summary

Full spec: `docs/API_SPEC.md`

### `server.py` (port 8000)

| Method | Path | Description |
|---|---|---|
| GET | `/` | Health/status |
| POST | `/chat` | Chat with NaMo (no auth) |
| POST | `/v1/chat` | Chat with NaMo (optional `X-API-Key`) |
| GET | `/v1/health` | Health check |
| GET | `/media/visual/{path}` | Serve Visual_Scenes assets |
| GET | `/media/audio/{path}` | Serve Audio_Layers assets |
| GET | `/ui` | Static web client |

### `memory_service.py` (port 8081)

| Method | Path | Description |
|---|---|---|
| POST | `/store` | Store a memory record |
| POST | `/recall` | Retrieve memories by query |
| GET | `/health` | Health + record count |

---

## Development Workflows

### Setup

```bash
# macOS/Linux
cp .env.example .env        # edit with your keys
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install
```

Or use the Makefile:

```bash
make setup
```

### Running Services

```bash
# REST API (NaMoOmegaEngine)
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
# or
make run

# Memory microservice
uvicorn memory_service:app --host 0.0.0.0 --port 8081 --reload

# CLI (DarkNaMoSystem)
python app.py

# CLI (CharacterProfile)
python main.py

# Static web client
cd web && python -m http.server 5173
```

### Testing

```bash
pytest           # or: make test
pytest -q        # quiet output (same as make test)
pytest --cov --cov-report=term-missing   # with coverage
```

Test files are under `tests/`. `pytest.ini` sets `testpaths = tests`.

### Linting & Formatting

```bash
make lint        # ruff check
make format      # ruff --fix + black
make precommit   # run all pre-commit hooks
```

Tools configured:
- **ruff** — linter (also applies fixes)
- **black** — formatter
- **pyupgrade** — auto-upgrade to Python 3.11+ syntax
- **pre-commit-hooks** — trailing whitespace, end-of-file fixer

### Security Audit

```bash
make audit       # pip-audit + bandit
```

### Knowledge Base

```bash
# 1. Place set.zip in learning_set/
# 2. Build FAISS index (requires OPENAI_API_KEY)
python learn_from_set.py

# 3. Query
python query_learned_knowledge.py
```

---

## CI/CD

GitHub Actions workflow: `.github/workflows/ci.yml`

Runs on push/PR to `main`/`master`:
1. Install `requirements.txt` + `requirements-dev.txt`
2. `ruff check .`
3. `black --check .`
4. `pytest --cov`
5. `pip-audit -r requirements.txt`
6. `bandit -r .`

**Before pushing, ensure `make lint`, `make format`, and `pytest` all pass.**

---

## Docker

```bash
# Main API
docker build -t namo-api .
docker run -p 8000:8000 --env-file .env namo-api

# Memory service
docker build -f Dockerfile.memory -t namo-memory .
docker run -p 8081:8081 --env-file .env namo-memory
```

Cloud Run endpoint (private):
`https://namo-forbidden-archive-185116032835.asia-southeast1.run.app`

---

## Key Conventions

1. **Configuration via env/Settings only** — never hardcode API keys or secrets. All runtime config goes through `config.py` → `settings`.
2. **Adapters for external I/O** — external services (emotion API, TTS, memory) are accessed only through `adapters/`. This makes them mockable in tests.
3. **Core engines are pure Python** — `core/` modules should not have heavy I/O; adapters inject that.
4. **`extra="ignore"` in Settings** — unknown `.env` vars are silently ignored; this is intentional.
5. **Optional dependencies degrade gracefully** — TTSAdapter, EmotionAdapter, and LLM client all check for keys/availability at init and no-op if absent.
6. **Tests go in `tests/`** — not `test_main.py` at root (that file exists but `pytest.ini` points to `tests/`).
7. **Python 3.11+ syntax** — pyupgrade enforces this; use `str | None` unions, `match` statements, etc.
8. **NSFW content is intentional** — the codebase simulates adult dialogue. Do not add safety wrappers unless explicitly asked. The `SAFETY_FILTER_ENABLED` / `NSFW_ALLOWED` config flags control behavior at runtime.

---

## Important Files Reference

| File | Purpose |
|---|---|
| `config.py` | All app configuration (pydantic-settings) |
| `server.py` | FastAPI app + API key auth + media URL resolution |
| `core/namo_omega_engine.py` | Main engine: SinSystem, SensoryOverload, Personas, LLM |
| `memory_service.py` | Standalone memory microservice |
| `adapters/memory.py` | Local JSON memory read/write |
| `adapters/tts.py` | ElevenLabs TTS wrapper |
| `docs/ARCHITECTURE.md` | Component diagram (Mermaid) |
| `docs/API_SPEC.md` | Full request/response spec |
| `Makefile` | setup, lint, format, test, run, audit targets |
| `.pre-commit-config.yaml` | black, ruff, pyupgrade, whitespace hooks |
