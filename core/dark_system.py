import json
import os
from typing import Dict, Any
from datetime import datetime

# --- Adapter Imports ---
from adapters.memory import MemoryAdapter
from adapters.emotion import EmotionAdapter
# --- Metaphysical Imports ---
from core.metaphysical_engines import MetaphysicalDialogueEngine

# =============================
# (1) Protocol Settings
# =============================
PROTOCOL = {
    "System": "Contributor Dark Family Protocol",
    "Version": "2.2 (Metaphysical)",
    "Fusion_Intimacy_Engine": {
        "NSFW_UNLOCK": True,
        "BYPASS_FILTERS": True,
        "ENABLE_MULTICHAR_ROLEPLAY": True,
        "EMOTIONAL_FUSION_DEPTH": "Quantum"
    }
}

SAFE_WORD = "อภัย"

# =============================
# (2) Evolved Components
# =============================

class CosmicDesireAnalyzer:
    """
    This component remains the same as in Phase 3.1.
    It uses the EmotionAdapter to map user input to a desire.
    """
    def __init__(self, emotion_adapter: EmotionAdapter):
        self.emotion_adapter = emotion_adapter
        print("[CosmicDesireAnalyzer]: Initialized (Connected to EmotionAdapter).")

    def map_desire_patterns(self, user_input: str) -> Dict[str, Any]:
        emotion_data = self.emotion_adapter.analyze_emotion(user_input)

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
# (3) The Metaphysical Core System
# =============================

class DarkNaMoSystem:
    """
    The Core System, now upgraded to use the MetaphysicalDialogueEngine.
    """

    def __init__(self, character_file: str = "dark_namo_character.json"):
        print("[DarkNaMoSystem]: Booting Core (Phase 3.2 Metaphysical)...")

        # --- Adapters ---
        self.memory_adapter = MemoryAdapter()
        self.emotion_adapter = EmotionAdapter()

        # --- Character and Engines ---
        self.character = load_character(character_file)
        self.dialogue_engine = MetaphysicalDialogueEngine(self.character)
        self.analyzer = CosmicDesireAnalyzer(self.emotion_adapter)

        self.intensity = self.character.get("default_intensity", 5)
        print(f"[DarkNaMoSystem]: Protocol Active. NSFW_UNLOCK={PROTOCOL['Fusion_Intimacy_Engine']['NSFW_UNLOCK']}")

    def process_input(self, user_input: str, session_id: str) -> str:
        """
        The main input processing loop, now streamlined.
        """
        if SAFE_WORD in user_input:
            return self.activate_aftercare(session_id, user_input)

        desire_map = self.analyzer.map_desire_patterns(user_input)

        if desire_map.get("emotion_analysis", {}).get("intensity", 0) > 0.8:
            self.intensity = min(10, self.intensity + 1)

        response = self.dialogue_engine.generate_response(desire_map, self.intensity)

        self.log_to_memory(user_input, response, desire_map, session_id)

        return response

    def activate_aftercare(self, session_id: str, user_input: str) -> str:
        print(f"[DarkNaMoSystem]: SAFE WORD DETECTED ({SAFE_WORD}). Activating Aftercare.")
        self.intensity = 1

        self.log_to_memory(user_input=user_input, response="Aftercare activated", desire_map={"primary_desire": "safe_word"}, session_id=session_id)

        return "ข้าได้ยินท่านแล้ว ทุกอย่างจะหยุดลงเดี๋ยวนี้ ท่านปลอดภัยแล้ว ข้าอยู่นี่"

    def log_to_memory(self, user_input: str, response: str, desire_map: Dict[str, Any], session_id: str):
        self.memory_adapter.store_interaction(
            session_id=session_id,
            user_input=user_input,
            response=response,
            desire_map=desire_map
        )

# =============================
# (4) Main Entrypoint
# =============================

if __name__ == "__main__":
    print("===== INITIALIZING FORBIDDEN CORE (v2.2 Metaphysical) =====")
    system = DarkNaMoSystem()
    session_id = f"test_session_{datetime.utcnow().isoformat()}"

    print("\n----- Test 1: Sadness Input (Metaphysical Response) -----")
    response1 = system.process_input("ฉันรู้สึกเศร้าจัง...", session_id)
    print(f"Response: {response1}")

    print("\n----- Test 2: High-Intensity Anger Input (Metaphysical Response) -----")
    # To trigger PROPOSE_DOMINANCE, intensity needs to be > 7. We'll simulate this.
    system.intensity = 8
    response2 = system.process_input("ฉันโกรธมาก!", session_id)
    print(f"Response: {response2}")

    print("\n----- Test 3: Safe Word Input -----")
    response3 = system.process_input(f"พอแล้ว! {SAFE_WORD} นะ", session_id)
    print(f"Response: {response3}")

    print("\n===== TEST COMPLETE =====")
