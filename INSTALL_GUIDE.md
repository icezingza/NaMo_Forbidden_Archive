# คู่มือการติดตั้งและใช้งานแบบละเอียด (NaMo Forbidden Archive)

เอกสารนี้อธิบายการติดตั้งและการใช้งานฟีเจอร์หลักทั้งหมดใน repo นี้
โดยแบ่งเป็นขั้นตอนที่ทำตามได้ทันทีทั้ง Windows และ macOS/Linux

## ข้อกำหนดเบื้องต้น
- Python 3.11+ (แนะนำให้ตรงกับ CI)
- Git (ถ้าต้องการ clone ผ่านคำสั่ง)
- (ตัวเลือก) OpenAI API key สำหรับ `learn_from_set.py` และ `query_learned_knowledge.py`
- (ตัวเลือก) ElevenLabs API key สำหรับ TTS
- (ตัวเลือก) Telegram bot token หากใช้ `Core_Scripts/namo_auto_AI_reply.py`

## โครงสร้างสำคัญของโปรเจค
- REST API: `server.py`
- Memory service: `memory_service.py`
- CLI (หลัก): `app.py`
- CLI (ทดลอง): `main.py`
- Knowledge base: `learn_from_set.py`, `query_learned_knowledge.py`
- Telegram bot (ตัวเลือก): `Core_Scripts/namo_auto_AI_reply.py`

## ติดตั้งแบบปกติ

### 1) เตรียมไฟล์ .env
คัดลอกไฟล์ตัวอย่างแล้วกรอกค่าที่จำเป็น

Windows (PowerShell)
```powershell
Copy-Item .env.example .env
```

macOS/Linux
```bash
cp .env.example .env
```

### 2) สร้างและเปิดใช้งาน virtual environment + ติดตั้ง dependencies

Windows (PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## ตัวแปรแวดล้อมที่สำคัญ (.env)
อ้างอิงจาก `.env.example`:
- `OPENAI_API_KEY` สำหรับ embedding/query (Knowledge base)
- `TELEGRAM_TOKEN` สำหรับ Telegram bot
- `ELEVENLABS_API_KEY` และ `ELEVENLABS_VOICE_ID` สำหรับ TTS
- `EMOTION_API_URL` สำหรับ emotion service (ถ้ามี service แยก)
- `MEMORY_API_URL` และ `MEMORY_API_KEY` หากใช้ memory service ภายนอก
- `MEMORY_LOGGING` เปิดการบันทึก memory ผ่าน REST API (ค่า 1/0)
- `PUBLIC_BASE_URL` สำหรับสร้าง media URL ที่เป็น absolute ใน REST API
- `CORS_ALLOW_ORIGINS` สำหรับกำหนด origin ที่อนุญาตใน REST API
- `NAMO_API_URL` สำหรับให้ Telegram bot เรียก REST API
- `NAMO_API_TIMEOUT` timeout ของ Telegram bot
- `TELEGRAM_SHOW_STATUS` แสดง status เพิ่มเติมใน Telegram (ค่า 1/0)
- `TELEGRAM_INCLUDE_MEDIA` แนบ media URL ใน Telegram (ค่า 1/0)

## การใช้งานฟีเจอร์หลัก

### 1) CLI โหมดหลัก (DarkNaMoSystem)
```bash
python app.py
```

### 2) CLI โหมดทดลอง (CharacterProfile + emotion_parasite_engine)
```bash
python main.py
```

### 3) REST API (NaMo Omega Engine)
```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

ตัวอย่างเรียก API:
```bash
curl -X POST http://localhost:8000/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"text\": \"สวัสดี\", \"session_id\": \"demo-session\"}"
```

> รูปแบบ response อ้างอิง `docs/API_SPEC.md`

หมายเหตุเพิ่มเติม:
- REST API จะเสิร์ฟไฟล์ media ที่ `/media/visual` และ `/media/audio`
- ตั้งค่า `PUBLIC_BASE_URL` หากต้องการให้ media URL เป็น absolute
- ตั้งค่า `CORS_ALLOW_ORIGINS` หากใช้เว็บ client แยกโดเมน

### 4) Memory Service
```bash
uvicorn memory_service:app --host 0.0.0.0 --port 8081 --reload
```

ตัวอย่างเรียก API:
```bash
curl -X POST http://localhost:8081/store ^
  -H "Content-Type: application/json" ^
  -d "{\"content\":\"hello\",\"type\":\"contextual\",\"session_id\":\"demo\"}"
```

ตรวจสอบสุขภาพ:
```bash
curl http://localhost:8081/health
```

### 4.1) Web Client (Static)
ใช้ไฟล์ใน `web/` เพื่อคุยกับ REST API ผ่านหน้าเว็บ

ตัวอย่างรันแบบ local:
```bash
cd web
python -m http.server 5173
```

เปิด `http://localhost:5173` แล้วตั้งค่า Base URL ใน Settings

### 5) Knowledge Base (Embedding + FAISS)
1) วางไฟล์ `set.zip` ใน `learning_set/`
2) สร้างฐานความรู้:
   ```bash
   python learn_from_set.py
   ```
3) ค้นหาข้อมูล:
   ```bash
   python query_learned_knowledge.py
   ```

### 6) Telegram Auto Reply (ตัวเลือก)
ติดตั้ง dependency เพิ่ม:
```bash
pip install python-telegram-bot
```

ตั้งค่า `TELEGRAM_TOKEN` ใน `.env` แล้วรัน:
```bash
python Core_Scripts/namo_auto_AI_reply.py
```

หากต้องการให้ Telegram bot เรียก REST API ให้ตั้งค่า `NAMO_API_URL`
และตั้งค่า `TELEGRAM_SHOW_STATUS` หรือ `TELEGRAM_INCLUDE_MEDIA` ตามต้องการ

### 7) ElevenLabs TTS (ตัวเลือก)
ตั้งค่า `ELEVENLABS_API_KEY` และ `ELEVENLABS_VOICE_ID` ใน `.env`
ระบบจะเรียกใช้งานผ่าน `adapters/tts.py` เมื่อ flow ที่เกี่ยวข้องถูกใช้งาน

## การทดสอบ
ติดตั้ง dependencies สำหรับ dev แล้วรัน pytest:
```bash
pip install -r requirements-dev.txt
pytest
```

## Docker (ตัวเลือก)
```bash
docker build -t namo-forbidden-archive .
docker run --rm -e PORT=8080 -p 8080:8080 namo-forbidden-archive
```

## Deploy บน Cloud Run (ตัวเลือก)
มีสคริปต์ตัวอย่างใน `deploy.sh` และ `deploy_fixed.sh`
ให้แก้ `PROJECT_ID`, `SERVICE_NAME`, และ `REGION` ให้ตรงกับโปรเจคของคุณ

### Endpoint ที่ใช้งานอยู่ (สำหรับผู้ใช้เดียว)
- Project ID: `arctic-signer-471822-i8`
- Project Number: `185116032835`
- Service URL: `https://namo-forbidden-archive0-185116032835.asia-southeast1.run.app`

ตัวอย่างทดสอบ:
```bash
curl https://namo-forbidden-archive0-185116032835.asia-southeast1.run.app/
```

```bash
curl -X POST https://namo-forbidden-archive0-185116032835.asia-southeast1.run.app/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"สวัสดี\",\"session_id\":\"cloud-demo\"}"
```

### สคริปต์เช็ค API แบบเร็ว (ตัวเลือก)
ใช้ `tools/check_api.py` เพื่อตรวจสอบ API ทั้งแบบ local และ Cloud Run

ตัวอย่าง (local):
```bash
python tools/check_api.py --base-url http://localhost:8000
```

ตัวอย่าง (Cloud Run):
```bash
python tools/check_api.py --base-url https://namo-forbidden-archive0-185116032835.asia-southeast1.run.app
```

## Troubleshooting
- `ModuleNotFoundError`: ตรวจสอบว่าเปิด venv แล้ว และติดตั้ง `requirements.txt` แล้วหรือไม่
- `No TELEGRAM_TOKEN set`: ตั้งค่า `TELEGRAM_TOKEN` ใน `.env`
- `OpenAI authentication error`: ตั้งค่า `OPENAI_API_KEY`
- Port ชนกัน: เปลี่ยนพอร์ตตอนรัน `uvicorn` เช่น `--port 8001`

## หมายเหตุ
`README.md` ระบุว่าตัวอย่างบทสนทนาบางส่วนเป็น NSFW
