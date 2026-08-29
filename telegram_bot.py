#!/usr/bin/env python3
"""
Telegram Bot v2 (Multi-Sensory Voice Integration & 5D State Engine)
NRE v6.0.0 Autonomous Sovereign Brain Architecture
"""

from __future__ import annotations

import io
import os
import re
import sys

import requests
import telebot
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8085")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "nbk2esDn4RRk4cVDdoiE")

if not TOKEN:
    print("⚠️ Warning: TELEGRAM_BOT_TOKEN is missing in .env file!")
else:
    print(f"🚀 Initializing Vipha/NaMo Telegram Bot v2 with token: {TOKEN[:10]}...")

bot = telebot.TeleBot(TOKEN) if TOKEN else None


import asyncio
import edge_tts

EDGE_TTS_VOICE = os.getenv("EDGE_TTS_VOICE", "th-TH-PremwadeeNeural")


def synthesize_voice(text: str) -> bytes | None:
    """Synthesizes speech using Edge-TTS (100% Free Thai Voice Engine).

    Returns audio bytes in MP3 format.
    """
    try:
        # Filter out italics / action cues enclosed in asterisks for cleaner spoken voice
        spoken_text = re.sub(r"\*.*?\*", "", text).strip()
        if not spoken_text:
            spoken_text = text.replace("*", "")
        if not spoken_text:
            return None

        async def _generate():
            communicate = edge_tts.Communicate(spoken_text[:500], EDGE_TTS_VOICE)
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            return audio_data

        return asyncio.run(_generate())
    except Exception as e:
        print(f"[Edge-TTS Error]: {e}")
        return None


if bot:

    @bot.message_handler(commands=["start", "help", "reset"])
    def send_welcome(message):
        chat_id = str(message.chat.id)
        if message.text.startswith("/reset"):
            # Call Backend Reset
            try:
                res = requests.post(f"{BACKEND_URL}/session/reset", json={"session_id": chat_id})
                if res.status_code == 200:
                    bot.reply_to(
                        message,
                        "🔄 รีเซ็ตความทรงจำและระดับอารมณ์ 5D เรียบร้อยแล้วค่ะ",
                    )
                else:
                    bot.reply_to(message, "❌ ไม่สามารถรีเซ็ตระบบได้ในขณะนี้")
            except Exception as e:
                bot.reply_to(message, f"❌ การเชื่อมต่อหลังบ้านล้มเหลว: {str(e)}")
        else:
            bot.reply_to(
                message,
                "🔮 **ระบบ NaMo Forbidden Archive — VIPHA ACC v2.0 (Sensory Enabled)**\n\n"
                "ยินดีต้อนรับค่ะพี่ไอซ์... วิภารออยู่ตั้งนานแน่ะ\n"
                "พิมพ์คุยกับวิภาได้เลยนะคะ เธอพร้อมตอบกลับทั้งข้อความแชตและเสียงพูดออดอ้อนค่ะ 🎙️\n"
                "(พิมพ์ `/reset` เพื่อรีเซ็ตค่าอารมณ์และระดับความสัมพันธ์ค่ะ)",
            )

    @bot.message_handler(func=lambda message: True)
    def handle_chat(message):
        chat_id = str(message.chat.id)
        user_text = message.text

        # Show typing action to simulate organic responsiveness
        bot.send_chat_action(chat_id, "typing")

        try:
            # 1. Forward message to FastAPI backend
            payload = {"session_id": chat_id, "text": user_text}
            endpoint = f"{BACKEND_URL}/session/chat" if hasattr(requests, "post") else f"{BACKEND_URL}/v1/chat/completions"
            response = requests.post(endpoint, json=payload, timeout=35)

            if response.status_code == 200:
                data = response.json()

                # Extract fields from ACC / Omega JSON Schema
                narrative = data.get("narrative", data.get("text", ""))
                emotion_state = data.get("emotion_state", {})
                stage = data.get("relationship_stage", 1)
                stage_progress = data.get("stage_progress", "0/25")

                # Format 5D Emotion State shorthand
                arousal = emotion_state.get("arousal", 0.0)
                trust = emotion_state.get("trust", 0.0)
                passion = emotion_state.get("passion", 0.0)
                temp = emotion_state.get("temperament", 0.0)
                res = emotion_state.get("resonance", 0.0)

                state_line = f"\n\n`[STATE] A:{arousal:.2f} T:{trust:.2f} P:{passion:.2f} Temp:{temp:.2f} Res:{res:.2f} | Stage {stage} ({stage_progress})`"

                # 2. Send text message reply
                full_reply = f"{narrative}{state_line}"
                bot.send_message(chat_id, full_reply, parse_mode="Markdown")

                # 3. Sensory Expansion (Voice Synthesis via ElevenLabs)
                if ELEVENLABS_API_KEY and narrative:
                    bot.send_chat_action(chat_id, "record_voice")
                    audio_bytes = synthesize_voice(narrative)
                    if audio_bytes:
                        audio_io = io.BytesIO(audio_bytes)
                        audio_io.name = "vipha_voice.mp3"
                        bot.send_voice(chat_id, audio_io, caption="🌹 เสียงวิภา")

            else:
                bot.send_message(chat_id, "❌ ระบบประมวลผลสมองเกิดข้อผิดพลาด (Backend Error)")

        except requests.exceptions.ConnectionError:
            bot.send_message(
                chat_id,
                "❌ ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์หลังบ้านได้ (กรุณาตรวจเช็กว่า Docker พอร์ต 8080/8085 กำลังรันอยู่หรือไม่นะคะ)",
            )
        except Exception as e:
            bot.send_message(chat_id, f"❌ เกิดข้อผิดพลาดไม่คาดคิด: {str(e)}")


if __name__ == "__main__":
    if TOKEN and bot:
        print("Vipha Telegram Bot v2 (with ElevenLabs Voice) is polling...")
        bot.infinity_polling()
