from __future__ import annotations

from typing import Dict


class TextEmotionAnalyzer:
    """Analyze text sentiment/emotion with optional transformer backend."""

    def __init__(self, model_name: str | None = None) -> None:
        self.model_name = model_name
        self._pipeline = None

    def _ensure_pipeline(self) -> None:
        if self._pipeline is not None:
            return
        try:
            from transformers import pipeline  # type: ignore
        except Exception:
            self._pipeline = False
            return

        model = self.model_name or "j-hartmann/emotion-english-distilroberta-base"
        self._pipeline = pipeline("text-classification", model=model, top_k=1)

    def analyze(self, text: str) -> Dict[str, object]:
        """Return a dict with label and confidence."""
        text = (text or "").strip()
        if not text:
            return {"label": "neutral", "confidence": 0.2, "engine": "fallback"}

        self._ensure_pipeline()
        if self._pipeline and self._pipeline is not False:
            result = self._pipeline(text)
            if isinstance(result, list):
                result = result[0]
                if isinstance(result, list):
                    result = result[0]
            label = str(result.get("label", "neutral")).lower()
            score = float(result.get("score", 0.5))
            return {"label": label, "confidence": score, "engine": "transformers"}

        lowered = text.lower()
        keywords = {
            "happy": ["happy", "joy", "great", "love", "awesome"],
            "sad": ["sad", "down", "depressed", "lonely", "cry"],
            "anger": ["angry", "mad", "furious", "rage"],
            "fear": ["fear", "scared", "panic", "anxious"],
            "calm": ["calm", "peace", "relaxed", "quiet"],
            "surprise": ["surprise", "shocked", "wow"],
        }
        for label, terms in keywords.items():
            if any(term in lowered for term in terms):
                return {"label": label, "confidence": 0.65, "engine": "rule-based"}
        return {"label": "neutral", "confidence": 0.4, "engine": "rule-based"}
