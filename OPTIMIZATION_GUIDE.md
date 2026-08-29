# 🚀 Optimization Guide - ลดขนาด & เพิ่มความเร็ว

## 📊 ปัจจุบัน (Current)
- **Image Size**: 681 MB
- **Build Time**: ~3-5 min (dependencies recompile)
- **Runtime Start**: ~10-15 sec (engine initialization)

---

## 1️⃣ ลดขนาด Image (Size Reduction)

### Strategy A: Aggressive .dockerignore ✅
- แยกไฟล์ที่ไม่ต้องใช้: JSON state, audio/video assets, docs
- **ผลลัพธ์**: ~681 MB → 250-300 MB (60% reduction)
- ✅ **ใช้แล้ว**: Dockerfile.lean + enhanced .dockerignore

### Strategy B: Slim → Distroless (Advanced)
```dockerfile
FROM python:3.12-slim  # 150 MB base
# ↓
FROM gcr.io/distroless/python312  # 45 MB base
```
- **ขนาดลดเพิ่ม**: 250 MB → 180 MB
- ⚠️ **Tradeoff**: ไม่มี shell/curl (healthcheck ต้องใช้ TCP probe)

### Strategy C: Wheels สำหรับ slim dependencies
```bash
# Optimize requirements.txt - ใช้เฉพาะ production deps
# REMOVE: pytest, black, ruff, dev tools
```
- **ผลลัพธ์**: 250 MB → 200 MB

---

## 2️⃣ เพิ่มความเร็ว Build (Build Speed)

### Strategy A: BuildKit Cache Mounts ✅
```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip
```
- **ประโยชน์**: ครั้งแรก 3 min → ครั้งต่อไป 30 sec (90% faster)
- ✅ **ใช้แล้ว**: Dockerfile.lean

### Strategy B: Layer Caching (Order Matters)
1. COPY requirements.txt first (ไม่เปลี่ยนบ่อย)
2. RUN pip install (cache hit 99% of time)
3. COPY source code last (เปลี่ยนทุกครั้ง)

✅ **ใช้แล้ว**: จัดเรียงใหม่ให้ดีที่สุด

### Strategy C: Parallel Build (Docker Buildx)
```bash
docker buildx create --name mybuilder
docker buildx build --builder mybuilder -t namo-lean:latest .
```
- **ประโยชน์**: Build stages ขนานกัน → 30% ลด build time

### Strategy D: Minimal requirements.txt
```bash
# Remove:
# - tensorflow, transformers (heavy AI libs mentioned in logs)
# - dev dependencies
```

---

## 3️⃣ เพิ่มความเร็ว Runtime (Runtime Speed)

### Strategy A: Uvicorn Workers
```bash
# Current: 1 worker
CMD ["python", "-m", "uvicorn", "server:app", "--workers", "4"]

# +30-40% throughput แต่ใช้ RAM มากขึ้น
```

### Strategy B: Healthcheck Optimization
```dockerfile
# Current: 30s interval
HEALTHCHECK --interval=5s --timeout=3s --retries=3

# ลดจาก 30s → 5s = detect failures 6x faster
```

### Strategy C: Remove PYTHONDONTWRITEBYTECODE
```bash
# .pyc files ช้ามาก ให้สร้าง:
# ENV PYTHONUNBUFFERED=1
# ลบ PYTHONDONTWRITEBYTECODE
```

---

## 📈 ผลลัพธ์ที่คาดหวัง

| Optimization | Size | Build | Runtime |
|---|---|---|---|
| **Current** | 681 MB | 3-5 min | 10-15s startup |
| **+ .dockerignore** | 250 MB (-63%) | 3-5 min | 10s |
| **+ BuildKit cache** | 250 MB | **30s** (-90%) | 10s |
| **+ Distroless** | 180 MB (-73%) | 30s | 8s |
| **+ Workers + healthcheck** | 180 MB | 30s | **+40% throughput** |

---

## 🎯 ทำตอนนี้ (Recommended Order)

1. ✅ ใช้ `Dockerfile.lean` (สร้าง)
2. ✅ ใช้ .dockerignore ที่ enhanced (สร้าง)
3. 🔄 Test `docker build -f Dockerfile.lean -t namo-lean:latest .`
4. 📊 Compare size: `docker images`
5. ⚡ Enable BuildKit: `export DOCKER_BUILDKIT=1`
6. 🚀 Switch to distroless (optional, advanced)

---

## ❓ คำถาม

- **Distroless ใช้ได้ไหม** (ต้อง update healthcheck → TCP port probe)
- **ลบ dev libraries จาก requirements** (ปลอดภัยไหม)
- **Uvicorn workers เพิ่มจากนี้** (จาก 1 → 4)
