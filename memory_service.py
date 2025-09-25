
import json
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# --- Pydantic Models based on OpenAPI Spec ---

class EmotionContext(BaseModel):
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1)
    emotion_type: Optional[str] = None # In a real scenario, this would be an Enum
    intensity: Optional[int] = Field(None, ge=1, le=10)

class MemoryStorageRequest(BaseModel):
    content: str
    type: str = "contextual"
    session_id: Optional[str] = None
    emotion_context: Optional[EmotionContext] = None
    dharma_tags: Optional[List[str]] = None # We will map this to Dark Erotic Concepts

class MemoryRecord(MemoryStorageRequest):
    id: str
    created_at: datetime

class MemoryQuery(BaseModel):
    query: Optional[str] = None
    memory_types: Optional[List[str]] = ["short-term", "long-term", "contextual"]
    emotion_filter: Optional[EmotionContext] = None
    # Re-mapped field
    dark_concepts_filter: Optional[List[str]] = None
    time_range: Optional[Dict[str, datetime]] = None
    limit: int = 10

# --- Augmented MemoryManager ---

class MemoryManager:
    def __init__(self, file_path="memory_protocol.json"):
        self.file_path = file_path
        self.memory = self.load_memory()

    def load_memory(self):
        if not os.path.exists(self.file_path):
            print(f"[!] Memory file not found, creating new one: {self.file_path}")
            # Added a top-level key to store records
            return {"records": [], "protocol_metadata": {}}
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_memory(self):
        # Custom JSON encoder to handle datetime
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, datetime):
                    return o.isoformat()
                return json.JSONEncoder.default(self, o)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)

    def store_record(self, memory_request: MemoryStorageRequest) -> MemoryRecord:
        new_id = f"mem_{int(datetime.now().timestamp())}_{len(self.memory['records'])}"
        record_data = memory_request.dict()
        record_data['id'] = new_id
        record_data['created_at'] = datetime.now()
        
        # Thematic Re-mapping
        if record_data.get('dharma_tags'):
            record_data['dark_concepts'] = self.remap_to_dark(record_data.pop('dharma_tags'))

        new_record = MemoryRecord(**record_data)
        self.memory['records'].append(new_record.dict())
        self.save_memory()
        return new_record

    def recall_records(self, query: MemoryQuery) -> List[MemoryRecord]:
        # This is a simple, non-optimized search for demonstration.
        # A real implementation would use BigQuery with vector search as designed.
        
        # For now, just return the last N records.
        records_to_return = self.memory['records'][-query.limit:]
        return [MemoryRecord(**rec) for rec in records_to_return]

    def remap_to_dark(self, dharma_tags: List[str]) -> List[str]:
        mapping = {
            "metta": "Obsession",
            "karuna": "Sadistic Empathy",
            "mudita": "Conquest Joy",
            "upekkha": "Cold Detachment",
            "anicca": "Erosion of Will",
            "dukkha": "Managed Suffering",
            "anatta": "Identity Dissolution",
        }
        return [mapping.get(tag, tag) for tag in dharma_tags]


# --- FastAPI App ---

app = FastAPI(title="Infinity Awareness Engine - Memory Service")
memory_manager = MemoryManager()

@app.post("/store", response_model=MemoryRecord)
async def store(request: MemoryStorageRequest):
    """
    Stores a new memory record.
    Thematic re-mapping from 'dharma_tags' to 'dark_concepts' is applied here.
    """
    try:
        stored_record = memory_manager.store_record(request)
        return stored_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recall", response_model=List[MemoryRecord])
async def recall(query: MemoryQuery):
    """
    Recalls memory records based on a query.
    This is a simplified implementation.
    """
    try:
        records = memory_manager.recall_records(query)
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok", "memory_records": len(memory_manager.memory.get("records", []))}

print("Memory Service script created. Ready to be run with Uvicorn.")
