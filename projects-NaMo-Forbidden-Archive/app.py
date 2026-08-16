from fastapi import FastAPI, HTTPException
from llm_provider_v2 import LLMProvider
from memory_service_v2 import MemoryService
from pydantic import BaseModel

app = FastAPI(
    title="NaMo Forbidden Archive (ACC) API",
    description="Virtual ACC Server running on Gemini 1.5 Flash Brain",
    version="2.0.0",
)

# Initialize Providers
llm_provider = LLMProvider()
memory_service = MemoryService()


class ChatRequest(BaseModel):
    session_id: str
    text: str


class ResetRequest(BaseModel):
    session_id: str


@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "NaMo Forbidden Archive (ACC) Virtual Server",
        "brain": "Gemini 1.5 Flash (Context Few-Shot Mode)",
    }


@app.post("/session/chat")
async def chat_endpoint(payload: ChatRequest):
    """
    Main endpoint for roleplay and conversation processing.
    Integrates 5D Emotion Engine, Context Memory, and Cognitive Stream.
    """
    try:
        session_id = payload.session_id
        user_message = payload.text

        # 1. Fetch current session state (Emotion Engine & Stage)
        session_state = await memory_service.get_session_state(session_id)

        # 2. Add Context RAG or Few-shot parameters (Handled internally or by sending history)
        # In our optimized brain mode, the entire dataset can be loaded as system instruction,
        # but we also append recent chat turns for short-term memory.
        chat_history = await memory_service.get_chat_history(session_id, limit=10)
        session_state["rag_context"] = chat_history

        # 3. Generate response via Gemini Flash (Brain)
        response_data = await llm_provider.generate_response(user_message, session_state)

        if "error_code" in response_data:
            raise HTTPException(
                status_code=response_data["error_code"], detail=response_data["message"]
            )

        # 4. Save interaction and update 5D state in GCS / Local Memory
        await memory_service.save_interaction(
            session_id=session_id, user_message=user_message, response_data=response_data
        )

        return response_data

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """
    Retrieve current 5D Emotion State and Stage for a session.
    """
    try:
        state = await memory_service.get_session_state(session_id)
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/session/reset")
async def reset_session(payload: ResetRequest):
    """
    Reset a session back to initial Stage 1 values.
    """
    try:
        await memory_service.reset_session(payload.session_id)
        return {"status": "success", "message": f"Session {payload.session_id} has been reset."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
