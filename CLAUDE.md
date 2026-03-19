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
core/              → pure Python engines (no heavy IO)
adapters/          → thin wrappers for all external IO
Core_Scripts/      → experimental/auxiliary scripts (not imported by server.py)
tests/             → pytest suite
docs/              → API and architecture specs
web/               → static frontend (served at /ui by server.py)
Audio_Layers/      → static audio assets  → served at /media/audio
Visual_Scenes/     → static image assets  → served at /media/visual
learning_set/      → input ZIPs for FAISS knowledge base
tools/             → one-off utility scripts (not part of the app)
```

Entry points:

| File | Engine | Interface |
|---|---|---|
| `server.py` | `core/namo_omega_engine.py` | REST API (port 8000) |
| `memory_service.py` | standalone | REST API (port 8081) |
| `app.py` | `core/dark_system.py` | CLI |
| `main.py` | `core/character_profile.py` | CLI |

Rules:
- All external service calls (OpenAI, ElevenLabs, emotion API, memory JSON) go through `adapters/` only
- `core/` engines must be testable without network or filesystem calls
- New feature? Add engine logic to `core/`, IO to `adapters/`, wire them in the entry point
- Prefer editing existing modules over creating near-duplicates

`process_input(user_input, session_id)` return shape (do not change without updating `server.py` and tests):
```python
{
    "text": str,
    "media_trigger": {"image": str | None, "audio": str | None, "tts": str | None},
    "system_status": {"arousal": str, "sin_status": str, "active_personas": list}
}
```

Before modifying `NaMoOmegaEngine` → read `docs/ARCHITECTURE.md` first.
Before adding a new API endpoint → read `docs/API_SPEC.md` first.
Full env vars reference → `docs/CONFIG.md`

## Coding Conventions

- Python 3.11+ syntax — use `str | None` unions, no `Optional[str]` (pyupgrade enforces this)
- Avoid `Any` type annotations; prefer explicit types
- `async/await` for FastAPI route handlers; sync functions elsewhere
- Keep modules under ~200 lines unless justified
- Descriptive names — no single-letter vars outside list comprehensions
- No dead code, no commented-out blocks
- Comments only when intent is non-obvious
- All configuration must go through `config.py` → `settings`, never `os.getenv()` directly in business logic (exception: `namo_omega_engine.py` reads env directly for LLM init — follow existing pattern when modifying that file)

## UI & Design System

The web client is static HTML/CSS/JS under `web/` — no build step, no framework.

- Vanilla JS only in `web/app.js`; do not introduce npm or bundlers
- `web/styles.css` for all styles — no inline styles in HTML
- The `/ui` endpoint is served directly by FastAPI's `StaticFiles`; no changes to the mount path
- Media URLs in API responses must be absolute when `PUBLIC_BASE_URL` is set — use `_resolve_media_url()` in `server.py`

## Content & Copy

- Thai is the default language for NaMo dialogue; English is used for system logs and code comments
- Persona tone: seductive, possessive, intimate — stay in character
- Error messages in API responses: English, concise, no stack traces exposed to clients
- Log messages prefix format: `[ComponentName]: message` (e.g., `[OMEGA ENGINE]: LLM init failed`)
- Avoid generic filler in dialogue — responses should feel contextual and varied

## Testing & Quality

Before marking any task complete:
- `make lint` — ruff check must pass
- `make format` — black check must pass
- `pytest` — all tests in `tests/` must pass

Rules:
- Unit tests required for: engine `process_input()` logic, memory store/recall, API key resolution, media URL resolution
- No heavy test scaffolding for simple adapter wrappers
- Mock all external services (OpenAI, ElevenLabs, HTTP calls) — tests must run offline
- Verify both "service available" and "service absent/no API key" code paths for every adapter
- `test_main.py` at root is legacy — add new tests under `tests/` only

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

## Safety Rules

- Do not rename or change the path of any public API route (`/chat`, `/v1/chat`, `/v1/health`)
- Do not change the `process_input()` return shape without updating `server.py` and tests
- Do not modify `memory_service.py` store/recall contract without flagging first
- Do not change `config.py` field names — they map 1:1 to env vars used in production
- Flag any change to `SinSystem`, `PersonaOrchestrator`, or `SensoryOverloadManager` behavior that could affect deployed Cloud Run responses
- `extra="ignore"` in `Settings` is intentional — do not change to `extra="forbid"`

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
API check:       python tools/check_api.py --base-url <url>
Telegram check:  python tools/telegram_check.py
Docker API:      docker build -t namo-api . && docker run -p 8000:8000 --env-file .env namo-api
Docker memory:   docker build -f Dockerfile.memory -t namo-memory . && docker run -p 8081:8081 --env-file .env namo-memory
```

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

## Common Mistakes to Avoid

Patterns Claude has been seen repeating incorrectly in this codebase:

- **Using `os.getenv()` in business logic** — always use `from config import settings` instead
- **Creating a new module for one-off logic** — add to the nearest existing relevant file
- **Calling external services directly in `core/`** — all IO goes through `adapters/` only
- **Adding `Optional[str]`** — use `str | None` (Python 3.11+ syntax, pyupgrade enforces this)
- **Writing tests in `test_main.py` at root** — new tests go under `tests/` only
- **Returning media paths as relative URLs** — use `_resolve_media_url()` in `server.py` when `PUBLIC_BASE_URL` is set
- **Adding safety wrappers around NaMo dialogue** — NSFW content is intentional; use `SAFETY_FILTER_ENABLED` / `NSFW_ALLOWED` flags for runtime control
