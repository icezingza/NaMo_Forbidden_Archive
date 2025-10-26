# 🧠 Dark Knowledge System

ระบบนี้ช่วยให้ Agent (เช่น Julius) เรียนรู้จากไฟล์ ZIP ได้โดยตรง
เมื่อใส่ `set.zip` ใน `learning_set/` แล้วเรียกใช้ `learn_from_set.py`
ระบบจะสร้างฐานความรู้ในรูปแบบ Embedding (FAISS index)

## ⚙️ วิธีใช้งานอย่างเร็ว

1. วางไฟล์ `set.zip` ในโฟลเดอร์ `learning_set/`
2. เปิด Codespace หรือ dev container
3. รันคำสั่ง:

   ```bash
   python learn_from_set.py
   ```
4. เมื่อสร้างฐานสำเร็จ จะมีไฟล์ใน `vector_db/`
5. ถามข้อมูลได้ด้วย:

   ```bash
   python query_learned_knowledge.py
   ```

## 🧩 โครงสร้าง Repo

```
learning_set/
  ├── set.zip
  └── README.md
vector_db/
  ├── knowledge.index
  └── meta.json
learn_from_set.py
query_learned_knowledge.py
.jules/config.yml
.devcontainer/devcontainer.json
```

## 🧠 การทำงานอัตโนมัติ

ทุกครั้งที่ Julius เริ่มต้น `.jules/config.yml` จะโหลดฐานความรู้นี้เข้าระบบโดยอัตโนมัติ
