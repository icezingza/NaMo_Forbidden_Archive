# NaMo Forbidden Archive — Advanced Conversational Core (ACC)

> A high-performance, multimodal conversational AI framework featuring continuous emotional simulation, semantic memory retrieval, and adaptive cognitive feedback loops.

**Brand:** NamoNexus  
**Author:** Kanin Raksaraj  
**Contact:** [contact@namonexus.com](mailto:contact@namonexus.com)

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Requirements](#system-requirements)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Deployment](#deployment)
- [License](#license)

---

## Overview

**NaMo Forbidden Archive** (ACC — Advanced Conversational Core) is an enterprise-grade conversational AI system built for high-fidelity, context-aware, and emotionally-consistent interactions. It combines:

- **Continuous 5-Dimensional Emotional Modeling** — real-time mood simulation with temporal momentum and decay
- **Semantic Memory (RAG)** — dual-layer vector + graph database for long-term context retrieval
- **Autonomous Cognitive Monologue** — internal reasoning stream that runs before every response
- **Multi-Modal I/O** — text, voice (Whisper STT + ElevenLabs TTS), and image generation (DALL-E 3)
- **Modular Persona Engine** — hot-swappable persona configurations at runtime

---

## Key Features

| Feature | Description |
|---|---|
| 5D Emotion Engine | Tracks Arousal, Trust, Passion, Temperament, Resonance with inertia & decay |
| RAG Memory | FAISS / Qdrant vector search with 100–150 token micro-chunking |
| Graph Memory | Neo4j for structural metadata and behavioral lineage |
| Cognitive Stream | FIFO thought queue (Impulse → Reflection → Conflict) prepended to every prompt |
| Relationship Engine | Evolves intimacy across 4 stages based on accumulated trust metrics |
| Session Isolation | Per-session memory pools with TTL-based eviction (default 3600 s) |
| Multi-Modal | Voice transcription, image generation, TTS synthesis |
| Telegram Bot | Async auto-reply bot with voice note and image support |
| REST API | FastAPI gateway with sliding-window rate limiter and SSE streaming |
| Docker & Cloud Run | One-command containerised deployment to Google Cloud Run |

---

## System Requirements

- Python 3.11+
- Docker Desktop (for local database containers)
- Google Cloud SDK (optional, for Cloud Run deployment)

### External Services (API Keys Required)

| Service | Purpose | Required |
|---|---|---|
| OpenAI | LLM generation + embeddings | Yes |
| ElevenLabs | Text-to-Speech synthesis | Optional |
| Telegram Bot API | Telegram interface | Optional |
| Qdrant | Cloud vector database | Optional |
| Neo4j | Graph database | Optional |

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://gitlab.com/namo4524325/na-mo-forbidden-archive.git
cd na-mo-forbidden-archive
```

### 2. Configure Environment Variables

```bash
# macOS / Linux
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

Edit `.env` and populate at minimum:

```env
OPENAI_API_KEY=sk-...
TELEGRAM_TOKEN=...          # optional
ELEVENLABS_API_KEY=...      # optional
QDRANT_URL=...              # optional
NEO4J_URI=...               # optional
```

### 3. Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Start the REST API

```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Send a Test Request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello", "session_id": "demo"}'
```

---

## Architecture

See [`Documentation/ARCHITECTURE.md`](Documentation/ARCHITECTURE.md) for the full architecture document including component diagrams and data flow.

```
Client Layer       →  Telegram Bot  |  Web Client (HTML5)
Integration Layer  →  FastAPI REST Gateway  |  Rate Limiter  |  Session TTL Manager
Cognitive Layer    →  Emotion Engine (5D)  |  Cognitive Stream  |  Relationship Engine
Storage Layer      →  FAISS / Qdrant (Vector)  |  Neo4j (Graph)  |  JSON Session Files
```

---

## API Reference

Full API specification: [`docs/API_SPEC.md`](docs/API_SPEC.md)

| Endpoint | Method | Description |
|---|---|---|
| `/chat` | POST | Send a message and receive a streamed response |
| `/health` | GET | System health check |
| `/media/visual` | GET | Serve generated visual assets |
| `/media/audio` | GET | Serve generated audio assets |
| `/store` | POST | Store a memory entry (Memory Service, port 8081) |

---

## Deployment

### Docker (Local)

```bash
docker build -t namo-acc .
docker run --rm -e PORT=8080 -p 8080:8080 namo-acc
```

### Google Cloud Run

```bash
bash deploy.sh
```

Replace `PROJECT_ID`, `SERVICE_NAME`, and `REGION` in `deploy.sh` before running.

---

## License

This project is licensed under the **MIT License** — see [`Documentation/LICENSE.txt`](Documentation/LICENSE.txt) for details.

Copyright (c) 2026 NamoNexus — Kanin Raksaraj  
Contact: [contact@namonexus.com](mailto:contact@namonexus.com)
