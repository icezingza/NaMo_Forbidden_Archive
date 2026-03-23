"""Lightweight intent analysis for determining user intent without heavy LLM calls.

This parses basic keywords and maps user inputs to the explicit intents supported
by EmotionEngine and CognitiveStream.
"""

from __future__ import annotations


class IntentAnalyzer:
    """Parses text to extract a dominant intent for the cognitive stack."""

    def __init__(self) -> None:
        # Maps to the exact keys in EmotionEngine._TRIGGER_MAP
        self.themes: dict[str, list[str]] = {
            "affection": ["รัก", "ชอบ", "สวย", "คิดถึง", "หวง", "น่ารัก", "ที่รัก", "คนดี", "จุ๊บ"],
            "command": ["สั่ง", "ต้อง", "ทำตาม", "ก้ม", "มานี่", "เชื่อฟัง", "อ้า", "เลีย", "คุกเข่า"],
            "lust": ["เย็ด", "เงี่ยน", "เสียว", "อยาก", "ถอด", "แข็ง", "ควย", "รุม", "แตก", "หี"],
            "tease": ["ยั่ว", "แกล้ง", "ล้อ", "หยอก", "กล้าเหรอ", "หึๆ", "ท้า"],
            "rejection": ["ไม่", "หยุด", "เกลียด", "ออกไป", "อย่า", "พอแล้ว"],
            "comfort": ["ปลอบ", "โอ๋", "กอด", "ไม่เป็นไร", "ลูบหัว", "พักผ่อน"],
            "anger": ["โกรธ", "รำคาญ", "โมโห", "งี่เง่า", "น่าเบื่อ"],
        }

    def analyze(self, text: str) -> str:
        """Return the highest priority intent matching the user input."""
        text_lower = text.lower()
        
        # We process in order of dictionary definition, relying on themes order 
        # as a rough priority.
        for intent, keywords in self.themes.items():
            if any(kw in text_lower for kw in keywords):
                return intent
                
        return "neutral"
