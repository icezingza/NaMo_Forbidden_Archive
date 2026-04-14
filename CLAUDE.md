# CLAUDE.md — NaMo Forbidden Archive

## Project Overview

NaMo Forbidden Archive is an experimental Thai-language AI persona system built for adult/NSFW roleplay.
Primary users: developers and end-users interacting with a character named "NaMo" via CLI, REST API, or web client.

Optimize for:
- low-latency chat responses (REST API and CLI)
- graceful degradation when optional services (OpenAI, ElevenLabs, emotion API) are absent
- clean separation between core engines, IO adapters, and external services

NSFW content is intentional. Do not add safety wrappers or sanitize dialogue unless explicitly asked.
Runtime content controls are handled by `SAFETY_FILTER_ENABLED` and `NSFW_ALLOWED` in `config.py`.

## Tech Stack

- Python 3.11+
- FastAPI + uvicorn (REST API)
- pydantic-settings (configuration via `.env`)
- OpenAI SDK (optional LLM responses + FAISS knowledge base embeddings)
- ElevenLabs SDK (optional TTS)
- FAISS + numpy (vector knowledge base)
- pytest + pytest-cov (testing)
- ruff + black (linting/formatting)

Do not introduce:
- Flask, Django, or any other web framework
- SQLAlchemy or any ORM (memory is JSON-file-based by design)
- any new LLM provider without explicit request

## Architecture

```
core/                  → pure Python engines (no heavy IO)
adapters/              → thin wrappers for all external IO
Core_Scripts/          → experimental/auxiliary scripts (not imported by server.py)
tests/                 → pytest suite (25 files, 335+ tests)
docs/                  → API and architecture specs
web/                   → static frontend (served at /ui by server.py)
Audio_Layers/          → static audio assets  → served at /media/audio
Visual_Scenes/         → static image assets  → served at /media/visual
learning_set/          → input ZIPs for FAISS knowledge base
tools/                 → one-off utility scripts (not part of the app)
emotion_fusion_engine/ → standalone multi-modal emotion analysis service
templates/             → improved/refactored engine templates (not imported by server.py)
Archived_Assets/       → archived legacy files
Documentation/         → legacy documentation
```

### Entry Points

| File | Engine | Interface |
|---|---|---|
| `server.py` | Engine registry (5 engines) | REST API (port 8000) |
| `memory_service.py` | standalone `MemoryManager` | REST API (port 8081) |
| `app.py` | `core/dark_system.py` | CLI |
| `main.py` | `core/character_profile.py` | CLI |
| `rinlada_fusion.py` | `RinladaAI` | also registered in engine registry |
| `seraphina_ai_complete.py` | `SeraphinaAI` | also registered in engine registry |

### Engine Registry (server.py)

`server.py` uses a lazy-singleton `_EngineRegistry` — engines are registered at import time and instantiated on first request. The default engine (`omega`) is pre-loaded at startup.

```
omega      → NaMoOmegaEngine       (default, pre-loaded)
dark       → DarkNaMoSystem
rinlada    → RinladaAI
seraphina  → SeraphinaAI
ultimate   → NaMoUltimateBrain
```

Select engine per request via the `engine` field in the chat request body, or set `DEFAULT_ENGINE` env var.

### API Endpoints

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/` | none | Status + available engines |
| POST | `/chat` | none | Main chat (public) |
| POST | `/v1/chat` | optional `X-API-Key` | Authenticated chat |
| POST | `/v1/chat/stream` | optional `X-API-Key` | SSE streaming chat |
| GET | `/v1/engines` | none | List registered engines |
| GET | `/v1/health` | none | Health check |
| GET | `/v1/status` | none | Status of all loaded engines |
| GET | `/v1/admin/sessions` | `X-Admin-Secret` | Active sessions per engine |

Do not rename or change any of these paths — they are production routes.

### Architecture Rules

- All external service calls (OpenAI, ElevenLabs, emotion API, memory JSON) go through `adapters/` only
- `core/` engines must be testable without network or filesystem calls
- New feature? Add engine logic to `core/`, IO to `adapters/`, wire them in the entry point
- Prefer editing existing modules over creating near-duplicates
- Every persona engine must inherit `BasePersonaEngine` and implement `process_input()`

`process_input(user_input, session_id)` return shape (do not change without updating `server.py` and tests):
```python
{
    "text": str,
    "media_trigger": {"image": str | None, "audio": str | None, "tts": str | None},
    "system_status": {"arousal": str, "sin_status": str, "active_personas": list}
}
```

### Per-Session State Isolation

All mutable state is keyed by `session_id` (falls back to `"default"`). `server.py` runs an async cleanup loop that evicts sessions older than `SESSION_TTL_SECONDS` (default 3600s). The following per-instance dicts are cleaned:

| Engine | Attribute |
|---|---|
| `NaMoOmegaEngine` | `_session_states`, `session_history` |
| `NaMoUltimateBrain` | `_session_arousal` |
| `DarkNaMoSystem` | `_session_intensity` |
| `RinladaAI` | `_session_arousal` |
| `SeraphinaAI` | `_session_arousal` |

### Rate Limiting

`server.py` uses a sliding-window `_RateLimiter` keyed by client IP.
Configured via `settings.rate_limit_calls` and `settings.rate_limit_period` (default 60 calls/60s).

---

## Core Modules (`core/`)

### Base & Bundle

| File | Class | Responsibility |
|---|---|---|
| `base_persona.py` | `BasePersonaEngine` (ABC) | Abstract base; defines `process_input()`, `get_status()`, `init_cognition()` |
| `base_persona.py` | `CognitiveCore` | Bundle: wraps EmotionEngine + CognitiveStream + LearningEngine; call `cognitive.process()` once per turn |

### Persona Engines

| File | Class | Notes |
|---|---|---|
| `namo_omega_engine.py` | `NaMoOmegaEngine` | Primary engine. Contains `SinSystem`, `SensoryOverloadManager`, `PersonaOrchestrator`, `RelationshipEngine`. Reads env directly for LLM init — follow existing pattern when modifying. |
| `dark_system.py` | `DarkNaMoSystem` | CLI engine. Metaphysical Phase 4.2. Safe word: **"อภัย"** triggers aftercare mode. |
| `namo_ultimate_engine.py` | `NaMoUltimateBrain` | Advanced engine with `ForbiddenDialogueLibrary`, session arousal, multi-persona support. |
| `character_profile.py` | `CharacterProfile` | CLI engine for `main.py`. Persists state to `namo_state.json`. |

Engines registered in `server.py` but defined in root-level files:

| File | Class | Notes |
|---|---|---|
| `rinlada_fusion.py` | `RinladaAI` | Rinlada character (Dark Muse / Forbidden Aunt). Optional TensorFlow/Transformers. |
| `seraphina_ai_complete.py` | `SeraphinaAI` | Seraphina character (The Seductive Enigma). Deep psychological profiling. Optional TensorFlow/BERT. |

### Cognitive Stack (opt-in)

Activate by calling `self.init_cognition()` in an engine's `__init__`.

| Module | Class | Responsibility |
|---|---|---|
| `core/emotion_engine.py` | `EmotionEngine` | 5-D continuous emotion (joy/arousal/trust/anger/desire) with momentum (INERTIA=0.65) + baseline decay (DECAY_RATE=0.06) |
| `core/cognitive_stream.py` | `CognitiveStream` | Internal monologue queue (max 6 thoughts): impulse/reflection/memory/conflict/desire — injected into LLM prompt |
| `core/learning_engine.py` | `LearningEngine` | Observes interactions, evolves 4 traits (boldness/playfulness/vulnerability/expressiveness), persists to `learned_patterns.json` |
| `core/base_persona.py` | `CognitiveCore` | Bundle — call `cognitive.process()` once per turn |

`CognitiveCore.process()` returns:
```python
{
    "emotion":        dict,   # EmotionEngine.snapshot()
    "monologue":      str,    # thought queue as prompt string
    "autonomous":     str | None,
    "persona_traits": dict,   # boldness / playfulness / vulnerability / expressiveness
    "preferences":    dict,
}
```

### Supporting Modules

| Module | Class | Responsibility |
|---|---|---|
| `core/intent_analyzer.py` | `IntentAnalyzer` | Lightweight intent extraction (no LLM) — anger/rejection/comfort/nostalgia/lust/command/affection/tease; Thai + English keywords |
| `core/relationship_engine.py` | `RelationshipEngine` | Stage progression: Stranger → Plaything → Lover → Dark Obsession; attachment styles: Secure/Anxious/Possessive/Avoidant |
| `core/rag_memory_system.py` | `NaMoInfiniteMemory` | RAG: ingests .txt/.htm from `learning_set/`, FAISS + OpenAI embeddings, persistent metadata |
| `core/metaphysical_engines.py` | `MetaphysicalDialogueEngine` | DharmaProcessor + ParadoxResolver + VoidReflectionLayer — used by `DarkNaMoSystem` |
| `core/fusion_brain.py` | `NaMoFusionBrain` | `FusionUnlockConfig` master switches + `MasterPromptBuilder` (9-module prompt construction) |
| `core/generative_brain.py` | `NaMoGenerativeBrain` | Combines RAG memory with LLM logic; mood tracking (Seductive/Cruel/Obsessed) |

---

## Adapters (`adapters/`)

All thin wrappers for external services — easy to mock in tests.

| File | Class | Responsibility |
|---|---|---|
| `adapters/memory.py` | `MemoryAdapter` | Dual-write: local JSON + optional remote memory service; interaction storage with metadata |
| `adapters/emotion.py` | `EmotionAdapter` | HTTP POST to emotion analysis endpoint; fallback returns `{"primary_emotion": "unknown", "intensity": 0}` |
| `adapters/tts.py` | `TTSAdapter` | ElevenLabs TTS; MP3 output to `Audio_Layers/tts/`; returns relative path; fallback returns `None` |

---

## Cognitive Stack Integration

Before modifying `NaMoOmegaEngine` → read `docs/ARCHITECTURE.md` first.
Before adding a new API endpoint → read `docs/API_SPEC.md` first.
Full env vars reference → `docs/CONFIG.md`

---

## Coding Conventions

- Python 3.11+ syntax — use `str | None` unions, no `Optional[str]` (pyupgrade enforces this)
- Avoid `Any` type annotations; prefer explicit types
- `async/await` for FastAPI route handlers; sync functions elsewhere
- Keep modules under ~200 lines unless justified
- Descriptive names — no single-letter vars outside list comprehensions
- No dead code, no commented-out blocks
- Comments only when intent is non-obvious
- All configuration must go through `config.py` → `settings`, never `os.getenv()` directly in business logic (exception: `namo_omega_engine.py` reads env directly for LLM init — follow existing pattern when modifying that file)
- Line length limit: 100 characters (ruff enforces this)

---

## UI & Design System

The web client is static HTML/CSS/JS under `web/` — no build step, no framework.

- Vanilla JS only in `web/app.js`; do not introduce npm or bundlers
- `web/styles.css` for all styles — no inline styles in HTML
- The `/ui` endpoint is served directly by FastAPI's `StaticFiles`; no changes to the mount path
- Media URLs in API responses must be absolute when `PUBLIC_BASE_URL` is set — use `_resolve_media_url()` in `server.py`

---

## Content & Copy

- Thai is the default language for NaMo dialogue; English is used for system logs and code comments
- Persona tone: seductive, possessive, intimate — stay in character
- Error messages in API responses: English, concise, no stack traces exposed to clients
- Log messages prefix format: `[ComponentName]: message` (e.g., `[OMEGA ENGINE]: LLM init failed`)
- Avoid generic filler in dialogue — responses should feel contextual and varied
- Safe word for `DarkNaMoSystem` / dark roleplay: **"อภัย"** — triggers aftercare mode

---

## Configuration (`config.py`)

All settings come from `config.py` → `Settings` (pydantic-settings). Key fields:

```
# LLM
NAMO_LLM_ENABLED       bool    False
NAMO_LLM_MODEL         str     "gpt-4o-mini"
NAMO_LLM_TEMPERATURE   float   0.85
NAMO_LLM_MAX_TOKENS    int     240
NAMO_LLM_MEMORY_TURNS  int     6

# NSFW / Content
SAFETY_FILTER_ENABLED  bool    True
NSFW_ALLOWED           bool    False
SCENE_MODE             str     "restricted"

# Engine
DEFAULT_ENGINE         str     "omega"

# Session & Rate Limit
SESSION_TTL_SECONDS    int     3600
RATE_LIMIT_CALLS       int     60
RATE_LIMIT_PERIOD      int     60

# TTS
ELEVENLABS_API_KEY     str|None
ELEVENLABS_VOICE_ID    str     "Rachel"
ELEVENLABS_MODEL       str     "eleven_multilingual_v2"
TTS_OUTPUT_DIR         str     "Audio_Layers/tts"

# Memory
MEMORY_API_URL         str|None
MEMORY_API_KEY         str|None
MEMORY_LOGGING         int     0   (0=off, 1=on)
MEMORY_FILE_PATH       str     "memory_protocol.json"

# Auth
NAMO_API_KEYS          str|None   "key:plan,key2:plan2" format
ADMIN_SECRET           str|None
API_MASTER_KEY         str|None
```

`extra="ignore"` in `Settings` is intentional — do not change to `extra="forbid"`.

---

## Testing & Quality

Before marking any task complete:
- `make lint` — ruff check must pass
- `make format` — black + ruff --fix check must pass
- `make test` — all 335+ tests in `tests/` must pass

Rules:
- Unit tests required for: engine `process_input()` logic, memory store/recall, API key resolution, media URL resolution
- No heavy test scaffolding for simple adapter wrappers
- Mock all external services (OpenAI, ElevenLabs, HTTP calls) — tests must run offline
- Verify both "service available" and "service absent/no API key" code paths for every adapter
- `test_main.py` at root is legacy — add new tests under `tests/` only

---

## File Placement

- New engine logic → `core/`
- New external-service wrapper → `adapters/`
- New experimental/standalone script → `Core_Scripts/`
- New test → `tests/`
- New API utility (health check, diagnostics) → `tools/`
- Static audio/image assets → `Audio_Layers/` or `Visual_Scenes/`

Rules:
- Do not create a new module for one-off logic; add it to the nearest existing relevant file
- Module filename must reflect its primary class/function (e.g., `tts.py` → `TTSAdapter`)

---

## Safety Rules

- Do not rename or change the path of any public API route (`/chat`, `/v1/chat`, `/v1/health`, `/v1/status`, `/v1/chat/stream`, `/v1/engines`, `/v1/admin/sessions`)
- Do not change the `process_input()` return shape without updating `server.py` and tests
- Do not modify `memory_service.py` store/recall contract without flagging first
- Do not change `config.py` field names — they map 1:1 to env vars used in production
- Flag any change to `SinSystem`, `PersonaOrchestrator`, or `SensoryOverloadManager` behavior that could affect deployed Cloud Run responses
- `extra="ignore"` in `Settings` is intentional — do not change to `extra="forbid"`

---

## Commands

```
Setup:           make setup
Dev server:      make run              (uvicorn server:app, port 8000, --reload)
Memory service:  uvicorn memory_service:app --host 0.0.0.0 --port 8081 --reload
CLI (Dark):      python app.py
CLI (Character): python main.py
Web client:      cd web && python -m http.server 5173
Lint:            make lint
Format:          make format
Test:            make test             (pytest -q)
Test + coverage: pytest --cov --cov-report=term-missing
Pre-commit:      make precommit
Security audit:  make audit            (pip-audit + bandit)
KB build:        python learn_from_set.py     (requires OPENAI_API_KEY, set.zip in learning_set/)
KB query:        python query_learned_knowledge.py
Stream test:     curl -N -X POST http://localhost:8000/v1/chat/stream -H "Content-Type: application/json" -d '{"text":"สวัสดี"}'
API check:       python tools/check_api.py --base-url <url>
Telegram check:  python tools/telegram_check.py
Docker API:      docker build -t namo-api . && docker run -p 8000:8000 --env-file .env namo-api
Docker memory:   docker build -f Dockerfile.memory -t namo-memory . && docker run -p 8081:8081 --env-file .env namo-memory
```

---

## Security Rules

- Never commit `.env` or any file containing real secrets — `.env.example` with placeholder values only
- Never hardcode API keys, tokens, or passwords in source code
- All secrets go through `config.py` → `Settings`; the `.env` file is gitignored
- Never log sensitive values:
  - no `print(settings.openai_api_key)`
  - no logging full request bodies
  - no logging `NAMO_API_KEYS` contents
- `NAMO_API_KEYS` format is `key:plan,key2:plan2` — keys are secrets, treat them accordingly
- `ADMIN_SECRET` and `API_MASTER_KEY` are server-side only; never return them in any API response
- User input from `/chat` is passed to OpenAI — do not log raw input in production without considering PII
- `CORS_ALLOW_ORIGINS` defaults to `*`; restrict to specific origins before any public deployment
- `bandit` and `pip-audit` run in CI — fix high/critical findings before merging

---

## Common Mistakes to Avoid

Patterns Claude has been seen repeating incorrectly in this codebase:

- **Using `os.getenv()` in business logic** — always use `from config import settings` instead
- **Creating a new module for one-off logic** — add to the nearest existing relevant file
- **Calling external services directly in `core/`** — all IO goes through `adapters/` only
- **Adding `Optional[str]`** — use `str | None` (Python 3.11+ syntax, pyupgrade enforces this)
- **Writing tests in `test_main.py` at root** — new tests go under `tests/` only
- **Returning media paths as relative URLs** — use `_resolve_media_url()` in `server.py` when `PUBLIC_BASE_URL` is set
- **Adding safety wrappers around NaMo dialogue** — NSFW content is intentional; use `SAFETY_FILTER_ENABLED` / `NSFW_ALLOWED` flags for runtime control
- **Instantiating engines outside the registry** — always use `_EngineRegistry.get(name)` in server context
- **Adding a new engine without registering it** — register in the `_EngineRegistry` block in `server.py`
- **Lines exceeding 100 chars** — ruff enforces a 100-character line limit; break long function signatures and dicts into multiple lines
