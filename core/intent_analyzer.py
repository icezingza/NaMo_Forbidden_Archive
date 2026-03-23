"""Lightweight intent analysis for determining user intent without heavy LLM calls.

This parses basic keywords and maps user inputs to the explicit intents supported
by EmotionEngine and CognitiveStream.
"""

from __future__ import annotations

import re
from collections.abc import Iterable


class IntentAnalyzer:
    """Parses text to extract a dominant intent for the cognitive stack."""

    _PRIORITY: tuple[str, ...] = (
        "anger",
        "rejection",
        "comfort",
        "nostalgia",
        "lust",
        "command",
        "affection",
        "tease",
    )

    def __init__(self) -> None:
        # Maps to the exact keys in EmotionEngine._TRIGGER_MAP
        self.themes: dict[str, tuple[str, ...]] = {
            "affection": (
                "รัก",
                "ชอบ",
                "สวย",
                "คิดถึง",
                "หวง",
                "น่ารัก",
                "ที่รัก",
                "คนดี",
                "จุ๊บ",
                "love",
                "miss you",
                "beautiful",
                "cute",
                "sweetheart",
                "darling",
                "kiss",
            ),
            "command": (
                "สั่ง",
                "ต้อง",
                "ทำตาม",
                "ก้ม",
                "มานี่",
                "เชื่อฟัง",
                "อ้า",
                "เลีย",
                "คุกเข่า",
                "obey",
                "listen",
                "do it",
                "kneel",
                "come here",
                "follow",
                "sit down",
            ),
            "lust": (
                "เย็ด",
                "เงี่ยน",
                "เสียว",
                "อยาก",
                "ถอด",
                "แข็ง",
                "ควย",
                "รุม",
                "แตก",
                "หี",
                "horny",
                "sexy",
                "naked",
                "touch me",
                "fuck",
                "moan",
                "desire",
            ),
            "tease": (
                "ยั่ว",
                "แกล้ง",
                "ล้อ",
                "หยอก",
                "กล้าเหรอ",
                "หึๆ",
                "ท้า",
                "tease",
                "dare",
                "mock",
                "brat",
            ),
            "rejection": (
                "หยุด",
                "เกลียด",
                "ออกไป",
                "อย่า",
                "พอแล้ว",
                "ไม่เอา",
                "ไม่ต้อง",
                "stop teasing",
                "leave me alone",
                "go away",
                "not now",
                "enough",
                "stop",
                "hate",
                "don't",
                "do not",
                "no",
            ),
            "comfort": (
                "ปลอบ",
                "โอ๋",
                "กอด",
                "ไม่เป็นไร",
                "ลูบหัว",
                "พักผ่อน",
                "อยู่ตรงนี้",
                "hug",
                "hold me",
                "it's okay",
                "its okay",
                "stay with me",
                "comfort",
                "rest",
                "calm down",
            ),
            "nostalgia": (
                "อดีต",
                "เมื่อก่อน",
                "จำได้ไหม",
                "จำได้",
                "ตอนนั้น",
                "ครั้งแรก",
                "วันนั้น",
                "สมัยก่อน",
                "ย้อนหลัง",
                "ตอนแรก",
                "remember",
                "remember when",
                "used to",
                "back then",
                "nostalgia",
                "miss those days",
                "old times",
                "in the past",
            ),
            "anger": (
                "โกรธ",
                "รำคาญ",
                "โมโห",
                "งี่เง่า",
                "น่าเบื่อ",
                "angry",
                "annoyed",
                "pissed",
                "furious",
                "mad",
                "idiot",
                "stupid",
            ),
        }

    def analyze(self, text: str) -> str:
        """Return the strongest matching intent for the user input."""
        normalized = self._normalize(text)
        if not normalized:
            return "neutral"

        best_intent = "neutral"
        best_score = 0
        for intent in self._PRIORITY:
            score = self._score_matches(normalized, self.themes.get(intent, ()))
            if score > best_score:
                best_intent = intent
                best_score = score

        return best_intent

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text.lower().strip())

    @staticmethod
    def _score_matches(text: str, keywords: Iterable[str]) -> int:
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += max(1, len(keyword.replace(" ", "")))
        return score
