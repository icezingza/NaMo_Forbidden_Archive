# ROADMAP.md - NaMo Forbidden Archive

**เวอร์ชัน:** 1.0
**วันที่:** 2026-07-09
**เป้าหมาย:** ทำให้โปรเจกต์ใช้งานได้จริง + พร้อมนำไปขายเชิงพาณิชย์ (Commercial Ready)

---

## ภาพรวม
NaMo Forbidden Archive เป็นระบบ AI Persona สำหรับบทสนทนาแบบผู้ใหญ่/NSFW ที่มี Emotion Engine, Memory RAG และ Multi-Persona

**สถานะปัจจุบัน:** ยังอยู่ในขั้นพัฒนา (มีโค้ดพื้นฐาน แต่ยังไม่ Production Ready และยังไม่พร้อมขาย)

---

## Roadmap ทั้งหมด (5 Phases)

### **Phase 0: เตรียมพื้นฐาน** (1-3 วัน)
- [x] อ่านเอกสารทั้งหมด (CLAUDE.md, README.md, INSTALL_GUIDE.md, ARCHITECTURE.md)
- [x] Clone repo และตั้งค่า `.env` จาก `.env.example`
- [x] ติดตั้ง dependencies และรันได้ทั้ง CLI (`app.py`) และ REST API (`server.py`)
- [x] รัน `make lint`, `make format`, `make test` และแก้ไขข้อผิดพลาด (ผ่านครบ 5 gate, 344 tests)
- [x] ทดสอบ Web UI (`/ui`)

**สถานะ:** ✅ เสร็จ

---

### **Phase 1: ทำให้เสถียรและ Production Ready** (1-2 สัปดาห์)

**โค้ดและคุณภาพ**
- [x] Refactor โค้ดหลักให้ตรง PEP 8 (black + ruff) — CI เขียวครบ
- [x] แก้ Bug และเพิ่ม Error Handling ที่เหมาะสม — `core/exceptions.py` + global handlers (server + memory), client-safe JSON, ซ่อน stack trace เมื่อ `debug=False`
- [x] เพิ่ม Structured Logging — `config.setup_logging()` + entry points `server.py`/`memory_service.py`
- [x] เพิ่ม/ปรับ Unit Test ให้ครอบคลุมมากขึ้น — 354 tests, coverage 91%; `adapters/memory.py` 100%, error/edge paths + unknown-engine ครอบคลุม
- [x] แยก Configuration สำหรับ Production / Development — `debug`/`log_level` คุม logging + error-detail exposure

**ระบบ**
- [x] ทำให้ Docker + docker-compose ใช้งานได้สมบูรณ์ — compose มี `api` + `memory` (+qdrant/neo4j), `docker compose up --build` รันทั้ง stack
- [x] แยก Memory Service เป็น microservice — `memory_service.py` + `Dockerfile.memory`
- [x] เพิ่ม Security (Rate Limiting, CORS, Admin Secret, API Key)
- [x] เพิ่ม Session Management และ Auto Cleanup — `SESSION_TTL_SECONDS` + cleanup loop
- [x] เพิ่ม Health Check + Monitoring — `/v1/health`, `/v1/status` (monitoring เพิ่มเติมทีหลัง)

**Deliverable:** Docker image ที่เสถียร + API ที่พร้อมใช้งาน

**สถานะ:** ✅ เสร็จ (100%) — ก้าว 1 (Logging), 2 (Docker Compose), 3 (Error Handling), 4 (Unit Tests) ครบทุกก้าว

---

### **Phase 2: ปรับปรุงประสบการณ์ผู้ใช้ (UX/UI)** (1-2 สัปดาห์)
- [~] ปรับ Web UI ให้สวยงาม ทันสมัย และ Responsive — ดีไซน์ ivory/crimson มีอยู่แล้ว + responsive breakpoints (ปรับเพิ่มได้)
- [x] เพิ่มฟีเจอร์ History, Settings, Persona Switch — Settings + local history มีแล้ว; เพิ่ม Persona Switch (topbar selector, ส่ง `engine`, จำผ่าน localStorage)
- [ ] เพิ่ม Voice Input/Output (Whisper + ElevenLabs)
- [ ] สร้าง Landing Page สำหรับขาย
- [x] เพิ่ม Age Gate / Content Warning — overlay 18+ (`web/`), ยืนยันแล้วจำผ่าน localStorage; verify ด้วย headless Chromium

**Deliverable:** เว็บแอพที่ใช้งานง่ายและดูเป็นผลิตภัณฑ์

**สถานะ:** 🟡 กำลังทำ — ก้าว 1 (Age Gate) + ก้าว 2 (Persona Switch UI) เสร็จ; เหลือ Voice I/O, Landing Page, ขัดเกลา responsive

---

### **Phase 3: ความปลอดภัย กฎหมาย และระบบการขาย** (2-3 สัปดาห์)

**Security**
- [ ] เพิ่ม Authentication (JWT / API Key Management)
- [ ] Encryption สำหรับข้อมูล敏感
- [ ] Audit Log
- [ ] Security Scan (bandit, pip-audit)

**กฎหมาย**
- [ ] เขียน Terms of Service, Privacy Policy, Disclaimer (18+)
- [ ] ระบบยืนยันอายุ (Age Verification)
- [ ] ตรวจสอบกฎหมายที่เกี่ยวข้อง

**ระบบขาย**
- [ ] เพิ่ม Subscription System (Stripe / Paddle)
- [ ] Feature Flag (Lite / Pro / Enterprise)
- [ ] Multi-tenant Support

**Deliverable:** ระบบพร้อมขาย + เอกสารทางกฎหมายครบถ้วน

**สถานะ:** ⬜ ยังไม่ทำ

---

### **Phase 4: Marketing & Launch** (1-2 สัปดาห์)
- [ ] สร้าง Landing Page + Demo ที่สวยงาม
- [ ] ทำ Video Demo การใช้งาน
- [ ] เขียน Documentation สำหรับลูกค้า
- [ ] ตั้งราคาและแผนการขาย
- [ ] เตรียมช่องทางการขาย (เว็บ, Gumroad, Patreon)
- [ ] Beta Testing กับกลุ่มผู้ใช้

**Deliverable:** เปิดขายได้จริง

**สถานะ:** ⬜ ยังไม่ทำ

---

### **Phase 5: หลัง Launch (Ongoing)**
- [ ] เก็บ Feedback และแก้ไขต่อเนื่อง
- [ ] เพิ่มฟีเจอร์ใหม่ (Image Generation, Mobile Support ฯลฯ)
- [ ] ปรับ Scaling และ Performance
- [ ] Marketing และ Community Building

---

## ลำดับความสำคัญในการเริ่มงาน
1. **Phase 0** → **Phase 1** (ต้องทำให้เสถียรก่อน)
2. Phase 3 (Security + Monetization) สำคัญมากเพราะเป็น NSFW
3. ทำทีละ Phase และทดสอบให้ผ่านก่อนไป Phase ถัดไป

---

**แนวทางการทำงานกับ Agent:**
- ให้ Agent อ่านไฟล์นี้ก่อนทุกครั้ง
- ทำงานตามลำดับ Phase
- รายงานความคืบหน้าทุก Phase
- Follow CLAUDE.md และ PEP 8 อย่างเคร่งครัด

---

**ติดตามความคืบหน้า:**
อัพเดทสถานะในไฟล์นี้เป็นประจำ (ใช้ [x] เมื่อเสร็จ)

---
