@echo off
echo [Sovereign System] Awakening All Modules...

:: 1. สตาร์ท Database ผ่าน Docker Compose
echo Starting Database Containers...
docker compose up -d
timeout /t 10

:: 2. เปิด Terminal สำหรับ API Server (พอร์ต 8000)
echo Starting API Server...
start "NamoNexus Core Server" cmd /k "python server.py"

:: 3. เปิด Terminal สำหรับ Memory Service (พอร์ต 8081)
echo Starting Memory Service...
start "NamoNexus Memory Service" cmd /k "python memory_service.py"

:: 4. เปิด Terminal สำหรับ Web UI
echo Starting Web UI...
start "NamoNexus Web UI" cmd /k "cd web && python -m http.server 5173"

:: 5. เปิด Terminal สำหรับ Telegram Bot
echo Starting Telegram Bot...
start "NamoNexus Telegram Bot" cmd /k "python core/integrations/telegram_bot.py"

echo [System] All NamoNexus engines are online and listening...
pause
