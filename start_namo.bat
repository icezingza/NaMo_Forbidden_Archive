@echo off
echo [Sovereign System] Awakening NaMo Omega and Telegram Orchestrator...

:: 1. เปิด Terminal สำหรับ API Server (พอร์ต 8000)
start "NaMo Core Server" cmd /k "python server.py"

:: 2. เปิด Terminal สำหรับ Telegram Bot
start "NaMo Telegram Bot" cmd /k "python Core_Scripts/namo_auto_AI_reply.py"

echo [System] All engines online. Sovereign NaMo is listening...
pause
