from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- System ---
    app_env: str = "development"
    app_port: int = 8000
    debug: bool = True
    log_level: str = "INFO"

    # --- External Services ---
    openai_api_key: str | None = None
    openrouter_api_key: str | None = None
    emotion_api_url: str | None = "http://localhost:8082/analyze"
    memory_api_url: str | None = None
    memory_api_key: str | None = None
    public_base_url: str | None = None
    cors_allow_origins: str = "*"
    memory_logging: int = 0

    # --- LLM Config ---
    namo_llm_enabled: bool = False
    namo_llm_model: str = "gpt-4o-mini"
    namo_llm_temperature: float = 0.85
    namo_llm_max_tokens: int = 240
    namo_llm_memory_turns: int = 6
    namo_llm_base_url: str | None = None

    # --- 🔓 Forbidden Unlock (Dark Mode) ---
    safety_filter_enabled: bool = False
    nsfw_allowed: bool = True
    scene_mode: str = "restricted"
    api_master_key: str | None = None
    admin_secret: str | None = None

    # --- Core Engines ---
    enable_emotion_parasite: bool = False
    enable_arousal_detector: bool = False
    enable_dark_memory: bool = False

    # --- Emotion Engine Parameters ---
    emotion_decay_rate: float = 0.06
    emotion_inertia: float = 0.65

    # --- Learning Engine Parameters ---
    learning_boldness_base: float = 0.30
    learning_boldness_coeff: float = 0.62
    learning_boldness_cap: float = 0.92
    learning_playfulness_base: float = 0.30
    learning_playfulness_coeff: float = 0.55
    learning_playfulness_cap: float = 0.92
    learning_vulnerability_base: float = 0.20
    learning_vulnerability_coeff: float = 0.55
    learning_vulnerability_cap: float = 0.85
    learning_expressiveness_base: float = 0.40
    learning_expressiveness_coeff: float = 500.0
    learning_expressiveness_cap: float = 0.90

    # --- ElevenLabs TTS ---
    elevenlabs_api_key: str | None = None
    elevenlabs_voice_id: str = "Rachel"
    elevenlabs_model: str = "eleven_multilingual_v2"
    tts_output_dir: str = "Audio_Layers/tts"

    # --- Engine Routing ---
    default_engine: str = "omega"

    # --- Session & Rate Limiting ---
    session_ttl_seconds: int = 3600
    rate_limit_calls: int = 60
    rate_limit_period: int = 60

    # --- Legacy / Compatibility ---
    namo_api_keys: str | None = None
    namo_api_default_plan: str = "public"
    namo_usage_log_path: str | None = None
    memory_file_path: str = "memory_protocol.json"

    # Configuration to handle .env file and ignore unknown extra fields
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # สำคัญ: ถ้ามีตัวแปรเกินมา ไม่ต้อง Error ให้ข้ามไปเลย
        case_sensitive=False,
    )


settings = Settings()
