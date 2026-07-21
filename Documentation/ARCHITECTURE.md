# Architecture Documentation — Advanced Conversational Core (ACC)

> Version 1.0 | NamoNexus — Advanced Conversational Core (ACC)  
> Author: Kanin Raksaraj | contact@namonexus.com

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Four-Layer Architecture](#2-four-layer-architecture)
3. [Component Reference](#3-component-reference)
4. [Request Lifecycle](#4-request-lifecycle)
5. [Data Storage Strategy](#5-data-storage-strategy)
6. [Multi-Modal Pipeline](#6-multi-modal-pipeline)
7. [Deployment Topology](#7-deployment-topology)
8. [Configuration Reference](#8-configuration-reference)

---

## 1. System Overview

The **Advanced Conversational Core (ACC)** is a layered cognitive AI system designed for stateful, emotionally-consistent, and context-aware conversational interactions. It is built around four primary concerns:

- **Emotional Continuity** — a 5-dimensional emotional state that persists and evolves across a session
- **Semantic Memory** — vector and graph databases that store and retrieve long-term contextual facts
- **Cognitive Transparency** — an internal monologue stream that simulates reasoning before generating responses
- **Multi-Modal Output** — text, synthesised speech, and generated images delivered in a single response payload

---

## 2. Four-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                         │
│         Telegram Bot              HTML5 Web Client          │
└───────────────────────────┬─────────────────────────────────┘
                            │  HTTPS / SSE Streaming
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     INTEGRATION LAYER                       │
│   FastAPI REST Gateway        Sliding-Window Rate Limiter   │
│   Session TTL Manager         Lazy Engine Registry          │
└───────────────────────────┬─────────────────────────────────┘
                            │  Async Context Calls
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      COGNITIVE LAYER                        │
│   Arousal Detection Matrix    Emotion Engine (5D State)     │
│   Cognitive Monologue Stream  Relationship Logic Engine     │
│   Intent Analyzer             Meta-Cognition Module         │
└───────────────────────────┬─────────────────────────────────┘
                            │  Query / Dual-Write I/O
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       STORAGE LAYER                         │
│   JSON Session Files          FAISS Knowledge Index         │
│   Qdrant Vector Database      Neo4j Graph Database          │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Component Reference

### 3.1 Client Layer

| Component | File / Path | Description |
|---|---|---|
| HTML5 Web Client | `web/` | Lightweight static frontend using XMLHttpRequest and SSE for streaming responses |
| Telegram Bot | `Core_Scripts/namo_auto_AI_reply.py` | Async bot supporting voice notes (Whisper STT) and image generation triggers |

### 3.2 Integration Layer

| Component | File / Path | Description |
|---|---|---|
| REST Gateway | `server.py` | FastAPI application; main entry point for all API requests |
| Memory Service | `memory_service.py` | Isolated microservice for memory read/write operations (port 8081) |
| Rate Limiter | `server.py` | Sliding-window IP-based rate limiter to prevent abuse |
| Session TTL Manager | `server.py` | Evicts inactive sessions after a configurable TTL (default: 3600 s) |
| Lazy Engine Registry | `server.py` | Loads persona engines into memory only on first request, reducing startup time |

### 3.3 Cognitive Layer

| Component | File / Path | Description |
|---|---|---|
| Emotion Engine (5D) | `core/emotion_engine.py` | Tracks five emotional dimensions with momentum (inertia = 0.65) and decay (rate = 0.06) |
| Arousal Detection Matrix | `Core_Scripts/arousal_detector.py` | Scores incoming input across text, vocal, and behavioural signals (composite 0.0–1.0) |
| Cognitive Monologue | `core/cognitive_stream.py` | FIFO thought queue (Impulse → Reflection → Conflict) prepended to every LLM prompt |
| Relationship Engine | `core/relationship_engine.py` | Evolves intimacy stage (Stranger → Companion → Partner → Deep Attachment) via trust metrics |
| Intent Analyzer | `core/intent_analyzer.py` | Classifies user intent (Affection, Rejection, Command, etc.) before cognitive processing |
| Meta-Cognition | `core/engines/meta_cognition.py` | Monitors and adjusts the cognitive stream for consistency and context adherence |
| Reasoning Engine | `core/engines/reasoning_engine.py` | 9-dimension recursive psychological analysis module |
| NamoNexus Fusion | `core/engines/namonexus_fusion.py` | Fuses outputs from all cognitive sub-engines into a unified context object |
| ASI Simulation | `core/engines/asi_simulation_engine.py` | High-level orchestration of the full cognitive pipeline |

### 3.4 Storage Layer & Adapters

| Component | File / Path | Description |
|---|---|---|
| RAG Memory System | `core/rag_memory_system.py` | Manages embedding, chunking (100–150 tokens, 20-token overlap), and retrieval |
| FAISS Index | `learning_set/` | Local vector index built from ingested knowledge documents |
| Qdrant Adapter | `adapters/memory.py` | Remote vector database adapter for production deployments |
| Neo4j Graph | `adapters/memory.py` | Graph database adapter for structural metadata and interaction lineage |
| Emotion Adapter | `adapters/emotion.py` | Decoupled I/O wrapper for the emotion engine |
| TTS Adapter | `adapters/tts.py` | ElevenLabs Text-to-Speech integration |

---

## 4. Request Lifecycle

The following sequence describes the full processing pipeline for a single `/chat` request:

```
1. GATEKEEPING
   └─ Rate Limiter checks client IP
   └─ API token validated from Authorization header

2. INTENT ANALYSIS
   └─ Input text classified by Intent Analyzer
   └─ Arousal Detection Matrix scores the input (0.0–1.0)

3. COGNITIVE PROCESSING
   └─ Arousal score updates the active session's Emotion Engine state
   └─ Cognitive Monologue appends a new internal thought to the FIFO queue
   └─ Relationship Engine recalculates intimacy stage and trust delta

4. CONTEXT INGESTION (RAG)
   └─ Input is embedded using text-embedding-3-large
   └─ FAISS / Qdrant queried for semantically relevant memory fragments
   └─ Neo4j queried for structural/behavioural lineage

5. PROMPT SYNTHESIS
   └─ System instruction assembled from:
       • Active persona profile rules
       • Current emotional state snapshot
       • Cognitive monologue (last N thoughts)
       • Retrieved memory fragments
   └─ Context Allocator reserves response capacity, applies section budgets,
      and retains the newest history that fits the model context window
   └─ Critical persona/rule text is allocated before dynamic relationship,
      cognitive, memory, and history context

6. RESPONSE GENERATION
   └─ LLM streams output via Server-Sent Events (SSE)

7. SENSORY FEEDBACK (conditional)
   └─ If arousal ≥ threshold → ElevenLabs TTS audio generated
   └─ If arousal ≥ threshold → DALL-E 3 image URL generated
   └─ Media URLs attached to response payload

8. MEMORY COMMIT
   └─ Transaction logged asynchronously to JSON session file
   └─ Embedding written to vector store
```

---

## 5. Data Storage Strategy

### 5.1 Vector Storage (Semantic Memory)

- **Engine:** FAISS (local) or Qdrant (remote/cloud)
- **Chunking:** 100–150 tokens per chunk, 20-token overlap
- **Embedding Model:** `text-embedding-3-large` (OpenAI)
- **Use Case:** Retrieving historically relevant facts and conversation fragments

### 5.2 Graph Storage (Structural Memory)

- **Engine:** Neo4j
- **Use Case:** Mapping interaction metadata, behavioural lineage, and relationship progression
- **Benefit:** Enables traversal queries that vector search cannot express (e.g. "all events that led to trust increase")

### 5.3 Session Storage (Ephemeral State)

- **Engine:** Local JSON files
- **Scope:** Per-session, isolated memory pools
- **Eviction:** TTL-based (configurable, default 3600 s)
- **Security:** Prevents cross-session data contamination

---

## 6. Multi-Modal Pipeline

```
User Input
    │
    ├─ Text  ──────────────────────────────► LLM (GPT-4o / OpenRouter)
    │                                              │
    ├─ Voice Note (Telegram) ──► Whisper STT ─────┤
    │                                              │
    └─ Image Upload ───────────────────────────────┘
                                                   │
                                            Response Text
                                                   │
                              ┌────────────────────┼────────────────────┐
                              │                    │                    │
                         Text Reply          TTS Audio           DALL-E 3 Image
                         (SSE Stream)    (ElevenLabs)          (if arousal ≥ θ)
```

---

## 7. Deployment Topology

### Local Development

```
localhost:8000  ←→  FastAPI (server.py)
localhost:8081  ←→  Memory Service (memory_service.py)
localhost:6333  ←→  Qdrant (Docker)
localhost:7474  ←→  Neo4j (Docker)
```

Start all services:
```bash
./all_in_one_start.bat   # Windows
```

### Google Cloud Run (Production)

```
Internet
    │
    ▼
Cloud Run Service  (asia-southeast1)
    │
    ├─ FastAPI Container (auto-scaled)
    └─ Qdrant Cloud  /  Neo4j Aura  (managed databases)
```

Deploy:
```bash
bash deploy.sh
```

---

## 8. Configuration Reference

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | OpenAI API key (required) |
| `NAMO_LLM_ENABLED` | `0` | Enable LLM-powered responses (`1` = on) |
| `NAMO_LLM_MODEL` | `gpt-4o-mini` | LLM model identifier |
| `NAMO_LLM_TEMPERATURE` | `0.85` | Sampling temperature |
| `NAMO_LLM_MAX_TOKENS` | `240` | Maximum tokens per response |
| `NAMO_LLM_MEMORY_TURNS` | `6` | Number of past turns included in context |
| `NAMO_LLM_CONTEXT_WINDOW` | `8192` | Total model context window used by Omega prompt allocation |
| `TELEGRAM_TOKEN` | — | Telegram Bot API token |
| `ELEVENLABS_API_KEY` | — | ElevenLabs API key |
| `ELEVENLABS_VOICE_ID` | — | ElevenLabs voice identifier |
| `QDRANT_URL` | — | Qdrant instance URL |
| `NEO4J_URI` | — | Neo4j connection URI |
| `MEMORY_API_URL` | — | Remote memory service URL |
| `MEMORY_LOGGING` | `0` | Log interactions to memory service (`1` = on) |
| `PUBLIC_BASE_URL` | — | Base URL for absolute media asset URLs |
| `CORS_ALLOW_ORIGINS` | `*` | Allowed CORS origins |
| `NAMO_API_URL` | — | API URL used by the Telegram bot |
| `NAMO_API_TIMEOUT` | `30` | Timeout (seconds) for Telegram bot API calls |
| `TELEGRAM_SHOW_STATUS` | `0` | Append system status to Telegram messages |
| `TELEGRAM_INCLUDE_MEDIA` | `0` | Attach media URLs in Telegram messages |
