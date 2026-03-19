# CONFIG.md — Environment Variable Reference

All configuration is loaded via `config.py` → `Settings` (pydantic-settings).
Source of truth is always `config.py`. This file is a quick-reference summary.

Never use `os.getenv()` directly in business logic — always import `settings` from `config.py`.

---

## System

| Env var | Default | Description |
|---|---|---|
| `APP_ENV` | `development` | Runtime environment (`development` / `production`) |
| `APP_PORT` | `8000` | Port for the main API server |
| `DEBUG` | `true` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |

## External Services

| Env var | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required for LLM responses and FAISS KB embeddings |
| `EMOTION_API_URL` | `http://localhost:8082/analyze` | Optional external emotion analysis service |
| `MEMORY_API_URL` | — | Memory microservice URL (port 8081) |
| `MEMORY_API_KEY` | — | Sent as `x-api-key` to memory service |
| `MEMORY_LOGGING` | `0` | Set `1` to enable memory service logging |
| `PUBLIC_BASE_URL` | — | Absolute base URL for media links in API responses |
| `CORS_ALLOW_ORIGINS` | `*` | Comma-separated allowed CORS origins — restrict before public deploy |

## LLM Configuration

| Env var | Default | Description |
|---|---|---|
| `NAMO_LLM_ENABLED` | `false` | Enable LLM responses (auto-enables if `OPENAI_API_KEY` is set) |
| `NAMO_LLM_MODEL` | `gpt-4o-mini` | OpenAI model name |
| `NAMO_LLM_TEMPERATURE` | `0.85` | Sampling temperature |
| `NAMO_LLM_MAX_TOKENS` | `240` | Max tokens per response |
| `NAMO_LLM_MEMORY_TURNS` | `6` | Conversation turns kept in LLM context |

## Content Controls

| Env var | Default | Description |
|---|---|---|
| `SAFETY_FILTER_ENABLED` | `true` | Enable safety filter |
| `NSFW_ALLOWED` | `false` | Allow NSFW content |
| `SCENE_MODE` | `restricted` | Scene mode (`restricted` / `dark` / `forbidden`) |

## Auth & Security

| Env var | Default | Description |
|---|---|---|
| `API_MASTER_KEY` | — | Master API key — server-side only, never expose in responses |
| `ADMIN_SECRET` | — | Admin secret — server-side only, never expose in responses |
| `NAMO_API_KEYS` | — | Format: `key:plan,key2:plan2` — used for `/v1/chat` auth |
| `NAMO_API_DEFAULT_PLAN` | `public` | Default plan when no key is provided |
| `NAMO_USAGE_LOG_PATH` | — | JSONL file path for per-request usage logging |

## Core Engine Flags

| Env var | Default | Description |
|---|---|---|
| `ENABLE_EMOTION_PARASITE` | `false` | Enable emotion parasite engine |
| `ENABLE_AROUSAL_DETECTOR` | `false` | Enable arousal detector |
| `ENABLE_DARK_MEMORY` | `false` | Enable dark memory subsystem |

## Legacy / Compatibility

| Env var | Default | Description |
|---|---|---|
| `MEMORY_FILE_PATH` | `memory_protocol.json` | Local JSON memory file path |

---

## ElevenLabs TTS

Loaded directly by `adapters/tts.py` — not in `config.py` Settings class.

| Env var | Description |
|---|---|
| `ELEVENLABS_API_KEY` | ElevenLabs API key |
| `ELEVENLABS_VOICE_ID` | Voice ID for TTS synthesis |

## Telegram

Loaded directly by bot scripts in `Core_Scripts/`.

| Env var | Description |
|---|---|
| `TELEGRAM_TOKEN` | Telegram bot token |
