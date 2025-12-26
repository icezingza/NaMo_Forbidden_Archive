# Commercial Strategy

## โมเดลรายได้ (Phase 1)
- Usage-based สำหรับ API requests
- เพิ่ม feature gating สำหรับ TTS และ memory length ตาม plan

## Plan Tiers (ตัวอย่าง)
- public: ทดลองใช้งาน, ไม่มี API key หรือใช้ default key
- creator: จำกัดจำนวน requests/วัน และเปิดใช้ TTS
- studio: เพิ่ม limits และรองรับ custom persona

## การเชื่อมกับระบบ
- ใช้ `NAMO_API_KEYS` เพื่อกำหนด plan ต่อ API key
- ใช้ `NAMO_API_DEFAULT_PLAN` สำหรับผู้ใช้ที่ไม่มี key
- บันทึก usage events ด้วย `NAMO_USAGE_LOG_PATH` (JSONL)

## Metrics ที่ต้องเก็บ
- requests ต่อ plan
- text length โดยเฉลี่ยต่อ request
- session retention และ churn

## ขั้นตอนถัดไป
- เชื่อม usage log กับระบบ billing
- สร้าง dashboard สำหรับ analytics
