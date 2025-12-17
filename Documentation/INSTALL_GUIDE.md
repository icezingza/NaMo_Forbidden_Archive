# คู่มือการติดตั้ง NaMo Forbidden Archive

คู่มือนี้เน้นการติดตั้งและรันระบบหลักใน repo นี้ให้พร้อมใช้งาน

## ข้อกำหนดเบื้องต้น
- Python 3.11+ (แนะนำให้ตรงกับ CI)
- (ตัวเลือก) OpenAI API key สำหรับ `learn_from_set.py` และ `query_learned_knowledge.py`
- (ตัวเลือก) ElevenLabs API key สำหรับ TTS
- (ตัวเลือก) Telegram bot token หากใช้ `Core_Scripts/namo_auto_AI_reply.py`

## ติดตั้งแบบปกติ

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

## รันระบบหลัก

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

## Knowledge base (Embedding + FAISS)
1. วางไฟล์ `set.zip` ใน `learning_set/`
2. รัน:
   ```bash
   python learn_from_set.py
   ```
3. ค้นหา:
   ```bash
   python query_learned_knowledge.py
   ```

## Docker (ตัวเลือก)
```bash
docker build -t namo-forbidden-archive .
docker run --rm -e PORT=8080 -p 8080:8080 namo-forbidden-archive
```

## ทดสอบ
```bash
pytest
```
