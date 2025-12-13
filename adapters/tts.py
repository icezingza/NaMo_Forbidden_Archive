import os
import time
from pathlib import Path
from typing import Optional


class TTSAdapter:
    """
    Thin wrapper around ElevenLabs TTS.
    Requires ELEVENLABS_API_KEY in the environment.
    """

    def __init__(
        self,
        output_dir: str = "Audio_Layers/generated",
        default_voice_id: str = "eVItLK1UvXctxuaRV2Oq",
        model_id: str = "eleven_multilingual_v2",
    ):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID", default_voice_id)
        self.model_id = model_id
        self.output_dir = Path(output_dir)
        self.client = None

        if not self.api_key:
            print("[TTSAdapter]: ELEVENLABS_API_KEY not set; TTS disabled.")
            return

        try:
            from elevenlabs.client import ElevenLabs

            self.client = ElevenLabs(api_key=self.api_key)
            self.output_dir.mkdir(parents=True, exist_ok=True)
            print(f"[TTSAdapter]: Initialized (voice={self.voice_id}). Output -> {self.output_dir}")
        except Exception as e:
            print(f"[TTSAdapter]: Failed to init ElevenLabs client: {e}")
            self.client = None

    def synthesize(self, text: str, *, output_format: str = "mp3_44100_128") -> Optional[str]:
        """Synthesize speech from text. Returns the file path or None on failure."""
        if not self.client or not text:
            return None

        filename = f"tts_{int(time.time() * 1000)}.mp3"
        out_path = self.output_dir / filename
        try:
            audio = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id=self.model_id,
                output_format=output_format,
            )
            out_path.write_bytes(audio)
            return str(out_path)
        except Exception as e:
            print(f"[TTSAdapter]: synthesize failed: {e}")
            return None
