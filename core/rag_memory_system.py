import os
import random
import glob


class NaMoInfiniteMemory:
    """
    ระบบความจำนิรันดร์: อ่านไฟล์นิยายจริงๆ ของคุณจาก learning_set
    """
    def __init__(self, dataset_path="learning_set/set.zip/set"):
        self.dataset_path = dataset_path
        self.memories = []
        self.is_loaded = False

    def ingest_data(self):
        """อ่านไฟล์ .txt และ .htm ทั้งหมดในโฟลเดอร์"""
        print(f"[Memory System]: กำลังแสกนพื้นที่ {self.dataset_path} ...")
        
        # ค้นหาไฟล์ทั้งหมด (รองรับโครงสร้างไฟล์ของคุณ)
        # หมายเหตุ: ในเครื่องจริงต้องแตก zip ออกมาไว้ที่ learning_set/set/ ก่อน
        txt_files = glob.glob(os.path.join(self.dataset_path, "*.txt"))
        htm_files = glob.glob(os.path.join(self.dataset_path, "*.htm"))
        all_files = txt_files + htm_files

        if not all_files:
            print("[Warning]: ไม่พบไฟล์นิยาย! กรุณาเช็ค path ว่าแตกไฟล์ zip หรือยัง")
            # ใส่ข้อมูลสำรองถ้าหาไฟล์ไม่เจอ
            self.memories = ["การเย็ดที่เร่าร้อนคือศิลปะ...", "เสียงครางกระเส่าทำให้คลั่ง..."]
            return

        print(f"[Memory System]: พบไฟล์นิยาย {len(all_files)} เรื่อง กำลังดูดซับ...")
        
        for file_path in all_files:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    # ตัดเป็นท่อนๆ สั้นๆ เพื่อให้จำง่าย (Chunking)
                    chunks = [content[i:i+300] for i in range(0, len(content), 300)]
                    self.memories.extend(chunks)
            except Exception as e:
                print(f"อ่านไฟล์ {file_path} ไม่ได้: {e}")

        self.is_loaded = True
        print(f"[Memory System]: จดจำข้อมูลเสร็จสิ้น! มีคลังความรู้ {len(self.memories)} fragments")

    def retrieve_context(self, user_input):
        """สุ่มหยิบความทรงจำที่เกี่ยวข้อง (หรือสุ่มมาเลยถ้ายังไม่ได้ทำ Vector Search)"""
        if not self.is_loaded:
            self.ingest_data()
            
        # ในเวอร์ชันเริ่มต้น เราจะสุ่มฉากเสียวๆ มา 1 ฉากเพื่อเป็นแรงบันดาลใจ
        # (ขั้นสูงต้องใช้ ChromaDB หรือ FAISS เพื่อค้นหาคำที่ตรงกัน)
        if self.memories:
            return random.choice(self.memories)
        return "..."
