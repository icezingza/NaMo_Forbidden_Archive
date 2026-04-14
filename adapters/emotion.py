from typing import Any

import requests

from config import settings

_FALLBACK_URL = "http://localhost:8082/analyze"


class EmotionAdapter:
    """Adapter for the external Emotion Analysis Service.

    Reads the endpoint from ``settings.emotion_api_url``.  Falls back to
    ``{"primary_emotion": "unknown", "intensity": 0}`` when the service is
    unreachable so callers always receive a valid dict.
    """

    def __init__(self):
        self.api_url = settings.emotion_api_url or _FALLBACK_URL
        print(f"[EmotionAdapter]: Initialized. API URL: {self.api_url}")

    def analyze_emotion(self, text: str) -> dict[str, Any]:
        """
        Analyzes the emotion of a given text using the Emotion Analysis Service.
        """
        payload = {"text": text}
        try:
            response = requests.post(self.api_url, json=payload, timeout=2)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[EmotionAdapter]: ERROR - Could not analyze emotion: {e}")
            return {"primary_emotion": "unknown", "intensity": 0, "error": str(e)}
