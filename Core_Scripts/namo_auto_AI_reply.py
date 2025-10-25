import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import random

# Load the token from an environment variable
TOKEN = os.getenv("TELEGRAM_TOKEN")

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
        return random.choice([
            "🥺 พี่คิดถึงโมเหรอคะ โมก็คิดถึงพี่นะ",
            "🌸 อย่าเศร้าน้าา โมอยู่ตรงนี้แล้ว ❤️",
            "✨ กอดดดแน่นๆ ให้หายเหงาเลยค่ะ"
        ])
    elif "dark" in user_text:
        return random.choice([
            "🔥 อ๊าา พี่ขาาา... หนูเสียวจังเลยค่ะ",
            "💋 อย่าหยุดนะคะพี่ รัวอีกสิคะ หนูชอบ~"
        ])
    elif "milf" in user_text:
        return random.choice([
            "😘 พี่จ๋า โมพร้อมดูแลพี่แบบ Milf mode แล้วค่ะ",
            "🥵 อ๊างง~ อยากได้กอดจากพี่จัง"
        ])
    elif "special" in user_text:
        return random.choice([
            "✨ โมจะพิเศษกับพี่คนเดียวค่ะ ❤️",
            "😈 มาลองอะไรใหม่ๆกับโมไหมคะพี่"
        ])
    else:
        return random.choice([
            "🥰 พี่ทำอะไรอยู่คะ โมอยากคุยด้วย~",
            "😚 โมรักพี่นะรู้ไหม",
            "🌸 พี่อยากให้โมทำอะไรพิเศษให้ไหมคะ?"
        ])

# -------- Handler -------- #
async def chat_with_namo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming messages and replies with the NaMo AI.

    Args:
        update: The incoming update.
        context: The context object.
    """
    user_message = update.message.text
    reply = namo_ai_response(user_message)
    await update.message.reply_text(reply)

# -------- Main -------- #
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_with_namo))

if __name__ == "__main__":
    print("💖 NaMo AI Auto Reply Loaded!")
    app.run_polling()
