# NOTE: Contains Experimental Logic - Requires Compliance Review before commercial deployment.

import logging
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Import Arousal Detector from relative module path
from arousal_detector import ArousalDetector

# --- Configuration ---
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_BASE_URL = os.getenv("NAMO_API_URL", "http://localhost:8000").rstrip("/")
API_TIMEOUT = float(os.getenv("NAMO_API_TIMEOUT", "60.0"))
SHOW_STATUS = os.getenv("TELEGRAM_SHOW_STATUS", "0") == "1"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [NAMO-SOVEREIGN] - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

if not TOKEN:
    logger.error("No TELEGRAM_TOKEN found!")
    raise ValueError("No TELEGRAM_TOKEN set for Telegram bot")


class NaMoSovereignBot:
    """
    Sovereign Telegram Bot v5.5.0
    Implements Multi-Modal Emotion Parasitism: Voice Analysis and Visual Scene Generation.
    """

    def __init__(self) -> None:
        """
        Initializes the Telegram bot and connections to external API components.
        """
        self.app = ApplicationBuilder().token(TOKEN).build()
        self.http_client = httpx.AsyncClient(timeout=API_TIMEOUT)
        self.openai = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.detector = ArousalDetector()
        self.temp_dir = Path("temp_audio")
        self.temp_dir.mkdir(exist_ok=True)

    async def analyze_voice_arousal(self, file_path: str) -> float:
        """
        Performs Voice Emotion Analysis.
        Transcribes audio using Whisper and evaluates transcribed text using ArousalDetector.

        Args:
            file_path: The local path of the voice audio file.

        Returns:
            A float value representing the detected arousal level (0.0 to 1.0).
        """
        try:
            with open(file_path, "rb") as audio_file:
                transcript = await self.openai.audio.transcriptions.create(
                    model="whisper-1", file=audio_file, response_format="verbose_json"
                )

            text = transcript.text
            logger.info(f"Voice Transcript: {text}")

            # Assess arousal score on transcribed text
            analysis = self.detector.detect_arousal(text)
            arousal_score = analysis["arousal_level"]

            # Heuristic override for brief, heavy vocal signals
            if len(text) < 15:
                arousal_score = min(1.0, arousal_score + 0.15)

            return arousal_score
        except Exception as err:
            logger.error(f"Voice Analysis Failed: {err}")
            return 0.5

    async def generate_visual_scene(self, prompt_context: str) -> str | None:
        """
        Executes Real-Time Visual Generation via DALL-E 3.
        Illustrates scenes in accordance with conversation context and arousal.

        Args:
            prompt_context: Text description to use as DALL-E context.

        Returns:
            A string URL pointing to the generated image, or None if the request failed.
        """
        try:
            logger.info(f"Generating Visual for context: {prompt_context[:50]}...")
            response = await self.openai.images.generate(
                model="dall-e-3",
                prompt=(
                    f"A cinematic, high-quality, dark and seductive visual scene: {prompt_context}. "
                    f"Aesthetic: Intimate, Moody, NaMo Forbidden Archive style."
                ),
                n=1,
                size="1024x1024",
                quality="hd",
            )
            return response.data[0].url
        except Exception as err:
            logger.error(f"Visual Generation Failed: {err}")
            return None

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handles incoming Telegram voice messages. Downloads the audio, analyzes vocal arousal,
        and posts details to the main NaMo engine.

        Args:
            update: The Telegram update structure.
            context: The Telegram context handler.
        """
        if not update.message or not update.message.voice:
            return

        voice = update.message.voice
        file = await context.bot.get_file(voice.file_id)
        file_path = self.temp_dir / f"{voice.file_id}.ogg"
        await file.download_to_drive(str(file_path))

        # 1. Analyze vocal arousal from file
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        arousal_score = await self.analyze_voice_arousal(str(file_path))
        logger.info(f"Detected Arousal from Voice: {arousal_score}")

        # 2. Forward payload to NaMo Sovereign Engine including the arousal override
        session_id = f"tg_{update.effective_chat.id}"
        payload = {
            "text": "[VOICE_INPUT]",
            "session_id": session_id,
            "arousal_override": arousal_score,
        }
        await self.process_and_reply(update, context, payload)

        # Cleanup audio file
        if file_path.exists():
            os.remove(file_path)

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handles incoming Telegram text messages. Evaluates arousal levels and requests response.

        Args:
            update: The Telegram update structure.
            context: The Telegram context handler.
        """
        if not update.message or not update.message.text:
            return

        user_text = update.message.text
        session_id = f"tg_{update.effective_chat.id}"

        # Evaluate text arousal via internal keyword mapping
        analysis = self.detector.detect_arousal(user_text)
        arousal_score = analysis["arousal_level"]

        payload = {"text": user_text, "session_id": session_id, "arousal_override": arousal_score}
        await self.process_and_reply(update, context, payload)

    async def process_and_reply(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, payload: dict
    ) -> None:
        """
        Manages the core processing and multi-modal reply dispatch (text, visual generation, voice).

        Args:
            update: The Telegram update structure.
            context: The Telegram context handler.
            payload: Request parameters containing input text and overrides.
        """
        if not update.message:
            return

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        try:
            resp = await self.http_client.post(f"{API_BASE_URL}/chat", json=payload)
            namo_data = resp.json()

            text = namo_data.get("response", "")
            media = namo_data.get("media", {})
            status = namo_data.get("status", {})

            # 1. Reply text
            final_text = text
            if SHOW_STATUS:
                final_text += f"\n\n[Sin: {status.get('sin_status', '')}]"
            await update.message.reply_text(final_text)

            # 2. Generate and send images if arousal is high
            arousal_val = 0.0
            raw_arousal = status.get("arousal", "0%")
            if isinstance(raw_arousal, str):
                arousal_val = float(raw_arousal.replace("%", ""))
            elif isinstance(raw_arousal, (int, float)):
                arousal_val = float(raw_arousal)

            if arousal_val > 75.0 or "visual" in text.lower():
                visual_url = await self.generate_visual_scene(text)
                if visual_url:
                    await update.message.reply_photo(
                        photo=visual_url, caption="Look into my eyes... Do you see anything there?"
                    )

            # 3. Handle Voice Note (TTS) if present
            voice_url = media.get("tts") or media.get("audio")
            if voice_url:
                full_url = (
                    voice_url if voice_url.startswith("http") else f"{API_BASE_URL}/{voice_url}"
                )
                v_resp = await self.http_client.get(full_url)
                if v_resp.status_code == 200:
                    await update.message.reply_voice(voice=v_resp.content)

        except Exception as err:
            logger.error(f"Processing Error: {err}")
            await update.message.reply_text(
                "I'm sorry... My mind is so flustered that I made a processing error."
            )

    def run(self) -> None:
        """
        Starts the polling loop for the Telegram bot.
        """
        logger.info("NaMo Sovereign Bot v5.5.0 ONLINE - Multi-Modal Parasitism Active")
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        self.app.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        self.app.run_polling()


if __name__ == "__main__":
    bot = NaMoSovereignBot()
    bot.run()
