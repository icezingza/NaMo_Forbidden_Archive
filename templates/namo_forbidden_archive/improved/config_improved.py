"""
Enhanced configuration management with environment variables and validation.
"""

from pydantic import BaseSettings, validator
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings with validation."""

    # Server
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    MEMORY_SERVICE_URL: str = "http://localhost:8081"

    # Engine
    SESSION_TIMEOUT_MINUTES: int = 60
    MAX_INPUT_LENGTH: int = 5000
    ENABLE_CACHING: bool = True
    CACHE_SIZE: int = 1000

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Features
    ENABLE_TTS: bool = False
    ENABLE_MEMORY_PERSISTENCE: bool = True

    # Security
    CORS_ORIGINS: list = ["*"]
    API_KEY: Optional[str] = None

    @validator("API_PORT")
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @validator("SESSION_TIMEOUT_MINUTES")
    def validate_timeout(cls, v):
        if v < 1:
            raise ValueError("Timeout must be at least 1 minute")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Load settings
settings = Settings()

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL), format=settings.LOG_FORMAT)

logger.info("Settings loaded successfully")
