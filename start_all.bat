@echo off
echo [Sovereign System] Awakening All ASI Modules...

:: 1. เปิด Terminal สำหรับ API Server
start "NaMo Core Server" cmd /k "python server.py"

:: 2. เปิด Terminal สำหรับ Memory Service (Assuming it's a separate process as per architecture)
start "Memory Service" cmd /k "python memory_service.py"

:: 3. เปิด Terminal สำหรับ Ingestion Pipeline (Dream Loop)
start "Dream Loop" cmd /k "python core/memory/ingestion_pipeline.py"

:: 4. เปิด Terminal สำหรับ Telegram Bot
start "NaMo Telegram Bot" cmd /k "python Core_Scripts/namo_auto_AI_reply.py"

echo [System] All ASI engines and sensors are ONLINE.
pause
