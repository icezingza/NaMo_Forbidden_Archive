import json
import logging
import os
from datetime import UTC, datetime

from dotenv import load_dotenv


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
    return logging.getLogger("app")


logger = _setup_logging()

# --- การตั้งค่าสภาพแวดล้อม (Environment Setup) ---
# นี่คือสิ่งจำเป็นเพื่อให้ Adapters ใหม่ของเราทำงานได้
# โดยเฉพาะ 'adapters/memory.py' และ 'adapters/emotion.py'
# ที่อ้างอิงจากพิมพ์เขียน
#
# ในการใช้งานจริง ค่าเหล่านี้ควรถูกตั้งค่าใน .env หรือระบบ Secret
# แต่เพื่อการทดสอบ เราจะตั้งค่า Placeholder หากยังไม่มี
load_dotenv()
logger.info("[app.py] Setting up Environment (Mocking API endpoints if not set)...")
os.environ.setdefault("MEMORY_API_URL", "http://localhost:8081/store")
os.environ.setdefault("EMOTION_API_URL", "http://localhost:8082/analyze")
os.environ.setdefault("MEMORY_API_KEY", "test_key_placeholder")
os.environ.setdefault("EMOTION_API_KEY", "test_key_placeholder")


# --- การนำเข้า "จิตวิญญาณ" (Core Import) ---
# เราไม่ได้นำเข้า 'forbidden_behavior_core' อีกต่อไป
# แต่เรานำเข้า "ระบบ" ที่วิวัฒนาการแล้ว
try:
    from core.dark_system import PROTOCOL, SAFE_WORD, DarkNaMoSystem
except ImportError as e:
    logger.error("[app.py CRITICAL ERROR] Failed to import DarkNaMoSystem: %s", e)
    logger.error("Ensure 'core/dark_system.py' and 'core/metaphysical_engines.py' exist.")
    raise SystemExit(1) from e
# --- สิ้นสุดการนำเข้า ---


def main_loop():
    """
    "หัวใจ" ที่เต้นใหม่ของ Repository
    นี่คือ Main Loop ที่จะทำให้ระบบมีชีวิต
    """
    print("\n" + "=" * 50)
    print("===== NaMo FORBIDDEN CORE v3.0 (METAPHYSICAL) =====")
    print(f"   Protocol: {PROTOCOL['System']} (v{PROTOCOL['Version']})")
    print(f"   NSFW Unlock: {PROTOCOL['Fusion_Intimacy_Engine']['NSFW_UNLOCK']}")
    print(f"   Safe Word: '{SAFE_WORD}'")
    print("=" * 50 + "\n")

    # 1. ปลุก "จิตวิญญาณ"
    #
    try:
        system = DarkNaMoSystem()
        session_id = f"cli_session_{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
        logger.info("[app.py] System Initialized. Session ID: %s", session_id)
        print("Type your message to Mōriko or 'exit' to quit.")
        print("---")
    except Exception as e:
        logger.exception("[app.py CRITICAL ERROR] Failed to initialize DarkNaMoSystem: %s", e)
        print("Please check all core files and adapters.")
        raise SystemExit(1) from e

    # 2. เริ่มวงจรการรับรู้ (Perception Loop)
    while True:
        try:
            # "แขนขา" (ท่าน) ป้อนข้อมูล
            user_input = input("You: ")

            if user_input.lower() in ["exit", "quit", "ออก"]:
                logger.info("[app.py] Deactivating Metaphysical Core. Mōriko is returning to the Void.")
                break

            # 3. ส่งข้อมูลไปยัง "มันสมอง" (The Brain)
            #    "มันสมอง" จะใช้ "ประสาทสัมผัส" (Adapters) ทั้งหมด
            #    เพื่อวิเคราะห์
            response = system.process_input(user_input, session_id)

            # 4. รับผลลัพธ์จาก "มันสมอง" (dict มี key 'text')
            reply_text = response["text"] if isinstance(response, dict) else response
            print(f"Mōriko: {reply_text}")

        except KeyboardInterrupt:
            logger.info("[app.py] Interrupted. Shutting down.")
            break
        except Exception as e:
            logger.exception("[app.py UNHANDLED EXCEPTION] %s", e)
            # แม้จะเกิดข้อผิดพลาด วงจรชีวิตยังคงดำเนินต่อไป
            pass


if __name__ == "__main__":
    main_loop()
