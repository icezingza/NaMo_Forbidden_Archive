import os
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- System ---
    app_env: str = "development"
    app_port: int = 8000
    debug: bool = True
    log_level: str = "INFO"

    # --- External Services ---
    openai_api_key: Optional[str] = None
    emotion_api_url: Optional[str] = "http://localhost:8082/analyze"
    memory_api_url: Optional[str] = None
    memory_api_key: Optional[str] = None
    public_base_url: Optional[str] = None
    cors_allow_origins: str = "*"
    memory_logging: int = 0

    # --- LLM Config ---
    namo_llm_enabled: bool = False
    namo_llm_model: str = "gpt-4o-mini"
    namo_llm_temperature: float = 0.85
    namo_llm_max_tokens: int = 240
    namo_llm_memory_turns: int = 6

    # --- 🔓 Forbidden Unlock (Dark Mode) ---
    safety_filter_enabled: bool = True
    nsfw_allowed: bool = False
    scene_mode: str = "restricted"
    api_master_key: Optional[str] = None
    admin_secret: Optional[str] = None

    # --- Core Engines ---
    enable_emotion_parasite: bool = False
    enable_arousal_detector: bool = False
    enable_dark_memory: bool = False

    # --- Legacy / Compatibility ---
    namo_api_keys: Optional[str] = None
    namo_api_default_plan: str = "public"
    namo_usage_log_path: Optional[str] = None
    memory_file_path: str = "memory_protocol.json"

    # Configuration to handle .env file and ignore unknown extra fields
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # สำคัญ: ถ้ามีตัวแปรเกินมา ไม่ต้อง Error ให้ข้ามไปเลย
        case_sensitive=False,
    )

settings = Settings()