from __future__ import annotations

import tempfile
from typing import Dict


class ImageEmotionAnalyzer:
    """Analyze facial emotion using DeepFace if available."""

    def __init__(self) -> None:
        self._deepface = None

    def _ensure_backend(self) -> None:
        if self._deepface is not None:
            return
        try:
            from deepface import DeepFace  # type: ignore
        except Exception:
            self._deepface = False
            return
        self._deepface = DeepFace

    def analyze(self, image_bytes: bytes) -> Dict[str, object]:
        """Return label and confidence for the most likely emotion."""
        if not image_bytes:
            return {"label": "neutral", "confidence": 0.2, "engine": "fallback"}

        self._ensure_backend()
        if self._deepface and self._deepface is not False:
            with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
                tmp.write(image_bytes)
                tmp.flush()
                result = self._deepface.analyze(
                    img_path=tmp.name,
                    actions=["emotion"],
                    enforce_detection=False,
                )
            if isinstance(result, list):
                result = result[0]
            emotions = result.get("emotion", {}) if isinstance(result, dict) else {}
            if emotions:
                label = max(emotions, key=emotions.get)
                confidence = float(emotions[label]) / 100.0
                return {"label": label.lower(), "confidence": confidence, "engine": "deepface"}

        return {"label": "neutral", "confidence": 0.3, "engine": "fallback"}
