# Architecture Overview

## System Goals
- Clarity: แยก core logic ออกจาก IO และ external services
- Testability: โมดูลหลักต้องทดสอบแยกได้
- Reproducibility: ใช้ config และ tooling เดียวกันกับ CI

## Components
- `core/` กลไกหลัก (DarkNaMoSystem, MetaphysicalDialogueEngine, NaMoOmegaEngine)
- `adapters/` IO adapters (emotion API, memory JSON, TTS)
- `server.py` REST API สำหรับ NaMoOmegaEngine
- `memory_service.py` Memory service แยกต่างหาก
- `learn_from_set.py` + `query_learned_knowledge.py` สำหรับฐานความรู้แบบ embedding
- `Core_Scripts/` โค้ดทดลอง/สคริปต์เสริม

## Data Flow (Mermaid)
```mermaid
graph TD
    U[User] -->|CLI| APP[app.py / main.py]
    U -->|REST| API[server.py]
    APP --> CORE1[DarkNaMoSystem]
    API --> CORE2[NaMoOmegaEngine]
    CORE1 --> EMO[EmotionAdapter]
    CORE1 --> MEM[MemoryAdapter]
    CORE2 --> TTS[TTSAdapter]
    MEM --> MEMFILE[memory_history.json]
    EMO --> EMOAPI[Emotion Service (optional)]
    TTS --> AUDIO[Audio_Layers/generated]
    KB[learn_from_set.py] --> OPENAI[OpenAI Embeddings]
    OPENAI --> FAISS[vector_db/knowledge.index]
    MEMSVC[memory_service.py] --> MEMPROTO[memory_protocol.json]
```

## Notes
- `server.py` และ `memory_service.py` รันแยก process กันได้
- `learn_from_set.py` ต้องใช้ `OPENAI_API_KEY`
