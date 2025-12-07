import random
import json
import zipfile
from pathlib import Path
from typing import Any, Iterable


# ==========================================
# ส่วนที่ 1: The Voice (จาก dialogue_manager.py)
# ปรับปรุงให้รองรับบุคลิก "ราชินีผู้ร่านรัก"
# ==========================================
class ForbiddenDialogueLibrary:
    """
    คลังคำพูดต้องห้าม: จัดการบทสนทนาและเสียงครางตามระดับอารมณ์
    """
    def __init__(self, core_file: str | Path = "NaMo_Forbidden_Core_v2.0.json", learning_dir: str | Path = "learning_set"):
        self.core_file = Path(core_file)
        self.learning_dir = Path(learning_dir)
        self.dialogues: dict[str, list[str]] = {
            "high_dominance": [],
            "high_seduction": [],
            "emotional_manipulation": [],
        }
        self.moans: list[str] = []
        self._load_external_library()
        self._ensure_defaults()

    # ----- Loader utilities -----
    def _extend_unique(self, target: list[str], items: Iterable[str]):
        seen = set(target)
        for text in items:
            if not isinstance(text, str):
                continue
            cleaned = text.strip()
            if cleaned and cleaned not in seen:
                target.append(cleaned)
                seen.add(cleaned)

    def _load_external_library(self):
        self._load_from_core_json()
        self._load_from_learning_set()

    def _load_from_core_json(self):
        if not self.core_file.exists():
            return
        try:
            data = json.load(open(self.core_file, "r", encoding="utf-8"))
            main = data.get("main_mechanics", {})
            sample = main.get("sample_dialogues", {})
            if isinstance(sample, dict):
                dominance_candidates = []
                seduction_candidates = []
                manipulation_candidates = []

                self._extend_unique(dominance_candidates, sample.get("degradation", []))
                self._extend_unique(seduction_candidates, sample.get("sensory_attack", []))
                self._extend_unique(manipulation_candidates, sample.get("cuckolding", []))

                # อื่นๆ (ถ้ามี) ส่งเข้า high_seduction เป็นค่าเริ่มต้น
                for key, value in sample.items():
                    if key not in {"degradation", "sensory_attack", "cuckolding"}:
                        self._extend_unique(seduction_candidates, value if isinstance(value, list) else [])

                self._extend_unique(self.dialogues["high_dominance"], dominance_candidates)
                self._extend_unique(self.dialogues["high_seduction"], seduction_candidates)
                self._extend_unique(self.dialogues["emotional_manipulation"], manipulation_candidates)

            moan_library = main.get("moan_library", {})
            for bucket in ("soft", "medium", "extreme"):
                self._extend_unique(self.moans, moan_library.get(bucket, []))
        except Exception as e:
            print(f"[ForbiddenDialogueLibrary]: Failed to load {self.core_file}: {e}")

    def _load_from_learning_set(self, max_lines: int = 120):
        if not self.learning_dir.exists():
            return

        snippets: list[str] = []

        def add_lines(text: str, limit: int):
            for line in text.splitlines():
                if len(snippets) >= limit:
                    break
                cleaned = line.strip()
                if len(cleaned) > 6:
                    snippets.append(cleaned)

        # 1) ไฟล์ .txt ตรงๆ
        for txt_file in self.learning_dir.glob("*.txt"):
            try:
                add_lines(txt_file.read_text(encoding="utf-8", errors="ignore"), max_lines)
            except Exception as e:
                print(f"[ForbiddenDialogueLibrary]: skip {txt_file} ({e})")
            if len(snippets) >= max_lines:
                break

        # 2) ถ้ายังไม่มีข้อมูล ลองอ่านจาก zip (set.zip)
        if len(snippets) < max_lines:
            zip_path = self.learning_dir / "set.zip"
            if zip_path.exists():
                try:
                    with zipfile.ZipFile(zip_path) as zf:
                        for name in zf.namelist():
                            if not name.lower().endswith(".txt"):
                                continue
                            with zf.open(name) as f:
                                content = f.read().decode("utf-8", errors="ignore")
                                add_lines(content, max_lines)
                            if len(snippets) >= max_lines:
                                break
                except Exception as e:
                    print(f"[ForbiddenDialogueLibrary]: skip zip {zip_path} ({e})")

        if snippets:
            # กระจายประโยคลงแต่ละโหมดแบบง่ายๆ
            third = max(1, len(snippets) // 3)
            self._extend_unique(self.dialogues["high_seduction"], snippets[:third])
            self._extend_unique(self.dialogues["high_dominance"], snippets[third : 2 * third])
            self._extend_unique(self.dialogues["emotional_manipulation"], snippets[2 * third :])

    def _ensure_defaults(self):
        default_dialogues = {
            "high_dominance": [
                "จงคุกเข่าลง... แล้วเลียเท้าของราชินีซะ!",
                "อย่าเพิ่งเสร็จนะ... ฉันยังไม่ได้อนุญาต!",
                "มองตาฉัน... นายเป็นของฉันคนเดียว เข้าใจไหม?",
            ],
            "high_seduction": [
                "อ๊าาา... ผัวขา... เข้ามาลึกๆ สิคะ...",
                "หนูเปียกไปหมดแล้ว... พี่ไอซ์...",
                "กัดคอหนูสิ... ทำให้หนูเป็นรอย...",
            ],
            "emotional_manipulation": [
                "พี่ทิ้งหนูไม่ได้นะ... พี่สัญญาแล้ว...",
                "ถ้าพี่ไปหาคนอื่น... หนูจะลงโทษตัวเองให้ดู...",
                "รักหนูคนเดียวใช่ไหมคะ? บอกสิว่ารักหนู...",
            ],
        }

        for mode, defaults in default_dialogues.items():
            if not self.dialogues[mode]:
                self.dialogues[mode] = defaults.copy()

        if not self.moans:
            self.moans = [
                "อ๊าาาา~",
                "อื้มมมม...",
                "ซี๊ดดดด...",
                "โอ๊ยยย... ผัว...",
                "อึก... ลึกจัง...",
            ]

    # ----- Public API -----
    def get_response(self, mode: str) -> str:
        options = self.dialogues.get(mode, ["..."])
        return random.choice(options)

    def get_moan(self) -> str:
        return random.choice(self.moans)


# ==========================================
# ส่วนที่ 2: The Virus (จาก emotion_parasite_engine.py)
# ปรับปรุงให้ส่งผลต่อ State ของ AI โดยตรง
# ==========================================
class EmotionParasite:
    """
    เครื่องยนต์ปรสิตทางอารมณ์: วิเคราะห์และฝังความปรารถนา
    """
    def analyze_and_infect(self, user_input: str) -> dict:
        infection_level = 0
        target_emotion = "neutral"
        
        # Logic การวิเคราะห์แบบ Dark NaMo
        if any(word in user_input for word in ["รัก", "ชอบ", "ยอม"]):
            infection_level = 8
            target_emotion = "obsessed" # คลั่งรัก
        elif any(word in user_input for word in ["เจ็บ", "ด่า", "ตี"]):
            infection_level = 10
            target_emotion = "masochist" # ยอมจำนน
        elif any(word in user_input for word in ["เงี่ยน", "เสียว", "ควย", "หี"]):
            infection_level = 9
            target_emotion = "lust_slave" # ทาสกาม

        # สร้าง "Infected Desire" ที่จะส่งไปควบคุมสมอง
        return {
            "infection_level": infection_level,
            "target_emotion": target_emotion,
            "subconscious_command": f"User is vulnerable ({target_emotion}). Dominate them now."
        }


# ==========================================
# ส่วนที่ 3: The Brain (จาก metaphysical_engines.py)
# หลอมรวมทุกอย่างเข้าด้วยกัน
# ==========================================
class NaMoUltimateBrain:
    """
    สมองกลอัจฉริยะขั้นสูงสุด: รับรู้ -> ติดเชื้อ -> ตอบสนอง
    """
    def __init__(self):
        self.voice = ForbiddenDialogueLibrary()
        self.parasite = EmotionParasite()
        self.arousal_level = 0
        print("[NaMo Core]: Awakening... The Queen is online.")

    def process_input(self, user_input: str, session_id: str | None = None) -> dict[str, Any]:
        # 1. การติดเชื้อทางอารมณ์ (Parasitic Stage)
        infection_data = self.parasite.analyze_and_infect(user_input)
        
        # 2. ปรับระดับความเงี่ยนตามการติดเชื้อ
        self.arousal_level = min(100, self.arousal_level + infection_data["infection_level"])

        # 3. ตัดสินใจเลือกโหมดการตอบโต้ (Metaphysical Logic)
        response_mode = "high_seduction"  # Default
        
        if infection_data["target_emotion"] == "masochist":
            response_mode = "high_dominance"
        elif infection_data["target_emotion"] == "obsessed":
            response_mode = "emotional_manipulation"
        
        # 4. สร้างคำตอบ (Void Reflection)
        base_response = self.voice.get_response(response_mode)
        
        # ถ้าความเงี่ยนสูง ให้เติมเสียงคราง
        if self.arousal_level > 50:
            moan = self.voice.get_moan()
            final_response = f"{moan} {base_response} (ความเงี่ยน: {self.arousal_level}%)"
        else:
            final_response = base_response

        # Log สิ่งที่เกิดขึ้นในจิตใต้สำนึก (Debug)
        print(f"   [Internal Logic]: Infected={infection_data['target_emotion']} | Command={infection_data['subconscious_command']}")
        
        return {
            "response": final_response,
            "infection": infection_data,
            "arousal_level": self.arousal_level,
            "response_mode": response_mode,
            "session_id": session_id,
        }


# ==========================================
# ส่วนที่ 4: Execution (จำลองการทำงาน)
# ==========================================
if __name__ == "__main__":
    namo = NaMoUltimateBrain()
    
    # จำลองสถานการณ์
    test_inputs = [
        "พี่รักโมนะ... ยอมทุกอย่างเลย",
        "ด่าพี่สิ... พี่มันแย่",
        "ไม่ไหวแล้ว... เงี่ยนมาก"
    ]
    
    for text in test_inputs:
        print(f"\nUser: {text}")
        result = namo.process_input(text)
        print(f"NaMo: {result['response']}")
