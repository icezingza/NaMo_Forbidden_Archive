import uuid
from pathlib import Path
from typing import Any

from config import settings

try:
    from elevenlabs.client import ElevenLabs as _ElevenLabsClient

    _ELEVENLABS_AVAILABLE = True
except ImportError:
    _ELEVENLABS_AVAILABLE = False


class TTSAdapter:
    """Adapter for ElevenLabs text-to-speech synthesis.

    Returns a relative file path under Audio_Layers/tts/ that is served
    by the /media/audio mount in server.py.  Returns None when ElevenLabs
    is not configured or the synthesis fails.
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
                print(
                    f"[TTSAdapter]: ElevenLabs ONLINE "
                    f"(voice={self._voice_id}, model={self._model})"
                )
            except Exception as exc:
                print(f"[TTSAdapter]: ElevenLabs init failed: {exc}")
                self._client = None
        else:
            reason = "elevenlabs package missing" if not _ELEVENLABS_AVAILABLE else "no API key"
            print(f"[TTSAdapter]: offline ({reason})")

    def synthesize(self, text: str) -> str | None:
        """Synthesize *text* and return a relative audio path, or None on failure."""
        if not self._client:
            return None

        try:
            audio_bytes = self._client.generate(
                text=text,
                voice=self._voice_id,
                model=self._model,
            )
            # audio_bytes may be a generator — consume it
            if not isinstance(audio_bytes, (bytes, bytearray)):
                audio_bytes = b"".join(audio_bytes)

            filename = f"{uuid.uuid4().hex}.mp3"
            file_path = self._output_dir / filename
            file_path.write_bytes(audio_bytes)

            # Return relative path compatible with _resolve_media_url()
            return f"Audio_Layers/tts/{filename}"
        except Exception as exc:
            print(f"[TTSAdapter]: synthesis failed: {exc}")
            return None
