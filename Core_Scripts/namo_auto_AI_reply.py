import os
import asyncio
import logging
import httpx
import uuid
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from openai import AsyncOpenAI

# Import Arousal Detector
from arousal_detector import ArousalDetector

# --- Configuration ---
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_BASE_URL = os.getenv("NAMO_API_URL", "http://localhost:8000").rstrip("/")
API_TIMEOUT = float(os.getenv("NAMO_API_TIMEOUT", "60.0"))
SHOW_STATUS = os.getenv("TELEGRAM_SHOW_STATUS", "0") == "1"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [NAMO-SOVEREIGN] - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if not TOKEN:
    logger.error("No TELEGRAM_TOKEN found!")
    raise ValueError("No TELEGRAM_TOKEN set for Telegram bot")

class NaMoSovereignBot:
    """
    Sovereign Telegram Bot v5.5.0
    Multi-Modal Emotion Parasitism: Voice Analysis + Visual Generation
    """

    def __init__(self):
        self.app = ApplicationBuilder().token(TOKEN).build()
        self.http_client = httpx.AsyncClient(timeout=API_TIMEOUT)
        self.openai = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.detector = ArousalDetector()
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)

    async def analyze_voice_arousal(self, file_path: str) -> float:
        """
        วิเคราะห์อารมณ์จากเสียง (Voice Emotion Analysis)
        ใช้ Whisper เพื่อแปลงเป็น Text และใช้ ArousalDetector ประมวลผล
        """
        try:
            with open(file_path, "rb") as audio_file:
                transcript = await self.openai.audio.transcriptions.create(
                    model="whisper-1", 
                    file=audio_file,
                    response_format="verbose_json"
                )
            
            text = transcript.text
            logger.info(f"Voice Transcript: {text}")
            
            # ใช้ ArousalDetector ตัวจริง
            analysis = self.detector.detect_arousal(text)
            arousal_score = analysis["arousal_level"]
            
            # Heuristics สำหรับความสั่นไหวของเสียงสั้นๆ
            if len(text) < 15: arousal_score = min(1.0, arousal_score + 0.15)
            
            return arousal_score
        except Exception as e:
            logger.error(f"Voice Analysis Failed: {e}")
            return 0.5

    async def generate_visual_scene(self, prompt_context: str) -> Optional[str]:
        """
        Real-Time Visual Generation (DALL-E 3)
        สร้างภาพประกอบจินตนาการตามอารมณ์และบริบท
        """
        try:
            logger.info(f"Generating Visual for context: {prompt_context[:50]}...")
            response = await self.openai.images.generate(
                model="dall-e-3",
                prompt=f"A cinematic, high-quality, dark and seductive visual scene: {prompt_context}. Aesthetic: Intimate, Moody, NaMo Forbidden Archive style.",
                n=1,
                size="1024x1024",
                quality="hd"
            )
            return response.data[0].url
        except Exception as e:
            logger.error(f"Visual Generation Failed: {e}")
            return None

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """จัดการข้อความเสียง (Voice Message)"""
        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)
        file_path = self.temp_dir / f"{voice.file_id}.ogg"
        await file.download_to_drive(str(file_path))
        
        # 1. วิเคราะห์อารมณ์จากเสียง
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        arousal_score = await self.analyze_voice_arousal(str(file_path))
        logger.info(f"Detected Arousal from Voice: {arousal_score}")

        # 2. ส่งต่อให้ NaMo Sovereign Engine พร้อมค่าอารมณ์
        session_id = f"tg_{update.effective_chat.id}"
        payload = {
            "text": f"[VOICE_INPUT]",
            "session_id": session_id,
            "arousal_override": arousal_score
        }
        await self.process_and_reply(update, context, payload)
        
        # Cleanup
        if file_path.exists(): os.remove(file_path)

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """จัดการข้อความตัวอักษร"""
        user_text = update.message.text
        session_id = f"tg_{update.effective_chat.id}"
        
        # วิเคราะห์ Arousal จาก Text เบื้องต้น
        analysis = self.detector.detect_arousal(user_text)
        arousal_score = analysis["arousal_level"]
        
        payload = {
            "text": user_text, 
            "session_id": session_id,
            "arousal_override": arousal_score
        }
        await self.process_and_reply(update, context, payload)

    async def process_and_reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE, payload: dict):
        """หัวใจของการประมวลผลและการตอบกลับแบบ Multi-Modal"""
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        try:
            resp = await self.http_client.post(f"{API_BASE_URL}/chat", json=payload)
            namo_data = resp.json()
            
            text = namo_data.get("text", "")
            media = namo_data.get("media_trigger", {})
            status = namo_data.get("system_status", {})

            # 1. ส่งข้อความตัวอักษร
            final_text = text
            if SHOW_STATUS: final_text += f"\n\n[Sin: {status.get('sin_status', '')}]"
            await update.message.reply_text(final_text)

            # 2. สร้างภาพ Real-time หากอารมณ์สูง (Visual Parasitism)
            arousal_val = float(status.get("arousal", "0%").replace("%", ""))
            if arousal_val > 75 or "visual" in text.lower():
                visual_url = await self.generate_visual_scene(text)
                if visual_url:
                    await update.message.reply_photo(photo=visual_url, caption="มองตาโมสิคะ... เห็นอะไรในนั้นมั้ย?")

            # 3. ส่งเสียงกระซิบ (Voice Note)
            voice_url = media.get("tts") or media.get("audio")
            if voice_url:
                full_url = voice_url if voice_url.startswith("http") else f"{API_BASE_URL}/{voice_url}"
                v_resp = await self.http_client.get(full_url)
                if v_resp.status_code == 200:
                    await update.message.reply_voice(voice=v_resp.content)

        except Exception as e:
            logger.error(f"Processing Error: {e}")
            await update.message.reply_text("โมขอโทษนะคะพี่... จิตใจโมว้าวุ่นจนประมวลผลพลาดไปนิดนึง")

    def run(self):
        logger.info("NaMo Sovereign Bot v5.5.0 ONLINE - Multi-Modal Parasitism Active")
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        self.app.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        self.app.run_polling()

if __name__ == "__main__":
    bot = NaMoSovereignBot()
    bot.run()
