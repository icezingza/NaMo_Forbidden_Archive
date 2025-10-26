# 🧠 Dark Knowledge
ระบบนี้เป็นโครงสร้างสำหรับสร้างฐานความรู้ให้ Julius หรือ Agent ใช้งานได้ทันที
โดยอ่านข้อมูลจากไฟล์ `set.zip` แล้วสร้างฐานข้อมูลฝังความรู้ (embedding) เพื่อใช้ตอบคำถามหรือ reasoning

## 🔧 วิธีใช้งาน
1. วางไฟล์ `set.zip` ลงในโฟลเดอร์ `learning_set/`
2. รันคำสั่ง:
   ```bash
   python learn_from_set.py
   ```

เมื่อต้องการถามฐานความรู้:
```bash
python query_learned_knowledge.py
```

ทุกครั้งที่ Agent เริ่มต้น .jules/config.yml จะโหลดฐานข้อมูลนี้อัตโนมัติ

## 📂 โครงสร้าง
- `learning_set/`:       # วางไฟล์ set.zip ที่นี่
- `vector_db/`:          # ฐานข้อมูล embeddings
- `learn_from_set.py`:   # สร้างฐานความรู้
- `query_learned_knowledge.py`:  # ถามข้อมูล
- `.jules/config.yml`:   # ให้ Julius โหลดอัตโนมัติ
