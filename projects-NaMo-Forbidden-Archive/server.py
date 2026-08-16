import os
import logging
from fastapi import FastAPI, HTTPException, Body, Header
from pydantic import BaseModel
from typing import Dict, Any, Optional
import httpx
from llm_provider_v2 import LLMProvider
from memory_service_v2 import MemoryService
from telegram_security import validate_telegram_update, get_user_session_id
from rate_limiter import rate_limiter
from health_check import health_check, liveness_probe, readiness_probe
from logger_config import logger

app = FastAPI(
    title="NaMo Forbidden Archive (ACC) + Telegram",
    description="Virtual ACC Server with Telegram Bot Integration",
    version="2.0.0"
)

# Initialize Providers
llm_provider = LLMProvider()
memory_service = MemoryService()

# Telegram Config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# ============= REST API MODELS =============

class ChatRequest(BaseModel):
    session_id: str
    text: str

class ResetRequest(BaseModel):
    session_id: str

# ============= HEALTH CHECK ENDPOINTS =============

@app.get("/health")
async def health():
    """Detailed health check."""
    return await health_check()

@app.get("/live")
async def live():
    """Kubernetes liveness probe."""
    return await liveness_probe()

@app.get("/ready")
async def ready():
    """Kubernetes readiness probe."""
    return await readiness_probe()

# ============= REST API ENDPOINTS =============

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "NaMo Forbidden Archive (ACC) Virtual Server",
        "brain": "Gemini 1.5 Flash (Context Few-Shot Mode)",
        "telegram": "enabled",
        "version": "2.0.0"
    }

@app.post("/chat")
@app.post("/session/chat")
async def chat_endpoint(payload: ChatRequest):
    """
    Main endpoint for roleplay and conversation processing.
    """
    try:
        session_id = payload.session_id
        user_message = payload.text

        # Check rate limit
        if not rate_limiter.is_allowed(session_id):
            logger.warning(f"Rate limit exceeded for user {session_id}")
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please wait a moment."
            )

        # Fetch current session state
        session_state = await memory_service.get_session_state(session_id)
        
        # Generate response via Gemini Flash
        response_data = await llm_provider.generate_response(user_message, session_state)

        if "error_code" in response_data:
            raise HTTPException(
                status_code=response_data["error_code"],
                detail=response_data["message"]
            )

        # Save interaction
        await memory_service.save_interaction(
            session_id=session_id,
            user_message=user_message,
            response_data=response_data
        )

        logger.info(f"Chat completed for user {session_id}")
        return response_data

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in chat_endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "namo-acc",
        "version": "2.0.0"
    }

@app.get("/live")
async def live():
    return {"status": "alive"}

@app.get("/ready")
async def ready():
    return {"status": "ready"}

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Retrieve current 5D Emotion State and Stage for a session."""
    try:
        state = await memory_service.get_session_state(session_id)
        return state
    except Exception as e:
        logger.error(f"Error in get_session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/session/reset")
async def reset_session(payload: ResetRequest):
    """Reset a session back to initial Stage 1 values."""
    try:
        state = await memory_service.get_session_state(payload.session_id)
        state["relationship_stage"] = 1
        state["stage_progress"] = "0/25"
        state["emotion_state"] = {
            "arousal": 0.2,
            "trust": 0.4,
            "passion": 0.1,
            "temperament": 0.7,
            "resonance": 0.3
        }
        state["history"] = []
        
        await memory_service.save_interaction(
            session_id=payload.session_id,
            user_message="[SYSTEM RESET]",
            response_data=state
        )
        
        logger.info(f"Session reset for user {payload.session_id}")
        return {"status": "success", "message": f"Session {payload.session_id} has been reset."}
    except Exception as e:
        logger.error(f"Error in reset_session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============= TELEGRAM WEBHOOK ENDPOINTS =============

@app.post("/webhook/telegram")
async def telegram_webhook(
    update: Dict[str, Any],
    x_telegram_bot_api_secret_hash: str = Header(None)
):
    """
    Telegram webhook endpoint - receives messages and forwards to ACC brain.
    Validates webhook signature for security.
    """
    try:
        # Validate webhook
        if not validate_telegram_update(update, x_telegram_bot_api_secret_hash):
            logger.warning(f"Invalid Telegram update received")
            return {"ok": False, "error": "Invalid signature"}
        
        logger.info(f"Telegram update received: {update.get('update_id')}")
        
        # Extract message data
        if "message" not in update:
            return {"ok": True}
        
        message = update["message"]
        user_id = get_user_session_id(update)
        chat_id = message["chat"]["id"]
        user_text = message.get("text", "")

        if not user_text or not user_id:
            return {"ok": True}

        # Rate limit check
        if not rate_limiter.is_allowed(user_id):
            await send_telegram_message(chat_id, "⏱️ Too many messages. Please wait a moment.")
            logger.warning(f"Rate limit hit for Telegram user {user_id}")
            return {"ok": True}

        # Handle special commands
        if user_text.startswith("/start"):
            welcome_text = (
                "🌹 **Welcome to Vipha - NaMo Forbidden Archive (ACC)**\n\n"
                "I'm Vipha, a 42-year-old elegant and intense neighbor.\n"
                "Your reserved partner will be waiting...\n\n"
                "Just send me a message to begin our conversation.\n"
                "_Commands: /reset to start over_"
            )
            await send_telegram_message(chat_id, welcome_text)
            logger.info(f"Start command from user {user_id}")
            return {"ok": True}

        if user_text.startswith("/reset"):
            await reset_session(ResetRequest(session_id=user_id))
            await send_telegram_message(chat_id, "✨ Session reset. Let's start fresh...")
            logger.info(f"Reset command from user {user_id}")
            return {"ok": True}

        # Process chat message through ACC brain
        chat_request = ChatRequest(session_id=user_id, text=user_text)
        response = await chat_endpoint(chat_request)

        # Extract Vipha's narrative response
        vipha_narrative = response.get("narrative", "I'm thinking...")
        emotion_state = response.get("emotion_state", {})
        hook = response.get("hook", "")
        relationship_stage = response.get("relationship_stage", 1)

        # Format response with emotion indicators
        formatted_response = (
            f"{vipha_narrative}\n\n"
            f"💌 **Emotional State:**\n"
            f"• Arousal: {emotion_state.get('arousal', 0):.0%}\n"
            f"• Trust: {emotion_state.get('trust', 0):.0%}\n"
            f"• Passion: {emotion_state.get('passion', 0):.0%}\n"
            f"• Temperament: {emotion_state.get('temperament', 0):.0%}\n"
            f"• Resonance: {emotion_state.get('resonance', 0):.0%}\n\n"
            f"📍 *Stage {relationship_stage}*\n"
            f"_{hook}_"
        )

        await send_telegram_message(chat_id, formatted_response)
        logger.info(f"Response sent to user {user_id}")

        return {"ok": True}

    except Exception as e:
        logger.error(f"Error in telegram_webhook: {e}", exc_info=True)
        try:
            await send_telegram_message(
                message.get("chat", {}).get("id", ""),
                f"❌ Error: {str(e)[:100]}"
            )
        except:
            pass
        return {"ok": False, "error": str(e)}

# ============= TELEGRAM API HELPERS =============

async def send_telegram_message(chat_id: int, text: str):
    """Send a message to Telegram chat."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = f"{TELEGRAM_API_URL}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            response = await client.post(url, json=payload)
            if response.status_code != 200:
                logger.error(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")

async def register_telegram_webhook(webhook_url: str):
    """Register webhook with Telegram."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = f"{TELEGRAM_API_URL}/setWebhook"
            payload = {"url": webhook_url}
            response = await client.post(url, json=payload)
            logger.info(f"Webhook registration response: {response.json()}")
            return response.json()
    except Exception as e:
        logger.error(f"Error registering webhook: {e}")
        raise

@app.post("/telegram/register-webhook")
async def register_webhook(webhook_url: str):
    """Endpoint to manually register Telegram webhook."""
    result = await register_telegram_webhook(webhook_url)
    return result

@app.get("/telegram/webhook-info")
async def get_webhook_info():
    """Get current Telegram webhook info."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            url = f"{TELEGRAM_API_URL}/getWebhookInfo"
            response = await client.get(url)
            return response.json()
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        raise

# ============= STARTUP =============

@app.on_event("startup")
async def startup():
    """On startup, log system info."""
    logger.info("=" * 60)
    logger.info("✨ NaMo Forbidden Archive (ACC) + Telegram Bot Starting...")
    logger.info(f"Bot Token: {'✅ Set' if TELEGRAM_BOT_TOKEN else '❌ Not set'}")
    logger.info(f"Version: 2.0.0")
    logger.info(f"Debug Mode: {os.getenv('DEBUG', 'false')}")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown():
    """On shutdown, log info."""
    logger.info("🛑 NaMo ACC Bot shutting down...")
