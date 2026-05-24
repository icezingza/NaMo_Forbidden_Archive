import os
import logging
from dotenv import load_dotenv
from qdrant_client import QdrantClient
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NaMoDiagnostic")

def diagnose():
    logger.info("--- เริ่มการวิเคราะห์ระบบ Sovereign NaMo ---")
    load_dotenv()
    
    # 1. ตรวจสอบ Environment Variables
    token = os.getenv("TELEGRAM_TOKEN")
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    api_url = os.getenv("NAMO_API_URL", "http://localhost:8000")
    
    logger.info(f"Telegram Token found: {token is not None}")
    logger.info(f"Qdrant URL: {qdrant_url}")
    logger.info(f"API Base URL: {api_url}")
    
    # 2. ตรวจสอบ Qdrant Connection
    try:
        client = QdrantClient(url=qdrant_url)
        client.get_collections()
        logger.info("✅ Qdrant Connection: SUCCESS")
    except Exception as e:
        logger.error(f"❌ Qdrant Connection: FAILED - {e}")
        
    # 3. ตรวจสอบ API Server
    try:
        resp = requests.get(f"{api_url}/v1/health", timeout=5)
        if resp.status_code == 200:
            logger.info("✅ API Server Connection: SUCCESS")
        else:
            logger.error(f"❌ API Server Connection: FAILED - Status {resp.status_code}")
    except Exception as e:
        logger.error(f"❌ API Server Connection: FAILED - {e}")

    logger.info("--- จบการวิเคราะห์ ---")

if __name__ == "__main__":
    diagnose()
