# Technical Whitepaper: System Architecture of the Advanced Conversational Core (ACC)

## 🌌 Introduction
Modern conversational systems struggle to maintain emotional consistency and retrieve semantic facts over extended user interactions. The **Advanced Conversational Core (ACC)** addresses these limitations through a layered cognitive mesh, coupling multi-modal interfaces, real-time continuous emotional modeling, and dual-layer vector/graph database indexing.

This document details the architectural specifications and data flows within the ACC.

---

## 🏗️ 1. Multi-Tier Architecture

The ACC architecture is segregated into four primary layers to isolate concerns, facilitate easy unit-testing, and support zero-downtime scaling:

```
+-------------------------------------------------------------+
|                        Client Layer                         |
|    - Telegram Auto-Reply Bot   - Static HTML5 Web Client   |
+------------------------------+------------------------------+
                               | (HTTPS / SSE Streaming)
                               v
+-------------------------------------------------------------+
|                      Integration Layer                      |
|    - FastAPI REST Gateway      - Rate Limiter (IP-based)    |
|    - Session TTL Manager       - Engine Registry (Lazy)     |
+------------------------------+------------------------------+
                               | (Async Context Calls)
                               v
+-------------------------------------------------------------+
|                       Cognitive Layer                       |
|    - Arousal Detection Matrix  - Emotion Engine (5D State)  |
|    - Cognitive Monologue Stream - Relationship Logic Engine  |
+------------------------------+------------------------------+
                               | (Query / Dual-Write IO)
                               v
+-------------------------------------------------------------+
|                        Storage Layer                        |
|    - local JSON Session File   - FAISS Knowledge Index      |
|    - remote Neo4j Graph DB     - Qdrant Cognitive Mesh      |
+-------------------------------------------------------------+
```

### 1.1 Client Layer
* **Static Web Client**: Lightweight HTML5/CSS3 interface making asynchronous XMLHttpRequests and Server-Sent Event (SSE) streaming connections to backend endpoints.
* **Sovereign Telegram Bot**: Implements asynchronous voice transcription via OpenAI Whisper, processes local arousal calculations, and triggers DALL-E 3 visual illustrations based on arousal levels.

### 1.2 Integration Layer (REST Gateway)
* **FastAPI Server**: Orchestrates all endpoints. Built-in sliding-window rate limiters prevent denial-of-service attempts by throttling client IPs.
* **Session TTL Manager**: Periodically evicts inactive session states from all loaded memory instances (default: 3600 seconds) to prevent memory leaks and secure privacy.
* **Lazy Engine Registry**: Loads engines (e.g. Omega Core, Dark Core, or simulated reasoning modules) into memory only upon the first request, reducing initialization time.

### 1.3 Cognitive Layer
* **Arousal Detection Matrix (ADM)**: Evaluates incoming messages for arousal triggers based on explicit and implicit keyword dictionaries.
* **Emotion Engine**: Evaluates continuous emotional values (Joy, Arousal, Trust, Passion, Temper) utilizing momentum constants (Inertia = 0.65) and decay rates (Decay = 0.06).
* **Cognitive Stream (Monologue)**: A FIFO thought queue simulating reasoning pathways (Impulse, Reflection, Conflict) which are dynamically prepended to generator prompts.
* **Relationship Engine**: Evolves intimacy levels across relational stages (Stranger, Companion, Partner, Deep Attachment) based on accumulated trust metrics.

### 1.4 Storage & Data Adapters
* All read/write IO operations are decoupled into thin **Adapter Wrappers** (`adapters/`).
* **Vector Storage (FAISS/Qdrant)**: Ingests documents into micro-chunks of 100–150 tokens with a 20-token overlap, yielding precise semantic matching.
* **Graph Storage (Neo4j)**: Maps structural metadata and behavioral lineage to trace interaction reasoning.

---

## ⚡ 2. Core Data Flow & Request Lifecycle

When a client submits input, the following operations run asynchronously:

1. **Gatekeeping**: The Rate Limiter inspects the client IP. The Auth Header verifies the API token mapping.
2. **Intent Analysis**: The input text is evaluated for intents (Affection, Rejection, Lust, commands) and arousal levels.
3. **Cognitive Processing**: 
   * The Arousal score updates the active session's emotional snapshot.
   * The Cognitive Stream appends a new internal thought to the monologue.
   * The Relationship Engine calculates stage progress.
4. **Context Ingestion**: 
   * The input query is embedded using `text-embedding-3-large`.
   * Semantic matching queries FAISS/Qdrant for historic fragments.
5. **Prompt Synthesis**: The generator builds a multi-module system instruction containing the active profile rules, active session stats, cognitive monologue, and retrieved memory fragments.
6. **Response Generation**: The LLM streams the output text back to the client via Server-Sent Events (SSE).
7. **Sensory & TTS Feedback**: If arousal crosses threshold values, synthetic speech files (ElevenLabs TTS) and illustration URLs are attached to the response payload.
8. **Memory Commit**: The transaction is logged asynchronously to the local JSON file.

---

## 🛡️ Ethics, Compliance, and Sandbox Controls
To facilitate safe deployment, all modules containing complex human-simulation or simulated bonding dynamics (BDSM, fetish-teasing, obsessions) are isolated under specific permission sets and flagged with internal compliance comments for regular auditing:
`# NOTE: Contains Experimental Logic - Requires Compliance Review before commercial deployment.`
Additionally, the system implements a runtime safe-word parser (`apologize` or `อภัย`) which bypasses the cognitive core and immediately resets the session to a safe state.
