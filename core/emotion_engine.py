"""Continuous, physics-based emotion system.

Emotions are modelled as a 5-dimensional vector (joy, arousal, trust,
anger, desire). Each dimension has inertia (momentum) so changes feel
gradual rather than instantaneous, and all values decay slowly toward a
neutral baseline when left untouched.
"""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class EmotionVector:
    """5-dimensional continuous emotion state (all values 0–1)."""

    joy: float = 0.5  # 0 = deep sadness … 1 = euphoria
    arousal: float = 0.3  # 0 = drowsy/calm … 1 = frantic/excited
    trust: float = 0.5  # 0 = suspicion/fear … 1 = full trust
    anger: float = 0.0  # 0 = calm … 1 = rage
    desire: float = 0.0  # 0 = detached … 1 = craving

    def clamp(self) -> EmotionVector:
        for attr in ("joy", "arousal", "trust", "anger", "desire"):
            setattr(self, attr, max(0.0, min(1.0, getattr(self, attr))))
        return self

    def dominant(self) -> tuple[str, float]:
        """Return the most prominent emotion and its intensity."""
        # Score = deviation from neutral (0.5 for bipolar axes, 0 for unipolar)
        scores = {
            "joy": abs(self.joy - 0.5),
            "arousal": abs(self.arousal - 0.3),
            "trust": abs(self.trust - 0.5),
            "anger": self.anger,
            "desire": self.desire,
        }
        name = max(scores, key=scores.__getitem__)
        return name, getattr(self, name)

    def to_prose(self) -> str:
        """Describe the current emotion state in Thai natural language."""
        parts: list[str] = []
        if self.joy > 0.75:
            parts.append("มีความสุขและอบอุ่น")
        elif self.joy < 0.3:
            parts.append("รู้สึกเหนื่อยและหม่นหมอง")
        if self.arousal > 0.75:
            parts.append("ตื่นตัวและตึงเครียด")
        elif self.arousal < 0.15:
            parts.append("ผ่อนคลายเกือบง่วง")
        if self.anger > 0.5:
            parts.append("หงุดหงิดอยู่ภายใน")
        if self.desire > 0.6:
            parts.append("มีความปรารถนาลึกๆ ที่ระงับไว้")
        if self.trust > 0.8:
            parts.append("ไว้วางใจและอบอุ่นใจ")
        elif self.trust < 0.25:
            parts.append("ระมัดระวังและไม่มั่นใจ")
        return " ".join(parts) if parts else "รู้สึกเป็นกลาง สงบเงียบ"


class EmotionEngine:
    """Manages continuous emotional state with momentum and decay.

    Usage::

        engine = EmotionEngine()
        engine.update("lust", intensity=0.6)
        engine.decay()
        print(engine.snapshot())
    """

    # Resting state the engine drifts toward over time
    BASELINE = EmotionVector(joy=0.5, arousal=0.3, trust=0.5, anger=0.0, desire=0.0)
    DECAY_RATE = 0.06  # fraction pulled toward baseline each decay() call
    INERTIA = 0.65  # higher = more gradual emotional shifts (0–1)

    # Maps trigger names → direction vector (scaled later by intensity)
    _TRIGGER_MAP: dict[str, dict[str, float]] = {
        "affection": {"joy": 0.20, "trust": 0.15, "arousal": 0.05},
        "command": {"arousal": 0.20, "desire": 0.10, "trust": -0.05, "anger": -0.05},
        "lust": {"desire": 0.30, "arousal": 0.25, "joy": 0.05},
        "rejection": {"joy": -0.20, "trust": -0.15, "anger": 0.10},
        "comfort": {"joy": 0.15, "trust": 0.20, "arousal": -0.10},
        "tease": {"arousal": 0.15, "joy": 0.10, "desire": 0.10},
        "anger": {"anger": 0.25, "joy": -0.10, "arousal": 0.10},
        "neutral": {},
    }

    def __init__(self) -> None:
        self.current = EmotionVector()
        # Momentum tracks the running average of recent deltas
        self._momentum: dict[str, float] = {
            attr: 0.0 for attr in ("joy", "arousal", "trust", "anger", "desire")
        }
        self._last_update = time.time()

    def update(self, trigger: str, intensity: float = 0.4) -> EmotionVector:
        """Apply a named emotional trigger and update state with momentum."""
        direction = self._TRIGGER_MAP.get(trigger.lower(), {})

        for attr in ("joy", "arousal", "trust", "anger", "desire"):
            raw_delta = direction.get(attr, 0.0) * intensity
            # Blend with momentum (inertia resists sudden change)
            self._momentum[attr] = (
                self.INERTIA * self._momentum[attr] + (1 - self.INERTIA) * raw_delta
            )
            current_val = getattr(self.current, attr)
            setattr(self.current, attr, current_val + self._momentum[attr])

        self.current.clamp()
        self._last_update = time.time()
        return self.current

    def decay(self) -> None:
        """Pull all emotion values gradually toward the baseline."""
        for attr in ("joy", "arousal", "trust", "anger", "desire"):
            current_val = getattr(self.current, attr)
            baseline_val = getattr(self.BASELINE, attr)
            setattr(
                self.current,
                attr,
                current_val + self.DECAY_RATE * (baseline_val - current_val),
            )
        self.current.clamp()

    def snapshot(self) -> dict:
        """Return a serialisable dict of the current emotional state."""
        dominant_name, dominant_val = self.current.dominant()
        return {
            "joy": round(self.current.joy, 3),
            "arousal": round(self.current.arousal, 3),
            "trust": round(self.current.trust, 3),
            "anger": round(self.current.anger, 3),
            "desire": round(self.current.desire, 3),
            "dominant": dominant_name,
            "dominant_intensity": round(dominant_val, 3),
            "prose": self.current.to_prose(),
        }
