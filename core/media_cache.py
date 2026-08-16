"""
NaMo Forbidden Archive — Media Asset Caching Engine
Caches audio TTS generations and DALL-E image generations by prompt/hash to prevent duplicate API cost.
"""

import hashlib
import json
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("NamoMediaCache")


class MediaCacheManager:
    def __init__(self, cache_dir: str = "/root/NaMo_Forbidden_Archive/Archived_Assets"):
        self.cache_dir = cache_dir
        self.audio_dir = os.path.join(cache_dir, "audio")
        self.visual_dir = os.path.join(cache_dir, "visual")
        self.index_file = os.path.join(cache_dir, "media_index.json")

        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.visual_dir, exist_ok=True)

        self._index: Dict[str, Dict[str, Any]] = self._load_index()

    def _load_index(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading media index: {e}")
        return {}

    def _save_index(self) -> None:
        try:
            with open(self.index_file, "w") as f:
                json.dump(self._index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving media index: {e}")

    def compute_hash(self, text: str, voice_or_style: str = "default") -> str:
        content = f"{text.strip().lower()}::{voice_or_style.strip().lower()}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def get_cached_audio(self, text: str, voice_id: str = "default") -> Optional[str]:
        h = self.compute_hash(text, voice_id)
        if h in self._index and self._index[h]["type"] == "audio":
            file_path = self._index[h]["file_path"]
            if os.path.exists(file_path):
                logger.info(f"🔊 Audio Cache HIT: {file_path}")
                return file_path
        return None

    def store_cached_audio(self, text: str, voice_id: str, audio_bytes: bytes, file_ext: str = ".mp3") -> str:
        h = self.compute_hash(text, voice_id)
        filename = f"tts_{h[:16]}{file_ext}"
        file_path = os.path.join(self.audio_dir, filename)

        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        self._index[h] = {
            "type": "audio",
            "text": text,
            "voice_id": voice_id,
            "file_path": file_path,
            "hash": h
        }
        self._save_index()
        logger.info(f"💾 Audio Cache Stored: {file_path}")
        return file_path

    def get_cached_image(self, prompt: str, style: str = "default") -> Optional[str]:
        h = self.compute_hash(prompt, style)
        if h in self._index and self._index[h]["type"] == "image":
            file_path = self._index[h]["file_path"]
            if os.path.exists(file_path):
                logger.info(f"🖼️ Image Cache HIT: {file_path}")
                return file_path
        return None

    def store_cached_image(self, prompt: str, style: str, image_bytes: bytes, file_ext: str = ".png") -> str:
        h = self.compute_hash(prompt, style)
        filename = f"img_{h[:16]}{file_ext}"
        file_path = os.path.join(self.visual_dir, filename)

        with open(file_path, "wb") as f:
            f.write(image_bytes)

        self._index[h] = {
            "type": "image",
            "prompt": prompt,
            "style": style,
            "file_path": file_path,
            "hash": h
        }
        self._save_index()
        logger.info(f"💾 Image Cache Stored: {file_path}")
        return file_path
