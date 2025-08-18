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

# เปิดพอร์ต 8000
EXPOSE 8000

# คำสั่งรัน Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]