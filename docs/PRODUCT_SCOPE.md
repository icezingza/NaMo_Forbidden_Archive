# Product Scope: NaMo Forbidden Archive

## เป้าหมายของผลิตภัณฑ์
สร้างบริการ AI persona ที่ตอบสนองแบบ real-time พร้อม media/voice แบบต่อยอดได้ (API-first) เพื่อเปิดตลาดทั้ง B2C (companion experience) และ B2B (persona AI API).

## กลุ่มเป้าหมายหลัก (Phase 1)
- นักพัฒนา/ผู้สร้างคอนเทนต์ที่ต้องการ API สำหรับ persona AI
- ทีมที่ต้องการ demo persona AI + media integration แบบรวดเร็ว

## Value Proposition
- Persona AI ที่มีเอกลักษณ์ + stateful session
- รองรับ media trigger (ภาพ/เสียง) และ TTS
- ติดตั้ง/รันได้รวดเร็ว และต่อยอดเป็น SaaS ได้

## MVP Feature Set (ขายได้เร็ว)
- REST API `/v1/chat` พร้อม API key option
- Web demo ที่เชื่อม API และแสดง media
- Usage logging สำหรับ analytics/billing
- เอกสาร API และ Developer Quickstart

## KPI แนะนำ
- Weekly Active Developers (WAD)
- API requests/day
- Conversion rate จาก demo → API key request

## ขอบเขตที่ยังไม่ทำ (คงเดิม)
- การเปลี่ยนแปลงด้าน content policy/safety
- การปรับ architecture เพื่อ scale แบบ multi-instance
