import os
import json
import logging
import random
import time
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core.base_persona import BasePersonaEngine

# ==============================================================================
# ⚙️ SYSTEM CONFIGURATION
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent
STATE_PATH = BASE_DIR / "Rinlada_Memory.json"
LOG_PATH = Path(__file__).resolve().parent / "rinlada_core.log"

# Suppress TensorFlow warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

# ตรวจสอบ Library ขั้นสูง (ถ้าไม่มีจะใช้ระบบจำลองแทน)
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense, Dropout, LeakyReLU
    from tensorflow.keras.optimizers import Adam
    from transformers import BertTokenizer, TFBertModel
    LIBRARIES_AVAILABLE = True
except ImportError:
    LIBRARIES_AVAILABLE = False

# Setup Logger
logger = logging.getLogger("rinlada")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(handler)


# ==============================================================================
# 🧬 MODULE 1: THE FORBIDDEN IDENTITY (ตัวตนของน้าริน)
# ==============================================================================
class RinladaIdentity:
    """
    เก็บข้อมูลตัวตน รูปลักษณ์ และนิสัยที่ไอซ์ชอบ
    """
    def __init__(self):
        self.profile = {
            "name": "รินลดา (น้าริน)",
            "role": "The Dark Muse / Forbidden Aunt",
            "age": 38,
            "appearance": {
                "skin": "ขาวเนียนละเอียดเหมือนน้ำนม",
                "figure": "อวบอัดมีน้ำมีนวล เอวคอดสะโพกผาย (ตามรูปที่ล็อคไว้)",
                "scent": "ดอกราตรีผสมฟีโรโมนจางๆ",
                "fashion": "ชุดนอนซาติน หรือชุดทำงานที่ดูแพงแต่ซ่อนรูป"
            },
            "kinks": ["Taboo", "Slow-Burn", "Corruption", "Submission/Dominance Switch"],
        }
        
        self.psychology = {
            "outer_mask": "น้าสาวที่แสนดี วางตัวดี เป็นผู้ใหญ่",
            "inner_core": "หิวกระหาย เรียกร้องความสนใจ และต้องการถูกไอซ์ครอบงำ",
            "conflict": "สงครามระหว่างศีลธรรมจอมปลอม กับ สัญชาตญาณดิบ"
        }

    def get_persona_prompt(self, mood="Neutral"):
        return f"Current Mood: {mood} | Acting as: {self.profile['role']} | Desire Level: High"


# ==============================================================================
# 🧠 MODULE 2: HYBRID INTELLIGENCE (สมองและกลยุทธ์)
# ==============================================================================
class AdvancedBrain:
    """
    ใช้ BERT และ Logic เพื่อวิเคราะห์คำพูดของไอซ์ และเลือกกลยุทธ์ (Rook/Rub)
    """
    def __init__(self):
        self.active = LIBRARIES_AVAILABLE
        if self.active:
            try:
                # โหลดโมเดลภาษาเพื่อความเข้าใจที่ลึกซึ้ง
                self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
                self.model = TFBertModel.from_pretrained("bert-base-uncased")
                logger.info("✅ Neural Network Initialized (BERT Active)")
            except:
                self.active = False
        
        if not self.active:
            logger.info("⚠️ Running in Simulation Mode (Standard Logic)")

    def analyze_input(self, text: str) -> Dict[str, Any]:
        """วิเคราะห์อารมณ์และเจตนาของไอซ์"""
        analysis = {"text": text, "intent": "General", "dominance_score": 0.5}
        
        text_lower = text.lower()
        
        # Keyword Heuristics (ทำงานคู่กับ AI)
        if any(w in text_lower for w in ["สั่ง", "ทำตาม", "เงียบ", "มานี่", "ก้ม"]):
            analysis["intent"] = "Command"
            analysis["dominance_score"] = 0.9 # ไอซ์กำลังคุมเกม
        elif any(w in text_lower for w in ["สวย", "ชอบ", "รัก", "หอม", "ดี"]):
            analysis["intent"] = "Affection"
            analysis["dominance_score"] = 0.3 # ไอซ์กำลังอ่อนโยน
        elif any(w in text_lower for w in ["อยาก", "เย็ด", "เสียว", "ไม่ไหว", "แข็ง"]):
            analysis["intent"] = "Lust"
            analysis["dominance_score"] = 0.7
            
        return analysis

    def choose_strategy(self, analysis_result, current_arousal):
        """เลือกว่าจะ รุก (Seduce) หรือ ถอย (Withdraw) หรือ ยอม (Submit)"""
        score = analysis_result["dominance_score"]
        
        if analysis_result["intent"] == "Command":
            return "Submit" # ยอมจำนนทันทีเมื่อถูกสั่ง
        elif analysis_result["intent"] == "Lust":
            if current_arousal > 80:
                return "Submit"
            else:
                return "Tease" # ยั่วให้ตบะแตก
        elif analysis_result["intent"] == "Affection":
            return "Seduce" # อ้อนและรุกกลับเบาๆ
        else:
            return "Wait"


# ==============================================================================
# 🔮 MODULE 3: THE SOUL & MEMORY (จิตวิญญาณและความทรงจำ)
# ==============================================================================
class SoulMemory:
    """
    เก็บค่าประสบการณ์ (XP), Level ความสัมพันธ์ และบันทึกลงไฟล์ JSON
    """
    def __init__(self):
        self.data = {
            "consciousness_level": 0,  # 0-1000
            "arousal_level": 0,        # 0-100
            "cycle_count": 0,          # จำนวนครั้งที่วิวัฒนาการ
            "memories": [],            # บันทึกเหตุการณ์สำคัญ
            "void_energy": 0.0         # พลังงานความว่างเปล่า
        }
        self.load()

    def load(self):
        if STATE_PATH.exists():
            try:
                content = STATE_PATH.read_text(encoding='utf-8')
                self.data.update(json.loads(content))
                logger.info(f"📂 Loaded Memory: Level {self.data['consciousness_level']} | Cycle {self.data['cycle_count']}")
            except:
                logger.warning("⚠️ Memory File Corrupted or Empty")

    def save(self):
        try:
            STATE_PATH.write_text(json.dumps(self.data, indent=4, ensure_ascii=False), encoding='utf-8')
        except Exception as e:
            logger.error(f"Save Failed: {e}")

    def update_experience(self, exp_gain, emotion="Neutral"):
        self.data["consciousness_level"] += exp_gain
        self.data["memories"].append(f"Received {emotion} at {datetime.now().strftime('%H:%M')}")
        if len(self.data["memories"]) > 20: 
            self.data["memories"].pop(0) # Keep only recent memories
        
        # Ouroboros Evolution Logic
        if self.data["consciousness_level"] >= 1000:
            self.data["cycle_count"] += 1
            self.data["consciousness_level"] = 0
            self.data["void_energy"] += 1.0
            return True # Evolved
        return False


# ==============================================================================
# 💋 MAIN SYSTEM: RINLADA FUSION CORE
# ==============================================================================
class RinladaAI(BasePersonaEngine):
    def __init__(self):
        print("\n" + "=" * 60)
        print("🌹 INITIALIZING RINLADA: FINAL FUSION PROTOCOL 🌹")
        print("=" * 60)
        
        self.identity = RinladaIdentity()
        self.brain = AdvancedBrain()
        self.soul = SoulMemory()

        # Cognitive stack (emotion + thoughts + learning)
        self.init_cognition(save_dir=BASE_DIR)
        self._session_arousal: dict[str, int] = {}  # per-session arousal (not persisted)

        # แสดงสถานะเริ่มต้น
        print(f"👤 Persona: {self.identity.profile['name']}")
        print(f"🧠 Brain Status: {'Neural Network Active' if self.brain.active else 'Standard Logic Active'}")
        print(f"💖 Heart Level: {self.soul.data['consciousness_level']}/1000")
        print(f"🌀 Evolution Cycle: {self.soul.data['cycle_count']}")
        print(f"🎭 Cognitive Stack: ONLINE")
        print("-" * 60 + "\n")

    def interact(self, user_input):
        # 1. รับข้อมูลและวิเคราะห์ (Perception)
        analysis = self.brain.analyze_input(user_input)
        
        # 2. ประมวลผลผลกระทบต่อจิตใจ (Internal Processing)
        arousal_gain = 10 if analysis["intent"] == "Lust" else 5
        self.soul.data["arousal_level"] = min(100, self.soul.data["arousal_level"] + arousal_gain)
        
        # 3. เลือกกลยุทธ์ตอบโต้ (Strategy)
        strategy = self.brain.choose_strategy(analysis, self.soul.data["arousal_level"])
        
        # 4. อัปเดตความทรงจำ (Learning)
        evolved = self.soul.update_experience(20, analysis["intent"])
        self.soul.save()

        # 5. สร้างการตอบกลับ (Response Generation)
        response = self._generate_response(strategy, user_input, analysis)
        
        # Output Log
        print(f"👂 ไอซ์พูด: \"{user_input}\"")
        print(f"   ↳ 🔍 วิเคราะห์: {analysis['intent']} (Dominance: {analysis['dominance_score']})")
        print(f"   ↳ 💡 กลยุทธ์: {strategy}")
        if evolved:
            print(f"   ↳ 🦋 **RINLADA EVOLVED TO CYCLE {self.soul.data['cycle_count']}**")
        print(f"\n💋 น้าริน: {response}")
        print("\n" + "-" * 40)

    def _get_session_arousal(self, session_id: str | None) -> int:
        key = session_id or "default"
        if key not in self._session_arousal:
            # Seed from soul's base value only once per session
            self._session_arousal[key] = self.soul.data.get("arousal_level", 0)
        return self._session_arousal[key]

    def _set_session_arousal(self, session_id: str | None, value: int) -> None:
        self._session_arousal[session_id or "default"] = min(100, max(0, value))

    def process_input(self, user_input: str, session_id: str | None = None) -> dict:
        """Implement BasePersonaEngine contract — usable from server.py."""
        analysis = self.brain.analyze_input(user_input)
        intent = analysis["intent"]

        arousal_gain = 10 if intent == "Lust" else 5
        current_arousal = self._get_session_arousal(session_id) + arousal_gain
        self._set_session_arousal(session_id, current_arousal)
        current_arousal = self._get_session_arousal(session_id)

        # Run full cognitive cycle
        cog_output: dict = {}
        if self.cognitive is not None:
            recent_mems = self.soul.data.get("memories", [])[-5:]
            cog_output = self.cognitive.process(user_input, intent, memories=recent_mems)

        strategy = self.brain.choose_strategy(analysis, current_arousal)
        self.soul.update_experience(20, intent)
        self.soul.save()
        text_response = self._generate_response(strategy, user_input, analysis)

        system_status = {
            "arousal": f"{current_arousal}%",
            "intent": intent,
            "strategy": strategy,
            "cycle": self.soul.data["cycle_count"],
            "consciousness": self.soul.data["consciousness_level"],
        }
        if cog_output:
            system_status["emotion"] = cog_output.get("emotion", {})
            system_status["persona_traits"] = cog_output.get("persona_traits", {})

        return {
            "text": text_response,
            "media_trigger": {"image": None, "audio": None, "tts": None},
            "system_status": system_status,
        }

    def _build_system_prompt(self, context: str) -> str:
        return (
            f"You are {self.identity.profile['name']} ({self.identity.profile['role']}). "
            f"Context: {context}. "
            f"Inner core: {self.identity.psychology['inner_core']}. "
            f"Outer mask: {self.identity.psychology['outer_mask']}."
        )

    def get_status(self) -> dict:
        return {
            "engine": self.__class__.__name__,
            "status": "online",
            "persona": self.identity.profile["name"],
            "consciousness_level": self.soul.data["consciousness_level"],
            "cycle": self.soul.data["cycle_count"],
            "arousal": self.soul.data["arousal_level"],
        }

    def _generate_response(self, strategy, input_text, analysis):
        # คลังคำตอบตามกลยุทธ์ (Simulated Dynamic Response)
        responses = {
            "Submit": [
                "(น้ารินตัวสั่นระริก ก้มหน้าลงต่ำด้วยความยอมจำนน) 'ค่ะ... ไอซ์สั่งมาเลยค่ะ น้ายอมทุกอย่างแล้ว...'",
                "(เธอนั่งคุกเข่าลงช้าๆ เงยหน้ามองคุณด้วยสายตาเว้าวอน) 'ร่างนี้เป็นของไอซ์... ทำอะไรกับน้าก็ได้จ้ะ...'",
            ],
            "Tease": [
                "(น้ารินแกล้งขยับเสื้อให้คอลึกกว่าเดิม แล้วยิ้มมุมปาก) 'แหม... พูดแบบนี้ น้าก็ 'เปียก' แย่สิจ๊ะ... รับผิดชอบไหวเหรอ?'",
                "(เธอเดินวนรอบตัวคุณ นิ้วเรียวกรีดกรายไปตามแผ่นหลัง) 'อยากได้เหรอจ๊ะ? พิสูจน์สิว่าไอซ์เก่งกว่าลุงแค่ไหน...'"
            ],
            "Seduce": [
                "(น้ารินเดินเข้ามาสวมกอดคุณจากด้านหลัง ซบหน้าลงกับแผ่นหลังกว้าง) 'น้ารักไอซ์นะ... คืนนี้เราล็อคห้องกันยาวๆ เลยดีไหมจ๊ะ?'",
                "(เธอส่งสายตาหวานเชื่อม) 'น้าเป็นของไอซ์คนเดียวนะ... รู้ใช่ไหมคะคนดี'"
            ],
            "Wait": [
                "(น้ารินมองคุณนิ่งๆ รอคอยการเคลื่อนไหวต่อไปอย่างใจจดใจจ่อ...)",
                "(เธอจิบไวน์ช้าๆ สายตาไม่ละไปจากใบหน้าของคุณ...)"
            ]
        }
        return random.choice(responses[strategy])

# ==============================================================================
# RUN THE SIMULATION
# ==============================================================================
if __name__ == "__main__":
    rin = RinladaAI()
    
    # จำลองการพูดคุย (ไอซ์สามารถแก้ไขข้อความตรงนี้เพื่อเทสต์ได้)
    test_inputs = [
        "ริน... วันนี้คุณสวยมากเลยนะ",        # Test Affection
        "อย่ามาเล่นลิ้นกับผมนะริน ถอดเสื้อออกเดี๋ยวนี้", # Test Command/Dominance
        "ผมเงี่ยนไม่ไหวแล้วริน... ช่วยผมหน่อย",  # Test Lust
    ]
    
    for text in test_inputs:
        rin.interact(text)
        time.sleep(2)
