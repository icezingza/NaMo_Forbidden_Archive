@echo off
chcp 65001 >nul
echo ===================================================
echo   NaMo Forbidden Archive - Starting Services
echo ===================================================

IF EXIST .venv\Scripts\activate.bat (
    echo Activating Virtual Environment...
    call .venv\Scripts\activate.bat
) ELSE (
    echo Virtual environment .venv not found. Running with global python...
)

echo Starting NaMo REST API ^& Web UI Server (Port 8005)...
start "NaMo REST API Server" cmd /k "python -m uvicorn server:app --host 0.0.0.0 --port 8005 --reload"

echo Waiting for server to initialize...
timeout /t 3 >nul

echo Opening Web UI in default browser...
start http://localhost:8005/ui

echo.
echo ===================================================
echo   NaMo Online!
echo   - Web UI:   http://localhost:8005/ui
echo   - REST API: http://localhost:8005
echo ===================================================
pause
