#!/bin/bash
# Script สำหรับ build และ deploy API ไปที่ Google Cloud Run 🚀

# หยุดทันทีถ้ามี error
set -e

# ===== CONFIG =====
PROJECT_ID="arctic-signer-471822-i8"   # Google Cloud Project ID ของคุณ
SERVICE_NAME="namo-forbidden-archive0" # ชื่อ service ที่ต้องการ deploy
REGION="asia-southeast1"       # region ที่ใช้
# ===================

echo "👉 ตั้งค่า project เป็น $PROJECT_ID..."
gcloud config set project $PROJECT_ID

echo "👉 สร้าง image และ deploy ไปยัง Cloud Run service: $SERVICE_NAME..."
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated

echo "✅ เสร็จเรียบร้อย! เช็ค URL ด้านบนได้เลย 🎉"
