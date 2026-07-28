# NamoNexus Integration Handbook

คู่มือนี้สรุปจุดเชื่อมต่อหลักสำหรับระบบที่ต้องการเชื่อมกับ NaMo Forbidden Archive

## Overview
NamoNexus สามารถผสานเข้ากับ:
- NaMo Omega API (`server.py`)
- Memory Service (`memory_service.py`)
- Knowledge base (`learn_from_set.py` + `query_learned_knowledge.py`)

## API Endpoints
### NaMo Omega API
- `POST /chat` ส่งข้อความเข้า engine และรับผลตอบกลับ
- `GET /` สำหรับตรวจสอบสถานะ

### Memory Service
- `POST /store` บันทึกความทรงจำ
- `POST /recall` เรียกคืนความทรงจำ
- `GET /health` ตรวจสอบสถานะ

## ตัวอย่างการเชื่อมต่อ
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"สวัสดี\",\"session_id\":\"demo\"}"
```

```bash
curl -X POST http://localhost:8081/store \
  -H "Content-Type: application/json" \
  -d "{\"content\":\"hello\",\"type\":\"contextual\"}"
```

## Deployment Notes
- รัน `server.py` และ `memory_service.py` แยก process
- ใช้ `.env` สำหรับกำหนด API keys (เช่น OpenAI, ElevenLabs)
