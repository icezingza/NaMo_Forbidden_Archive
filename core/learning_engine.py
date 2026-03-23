"""Self-learning engine: observes interactions and adapts the persona over time.

After every user turn the engine records what happened (intent, emotion
state, vocabulary) and uses that to:

1. Track which topics / intents appear most often.
2. Evolve persona trait values (boldness, playfulness, vulnerability,
   expressiveness) so that frequently encountered scenarios are handled
   more naturally over time.
3. Persist everything to a JSON file for cross-session continuity.

Nothing here generates text.  The output is structured data (trait values,
preferences) that other modules — primarily the LLM prompt builder — use
to personalise responses.
"""

from __future__ import annotations

import json
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class InteractionPattern:
    """Aggregated statistics for one (intent, dominant_emotion) combination."""

    trigger: str
    response_type: str
    count: int = 0
    total_arousal: float = 0.0
    last_seen: float = field(default_factory=time.time)

    @property
    def avg_arousal(self) -> float:
        return self.total_arousal / max(1, self.count)

    def record(self, arousal: float) -> None:
        self.count += 1
        self.total_arousal += arousal
        self.last_seen = time.time()


class LearningEngine:
    """Observes interactions and adapts persona traits over time.

    Usage::

        engine = LearningEngine(save_path=Path("learned.json"))
        engine.observe("ไอซ์สวยมากเลย", "affection", emotion_snapshot)
        traits = engine.adapt_traits()
        prefs  = engine.get_preferences()
    """

    SAVE_INTERVAL = 10  # write to disk every N observations
    MAX_PATTERNS = 200  # prune oldest patterns beyond this limit

    # Topic → Thai keywords
    _TOPIC_KEYWORDS: dict[str, list[str]] = {
        "romance": ["รัก", "ชอบ", "คิดถึง", "หวง", "อยากอยู่ด้วย", "คู่"],
        "dominance": ["สั่ง", "ทำตาม", "ก้ม", "เชื่อฟัง", "ต้อง"],
        "intimacy": ["กอด", "จูบ", "ใกล้", "ซบ", "แนบ", "แตะ"],
        "casual": ["ว่าไง", "ทำอะไร", "อยู่ไหน", "กินข้าว", "เป็นยังไง"],
        "emotional": ["เศร้า", "เหงา", "เหนื่อย", "ดีใจ", "กลัว", "อาย"],
    }

    def __init__(self, save_path: Path | None = None) -> None:
        self.save_path = save_path or Path("learned_patterns.json")
        self.patterns: dict[str, InteractionPattern] = {}
        self.user_vocabulary: Counter[str] = Counter()
        self.topic_affinity: dict[str, float] = defaultdict(float)

        # Trait values evolve from 0–1 based on observed interaction patterns
        self.persona_traits: dict[str, float] = {
            "boldness": 0.50,  # assertiveness in responses
            "playfulness": 0.50,  # tendency to tease / humour
            "vulnerability": 0.30,  # how much inner conflict surfaces
            "expressiveness": 0.50,  # richness of emotional language
        }

        self._observation_count = 0
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def observe(
        self,
        user_input: str,
        intent: str,
        emotion_snapshot: dict[str, Any],
    ) -> None:
        """Record one interaction turn."""
        dominant = emotion_snapshot.get("dominant", "neutral")
        key = f"{intent}_{dominant}"

        if key not in self.patterns:
            self.patterns[key] = InteractionPattern(trigger=intent, response_type=key)
        self.patterns[key].record(emotion_snapshot.get("arousal", 0.3))

        # Vocabulary tracking (skip very short words)
        self.user_vocabulary.update(w for w in user_input.split() if len(w) > 1)

        # Topic affinity
        for topic, keywords in self._TOPIC_KEYWORDS.items():
            if any(kw in user_input for kw in keywords):
                self.topic_affinity[topic] = min(1.0, self.topic_affinity[topic] + 0.04)

        # Slight natural decay on all affinities each turn
        for topic in self.topic_affinity:
            self.topic_affinity[topic] = max(0.0, self.topic_affinity[topic] - 0.005)

        self._observation_count += 1
        self._prune_patterns()
        self._maybe_save()

    def adapt_traits(self) -> dict[str, float]:
        """Recompute persona trait values from accumulated patterns."""
        counts = {k: p.count for k, p in self.patterns.items()}
        command_n = sum(v for k, v in counts.items() if k.startswith("Command"))
        lust_n = sum(v for k, v in counts.items() if k.startswith("Lust"))
        affection_n = sum(v for k, v in counts.items() if k.startswith("affection"))
        total = max(1, command_n + lust_n + affection_n)

        self.persona_traits["boldness"] = round(
            min(0.92, 0.30 + (command_n / total) * 0.62), 3
        )  # noqa: E501
        self.persona_traits["playfulness"] = round(
            min(0.92, 0.30 + (lust_n / total) * 0.55), 3
        )  # noqa: E501
        self.persona_traits["vulnerability"] = round(
            min(0.85, 0.20 + (affection_n / total) * 0.55), 3
        )  # noqa: E501
        # Expressiveness grows with overall experience (capped at 0.9)
        self.persona_traits["expressiveness"] = round(
            min(0.90, 0.40 + self._observation_count / 500), 3
        )
        return dict(self.persona_traits)

    def get_preferences(self) -> dict[str, Any]:
        """Summarise what has been learned about this user."""
        top_words = [w for w, _ in self.user_vocabulary.most_common(12) if len(w) > 2][:8]
        top_topics = sorted(self.topic_affinity, key=self.topic_affinity.__getitem__, reverse=True)[
            :3
        ]  # noqa: E501
        return {
            "frequent_words": top_words,
            "preferred_topics": top_topics,
            "trait_evolution": dict(self.persona_traits),
            "total_interactions": self._observation_count,
        }

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not self.save_path.exists():
            return
        try:
            data = json.loads(self.save_path.read_text(encoding="utf-8"))
            self.topic_affinity = defaultdict(float, data.get("topic_affinity", {}))
            self.persona_traits.update(data.get("persona_traits", {}))
            self._observation_count = data.get("observation_count", 0)
            vocab = data.get("user_vocabulary", {})
            self.user_vocabulary = Counter(vocab)
        except Exception:
            pass  # corrupt or missing — start fresh

    def _maybe_save(self) -> None:
        if self._observation_count % self.SAVE_INTERVAL != 0:
            return
        try:
            payload = {
                "topic_affinity": dict(self.topic_affinity),
                "persona_traits": self.persona_traits,
                "observation_count": self._observation_count,
                "user_vocabulary": dict(self.user_vocabulary.most_common(300)),
            }
            self.save_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except Exception:
            pass

    def _prune_patterns(self) -> None:
        if len(self.patterns) > self.MAX_PATTERNS:
            # Remove least-recently-seen patterns
            sorted_keys = sorted(self.patterns, key=lambda k: self.patterns[k].last_seen)
            for key in sorted_keys[: len(self.patterns) - self.MAX_PATTERNS]:
                del self.patterns[key]
