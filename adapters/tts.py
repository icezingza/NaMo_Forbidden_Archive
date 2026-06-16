import asyncio
import uuid
from pathlib import Path
from typing import Any

from config import settings

try:
    from elevenlabs.client import ElevenLabs as _ElevenLabsClient

    _ELEVENLABS_AVAILABLE = True
except ImportError:
    _ElevenLabsClient = None  # type: ignore[assignment,misc]
    _ELEVENLABS_AVAILABLE = False


class TTSAdapter:
    """
    Adapter for ElevenLabs TTS (Async NRE v5.0.0)
    รองรับการสร้างเสียงแบบ Non-blocking เพื่อประสิทธิภาพสูงสุด
    """

    def __init__(self) -> None:
        self._client: Any = None
        self._voice_id = settings.elevenlabs_voice_id
        self._model = settings.elevenlabs_model
        self._output_dir = Path(settings.tts_output_dir)

        if _ELEVENLABS_AVAILABLE and settings.elevenlabs_api_key:
            try:
                self._client = _ElevenLabsClient(api_key=settings.elevenlabs_api_key)
                self._output_dir.mkdir(parents=True, exist_ok=True)
                print("[TTSAdapter]: ElevenLabs ONLINE (Async Ready)")
            except Exception as exc:
                print(f"[TTSAdapter]: ElevenLabs init failed: {exc}")
                self._client = None
        else:
            print("[TTSAdapter]: offline (check API key or package)")

    async def synthesize(self, text: str) -> str | None:
        """Async wrapper for text-to-speech synthesis"""
        if not self._client or not text:
            return None

        try:
            # ใช้ asyncio.to_thread เพื่อไม่ให้ blocking main thread
            audio_bytes = await asyncio.to_thread(
                self._client.generate, text=text, voice=self._voice_id, model=self._model
            )

            # Consume generator if necessary
            if not isinstance(audio_bytes, (bytes, bytearray)):
                audio_bytes = b"".join(audio_bytes)

            filename = f"{uuid.uuid4().hex}.mp3"
            file_path = self._output_dir / filename

            # Async write (via thread for standard filesystem)
            await asyncio.to_thread(file_path.write_bytes, audio_bytes)

            return f"Audio_Layers/tts/{filename}"
        except Exception as exc:
            print(f"[TTSAdapter]: synthesis failed: {exc}")
            return None
