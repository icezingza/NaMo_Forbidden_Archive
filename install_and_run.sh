#!/bin/bash
# NaMo Forbidden Archive – Auto Installer & Runner
# Created for convenience setup and launch

set -e  # หยุดทันทีถ้ามี error

echo "🚀 เริ่มติดตั้ง NaMo_Forbidden_Archive..."

# 1. Clone repository
if [ ! -d "NaMo_Forbidden_Archive" ]; then
    echo "📦 กำลังดาวน์โหลด repository..."
    git clone https://github.com/icezingza/NaMo_Forbidden_Archive.git
else
    echo "📁 พบโฟลเดอร์ NaMo_Forbidden_Archive แล้ว — ข้ามการดาวน์โหลด"
fi

cd NaMo_Forbidden_Archive

# 2. Create and activate virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 สร้าง virtual environment..."
    python3 -m venv venv
fi

echo "🧠 เปิดใช้งาน environment..."
source venv/bin/activate

# 3. Install dependencies
if [ -f "requirements.txt" ]; then
    echo "📚 ติดตั้ง dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "⚠️ ไม่พบ requirements.txt — ข้ามขั้นตอนนี้"
fi

# 4. Optional: install dev tools if present
if [ -f "requirements-dev.txt" ]; then
    echo "🧩 ติดตั้ง dependencies สำหรับนักพัฒนา..."
    pip install -r requirements-dev.txt
fi

# 5. Run the main application
if [ -f "main.py" ]; then
    echo "🚀 รันโปรแกรมหลัก..."
    python main.py
else
    echo "❌ ไม่พบ main.py — กรุณาตรวจสอบชื่อไฟล์หรือ README.md"
fi
