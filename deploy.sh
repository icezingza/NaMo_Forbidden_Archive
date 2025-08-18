#!/bin/bash
# Script สำหรับ build และ deploy API ไปที่ Google Cloud Run 🚀

# หยุดทันทีถ้ามี error
set -e

# ===== CONFIG =====
PROJECT_ID="YOUR_PROJECT_ID"   # ใส่ Google Cloud Project ID ของคุณ
SERVICE_NAME="namo-api"        # ชื่อ service
REGION="asia-southeast1"       # ใช้ region ใกล้ไทย
# ===================

echo "👉 ตั้งค่า project..."
gcloud config set project $PROJECT_ID

echo "👉 สร้าง image และ deploy ไปยัง Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated

echo "✅ เสร็จเรียบร้อย! เช็ค URL ด้านบนได้เลย 🎉"