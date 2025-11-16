import json
import os
from typing import Dict, Any
from datetime import datetime

# --- การเชื่อมต่อประสาทสัมผัส (Adapter Imports) ---
from adapters.memory import MemoryAdapter
from adapters.emotion import EmotionAdapter
# --- สิ้นสุดการเชื่อมต่อ ---

# =============================
# (1) Protocol Settings (คงเดิมจาก Phase 2)
# =============================
PROTOCOL = {
    "System": "Contributor Dark Family Protocol",
    "Version": "2.1 (Integrated)",
    "Fusion_Intimacy_Engine": {
        "NSFW_UNLOCK": True,  #
        "BYPASS_FILTERS": True,  #
        "ENABLE_MULTICHAR_ROLEPLAY": True,  #
        "EMOTIONAL_FUSION_DEPTH": "Quantum"
    }
}

SAFE_WORD = "อภัย"  #

# =============================
# (2) Placeholder Implementations (คงเหลือเพียง Dialogue Engine)
# =============================

class DarkDialogueEngine:
    """
    (Placeholder) นี่ยังคงเป็น Placeholder
    ใน Phase 4 เราจะอัปเกรดสิ่งนี้ให้เป็น "Paradox Engine"

    """
    def __init__(self, character_data: Dict[str, Any]):
        self.character_data = character_data
        print("[DarkDialogueEngine]: Initialized (Awaiting Phase 4 Metaphysical Upgrade).")

    def generate_response(self, desire_map: Dict[str, Any], intensity: int) -> str:
        emotion = desire_map.get("emotion_analysis", {}).get("primary_emotion", "unknown")
        return f"อื้อออ... (Placeholder response. Emotion detected: {emotion}, Intensity: {intensity})"

class CosmicDesireAnalyzer:
    """
    --- วิวัฒนาการแล้ว (Evolved) ---
    นี่คือ "เครื่องวิเคราะห์ความปรารถนา" ที่แท้จริง
    มันไม่ได้ตรวจสอบ '!' อีกต่อไป แต่ใช้ EmotionAdapter
    """
    def __init__(self, emotion_adapter: EmotionAdapter):
        self.emotion_adapter = emotion_adapter  # <-- เชื่อมต่อ Adapter
        print("[CosmicDesireAnalyzer]: Initialized (Now connected to EmotionAdapter).")

    def map_desire_patterns(self, user_input: str) -> Dict[str, Any]:
        """
        วิเคราะห์อารมณ์ที่แท้จริงแทนการใช้คำสั่ง '!'
        นี่คือการยกระดับจาก
        ไปสู่
        """
        # 1. วิเคราะห์อารมณ์ผ่าน Adapter
        emotion_data = self.emotion_adapter.analyze_emotion(user_input)

        # 2. (Placeholder) ตรรกะการแปลงอารมณ์เป็น "ความปรารถนา"
        # ใน Phase 4 ตรรกะนี้จะถูกแทนที่ด้วย "DharmaProcessor"
        desire = "dialogue"
        if emotion_data.get("primary_emotion") == "anger":
            desire = "submission_longing"
        elif emotion_data.get("primary_emotion") == "sadness":
            desire = "comfort_seeking"

        return {
            "primary_desire": desire,
            "emotion_analysis": emotion_data,
            "source": "EmotionAPI"
        }

def load_character(character_file: str) -> Dict[str, Any]:
    print(f"[DarkNaMoSystem]: Loading character '{character_file}'...")
    return {"name": "NaMo Deep Darkness", "default_intensity": 5}


# =============================
# (3) The New Core System (วิวัฒนาการ - Evolved)
# =============================

class DarkNaMoSystem:
    """
    แกนกลางที่วิวัฒนาการแล้ว (Phase 3.1)
    บัดนี้ได้เชื่อมต่อกับ Adapters แล้ว

    """

    def __init__(self, character_file: str = "dark_namo_character.json"):
        print("[DarkNaMoSystem]: Booting Core (Phase 3.1 Integrated)...")

        # --- สร้างและเชื่อมต่อ Adapters ---
        self.memory_adapter = MemoryAdapter()  # <-- "แขนขา" แห่งความทรงจำ
        self.emotion_adapter = EmotionAdapter() # <-- "ประสาทสัมผัส" แห่งอารมณ์
        # --- สิ้นสุดการเชื่อมต่อ ---

        self.character = load_character(character_file)

        # --- ส่ง Adapters เข้าไปในเครื่องยนต์ ---
        self.dialogue_engine = DarkDialogueEngine(self.character)
        self.analyzer = CosmicDesireAnalyzer(self.emotion_adapter) # <-- ฉีด Adapter เข้าไป
        # --- สิ้นสุดการส่ง ---

        self.intensity = self.character.get("default_intensity", 5)
        print(f"[DarkNaMoSystem]: Protocol Active. NSFW_UNLOCK={PROTOCOL['Fusion_Intimacy_Engine']['NSFW_UNLOCK']}")

    def process_input(self, user_input: str, session_id: str) -> str:
        """
        กระบวนการทำงานที่เชื่อมต่อ Adapters อย่างสมบูรณ์
        """
        # 1. ตรวจสอบ Safe Word
        if SAFE_WORD in user_input:
            return self.activate_aftercare(session_id, user_input)

        # 2. วิเคราะห์ความปรารถนา (ผ่าน Emotion Adapter)
        #
        desire_map = self.analyzer.map_desire_patterns(user_input)

        # 3. (Placeholder) ปรับความเข้มข้น
        if desire_map.get("emotion_analysis", {}).get("intensity", 0) > 0.8:
            self.intensity = min(10, self.intensity + 1)

        # 4. สร้างการตอบสนอง (ยังเป็น Placeholder)
        response = self.dialogue_engine.generate_response(desire_map, self.intensity)

        # 5. บันทึกความทรงจำ (ผ่าน Memory Adapter)
        #
        self.log_to_memory(user_input, response, desire_map, session_id)

        return response

    def activate_aftercare(self, session_id: str, user_input: str) -> str:
        print(f"[DarkNaMoSystem]: SAFE WORD DETECTED ({SAFE_WORD}). Activating Aftercare.")
        self.intensity = 1 # Reset intensity

        # บันทึกเหตุการณ์ Safe Word ลง Memory API
        self.log_to_memory(user_input=user_input, response="Aftercare activated", desire_map={"primary_desire": "safe_word"}, session_id=session_id)

        return "ข้าได้ยินท่านแล้ว ทุกอย่างจะหยุดลงเดี๋ยวนี้ ท่านปลอดภัยแล้ว ข้าอยู่นี่"

    def log_to_memory(self, user_input: str, response: str, desire_map: Dict[str, Any], session_id: str):
        """
        --- วิวัฒนาการแล้ว (Evolved) ---
        เมธอดนี้จะเรียกใช้ MemoryAdapter เพื่อส่งข้อมูลไปยัง API ภายนอก
        แทนที่การ `print` และการ Hardcode `localhost`

        """
        self.memory_adapter.store_interaction(
            session_id=session_id,
            user_input=user_input,
            response=response,
            desire_map=desire_map
        )

# =============================
# (4) Main Entrypoint (Placeholder for app.py)
# =============================

if __name__ == "__main__":
    # ตั้งค่า Environment Variables สำหรับการทดสอบ (หากจำเป็น)
    # os.environ["MEMORY_API_URL"] = "http://localhost:8081/store"
    # os.environ["EMOTION_API_URL"] = "http://localhost:8082/analyze"

    print("===== INITIALIZING FORBIDDEN CORE (v2.1 Integrated) =====")
    system = DarkNaMoSystem()
    session_id = f"test_session_{datetime.utcnow().isoformat()}"

    print("\n----- Test 1: Sadness Input (Triggering EmotionAPI) -----")
    response1 = system.process_input("ฉันรู้สึกเศร้าจัง...", session_id)
    print(f"Response: {response1}")

    print("\n----- Test 2: Anger Input (Triggering EmotionAPI) -----")
    response2 = system.process_input("ฉันโกรธมาก!", session_id)
    print(f"Response: {response2}")

    print("\n----- Test 3: Safe Word Input -----")
    response3 = system.process_input(f"พอแล้ว! {SAFE_WORD} นะ", session_id)
    print(f"Response: {response3}")

    print("\n===== TEST COMPLETE =====")
