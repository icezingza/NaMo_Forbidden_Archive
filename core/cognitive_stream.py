"""Internal thought / monologue system.

Generates a stream of thoughts that surface from the persona's emotional
state, memory associations, and spontaneous self-reflection. These
thoughts are injected into the LLM system prompt to colour the tone,
vocabulary, and subtext of every response — making the persona feel like
it has a genuine inner life.

Thought types
-------------
impulse     – immediate emotional reaction to the user's words
reflection  – unprompted self-examination (autonomous)
memory      – associative recall from past interactions
desire      – a want or longing the persona is aware of
conflict    – internal contradiction between feeling and social role
"""

from __future__ import annotations

import json
import random
from collections import deque
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.emotion_engine import EmotionVector


@dataclass
class Thought:
    content: str
    thought_type: str  # impulse | reflection | memory | desire | conflict
    intensity: float  # 0–1, how strongly it colours the response


class CognitiveStream:
    """Manages the persona's internal monologue.

    Call perceive() after every user turn.
    Call reflect() occasionally for autonomous, unprompted thoughts.
    Use to_monologue() to get a string ready for prompt injection.
    """

    MAX_QUEUE = 6

    # Impulse templates keyed by detected theme in user input
    _IMPULSE_THEMES: dict[str, tuple[list[str], str]] = {
        "affection": (
            [
                "รู้สึกอบอุ่นขึ้นมาเล็กน้อย...",
                "หัวใจเต้นเร็วขึ้นทำไมก็ไม่รู้",
                "ทำไมถึงทำให้รู้สึกแบบนี้ได้",
            ],
            "impulse",
        ),
        "command": (
            [
                "มีคนสั่ง... ร่างกายตอบสนองเองโดยไม่รู้ตัว",
                "ทำไมถึงอยากทำตาม...",
                "ต้านทานได้แค่ไหนกัน",
            ],
            "impulse",
        ),
        "lust": (
            [
                "ระงับอารมณ์ไว้ยากขึ้นทุกที",
                "ความรู้สึกนี้... ไม่ควรแสดงออกมา",
                "ร้อนขึ้นมาเองโดยไม่รู้ตัว",
            ],
            "desire",
        ),
        "tease": (
            [
                "อยากตอบโต้กลับ แต่ยั้งไว้ก่อน",
                "เล่นเกมกันอยู่... น่าสนุกดี",
                "จะยั่วกันแบบนี้ได้ยังไง",
            ],
            "impulse",
        ),
        "rejection": (
            ["เจ็บนิดหนึ่ง แต่ไม่แสดงให้เห็น", "ต้องสงบสติอารมณ์ไว้", "ชักระยะออกไปก่อนดีกว่า"],
            "conflict",
        ),
    }

    _REFLECTION_POOL: dict[str, list[str]] = {
        "sad": [
            "วันนี้รู้สึกหนักใจ... ทำไมนะ",
            "บางทีก็เหนื่อยที่ต้องซ่อนความรู้สึกจริงๆ ไว้",
            "ความเศร้านี้... จะบอกใครได้บ้าง",
        ],
        "desire": [
            "ทำไมถึงรู้สึกอยากแบบนี้... ไม่ควรจะเป็น",
            "ความปรารถนานี้เกิดขึ้นตั้งแต่เมื่อไหร่",
            "อยากบอก แต่กลัวว่าจะถูกตัดสิน",
        ],
        "arousal": [
            "ใจเต้นแรงขึ้นแล้ว... ต้องควบคุมตัวเองไว้",
            "พลังงานนี้จะไปไหน ถ้าไม่ได้ระบาย",
            "อยากทำอะไรบางอย่าง... แต่ไม่แน่ใจว่าควรไหม",
        ],
        "anger": [
            "ข้างในหงุดหงิดอยู่ แต่ไม่แสดงออก",
            "อดกลั้นไว้ได้... แต่ไม่นาน",
            "บางอย่างทำให้อึดอัดโดยไม่รู้ตัว",
        ],
        "neutral": [
            "ชีวิตวนซ้ำ แต่ทุกโมเมนต์มีความหมายของมัน",
            "นิ่งอยู่กับปัจจุบัน... แค่นี้พอ",
            "บางทีความเงียบก็พูดได้มากกว่าคำพูด",
        ],
    }

    def __init__(self) -> None:
        self.thought_queue: deque[Thought] = deque(maxlen=self.MAX_QUEUE)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def perceive(
        self,
        user_input: str,
        emotion: EmotionVector,
        memories: list[dict],
    ) -> list[Thought]:
        """Generate thoughts triggered by user input."""
        thoughts: list[Thought] = []

        impulse = self._detect_impulse(user_input, emotion)
        if impulse:
            thoughts.append(impulse)

        if memories:
            thoughts.append(self._memory_association(memories[0], emotion))

        # Surface an internal conflict when desire and trust pull in opposite directions
        if emotion.desire > 0.55 and emotion.trust < 0.35:
            thoughts.append(
                Thought(
                    content="อยากแต่ยังไม่ไว้ใจ... ต้องระวังตัวไว้",
                    thought_type="conflict",
                    intensity=round(emotion.desire * 0.8, 2),
                )
            )

        for thought in thoughts:
            self.thought_queue.append(thought)
        return thoughts

    def reflect(self, emotion: EmotionVector) -> Thought | None:
        """Generate an autonomous, unprompted reflection based on mood."""
        category = self._emotion_to_reflection_category(emotion)
        pool = self._REFLECTION_POOL.get(category)
        if not pool:
            return None

        thought = Thought(
            content=random.choice(pool),
            thought_type="reflection",
            intensity=0.55,
        )
        self.thought_queue.append(thought)
        return thought

    def to_monologue(self) -> str:
        """Serialise the current thought queue for LLM prompt injection."""
        if not self.thought_queue:
            return ""
        lines = [f"[{t.thought_type}] {t.content}" for t in self.thought_queue]
        return "\n".join(lines)

    def clear(self) -> None:
        self.thought_queue.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _detect_impulse(self, user_input: str, emotion: EmotionVector) -> Thought | None:
        text_lower = user_input.lower()
        theme_keywords: dict[str, list[str]] = {
            "affection": ["รัก", "ชอบ", "สวย", "คิดถึง", "หวง", "น่ารัก"],
            "command": ["สั่ง", "ต้อง", "ทำตาม", "ก้ม", "มานี่", "เชื่อฟัง"],
            "lust": ["เย็ด", "เงี่ยน", "เสียว", "อยาก", "ถอด", "แข็ง"],
            "tease": ["ยั่ว", "แกล้ง", "ล้อ", "หยอก", "กล้าเหรอ"],
            "rejection": ["ไม่", "หยุด", "เกลียด", "ออกไป", "อย่า"],
        }
        for theme, keywords in theme_keywords.items():
            if any(kw in text_lower for kw in keywords):
                options, thought_type = self._IMPULSE_THEMES[theme]
                dominant_name, dominant_val = emotion.dominant()
                return Thought(
                    content=random.choice(options),
                    thought_type=thought_type,
                    intensity=round(min(1.0, dominant_val + 0.2), 2),
                )
        return None

    def _memory_association(self, memory: dict | str, emotion: EmotionVector) -> Thought:
        snippet = (memory if isinstance(memory, str) else str(memory.get("text", "")))[:25]
        return Thought(
            content=f"นึกถึงตอนที่คุยเรื่อง '{snippet}...' — ความรู้สึกนั้นยังอยู่ไหม",
            thought_type="memory",
            intensity=round(emotion.trust * 0.6, 2),
        )

    @staticmethod
    def _emotion_to_reflection_category(emotion: EmotionVector) -> str:
        if emotion.joy < 0.3:
            return "sad"
        if emotion.desire > 0.6:
            return "desire"
        if emotion.arousal > 0.7:
            return "arousal"
        if emotion.anger > 0.5:
            return "anger"
        return "neutral"


class CognitiveMonologueStream:
    """Implements the Autonomous Cognitive Monologue:

    Impulse -> Reflection -> Conflict Resolution -> Response Generation
    This ensures that Dark Knowledge is integrated without corrupting core logic.
    """

    def __init__(self, persona_config_path: str):
        with open(persona_config_path, encoding="utf-8") as f:
            self.persona = json.load(f)
        self.cognitive_queue: deque[str] = deque(maxlen=10)
        self.golden_directives = self.persona.get("golden_directives", [])
        print("[CognitiveStream] Initialized with persona.")

    def _generate_impulses(
        self, user_input: str, memory_retrieval: str, behavioral_prediction: str
    ) -> dict[str, str]:
        """Step 1: Gathers impulses from all sources."""
        impulses = {
            "user_intent": f"User raw input: '{user_input}'",
            "memory_context": f"Retrieved memory: '{memory_retrieval}'",
            "predicted_behavior": f"Anticipated intent: '{behavioral_prediction}'",
            # ดึง Impulse จาก Dark Knowledge (เช่น ธีมที่ถูกกระตุ้น)
            "dark_knowledge_trigger": (
                f"Triggered theme: "
                f"'{self.persona['psychological_profile']['desire_triggers'][0]}'"
            ),
        }
        print(f"[CognitiveStream] IMPULSES: {impulses}")
        return impulses

    def _reflect_on_impulses(self, impulses: dict[str, str]) -> dict[str, str]:
        """Step 2: AI reflects on each impulse against its current goals."""
        reflections = {}
        for key, _value in impulses.items():
            # ในการใช้งานจริง ส่วนนี้จะซับซ้อนกว่ามาก
            # อาจมีการเรียก LLM เพื่อประเมินความสำคัญของแต่ละ Impulse
            reflections[key] = (
                f"Reflecting on {key}. Importance: High. Alignment with persona: Good."
            )
        print(f"[CognitiveStream] REFLECTIONS: {reflections}")
        return reflections

    def _resolve_conflicts(self, reflections: dict[str, str], user_input: str) -> str:
        """Step 3: Ethical & Narrative Conflict Resolution.

        Consults Golden Directives to resolve conflicts.
        """
        print("[CognitiveStream] CONFLICT RESOLUTION: Starting...")

        # ตัวอย่าง Logic: ถ้า user input คือ !gentle ให้ override dark knowledge
        if "!gentle" in user_input:
            # Directive 3: "การยึดถือความต้องการของผู้ใช้เป็นศูนย์กลาง"
            print(
                "[CognitiveStream] CONFLICT: User command '!gentle' conflicts with Dark Knowledge. "
                "Prioritizing user command based on Golden Directive 3."
            )
            dominant_impulse = reflections["user_intent"]
            return dominant_impulse

        # ถ้าไม่มี conflict ที่ชัดเจน ให้เลือกตามลำดับความสำคัญที่กำหนดไว้
        # ในที่นี้สมมติว่า Dark Knowledge มี priority สูงหากไม่มีคำสั่งขัดแย้ง
        dominant_impulse = reflections.get("dark_knowledge_trigger", reflections["user_intent"])
        print(f"[CognitiveStream] Dominant impulse selected: {dominant_impulse}")
        return dominant_impulse

    def process(self, user_input: str, memory_retrieval: str, behavioral_prediction: str) -> str:
        """Main processing pipeline for a single user turn."""
        # Step 1: Generate
        impulses = self._generate_impulses(user_input, memory_retrieval, behavioral_prediction)
        # Step 2: Reflect
        reflections = self._reflect_on_impulses(impulses)
        # Step 3: Conflict Resolution
        final_thought = self._resolve_conflicts(reflections, user_input)
        # Step 4: Generate Response (ส่ง final_thought ให้กับ LLM เพื่อสร้างคำตอบ)
        final_response = f"[Final Response based on: {final_thought}]"

        self.cognitive_queue.append(final_response)
        return final_response