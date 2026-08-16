import os

TOKEN = os.environ.get("TELEGRAM_TOKEN", "") or os.environ.get("TELEGRAM_BOT_TOKEN", "")

if not TOKEN:
    raise ValueError("No TELEGRAM_TOKEN set for Telegram bot")
