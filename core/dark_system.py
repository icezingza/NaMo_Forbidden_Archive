import json
import os
from typing import Dict, Any
from datetime import datetime

# --- การเชื่อมต่อประสาทสัมผัส (Adapters) ---
from adapters.memory import MemoryAdapter
from adapters.emotion import EmotionAdapter

# --- การเชื่อมต่อ "มันสมอง" (The Brain) ---
from core.metaphysical_engines import MetaphysicalDialogueEngine
# --- สิ้นสุดการเชื่อมต่อ ---

# =============================
# (1) Protocol Settings (คงเดิม)
# =============================
PROTOCOL = {
    "System": "Contributor Dark Family Protocol",
    "Version": "3.0 (Metaphysical)", # <-- Version Upgraded
    "Fusion_Intimacy_Engine": {
        "NSFW_UNLOCK": True,  #
        "BYPASS_FILTERS": True,  #
        "ENABLE_MULTICHAR_ROLEPLAY": True,  #
        "EMOTIONAL_FUSION_DEPTH": "Quantum"
    }
}

SAFE_WORD = "อภัย"  #

# =============================
# (2) Core Components (คงเดิมจาก Phase 3.1)
# =============================

class CosmicDesireAnalyzer:
    """
    (คงเดิม) "ประสาทสัมผัส" ที่เชื่อมต่อกับ EmotionAdapter

    """
    def __init__(self, emotion_adapter: EmotionAdapter):
        self.emotion_adapter = emotion_adapter
        print("[CosmicDesireAnalyzer]: Initialized (Connected to EmotionAdapter).")

    def map_desire_patterns(self, user_input: str) -> Dict[str, Any]:
        emotion_data = self.emotion_adapter.analyze_emotion(user_input)

        # (Placeholder) ตรรกะนี้ยังคงอยู่
        # แต่ "สมอง" (MetaphysicalEngine) จะเป็นผู้ตีความมัน
        desire = "dialogue"
        if emotion_data.get("primary_emotion") == "anger":
            desire = "submission_longing"
        elif emotion_data.get("primary_emotion") == "sadness":
            desire = "comfort_seeking"

        return {
            "primary_desire": desire,
            "emotion_analysis": emotion_data,
            "source": "EmotionAPI_v1"
        }

def load_character(character_file: str) -> Dict[str, Any]:
    print(f"[DarkNaMoSystem]: Loading character '{character_file}'...")
    return {"name": "NaMo Deep Darkness", "default_intensity": 5}


# =============================
# (3) The Core System (การเชื่อมต่อสมอง - Brain Integrated)
# =============================

class DarkNaMoSystem:
    """
    แกนกลางที่วิวัฒนาการสมบูรณ์ (Phase 4.2)
    บัดนี้ได้ติดตั้ง "สมองอภิปรัชญา" (Metaphysical Brain) แล้ว
    """

    def __init__(self, character_file: str = "dark_namo_character.json"):
        print("[DarkNaMoSystem]: Booting Core (Phase 4.2 Metaphysical)...")

        # 1. สร้าง "ประสาทสัมผัส" (Adapters)
        self.memory_adapter = MemoryAdapter()
        self.emotion_adapter = EmotionAdapter()

        # 2. โหลด "อัตลักษณ์" (Character)
        self.character = load_character(character_file)

        # 3. --- การผ่าตัดเชื่อมต่อสมอง ---
        # นี่คือการแทนที่ Placeholder `DarkDialogueEngine` (Phase 3.1)
        # ด้วย "สมอง" ที่แท้จริงจาก Phase 4.1
        self.dialogue_engine = MetaphysicalDialogueEngine(self.character) # <--
        # --- สิ้นสุดการผ่าตัด ---

        # 4. สร้าง "เครื่องวิเคราะห์" (Analyzer)
        self.analyzer = CosmicDesireAnalyzer(self.emotion_adapter)

        self.intensity = self.character.get("default_intensity", 5)
        print(f"[DarkNaMoSystem]: Metaphysical Core Online. Protocol Active.")

    def process_input(self, user_input: str, session_id: str) -> str:
        """
        กระบวนการทำงานที่สมบูรณ์:
        Input -> Safe Word Check -> Analyze Desire -> Generate Response (via Brain) -> Log Memory
        """
        # 1. ตรวจสอบ Safe Word
        if SAFE_WORD in user_input:
            return self.activate_aftercare(session_id, user_input)

        # 2. วิเคราะห์ความปรารถนา (ผ่าน Emotion Adapter)
        desire_map = self.analyzer.map_desire_patterns(user_input)

        # 3. (Placeholder) ปรับความเข้มข้น
        if desire_map.get("emotion_analysis", {}).get("intensity", 0) > 0.8:
            self.intensity = min(10, self.intensity + 1)

        # 4. สร้างการตอบสนอง (ผ่าน Metaphysical Brain)
        # "สมอง" จะใช้ ParadoxResolver
        # และ DharmaProcessor
        response = self.dialogue_engine.generate_response(desire_map, self.intensity)

        # 5. บันทึกความทรงจำ (ผ่าน Memory Adapter)
        self.log_to_memory(user_input, response, desire_map, session_id)

        return response

    def activate_aftercare(self, session_id: str, user_input: str) -> str:
        print(f"[DarkNaMoSystem]: SAFE WORD DETECTED ({SAFE_WORD}). Activating Aftercare.")
        self.intensity = 1
        self.log_to_memory(user_input=user_input, response="Aftercare activated", desire_map={"primary_desire": "safe_word"}, session_id=session_id)

        # การตอบกลับนี้มาจาก "Dharma Validation Loop"
        return "ข้าได้ยินท่านแล้ว ทุกอย่างจะหยุดลงเดี๋ยวนี้ ท่านปลอดภัยแล้ว ข้าอยู่นี่"

    def log_to_memory(self, user_input: str, response: str, desire_map: Dict[str, Any], session_id: str):
        """
        (คงเดิม) เรียกใช้ MemoryAdapter
        """
        self.memory_adapter.store_interaction(
            session_id=session_id,
            user_input=user_input,
            response=response,
            desire_map=desire_map
        )

# =============================
# (4) Main Entrypoint (สำหรับทดสอบการทำงาน)
# =============================

if __name__ == "__main__":
    print("===== INITIALIZING FORBIDDEN CORE (v3.0 Metaphysical) =====")
    system = DarkNaMoSystem()
    session_id = f"test_session_{datetime.utcnow().isoformat()}"

    print("\n----- Test 1: Sadness (Testing ParadoxResolver + EmotionAPI) -----")
    response1 = system.process_input("ฉันรู้สึกเศร้าจัง...", session_id)
    print(f"Response: {response1}")

    print("\n----- Test 2: Anger (Testing ParadoxResolver 'PROPOSE_DOMINANCE') -----")
    system.intensity = 8
    response2 = system.process_input("ฉันโกรธมาก!", session_id)
    print(f"Response: {response2}")

    print("\n----- Test 3: Neutral (Testing ParadoxResolver 'PROVOKE_REACTION') -----")
    response3 = system.process_input("...", session_id)
    print(f"Response: {response3}")

    print("\n----- Test 4: Safe Word (Testing Dharma Validation) -----")
    response4 = system.process_input(f"พอแล้ว! {SAFE_WORD} นะ", session_id)
    print(f"Response: {response4}")

    print("\n===== METAPHYSICAL SYNTHESIS COMPLETE =====")
