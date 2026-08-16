#!/usr/bin/env python3
"""
Setup Telegram Webhook for NaMo ACC Bot

Usage:
    python setup_telegram.py --webhook-url https://yourdomain.com/webhook/telegram

Example:
    python setup_telegram.py --webhook-url https://example.com/webhook/telegram
"""

import argparse
import json
import os

import httpx

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def set_webhook(webhook_url: str):
    """Register webhook with Telegram."""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set")
        return False

    print(f"🔗 Setting Telegram webhook to: {webhook_url}")

    payload = {"url": webhook_url}
    response = httpx.post(f"{TELEGRAM_API_URL}/setWebhook", json=payload)

    result = response.json()
    print(f"📡 Response: {json.dumps(result, indent=2)}")

    if result.get("ok"):
        print("✅ Webhook registered successfully!")
        return True
    else:
        print("❌ Failed to register webhook")
        return False


def get_webhook_info():
    """Get current webhook info."""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set")
        return

    print("🔍 Getting webhook info...")
    response = httpx.get(f"{TELEGRAM_API_URL}/getWebhookInfo")
    result = response.json()

    print(json.dumps(result, indent=2))


def delete_webhook():
    """Delete current webhook."""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set")
        return False

    print("🗑️ Deleting webhook...")
    payload = {"url": ""}
    response = httpx.post(f"{TELEGRAM_API_URL}/setWebhook", json=payload)
    result = response.json()

    print(f"📡 Response: {json.dumps(result, indent=2)}")
    return result.get("ok", False)


def main():
    parser = argparse.ArgumentParser(description="Setup Telegram webhook for NaMo ACC Bot")
    parser.add_argument(
        "--webhook-url",
        type=str,
        help="Webhook URL (e.g., https://yourdomain.com/webhook/telegram)",
    )
    parser.add_argument("--info", action="store_true", help="Get current webhook info")
    parser.add_argument("--delete", action="store_true", help="Delete current webhook")

    args = parser.parse_args()

    if args.delete:
        delete_webhook()
    elif args.info:
        get_webhook_info()
    elif args.webhook_url:
        set_webhook(args.webhook_url)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
