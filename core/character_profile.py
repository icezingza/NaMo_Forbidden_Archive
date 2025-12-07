import json
import os


class CharacterProfile:
    def __init__(self, name="NaMo"):
        self.name = name
        self.state_file = "namo_state.json"
        # ค่าสถานะเริ่มต้น
        self.mood = "Neutral"          # Neutral, Horny, Obsessed, Angry
        self.corruption_level = 0      # 0-100 (ระดับความดำมืด)
        self.obedience_level = 50      # 0-100 (ระดับความเชื่อฟัง)
        self.arousal_level = 0         # 0-100 (ระดับความเงี่ยน)
        self.load_state()

    def update_state(self, mood_change=None, corruption_delta=0, arousal_delta=0):
        """อัปเดตสถานะตัวละครและบันทึกลงไฟล์"""
        if mood_change:
            self.mood = mood_change
        
        self.corruption_level = max(0, min(100, self.corruption_level + corruption_delta))
        self.arousal_level = max(0, min(100, self.arousal_level + arousal_delta))
        
        # Logic การเปลี่ยน Mood อัตโนมัติเมื่อค่าถึงกำหนด
        if self.arousal_level > 80:
            self.mood = "Horny"
        elif self.corruption_level > 90:
            self.mood = "Obsessed"
            
        self.save_state()

    def save_state(self):
        data = {
            "mood": self.mood,
            "corruption": self.corruption_level,
            "obedience": self.obedience_level,
            "arousal": self.arousal_level
        }
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.mood = data.get("mood", "Neutral")
                    self.corruption_level = data.get("corruption", 0)
                    self.obedience_level = data.get("obedience", 50)
                    self.arousal_level = data.get("arousal", 0)
            except:
                print("[System]: Memory corrupted. Resetting state.")

    def get_status_str(self):
        return f"[Mood: {self.mood} | Corruption: {self.corruption_level}% | Arousal: {self.arousal_level}%]"
