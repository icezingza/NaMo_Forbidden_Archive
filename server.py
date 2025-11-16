import os
import sys
import uuid

from fastapi import FastAPI
from pydantic import BaseModel

# --- Path Setup ---
# Add Core_Scripts to the Python path to find our custom modules
sys.path.append(os.path.join(os.path.dirname(__file__), "Core_Scripts"))

try:
    from dark_dialogue_engine import DarkDialogueEngine

    print("[INFO] Successfully imported DarkDialogueEngine.")
except ImportError as e:
    print(f"[FATAL] Could not import DarkDialogueEngine: {e}")
    # If this fails, the app can't run at all. We can let it crash.
    raise

# --- FastAPI App Initialization ---
app = FastAPI(
    title="NaMo Forbidden Archive - Web API",
    description="An API to interact with the Dark Dialogue Engine.",
)


# --- Data Models ---
class ChatInput(BaseModel):
    text: str
    session_id: str | None = None


class ChatOutput(BaseModel):
    response: str
    session_id: str
    debug_info: dict


# --- Engine Singleton ---
# Initialize the engine once when the server starts
try:
    engine = DarkDialogueEngine()
    print("[INFO] DarkDialogueEngine initialized successfully.")
except Exception as e:
    print(f"[FATAL] Failed to initialize DarkDialogueEngine: {e}")
    # If the engine fails to start, the server is useless.
    engine = None  # Set to None so endpoints can report an error


# --- API Endpoints ---
@app.get("/", summary="Root endpoint for health check")
def read_root():
    """
    Provides a simple status message to confirm the server is running.
    """
    return {"status": "NaMo Forbidden Archive API is running."}


@app.post("/chat", response_model=ChatOutput, summary="Interact with the dialogue engine")
async def chat_with_engine(payload: ChatInput):
    """
    Processes user input through the Dark Dialogue Engine.

    - **text**: The user's message to the engine.
    - **session_id**: (Optional) A unique ID for the conversation. If not provided, a new one will be generated.
    """
    if not engine:
        return {
            "response": "Error: Dialogue engine is not available.",
            "session_id": payload.session_id or "n/a",
            "debug_info": {"error": "Engine failed to initialize at startup."},
        }

    session_id = payload.session_id or str(uuid.uuid4())

    try:
        result = engine.process_input(payload.text, session_id)

        return {
            "response": result.get("response", "(No response)"),
            "session_id": session_id,
            "debug_info": {
                "arousal_level": result.get("arousal_level", 0),
                "intensity_category": result.get("intensity_category", "N/A"),
            },
        }
    except Exception as e:
        return {
            "response": f"An error occurred: {e}",
            "session_id": session_id,
            "debug_info": {"error": str(e)},
        }
