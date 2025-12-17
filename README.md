# NaMo Forbidden Archive

ชุดระบบทดลองที่รวม CLI, REST API, memory service และฐานความรู้แบบ embedding
เพื่อใช้งานกับ NaMo/Mōriko และสคริปต์ประกอบอื่นๆ ใน repo นี้

## สิ่งที่มีในโปรเจคนี้
- CLI โหมดหลัก: `app.py` (DarkNaMoSystem)
- CLI โหมดทดลอง: `main.py` (CharacterProfile + emotion_parasite_engine)
- REST API: `server.py` (NaMoOmegaEngine)
- Memory service: `memory_service.py`
- Knowledge base: `learn_from_set.py` + `query_learned_knowledge.py`
- Telegram auto reply (ตัวเลือก): `Core_Scripts/namo_auto_AI_reply.py`
- ElevenLabs TTS (ตัวเลือก): `adapters/tts.py`

## เริ่มต้นแบบเร็ว

### Windows (PowerShell)
```powershell
Copy-Item .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS/Linux
```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Cloud Run (ใช้งานส่วนตัว)
Endpoint ที่ใช้อยู่:
- `https://namo-forbidden-archive0-185116032835.asia-southeast1.run.app`

ทดสอบเร็ว:
```bash
curl https://namo-forbidden-archive0-185116032835.asia-southeast1.run.app/
```

```bash
curl -X POST https://namo-forbidden-archive0-185116032835.asia-southeast1.run.app/chat \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"สวัสดี\",\"session_id\":\"cloud-demo\"}"
```

Quick API check (optional):
```bash
python tools/check_api.py --base-url https://namo-forbidden-archive0-185116032835.asia-southeast1.run.app
```

## การใช้งานหลัก

### CLI (DarkNaMoSystem)
```bash
python app.py
```

### CLI (CharacterProfile)
```bash
python main.py
```

### REST API
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

### Memory service
```bash
uvicorn memory_service:app --host 0.0.0.0 --port 8081 --reload
```

## Web client (static)
ใช้ไฟล์ใน `web/` เพื่อคุยกับ API ผ่านหน้าเว็บ

ตัวอย่างรันแบบ local:
```bash
cd web
python -m http.server 5173
```

จากนั้นเปิด `http://localhost:5173` แล้วตั้งค่า Base URL ใน Settings

## Knowledge base (Embedding + FAISS)
1. วางไฟล์ `set.zip` ใน `learning_set/`
2. สร้างฐานความรู้:
   ```bash
   python learn_from_set.py
   ```
3. ค้นหาข้อมูล:
   ```bash
   python query_learned_knowledge.py
   ```

## ตัวแปรแวดล้อมที่สำคัญ
- `OPENAI_API_KEY` สำหรับสคริปต์ embedding/query
- `ELEVENLABS_API_KEY` และ `ELEVENLABS_VOICE_ID` สำหรับ TTS
- `TELEGRAM_TOKEN` สำหรับ Telegram bot
- `EMOTION_API_URL` สำหรับ EmotionAdapter (ถ้ามี service แยก)
- `PUBLIC_BASE_URL` สำหรับสร้าง media URL ที่เป็น absolute ใน REST API
- `CORS_ALLOW_ORIGINS` สำหรับกำหนด origin ที่อนุญาตใน REST API
- `MEMORY_LOGGING` เปิดการบันทึก memory ผ่าน REST API (ใช้กับ memory service)
- `NAMO_API_URL` สำหรับให้ Telegram bot เรียก REST API

## โครงสร้างหลักของ repo
```
adapters/            # IO adapters (emotion, memory, tts)
core/                # core engines
Core_Scripts/        # experimental scripts
docs/                # architecture & API docs
learning_set/        # zip input for knowledge base
tests/               # pytest
```

## เอกสารที่เกี่ยวข้อง
- `docs/ARCHITECTURE.md`
- `docs/API_SPEC.md`
- `docs/NamoNexus_Integration_Handbook.md`
- `INSTALL_GUIDE.md`

## ทดสอบ
```bash
pytest
```

หมายเหตุ: โค้ดตัวอย่างและ sample dialogue บางส่วนมีเนื้อหาเชิงผู้ใหญ่ (NSFW)
