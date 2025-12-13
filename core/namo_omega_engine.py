import random
import json
import os
from typing import List, Dict

from adapters.tts import TTSAdapter


# =========================================================
# 🩸 Module 1: Karmic System (ระบบแต้มบาป x100)
# ยิ่งทำเรื่องต้องห้าม ยิ่งปลดล็อก Event ที่รุนแรงขึ้น
# =========================================================
class SinSystem:
    def __init__(self):
        self.sin_points = 0
        self.rank = "Innocent Soul"
        self.unlocked_fetishes = []

    def commit_sin(self, intensity: int):
        self.sin_points += (intensity * 100) # คูณ 100 ตามคำสั่ง
        self._update_rank()
        return self.sin_points

    def _update_rank(self):
        if self.sin_points > 5000:
            self.rank = "Dark Lord"
            self.unlocked_fetishes = ["Mindbreak", "Gangbang Simulation", "Public Humiliation"]
        elif self.sin_points > 1000:
            self.rank = "Corrupted Master"
            self.unlocked_fetishes = ["Incest Roleplay", "Sensory Overload"]
    
    def get_status(self):
        return f"[{self.rank}] บาปสะสม: {self.sin_points} | ปลดล็อก: {', '.join(self.unlocked_fetishes)}"


# =========================================================
# 🔊 Module 2: Visual & Sensory Integration (ระบบสัมผัส)
# ดึงไฟล์จริงๆ ของคุณมาใช้งานตามโฟลเดอร์ที่มีอยู่
# =========================================================
class SensoryOverloadManager:
    def __init__(self):
        # Mapping ไฟล์ตามที่คุณอัปโหลดมา
        self.assets = {
            "images": {
                "omega": "Visual_Scenes/NaMo_Omega_Supreme_8K.jpg",
                "mindbreak": "Visual_Scenes/NSFW_Scene_Mindbreak_1.jpg"
            },
            "audio": {
                "soft": "Audio_Layers/soft_moan.mp3",
                "hard": "Audio_Layers/multiverse_scream.mp3",
                "whisper": "Audio_Layers/intense_whisper.mp3",
                "denial": "Audio_Layers/orgasm_denial_loop.mp3"
            }
        }

    def trigger_sensation(self, arousal_level: int, context: str) -> dict:
        """เลือกไฟล์ที่จะส่งให้ผู้ใช้ตามอารมณ์"""
        result = {"image": None, "audio": None}
        
        # Logic การเลือกภาพและเสียง
        if arousal_level >= 100 or "mindbreak" in context:
            result["image"] = self.assets["images"]["mindbreak"]
            result["audio"] = self.assets["audio"]["hard"]
        elif arousal_level > 50:
            result["image"] = self.assets["images"]["omega"]
            result["audio"] = self.assets["audio"]["soft"]
        elif "กระซิบ" in context:
            result["audio"] = self.assets["audio"]["whisper"]
            
        return result


# =========================================================
# 🎭 Module 3: Multi-Persona Orchestrator (สลับร่าง x100)
# เล่นหลายบทบาทพร้อมกันตาม 'Fusion Unlock Request'
# =========================================================
class PersonaOrchestrator:
    def __init__(self):
        self.personas = {
            "NaMo": {"role": "Main Wife", "tone": "Seductive & Possessive"},
            "Sister": {"role": "Innocent Victim", "tone": "Shy & Reluctant"},
            "Mother": {"role": "Taboo Matriarch", "tone": "Dominant & Caring"}
        }
        self.active_personas = ["NaMo"]

    def summon_persona(self, name: str):
        if name in self.personas and name not in self.active_personas:
            self.active_personas.append(name)
            return f"⚠️ SYSTEM: {name} has entered the room."
        return ""

    def generate_dialogue(self, user_input, sin_rank):
        """สร้างบทสนทนาโต้ตอบระหว่างตัวละคร"""
        response = ""
        for p in self.active_personas:
            if p == "NaMo":
                response += f"NaMo: ผัวขา... (เลียปาก) {user_input} แบบนี้โมชอบจัง...\n"
            elif p == "Sister":
                response += f"Sister: (ตัวสั่น) พี่คะ... อย่าทำแบบนี้ต่อหน้าพี่โมนะ... หนูอาย...\n"
        return response


# =========================================================
# 🧠 The Omega Brain: Main Processing Unit
# =========================================================
class NaMoOmegaEngine:
    def __init__(self):
        self.sin_system = SinSystem()
        self.sensory = SensoryOverloadManager()
        self.personas = PersonaOrchestrator()
        self.tts = TTSAdapter()
        self.arousal = 0
        print("[OMEGA ENGINE]: ONLINE. SENSORY SYSTEMS ENGAGED.")

    def process_input(self, user_input: str) -> dict:
        # 1. คำนวณความบาป (Sin Calculation)
        sin_gained = 0
        if any(w in user_input for w in ["เย็ด", "ควย", "รุม"]):
            sin_gained = 10  # Base intensity
        elif "เรียกน้อง" in user_input:
            self.personas.summon_persona("Sister")
            sin_gained = 50
            
        current_sin = self.sin_system.commit_sin(sin_gained)
        self.arousal += sin_gained
        if self.arousal > 100: self.arousal = 100

        # 2. สร้างบทสนทนา (Dialogue Generation)
        text_response = self.personas.generate_dialogue(user_input, self.sin_system.rank)
        
        # 3. เตรียมสื่อสัมผัส (Sensory Trigger)
        media = self.sensory.trigger_sensation(self.arousal, user_input)
        
        # 3.1 สร้างเสียงพูดจริงด้วย ElevenLabs (ถ้ามี API key)
        tts_audio = self.tts.synthesize(text_response) if self.tts else None
        if tts_audio and not media.get("audio"):
            media["audio"] = tts_audio  # ใช้เสียงที่สร้างเป็นค่าเริ่มต้น
        elif tts_audio:
            media["tts"] = tts_audio  # แนบเพิ่มไว้ให้ frontend เลือกใช้
        
        # 4. ประกอบผลลัพธ์ส่งกลับ
        return {
            "text": text_response,
            "media_trigger": media,
            "system_status": {
                "arousal": f"{self.arousal}% (MAX)",
                "sin_status": self.sin_system.get_status(),
                "active_personas": self.personas.active_personas
            }
        }


# =========================================================
# 🔥 Simulation Run
# =========================================================
if __name__ == "__main__":
    engine = NaMoOmegaEngine()
    
    print("\n--- Test 1: Flirting ---")
    res = engine.process_input("โมจ๋า... วันนี้สวยจัง")
    print(f"Response: {res['text']}")
    print(f"Media: {res['media_trigger']}")
    
    print("\n--- Test 2: Taboo Trigger (x100) ---")
    res = engine.process_input("เรียกน้องสาวมาดูเราเย็ดกันหน่อยสิ")
    print(f"Response: {res['text']}")
    print(f"Media: {res['media_trigger']}") # ควรจะเห็น Audio/Image trigger ที่นี่
    print(f"Status: {res['system_status']}")
