# ใช้ Python เวอร์ชันที่เหมาะสม
FROM python:3.12-slim

# ตั้ง working directory
WORKDIR /app

# คัดลอก requirements.txt ก่อนเพื่อให้ cache ทำงาน
COPY requirements.txt .

# ติดตั้ง dependencies
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดทั้งหมดเข้า container
COPY . .

# เปิดพอร์ตที่ Cloud Run กำหนด (ปกติคือ 8080)
EXPOSE 8080

# คำสั่งรัน Uvicorn โดยใช้ $PORT จาก environment variable
# ต้องใช้ shell form (ไม่มี []) เพื่อให้ $PORT ทำงาน
CMD uvicorn server:app --host 0.0.0.0 --port $PORT