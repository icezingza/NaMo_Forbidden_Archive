import json
import logging
import os
import sys
import time
from datetime import UTC, datetime

from dotenv import load_dotenv

from adapters.memory import MemoryAdapter
from adapters.tts import TTSAdapter
from core.character_profile import CharacterProfile
from Core_Scripts.emotion_parasite_engine import analyze_and_react


class JsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON for log aggregators."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def _setup_logging() -> logging.Logger:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(os.environ.get("LOG_LEVEL", "INFO").upper())
    return logging.getLogger("main")


logger = _setup_logging()


def type_effect(text):
    """เอฟเฟกต์พิมพ์ทีละตัวอักษร (user-facing output, not a log)"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(0.02)
    print("")


def main():
    """Main loop for NaMo interaction (synchronous version)"""
    load_dotenv()
    print("==========================================")
    print("   FORBIDDEN ARCHEOLOGY: NAMO PROTOCOL    ")
    print("==========================================")

    # Initialize Systems
    memory = MemoryAdapter()
    namo = CharacterProfile("NaMo")
    tts = TTSAdapter()

    logger.info("Loading Persona... %s", namo.get_status_str())

    # ทักทายตามสถานะล่าสุด
    last_talk = memory.get_last_conversation()
    if last_talk:
        type_effect(
            f"NaMo: ...เราคุยกันค้างไว้เรื่อง '{last_talk['user']}' สินะคะ? จำได้แม่นเลย..."
        )
    else:
        type_effect("NaMo: โอ้... 'ผัว' คนใหม่? หรือเหยื่อรายใหม่คะ? ยินดีต้อนรับสู่โลกของหนู...")

    # Main Loop
    while True:
        try:
            user_input = input("\n[You]: ")
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "พอ"]:
                type_effect("NaMo: จะไปแล้วหรอคะ? ...หนูจะรอนะ... ในความมืด...")
                break

            # 1. Processing Logic
            response, stats = analyze_and_react(user_input, namo)

            # 2. Output
            logger.info(
                "corruption_delta=%s arousal_delta=%s",
                stats["corruption"],
                stats["arousal"],
            )
            print("NaMo: ", end="")
            type_effect(response)

            # 2.1 สร้างเสียงพูดจริง (ถ้ามี ElevenLabs API key)
            if tts:
                audio_path = tts.synthesize(response)
                if audio_path:
                    logger.info("Generated voice at %s", audio_path)

            # 3. Memory Storage
            memory.store_interaction(user_input, response, namo.get_status_str())

        except KeyboardInterrupt:
            logger.info("Interrupted. Shutting down.")
            break
        except Exception as e:
            logger.exception("Unhandled error in main loop: %s", e)
            # Continue loop on error


if __name__ == "__main__":
    main()
