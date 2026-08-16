import json
import logging
import os
from datetime import datetime
from threading import Lock
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from config import settings, setup_logging
from core.exceptions import NamoAPIError, error_payload

setup_logging()
logger = logging.getLogger("namo.memory")

# --- Pydantic Models based on OpenAPI Spec ---


class EmotionContext(BaseModel):
    """Defines the emotional context of a memory record."""

    sentiment_score: float | None = Field(None, ge=-1, le=1)
    emotion_type: str | None = None  # In a real scenario, this would be an Enum
    intensity: int | None = Field(None, ge=1, le=10)


class MemoryStorageRequest(BaseModel):
    """Represents a request to store a new memory."""

    content: str
    type: str = "contextual"
    session_id: str | None = None
    emotion_context: EmotionContext | None = None
    dharma_tags: list[str] | None = None  # We will map this to Dark Erotic Concepts
    sin_stats: dict | None = None


class MemoryRecord(MemoryStorageRequest):
    """Represents a memory record that has been stored.

    Inherits from MemoryStorageRequest and adds fields for the record's ID
    and creation timestamp.
    """

    id: str
    created_at: datetime
    dark_concepts: list[str] | None = None  # Remapped from dharma_tags on store


class MemoryQuery(BaseModel):
    """Defines a query for recalling memories from the service."""

    query: str | None = None
    memory_types: list[str] | None = ["short-term", "long-term", "contextual"]
    emotion_filter: EmotionContext | None = None
    # Re-mapped field
    dark_concepts_filter: list[str] | None = None
    time_range: dict[str, datetime] | None = None
    limit: int = 10


# --- Augmented MemoryManager ---


class MemoryManager:
    """Manages the persistence of memory records to a JSON file.

    This class handles loading, saving, storing, and recalling memory records.
    It also provides a thematic re-mapping feature to translate concepts.
    """

    def __init__(self, file_path: str | None = None):
        """Initializes the MemoryManager.

        Args:
            file_path: The path to the JSON file. If None, it defaults to the
                       MEMORY_FILE_PATH environment variable, or "memory_protocol.json".
        """
        self.file_path = file_path or settings.memory_file_path
        self.memory = self.load_memory()
        self._lock = Lock()

    def load_memory(self) -> dict:
        """Loads memory records from the JSON file.

        If the file does not exist, it creates a new one with an empty structure.

        Returns:
            A dictionary containing the loaded memory data.
        """
        if not os.path.exists(self.file_path):
            logger.info("[MemoryService]: creating new memory file: %s", self.file_path)
            # Added a top-level key to store records
            return {"records": [], "protocol_metadata": {}}
        with open(self.file_path) as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"records": [], "protocol_metadata": {}}

    def save_memory(self):
        """Saves the current memory state to the JSON file.

        Uses a custom JSON encoder to handle datetime objects.
        """

        # Custom JSON encoder to handle datetime
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, datetime):
                    return o.isoformat()
                return json.JSONEncoder.default(self, o)

        with open(self.file_path, "w") as f:
            json.dump(
                self.memory, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder
            )

    def store_record(self, memory_request: MemoryStorageRequest) -> MemoryRecord:
        new_id = (
            f"mem_{int(datetime.now().timestamp())}_"
            f"{len(self.memory['records'])}"
        )
        record_data = memory_request.dict()
        record_data["id"] = new_id
        record_data["created_at"] = datetime.now()

        # Thematic Re-mapping
        if record_data.get("dharma_tags"):
            record_data["dark_concepts"] = self.remap_to_dark(
                record_data.pop("dharma_tags")
            )

        new_record = MemoryRecord(**record_data)
        self.memory["records"].append(new_record.dict())
        self.save_memory()
        return new_record

    def recall_records(self, query: MemoryQuery) -> List[MemoryRecord]:
        # This is a simple, non-optimized search for demonstration.
        # To prevent parroting, we recall from all memories *except* the most
        # recent one. A more sophisticated approach would filter by recency or
        # content similarity.

        searchable_records = self.memory["records"][:-1]  # Exclude the last element

        records_to_return = searchable_records[-query.limit :]
        return [MemoryRecord(**rec) for rec in records_to_return]

    def remap_to_dark(self, dharma_tags: list[str]) -> list[str]:
        """Remaps a list of dharma tags to dark erotic concepts."""
        mapping = {
            "wisdom": "Forbidden Knowledge",
            "compassion": "Obsessive Desire",
            "serenity": "Tension & Release",
        }
        return [mapping.get(tag, tag) for tag in dharma_tags]
