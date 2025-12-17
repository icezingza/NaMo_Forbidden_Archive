import argparse
import os
import sys

import requests
from dotenv import load_dotenv


load_dotenv()


def _get_token(args) -> str | None:
    return args.token or os.getenv("TELEGRAM_TOKEN")


def _api_base(token: str) -> str:
    return f"https://api.telegram.org/bot{token}"


def _get_me(base_url: str) -> dict | None:
    resp = requests.get(f"{base_url}/getMe", timeout=10)
    if not resp.ok:
        return None
    return resp.json()


def _get_latest_chat_id(base_url: str) -> int | None:
    resp = requests.get(f"{base_url}/getUpdates", params={"limit": 1}, timeout=10)
    if not resp.ok:
        return None
    data = resp.json()
    results = data.get("result", [])
    if not results:
        return None
    message = results[-1].get("message") or results[-1].get("channel_post")
    if not message:
        return None
    chat = message.get("chat", {})
    return chat.get("id")


def _send_message(base_url: str, chat_id: int, text: str) -> bool:
    resp = requests.post(
        f"{base_url}/sendMessage",
        json={"chat_id": chat_id, "text": text},
        timeout=10,
    )
    return resp.ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Telegram bot smoke check.")
    parser.add_argument("--token", help="Telegram bot token (default: TELEGRAM_TOKEN env).")
    parser.add_argument("--chat-id", type=int, help="Chat ID for sendMessage (optional).")
    parser.add_argument("--message", default="NaMo bot check-in.", help="Message to send.")
    parser.add_argument(
        "--send",
        action="store_true",
        help="Send a message to chat-id or latest update chat.",
    )
    args = parser.parse_args()

    token = _get_token(args)
    if not token:
        print("No TELEGRAM_TOKEN found. Set it in .env or pass --token.")
        return 1

    base_url = _api_base(token)
    me = _get_me(base_url)
    if not me:
        print("Failed to call getMe. Token may be invalid.")
        return 1

    username = me.get("result", {}).get("username", "unknown")
    print(f"Bot OK: @{username}")

    if not args.send:
        return 0

    chat_id = args.chat_id or _get_latest_chat_id(base_url)
    if not chat_id:
        print("No chat_id found. Send /start to the bot, then retry with --send.")
        return 2

    if _send_message(base_url, chat_id, args.message):
        print(f"Message sent to chat_id {chat_id}.")
        return 0

    print("Failed to send message.")
    return 3


if __name__ == "__main__":
    sys.exit(main())
