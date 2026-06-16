import logging
from datetime import datetime
from typing import Any

from arousal_detector import ArousalDetector

logger = logging.getLogger(__name__)

class SubconsciousAnalyzer:
    """
    วิเคราะห์ความฝันและจิตใต้สำนึก (Dream/Subconscious Analysis Engine)
    เชื่อมโยงความฝันเข้ากับค่าอารมณ์เพื่อทำความเข้าใจตัวตนผู้ใช้
    """

    def __init__(self):
        self.detector = ArousalDetector()

    def analyze_dream_log(self, dream_text: str, current_arousal: float) -> dict[str, Any]:
        """
        ประมวลผลบันทึกความฝันเทียบกับอารมณ์ในปัจจุบัน
        """
        logger.info("[Subconscious]: Analyzing dream patterns...")
        
        # วิเคราะห์ความเข้มข้นจากความฝัน
        analysis = self.detector.detect_arousal(dream_text)
        
        # สร้างโปรไฟล์จิตใต้สำนึก
        subconscious_profile = {
            "timestamp": datetime.utcnow().isoformat(),
            "dream_intensity": analysis["arousal_level"],
            "correlation_score": abs(analysis["arousal_level"] - current_arousal),
            "key_themes": self._extract_themes(dream_text)
        }
        
        return subconscious_profile

    def _extract_themes(self, text: str) -> list[str]:
        # Simple theme extraction placeholder
        themes = []
        if any(w in text for w in ["บิน", "ตก", "วิ่ง"]):
            themes.append("Freedom/Anxiety")
        if any(w in text for w in ["คนรัก", "สัมผัส", "จูบ"]):
            themes.append("Intimacy")
        if any(w in text for w in ["มืด", "ห้องปิด", "กับดัก"]):
            themes.append("Control")
        return themes
