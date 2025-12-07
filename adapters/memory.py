import json
import os
import datetime


class MemoryAdapter:
    """
    Adapter สำหรับบันทึกความทรงจำระยะยาวลงไฟล์ Local
    """
    def __init__(self, db_file="memory_history.json"):
        self.db_file = db_file
        if not os.path.exists(self.db_file):
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
        print(f"[MemoryAdapter]: Initialized. Storage: {self.db_file}")

    def store_interaction(
        self,
        user_input,
        response,
        emotions=None,
        *,
        arousal_level=None,
        infection_status=None,
        session_id=None,
        desire_map=None,
    ):
        """
        บันทึกสิ่งที่คุยกัน พร้อม metadata เพิ่มเติม
        - emotions: ภาพรวมสถานะอารมณ์/สเตตัส ณ ขณะนั้น
        - arousal_level: ค่าความเงี่ยนล่าสุด (0-100)
        - infection_status: สถานะการติดเชื้อ/อารมณ์ที่ถูกฝัง
        """
        entry = {
            "timestamp": str(datetime.datetime.now()),
            "session_id": session_id,
            "user": user_input,
            "bot": response,
            "state_snapshot": emotions,
            "arousal_level": arousal_level,
            "infection_status": infection_status,
            "desire_map": desire_map,
        }

        # ตัด key ที่เป็น None ออกเพื่อไม่ให้ไฟล์รก
        entry = {k: v for k, v in entry.items() if v is not None}
        
        try:
            with open(self.db_file, 'r+', encoding='utf-8') as f:
                history = json.load(f)
                history.append(entry)
                f.seek(0)
                json.dump(history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"[MemoryError]: {e}")

    def get_last_conversation(self):
        """ดึงบทสนทนาล่าสุดมาดูบริบท"""
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                return history[-1] if history else None
        except:
            return None
