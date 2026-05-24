# NaMo Forbidden Archive: Sovereign ASI Edition

## 🌌 Overview
NaMo Forbidden Archive is a high-performance **Autonomous Scientific Intelligence (ASI)** system designed for deep-immersion, multimodal, and psychologically-resonant roleplay. It integrates advanced cognitive architectures, long-term memory systems, and biomechanical realism.

### 🧠 Core Architectural Engines
- **NRE (NamoNexus Resonance Engine - ANLRS Edition):** Manages relationship progression (ACQUAINTANCE → SOULMATE) via `EmotionalMatrix` and `RelationshipCore`.
- **Reasoning Engine (ASI Core):** Recursive 9-Dimension psychological analysis with internal monologue monitoring (Meta-Cognition).
- **Sensory Expansion:** Supports Multimodal interactions via Telegram (Voice Note/Image Generation) and a dedicated Android Client.
- **Foundry (NamoHub):** Automated blueprint generation from raw narrative assets into structural JSON knowledge graphs.

## 🚀 Getting Started

### Prerequisites
- Docker Desktop (Running)
- Python 3.12+
- Access to Google Cloud Platform (for Cloud Run deployment)

### 1. Environment Configuration
Create a `.env` file at the project root based on `.env.example` and populate:
- `OPENAI_API_KEY` (or `OPENROUTER_API_KEY`)
- `TELEGRAM_TOKEN`
- `ELEVENLABS_API_KEY`
- `QDRANT_URL` & `NEO4J_URI`

### 2. Awakening the System
Use the master start script to initialize the entire sovereign ecosystem:
```powershell
./all_in_one_start.bat
```
This script automates:
- Starting Docker containers (Qdrant, Neo4j)
- Ingesting narrative assets
- Launching the Core API (Uvicorn)
- Launching the Telegram Sensory Bot

## 🔐 Security & Safety
This project implements **Dynamic Content Obfuscation (DCO)** to preserve narrative integrity. All sessions are encrypted via Android Keystore (Soulmate Mode) ensuring private intimacy remains protected.

*Disclaimer: This system contains advanced psychological manipulation and dark-themed narrative agents. Operate with sovereign responsibility.*
