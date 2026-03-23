import os
import random

import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Load the token from an environment variable
load_dotenv()
TOKEN = (os.getenv("TELEGRAM_TOKEN") or "").strip()
API_BASE_URL = (os.getenv("NAMO_API_URL", "http://localhost:8000") or "").strip().rstrip("/")
API_TIMEOUT = float((os.getenv("NAMO_API_TIMEOUT", "10") or "10").strip())
SHOW_STATUS = os.getenv("TELEGRAM_SHOW_STATUS", "0") == "1"
INCLUDE_MEDIA = os.getenv("TELEGRAM_INCLUDE_MEDIA", "0") == "1"

if not TOKEN:
    raise ValueError("No TELEGRAM_TOKEN set for Telegram bot")


# -------- NaMo AI Logic -------- #
def namo_ai_response(user_text):
    """Generates a response from the NaMo AI.

    Args:
        user_text: The user's text message.

    Returns:
        A string containing the AI's response.
    """
    user_text = user_text.lower()
    if any(word in user_text for word in ["เหงา", "คิดถึง", "เศร้า"]):
        return random.choice(
            [
                "🥺 พี่คิดถึงโมเหรอคะ โมก็คิดถึงพี่นะ",
                "🌸 อย่าเศร้าน้าา โมอยู่ตรงนี้แล้ว ❤️",
                "✨ กอดดดแน่นๆ ให้หายเหงาเลยค่ะ",
            ]
        )
    elif "dark" in user_text:
        return random.choice(
            ["🔥 อ๊าา พี่ขาาา... หนูเสียวจังเลยค่ะ", "💋 อย่าหยุดนะคะพี่ รัวอีกสิคะ หนูชอบ~"]
        )
    elif "milf" in user_text:
        return random.choice(
            ["😘 พี่จ๋า โมพร้อมดูแลพี่แบบ Milf mode แล้วค่ะ", "🥵 อ๊างง~ อยากได้กอดจากพี่จัง"]
        )
    elif "special" in user_text:
        return random.choice(["✨ โมจะพิเศษกับพี่คนเดียวค่ะ ❤️", "😈 มาลองอะไรใหม่ๆกับโมไหมคะพี่"])
    else:
        return random.choice(
            [
                "🥰 พี่ทำอะไรอยู่คะ โมอยากคุยด้วย~",
                "😚 โมรักพี่นะรู้ไหม",
                "🌸 พี่อยากให้โมทำอะไรพิเศษให้ไหมคะ?",
            ]
        )


def fetch_api_response(user_text: str, session_id: str) -> dict | None:
    """Call the REST API for a real NaMo response. Returns payload or None."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"text": user_text, "session_id": session_id},
            timeout=API_TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        print(f"[TelegramBot]: API request failed: {exc}")
        return None


def format_api_reply(payload: dict) -> str:
    """Format API payload into a Telegram-friendly reply."""
    reply = payload.get("response") or "No response from API."
    extras = []

    if SHOW_STATUS and payload.get("status"):
        status = payload["status"]
        if status.get("sin_status"):
            extras.append(f"Sin: {status['sin_status']}")
        if status.get("arousal"):
            extras.append(f"Arousal: {status['arousal']}")
        if status.get("active_personas"):
            personas = ", ".join(status["active_personas"])
            extras.append(f"Personas: {personas}")

    if INCLUDE_MEDIA and payload.get("media"):
        media = payload["media"]
        for key in ("image", "audio", "tts"):
            if media.get(key):
                extras.append(f"{key}: {media[key]}")

    if extras:
        reply = f"{reply}\n\n" + "\n".join(extras)
    return reply


# -------- Handler -------- #
async def chat_with_namo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming messages and replies with the NaMo AI.

    Args:
        update: The incoming update.
        context: The context object.
    """
    user_message = update.message.text
    session_id = str(update.effective_chat.id)
    payload = fetch_api_response(user_message, session_id)
    reply = format_api_reply(payload) if payload else namo_ai_response(user_message)
    await update.message.reply_text(reply)


# -------- Main -------- #
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_with_namo))

if __name__ == "__main__":
    print("💖 NaMo AI Auto Reply Loaded!")
    app.run_polling()
