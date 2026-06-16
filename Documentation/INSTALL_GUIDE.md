# Detailed Installation and Usage Guide (NaMo Forbidden Archive)

This document provides guidelines on how to install and utilize all core features in this repository.
These steps can be followed on both Windows and macOS/Linux environments.

## Prerequisites
- Python 3.11+ (recommended to align with CI environment)
- Git (if cloning via command line)
- (Optional) OpenAI API key for `learn_from_set.py` and `query_learned_knowledge.py`
- (Optional) ElevenLabs API key for Text-to-Speech (TTS)
- (Optional) Telegram bot token if deploying the Telegram bot interface in `Core_Scripts/namo_auto_AI_reply.py`

## Core Project Directory Layout
- REST API: `server.py`
- Memory Service: `memory_service.py`
- CLI Entrypoint (Main): `app.py`
- CLI Entrypoint (Experimental): `main.py`
- Knowledge Base: `learn_from_set.py`, `query_learned_knowledge.py`
- Telegram Bot (Optional): `Core_Scripts/namo_auto_AI_reply.py`

---

## Standard Installation Steps

### 1) Prepare Environment Variables (`.env`)
Copy the sample environment file and populate the necessary settings:

**Windows (PowerShell)**
```powershell
Copy-Item .env.example .env
```

**macOS/Linux**
```bash
cp .env.example .env
```

### 2) Create and Activate Virtual Environment & Install Dependencies

**Windows (PowerShell)**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**macOS/Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Important Environment Variables (`.env`)
Referencing `.env.example`:
- `OPENAI_API_KEY`: API key for vector embedding/querying (Knowledge Base).
- `NAMO_LLM_ENABLED`: Enables NaMo to respond with contextual memory (requires OpenAI).
- `NAMO_LLM_MODEL`, `NAMO_LLM_TEMPERATURE`, `NAMO_LLM_MAX_TOKENS`, `NAMO_LLM_MEMORY_TURNS`: Configures the LLM behavior.
- `TELEGRAM_TOKEN`: Bot token for the Telegram bot interface.
- `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID`: Configures ElevenLabs TTS.
- `EMOTION_API_URL`: Connection settings for external emotion analytics engines (if applicable).
- `MEMORY_API_URL` and `MEMORY_API_KEY`: Connection configurations if using remote memory storage.
- `MEMORY_LOGGING`: Enables logging interactions to the memory REST API (1 = enabled, 0 = disabled).
- `PUBLIC_BASE_URL`: Sets the public URL for generating absolute media URLs in REST responses.
- `CORS_ALLOW_ORIGINS`: Configures origins allowed for web requests.
- `NAMO_API_URL`: Points the Telegram bot to the active NaMo REST API server.
- `NAMO_API_TIMEOUT`: Timeout configurations for Telegram bot API calls.
- `TELEGRAM_SHOW_STATUS`: Appends system status notes to Telegram messages (1 = enabled, 0 = disabled).
- `TELEGRAM_INCLUDE_MEDIA`: Attaches media URLs in Telegram messages (1 = enabled, 0 = disabled).

---

## Utilizing Core Features

### 1) Main CLI Interface (DarkNaMoSystem)
Runs the CLI in the terminal with metaphysical features:
```bash
python app.py
```

### 2) Experimental CLI Interface (CharacterProfile + EmotionParasiteEngine)
Launches the experimental CLI testing loop:
```bash
python main.py
```

### 3) REST API Server (NaMo Omega Engine)
Starts the central API host:
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

Example API Chat Request:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "hello", "session_id": "demo-session"}'
```
> For complete specifications, see `docs/API_SPEC.md`

**Server Notes**:
- The server serves visual and audio media files at `/media/visual` and `/media/audio`.
- Set `PUBLIC_BASE_URL` if you want media assets to be returned with absolute URLs.
- Configure `CORS_ALLOW_ORIGINS` if connecting from external domain web clients.

### 4) Memory Service
Starts the isolated memory microservice:
```bash
uvicorn memory_service:app --host 0.0.0.0 --port 8081 --reload
```

Example Memory Store Request:
```bash
curl -X POST http://localhost:8081/store \
  -H "Content-Type: application/json" \
  -d '{"content":"hello","type":"contextual","session_id":"demo"}'
```

Health Check:
```bash
curl http://localhost:8081/health
```

### 4.1) Web Client Interface (Static HTML)
Launches a simple web client served locally to interact with the REST API:
```bash
cd web
python -m http.server 5173
```
Open `http://localhost:5173` in a browser and configure your Base API URL in Settings.
If served directly from the FastAPI server, you can access the UI at `/ui`, e.g. `http://localhost:8000/ui`.

### 5) Knowledge Base Management (FAISS Vector Search)
1) Place the source dataset archive as `set.zip` inside `learning_set/`.
2) Ingest and build the vector database:
   ```bash
   python learn_from_set.py
   ```
3) Query facts from the generated database:
   ```bash
   python query_learned_knowledge.py
   ```

### 6) Telegram Auto-Reply Bot Integration (Optional)
Install additional requirements:
```bash
pip install python-telegram-bot
```
Set `TELEGRAM_TOKEN` in `.env` and start the bot:
```bash
python Core_Scripts/namo_auto_AI_reply.py
```
To point the bot to a remote server, make sure to adjust `NAMO_API_URL`, `TELEGRAM_SHOW_STATUS`, or `TELEGRAM_INCLUDE_MEDIA` in the `.env` configuration file.

Quick check script:
```bash
python tools/telegram_check.py
```
To send a manual test message (make sure you send `/start` to the bot first):
```bash
python tools/telegram_check.py --send --message "ping from NaMo"
```

### 7) ElevenLabs Text-to-Speech (Optional)
Configure `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` inside `.env`.
Audio conversion will trigger automatically via `adapters/tts.py` during relevant response paths.

### 8) OpenAI Large Language Model (Optional)
To enable diverse, context-rich dialogue generations, update `.env` with:
```bash
NAMO_LLM_ENABLED=1
NAMO_LLM_MODEL=gpt-4o-mini
NAMO_LLM_TEMPERATURE=0.85
NAMO_LLM_MAX_TOKENS=240
NAMO_LLM_MEMORY_TURNS=6
```
Once enabled, the REST API uses OpenAI's GPT endpoints to process context.

---

## Running Test Suites
Install developer-specific dependencies and run the pytest suite:
```bash
pip install -r requirements-dev.txt
pytest
```

---

## Docker Support (Optional)
Build and run the API container locally:
```bash
docker build -t namo-forbidden-archive .
docker run --rm -e PORT=8080 -p 8080:8080 namo-forbidden-archive
```

---

## Deploying to Google Cloud Run (Optional)
Refer to deploy scripts `deploy.sh` and `deploy_fixed.sh`.
Make sure to replace `PROJECT_ID`, `SERVICE_NAME`, and `REGION` with your Google Cloud parameters.

### Pre-configured Deployment Details:
- Project ID: `arctic-signer-471822-i8`
- Project Number: `185116032835`
- Service URL: `https://namo-forbidden-archive-185116032835.asia-southeast1.run.app`
- UI URL: `https://namo-forbidden-archive-185116032835.asia-southeast1.run.app/ui`

Testing the Cloud Run Service:
```bash
curl https://namo-forbidden-archive-185116032835.asia-southeast1.run.app/
```
```bash
curl -X POST https://namo-forbidden-archive-185116032835.asia-southeast1.run.app/chat \
  -H "Content-Type: application/json" \
  -d '{"text":"hello","session_id":"cloud-demo"}'
```

### Quick API Diagnostic Command
Use `tools/check_api.py` to diagnose your endpoints:

Local diagnostics:
```bash
python tools/check_api.py --base-url http://localhost:8000
```
Cloud Run diagnostics:
```bash
python tools/check_api.py --base-url https://namo-forbidden-archive-185116032835.asia-southeast1.run.app
```

---

## Troubleshooting
- `ModuleNotFoundError`: Ensure your virtual environment is active and you have run `pip install -r requirements.txt`.
- `No TELEGRAM_TOKEN set`: Provide your Telegram bot token in the `.env` file.
- `OpenAI authentication error`: Provide a valid `OPENAI_API_KEY` in `.env`.
- Port Conflicts: Change the port parameter during uvicorn startup (e.g. `--port 8001`).

---

## Content Note
Please note that dialogue templates contain adult/NSFW simulation scripts.
