"""
Centralized configuration management using Pydantic's BaseSettings.

This module provides a single source of truth for all environment-based
configurations, offering validation, type-hinting, and default values.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Manages application settings, automatically reading from .env files."""

    # --- Server Settings ---
    public_base_url: str | None = Field(None, alias="PUBLIC_BASE_URL")
    cors_allow_origins: str = Field("*", alias="CORS_ALLOW_ORIGINS")
    namo_usage_log_path: str | None = Field(None, alias="NAMO_USAGE_LOG_PATH")

    # --- Memory Service Settings ---
    memory_file_path: str = Field("memory_protocol.json", alias="MEMORY_FILE_PATH")
    memory_logging: bool = Field(False, alias="MEMORY_LOGGING")
    memory_api_url: str | None = Field(None, alias="MEMORY_API_URL")
    memory_api_key: str | None = Field(None, alias="MEMORY_API_KEY")

    # --- API Key and Plan Settings ---
    namo_api_keys: str | None = Field(None, alias="NAMO_API_KEYS")
    namo_api_default_plan: str = Field("public", alias="NAMO_API_DEFAULT_PLAN")

    class Config:
        # This allows the settings to be loaded from a .env file.
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create a single, reusable instance of the settings to be used across the app.
settings = Settings()