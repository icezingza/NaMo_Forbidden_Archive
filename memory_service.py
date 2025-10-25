
import json
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# --- Pydantic Models based on OpenAPI Spec ---

class EmotionContext(BaseModel):
    """
    Defines the emotional context of a memory record.
    """
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1)
    emotion_type: Optional[str] = None # In a real scenario, this would be an Enum
    intensity: Optional[int] = Field(None, ge=1, le=10)

class MemoryStorageRequest(BaseModel):
    """
    Represents a request to store a new memory.
    """
    content: str
    type: str = "contextual"
    session_id: Optional[str] = None
    emotion_context: Optional[EmotionContext] = None
    dharma_tags: Optional[List[str]] = None # We will map this to Dark Erotic Concepts

class MemoryRecord(MemoryStorageRequest):
    """
    Represents a memory record that has been stored.

    Inherits from MemoryStorageRequest and adds fields for the record's ID
    and creation timestamp.
    """
    id: str
    created_at: datetime

class MemoryQuery(BaseModel):
    """
    Defines a query for recalling memories from the service.
    """
    query: Optional[str] = None
    memory_types: Optional[List[str]] = ["short-term", "long-term", "contextual"]
    emotion_filter: Optional[EmotionContext] = None
    # Re-mapped field
    dark_concepts_filter: Optional[List[str]] = None
    time_range: Optional[Dict[str, datetime]] = None
    limit: int = 10

# --- Augmented MemoryManager ---

class MemoryManager:
    """
    Manages the persistence of memory records to a JSON file.

    This class handles loading, saving, storing, and recalling memory records.
    It also provides a thematic re-mapping feature to translate concepts.
    """
    def __init__(self, file_path="memory_protocol.json"):
        """
        Initializes the MemoryManager.

        Args:
            file_path: The path to the JSON file used for memory storage.
        """
        self.file_path = file_path
        self.memory = self.load_memory()

    def load_memory(self) -> dict:
        """
        Loads memory records from the JSON file.

        If the file does not exist, it creates a new one with an empty structure.

        Returns:
            A dictionary containing the loaded memory data.
        """
        if not os.path.exists(self.file_path):
            print(f"[!] Memory file not found, creating new one: {self.file_path}")
            # Added a top-level key to store records
            return {"records": [], "protocol_metadata": {}}
        with open(self.file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"records": [], "protocol_metadata": {}}

    def save_memory(self):
        """
        Saves the current memory state to the JSON file.

        Uses a custom JSON encoder to handle datetime objects.
        """
        # Custom JSON encoder to handle datetime
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, datetime):
                    return o.isoformat()
                return json.JSONEncoder.default(self, o)
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)

    def store_record(self, memory_request: MemoryStorageRequest) -> MemoryRecord:
        """
        Stores a new memory record.

        Assigns a unique ID and timestamp, performs thematic re-mapping, and
        saves the new record to the memory file.

        Args:
            memory_request: The request object containing the memory data.

        Returns:
            The newly created MemoryRecord object.
        """
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
        """
        Recalls memory records based on a query.

        This is a simplified implementation that returns the last N records.
        A real implementation would use a more sophisticated search.

        Args:
            query: The query object specifying recall parameters.

        Returns:
            A list of MemoryRecord objects.
        """
        # This is a simple, non-optimized search for demonstration.
        # To prevent parroting, we recall from all memories *except* the most recent one.
        # A more sophisticated approach would filter by recency or content similarity.
        
        searchable_records = self.memory['records'][:-1] # Exclude the last element

        records_to_return = searchable_records[-query.limit:]
        return [MemoryRecord(**rec) for rec in records_to_return]

    def remap_to_dark(self, dharma_tags: List[str]) -> List[str]:
        """
        Remaps a list of "dharma tags" to "dark erotic concepts".

        Args:
            dharma_tags: A list of tags to be remapped.

        Returns:
            A list of remapped tags.
        """
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
    Stores a new memory record in the memory service.

    Thematic re-mapping from 'dharma_tags' to 'dark_concepts' is applied
    automatically if 'dharma_tags' are provided in the request.

    Args:
        request: A MemoryStorageRequest object from the request body.

    Returns:
        The created MemoryRecord object.
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

    This is a simplified implementation that returns the most recent records
    up to the specified limit.

    Args:
        query: A MemoryQuery object from the request body.

    Returns:
        A list of matching MemoryRecord objects.
    """
    try:
        records = memory_manager.recall_records(query)
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Provides a health check endpoint for the memory service.

    Returns:
        A dictionary with the service status and the current number of records.
    """
    return {"status": "ok", "memory_records": len(memory_manager.memory.get("records", []))}

print("Memory Service script created. Ready to be run with Uvicorn.")
