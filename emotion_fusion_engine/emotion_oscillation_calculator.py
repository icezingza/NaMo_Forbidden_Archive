from __future__ import annotations

from typing import Dict, List, Optional, Tuple


class EmotionOscillationCalculator:
    """Convert raw emotions into oscillation frequency and coherence metrics."""

    EMOTION_TO_HZ_RANGE: Dict[str, Tuple[float, float]] = {
        "fear": (0.1, 2.0),
        "anger": (3.0, 6.0),
        "disgust": (5.0, 8.0),
        "sad": (0.05, 0.5),
        "neutral": (7.0, 12.0),
        "calm": (0.5, 2.0),
        "compassion": (2.0, 4.0),
        "happy": (4.0, 6.0),
        "surprise": (6.0, 8.0),
    }

    POSITIVE_EMOTIONS = {"calm", "compassion", "happy", "surprise"}

    @classmethod
    def calculate_oscillation(
        cls,
        raw_emotion_label: str,
        confidence: float,
        recent_emotion_history: Optional[List[str]] = None,
    ) -> Dict[str, object]:
        """Calculate oscillation frequency, coherence, and amplitude."""

        history = recent_emotion_history or []
        label = (raw_emotion_label or "neutral").lower()
        hz_range = cls.EMOTION_TO_HZ_RANGE.get(label, (1.0, 3.0))

        base_freq = (hz_range[0] + hz_range[1]) / 2
        oscillation_freq = base_freq * (0.9 + 0.2 * float(confidence))

        coherence_score = cls._calculate_coherence(label, history)
        amplitude_score = float(confidence)

        return {
            "base_emotion": label,
            "oscillation_freq_hz": round(oscillation_freq, 2),
            "coherence_score": round(coherence_score, 2),
            "amplitude_score": round(amplitude_score, 2),
            "hz_range": hz_range,
        }

    @classmethod
    def _calculate_coherence(cls, current_emotion: str, history: List[str]) -> float:
        if not history:
            return 0.5

        base_score = 0.7 if current_emotion in cls.POSITIVE_EMOTIONS else 0.3
        unique_recent = set(history[-5:]) if len(history) >= 5 else set(history)
        stability_penalty = 0.1 * max(0, len(unique_recent) - 1)
        coherence = max(0.1, min(1.0, base_score - stability_penalty))
        return coherence
