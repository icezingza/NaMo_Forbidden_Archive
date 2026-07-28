import os
from typing import Any

import requests


class EmotionAdapter:
    """
    Adapter for interacting with the external Emotion Analysis Service.
    """

    def __init__(self):
        self.api_url = os.environ.get("EMOTION_API_URL", "http://localhost:8082/analyze")
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
