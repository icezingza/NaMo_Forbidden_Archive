"""
NaMo Sovereign Engine - Slack Integration (Socket Mode)
"""

import asyncio
import os

import edge_tts
import requests
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8085")
EDGE_TTS_VOICE = os.getenv("EDGE_TTS_VOICE", "th-TH-PremwadeeNeural")

# Initialize Slack App
app = App(token=SLACK_BOT_TOKEN)


def synthesize_voice(text: str) -> bytes | None:
    try:
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


def process_message(user_id, channel_id, user_text, say, client):
    if not user_text:
        return

    if user_text.strip().startswith("/reset"):
        try:
            res = requests.post(f"{BACKEND_URL}/session/reset", json={"session_id": user_id})
            if res.status_code == 200:
                say("🔄 รีเซ็ตความทรงจำและระดับอารมณ์ 5D เรียบร้อยแล้วค่ะ")
            else:
                say("❌ ไม่สามารถรีเซ็ตระบบได้ในขณะนี้")
        except Exception as e:
            say(f"❌ การเชื่อมต่อหลังบ้านล้มเหลว: {str(e)}")
        return

    try:
        # 1. Forward message to FastAPI backend
        payload = {"session_id": user_id, "text": user_text}
        endpoint = (
            f"{BACKEND_URL}/session/chat"
            if hasattr(requests, "post")
            else f"{BACKEND_URL}/v1/chat/completions"
        )
        response = requests.post(endpoint, json=payload, timeout=35)

        if response.status_code == 200:
            data = response.json()

            # Extract fields from ACC / Omega JSON Schema
            narrative = data.get("narrative", data.get("text", ""))
            emotion_state = data.get("emotion_state", {})
            stage = data.get("relationship_stage", 1)
            stage_progress = data.get("stage_progress", "0/25")

            arousal = emotion_state.get("arousal", 0.0)
            trust = emotion_state.get("trust", 0.0)
            passion = emotion_state.get("passion", 0.0)
            temp = emotion_state.get("temperament", 0.0)
            res = emotion_state.get("resonance", 0.0)

            state_line = f"\n\n`[STATE] A:{arousal:.2f} T:{trust:.2f} P:{passion:.2f} Temp:{temp:.2f} Res:{res:.2f} | Stage {stage} ({stage_progress})`"
            full_reply = f"{narrative}{state_line}"

            # 2. Send text message reply
            say(full_reply)

            # 3. Sensory Expansion (Voice Synthesis via Edge-TTS)
            if narrative:
                audio_bytes = synthesize_voice(narrative)
                if audio_bytes:
                    client.files_upload_v2(
                        channel=channel_id,
                        initial_comment="🌹 เสียงวิภา",
                        filename="vipha_voice.mp3",
                        content=audio_bytes,
                    )

        else:
            say("❌ ระบบประมวลผลสมองเกิดข้อผิดพลาด (Backend Error)")

    except requests.exceptions.ConnectionError:
        say(
            "❌ ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์หลังบ้านได้ (กรุณาตรวจเช็กว่า Docker พอร์ต 8080/8085 กำลังรันอยู่หรือไม่นะคะ)"
        )
    except Exception as e:
        say(f"❌ เกิดข้อผิดพลาดไม่คาดคิด: {str(e)}")


@app.message(".*")
def handle_direct_message(message, say, client):
    """Handle normal messages / DMs"""
    # Ignore messages from bots
    if message.get("bot_id") or message.get("subtype"):
        return

    channel_type = message.get("channel_type")
    # Only respond in DM, or if mentioned in channel (handled separately)
    if channel_type == "im":
        process_message(
            message.get("user"), message.get("channel"), message.get("text"), say, client
        )


@app.event("app_mention")
def handle_app_mention(event, say, client):
    """Handle @bot mentions in channels"""
    text = event.get("text", "")
    # Remove the bot mention from the text
    text = text.split(">", 1)[1].strip() if ">" in text else text
    process_message(event.get("user"), event.get("channel"), text, say, client)


if __name__ == "__main__":
    if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN:
        print("[Slack] Skipping Slack Bot: SLACK_BOT_TOKEN or SLACK_APP_TOKEN is missing in .env")
    else:
        print("[Slack] Starting NaMo Sovereign Engine on Slack (Socket Mode)...")
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        handler.start()
