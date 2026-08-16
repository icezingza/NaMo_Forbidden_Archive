---
name: namo-acc-guide
description: Comprehensive guide for NaMo Forbidden Archive (ACC - Advanced Conversational Core), 5D Emotion Modeling, Cognitive Stream, and LLM Token Optimization.
---

# 🧠 NaMo ACC (Advanced Conversational Core) Developer Guide

## 1. System Architecture Overview
NaMo Forbidden Archive is a high-performance multimodal conversational AI engine featuring:
* **Continuous 5D Emotional Simulation**: Arousal, Trust, Passion, Temperament, Resonance with temporal momentum.
* **Cognitive Stream**: Autonomous internal reasoning queue (Impulse → Reflection → Conflict).
* **Dual-Layer Memory**: Vector Search (FAISS/Qdrant) + Structural Graph (Neo4j).
* **FastAPI Gateway & Telegram Bot**: Sliding-window rate-limited SSE streaming REST endpoints.

---

## 2. LLM Optimization Engine (`core/llm_optimization.py`)
To minimize token costs by up to 95%:
1. **Prompt Cache**: Structuring static persona system prompts with `cache_control: {"type": "ephemeral"}`.
2. **Thinking Budget**: Allocating reasoning tokens dynamically (`low`: 1024, `medium`: 2048, `high`: 4096).
3. **Cache Miss Prevention**: Validating prefix stability to avoid cache misses caused by dynamic ISO timestamps or UUIDs.

---

## 3. Key Core Modules & Entry Points

| Module Path | Responsibilities |
| :--- | :--- |
| `core/model_router.py` | Model request validation, provider selection, and transport routing |
| `core/llm_optimization.py` | Prompt Caching, Thinking Budgeting, and Cache Audit |
| `core/emotion_engine.py` | 5D emotion state calculations, inertia decay, and resonance vectoring |
| `core/cognitive_stream.py` | Internal monologue reasoning stream |
| `server.py` | FastAPI gateway endpoint definitions (`/chat`, `/health`, `/media`) |
