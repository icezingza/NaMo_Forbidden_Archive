@echo off
echo [Sovereign System] Awakening All Modules...

:: 1. สตาร์ท Database ผ่าน Docker Compose
echo Starting Database Containers...
docker compose up -d
timeout /t 10

:: 2. รันการดูดซับความรู้ (Ingestion Pipeline)
echo Ingesting Knowledge...
python core/memory/ingestion_pipeline.py --mode dream_loop

:: 3. เปิด Terminal สำหรับ API Server
start "NaMo Core Server" cmd /k "python server.py"

:: 4. เปิด Terminal สำหรับ Web UI
start "Web UI" cmd /k "cd web && python -m http.server 5173"

:: 5. เปิด Terminal สำหรับ Telegram Bot
start "NaMo Telegram Bot" cmd /k "python Core_Scripts/namo_auto_AI_reply.py"

echo [System] All engines online. Sovereign NaMo is listening...
pause
