"""Shared interface and cognitive bundle for all NaMo persona engines.

BasePersonaEngine
-----------------
Every persona engine must implement process_input() and return the
standard dict shape documented below.  _build_system_prompt() and
get_status() have sensible defaults that subclasses may override.

CognitiveCore
-------------
An optional bundle of the three new cognitive subsystems:

    EmotionEngine    – continuous, momentum-based emotion state
    CognitiveStream  – internal monologue and autonomous reflection
    LearningEngine   – pattern learning and trait evolution

Attach it to any engine by calling init_cognition() in __init__.
If it is not attached the engine works exactly as before — backwards
compatible by design.

Standard process_input() return shape (do not break):
    {
        "text":         str,
        "media_trigger": {"image": str | None, "audio": str | None, "tts": str | None},
        "system_status": dict,
    }
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class CognitiveCore:
    """Bundle of the three cognitive subsystems.

    Provides a single process() call that runs the full cognitive cycle
    (emotion update → thought generation → learning) and returns an
    enriched context dict ready to be merged into the LLM prompt.
    """

    def __init__(self, save_dir: Path | None = None) -> None:
        from core.cognitive_stream import CognitiveStream
        from core.emotion_engine import EmotionEngine
        from core.learning_engine import LearningEngine

        base = save_dir or Path(".")
        self.emotion = EmotionEngine()
        self.thoughts = CognitiveStream()
        self.learning = LearningEngine(save_path=base / "learned_patterns.json")

    def process(
        self,
        user_input: str,
        intent: str,
        memories: list[dict[str, Any]],
        intensity: float = 0.45,
    ) -> dict[str, Any]:
        """Run one full cognitive cycle.

        Returns a dict with keys:
            emotion          – full emotion snapshot
            monologue        – internal thought string (prompt-ready)
            autonomous       – autonomous reflection text or None
            persona_traits   – current evolved trait values
            preferences      – summarised user preferences
        """
        # 1. Emotion: update then decay toward baseline
        self.emotion.update(intent.lower(), intensity=intensity)
        self.emotion.decay()

        # 2. Thoughts: reactive + autonomous
        new_thoughts = self.thoughts.perceive(
            user_input, self.emotion.current, memories
        )
        autonomous = self.thoughts.reflect(self.emotion.current)

        # 3. Learning: record this turn
        self.learning.observe(user_input, intent, self.emotion.snapshot())

        return {
            "emotion":        self.emotion.snapshot(),
            "monologue":      self.thoughts.to_monologue(),
            "autonomous":     autonomous.content if autonomous else None,
            "persona_traits": self.learning.adapt_traits(),
            "preferences":    self.learning.get_preferences(),
        }

    def build_context_block(self, cognitive_output: dict[str, Any]) -> str:
        """Format cognitive output as a terse string for LLM system prompt injection."""
        emo = cognitive_output.get("emotion", {})
        traits = cognitive_output.get("persona_traits", {})
        monologue = cognitive_output.get("monologue", "")
        autonomous = cognitive_output.get("autonomous")

        lines = [
            f"[感情状態] {emo.get('prose', '')}",
            f"[dominant] {emo.get('dominant', '')} ({emo.get('dominant_intensity', 0):.2f})",
            f"[traits] boldness={traits.get('boldness', 0.5):.2f} "
            f"playfulness={traits.get('playfulness', 0.5):.2f} "
            f"vulnerability={traits.get('vulnerability', 0.3):.2f}",
        ]
        if monologue:
            lines.append(f"[inner thoughts]\n{monologue}")
        if autonomous:
            lines.append(f"[autonomous reflection] {autonomous}")
        return "\n".join(lines)


class BasePersonaEngine(ABC):
    """Abstract base for all NaMo persona engines.

    Subclass and implement process_input().  Optionally call
    init_cognition() in __init__ to enable the full cognitive stack.
    """

    def init_cognition(self, save_dir: Path | None = None) -> None:
        """Attach a CognitiveCore to this engine instance."""
        self.cognitive: CognitiveCore | None = CognitiveCore(save_dir=save_dir)

    @abstractmethod
    def process_input(self, user_input: str, session_id: str | None = None) -> dict:
        """Process user input and return a structured response.

        Return shape (contract — do not change):
        {
            "text":          str,
            "media_trigger": {"image": str | None, "audio": str | None, "tts": str | None},
            "system_status": dict,
        }
        """
        ...

    def stream_input(self, user_input: str, session_id: str | None = None):
        """Yield text chunks for streaming responses (Server-Sent Events).

        Default implementation calls process_input() and yields the full
        text as a single chunk.  Override in subclasses that support true
        token-by-token LLM streaming.
        """
        result = self.process_input(user_input, session_id=session_id)
        yield result["text"]

    def _build_system_prompt(self, context: str) -> str:
        """Build the system prompt for the current context.

        Override to inject persona-specific instructions.
        """
        return f"[{self.__class__.__name__}] context: {context}"

    def get_status(self) -> dict[str, Any]:
        """Return current engine status for health / diagnostics endpoints."""
        status: dict[str, Any] = {
            "engine": self.__class__.__name__,
            "status": "online",
        }
        cognitive: CognitiveCore | None = getattr(self, "cognitive", None)
        if cognitive is not None:
            status["emotion"] = cognitive.emotion.snapshot()
            status["traits"]  = cognitive.learning.persona_traits
        return status
