"""
Enhanced security module for Telegram webhook validation.
"""

import hashlib
import hmac
import os
from typing import Any

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


def validate_telegram_update(
    update: dict[str, Any], x_telegram_bot_api_secret_hash: str = None
) -> bool:
    """
    Validate incoming Telegram webhook update.
    Telegram signs updates using HMAC-SHA256.
    """
    if not TELEGRAM_BOT_TOKEN:
        return False

    # Calculate expected hash
    secret_hash = hashlib.sha256(TELEGRAM_BOT_TOKEN.encode()).digest()

    # If Telegram provides X-Telegram-Bot-Api-Secret-Hash header
    if x_telegram_bot_api_secret_hash:
        update_json = str(update).encode()
        expected_hash = hmac.new(secret_hash, update_json, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected_hash, x_telegram_bot_api_secret_hash)

    # Basic validation - ensure update_id exists
    return "update_id" in update


def get_user_session_id(update: dict[str, Any]) -> str:
    """Extract and validate user session ID from Telegram update."""
    if "message" not in update:
        return None

    message = update["message"]
    user_id = message.get("from", {}).get("id")

    if not user_id or not isinstance(user_id, int):
        return None

    return str(user_id)
