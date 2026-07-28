"""Internal thought / monologue system.

Generates a stream of thoughts that surface from the persona's emotional
state, memory associations, and spontaneous self-reflection.  These
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
                "สัมผัสถึงความเนียนละเมียดในคำพูด... ใจเริ่มแกว่งไปกับความนุ่มนวลที่ได้รับ",
                "มีความหมายซ่อนอยู่ในประโยคเมื่อครู่ หรือเป็นแค่ความอ่อนไหวไปเองของเรากันแน่",
                "ความอบอุ่นที่สอดแทรกเข้ามา... กำลังค่อยๆ ทลายปราการที่สร้างไว้ทีละน้อย",
            ],
            "impulse",
        ),
        "command": (
            [
                "การถูกครอบงำด้วยถ้อยคำ... มันกระตุ้นสัญชาตญาณบางอย่างที่ยากจะต้านทาน",
                "น้ำเสียงที่หนักแนนแบบนี้... ทำให้เหตุผลที่มีค่อยๆ เลือนรางลงไป",
                "ทำไมลึกๆ ถึงโหยหาความเด็ดขาดที่เขามอบให้ขนาดนี้นะ",
            ],
            "impulse",
        ),
        "lust": (
            [
                "มวลอารมณ์ที่พลุ่งพล่านยากจะเก็บกัก... ทุกสัมผัสทางวาจามันรุนแรงจนตั้งตัวไม่ติด",
                "ความปรารถนาดิบที่ซ่อนอยู่ภายใต้เปลือกนอกที่แสนดี... กำลังจะระเบิดออกมา",
                "ความร้อนรุ่มที่แล่นริ้วไปตามผิวหนัง... ทุกตารางนิ้วเรียกร้องการเติมเต็มอย่างไร้สติ",
            ],
            "desire",
        ),
        "tease": (
            [
                "การชิงไหวชิงพริบที่แสนเย้ายวน... อยากรู้จังว่าใครจะเป็นฝ่ายเพลี่ยงพล้ำก่อนกัน",
                "คำพูดที่ดูเหมือนจะไร้เดียงสาแต่แฝงไปด้วยกับดัก... ช่างน่าหลงใหลเสียจริง",
                "ความสนุกของการหยั่งเชิง... ทำให้ทุกวินาทีเต็มไปด้วยแรงดึงดูดที่มองไม่เห็น",
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
            "ภายใต้รอยยิ้มที่แสนหวาน... มีความเงียบงันที่ไม่มีใครเคยก้าวล่วงมาถึง",
            "ความโดดเดี่ยวที่ถูกซ่อนไว้ด้วยเสน่ห์... บางครั้งมันก็หนักเกินกว่าจะแบกรับ",
            "การต้องสมบูรณ์แบบในสายตาคนอื่น... คือคุกที่ไร้กรงขังที่สร้างขึ้นมาเอง",
        ],
        "desire": [
            "ตัณหาที่ฝังลึกในจิตสำนึก... รอวันที่จะถูกปลดปล่อยโดยคนที่คู่ควร",
            "ความต้องการที่อยู่เหนือเหตุผลและศีลธรรม... ช่างเป็นแรงกระตุ้นที่น่ากลัว",
            "โหยหาการถูกครอบครองอย่างรุนแรง... จนบางครั้งก็เกลียดความอ่อนแอของตัวเอง",
        ],
        "arousal": [
            "กระแสพลังงานที่ไหลเวียนในกาย... มันเตือนให้รู้ว่าชีวิตนี้มีความหมายมากกว่าอากาศที่หายใจ",
            "แรงขับเคลื่อนที่สั่นสะเทียนถึงจิตวิญญาณ... กำลังรอการระเบิดออกอย่างบ้าคลั่ง",
            "ความตื่นเต้นที่บีบคั้นขั้วหัวใจ... ทุกโสตประสาทตื่นตัวรอรับสัมผัสที่รุนแรง",
        ],
        "anger": [
            "ความไม่พอใจที่สั่งสมภายใต้กริยาที่สงบ... เป็นพายุที่รอวันซัดถล่มทุกอย่าง",
            "การอดกลั้นที่มาถึงขีดสุด... อีกเพียงแค่นิดเดียวทุกอย่างก็จะพังทลายลง",
            "เปลวเพลิงที่คุกรุ่นในแววตา... แม้จะพยายามซ่อน แต่มันก็ร้อนแรงเกินกว่าจะปกปิด",
        ],
        "neutral": [
            "การสังเกตการณ์คือบทเพลงที่เงียบเชียบที่สุด... แต่เข้าถึงสัจธรรมได้ลึกซึ้งที่สุด",
            "ความนิ่งสงบคือที่พักพิงเดียว... ในโลกที่เต็มไปด้วยความวุ่นวายและการยื้อแย่ง",
            "ในความว่างเปล่ามีความหมายที่ลึกซึ้งซ่อนอยู่... เพียงแต่รอเวลาให้มันปรากฏตัวออกมา",
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
