@echo off
REM Quick Start: NaMo ACC Telegram Bot

setlocal enabledelayedexpansion

echo.
echo ====================================
echo  NaMo Forbidden Archive (ACC)
echo  Telegram Bot Quick Start
echo ====================================
echo.

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not found. Please install Docker Desktop.
    exit /b 1
)

REM Navigate to project
cd /d "%~dp0projects-NaMo-Forbidden-Archive"
if errorlevel 1 (
    echo ERROR: Cannot find projects-NaMo-Forbidden-Archive folder
    exit /b 1
)

echo [1/4] Stopping old container...
docker rm namo-acc -f >nul 2>&1

echo [2/4] Building Docker image...
docker build -t namo-acc-backend . >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker build failed
    exit /b 1
)

echo [3/4] Starting container...
docker run -d -p 8081:8080 --env-file .env --name namo-acc namo-acc-backend >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to start container
    exit /b 1
)

timeout /t 2 /nobreak >nul

echo [4/4] Checking status...
docker ps --filter "name=namo-acc" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo.
echo ====================================
echo  SETUP INSTRUCTIONS
echo ====================================
echo.
echo 1. Get your public HTTPS URL:
echo    - Use ngrok: ngrok http 8080
echo    - Or setup custom domain with SSL
echo.
echo 2. Set environment variables:
echo    - TELEGRAM_BOT_TOKEN (from @BotFather)
echo    - Edit .env file
echo.
echo 3. Register webhook:
echo    python setup_telegram.py --webhook-url https://YOUR_URL/webhook/telegram
echo.
echo 4. Test the bot:
echo    - Open Telegram: @Vipha_ACC_bot
echo    - Send /start
echo.
echo 5. View logs:
echo    docker logs -f namo-acc
echo.
echo ====================================
echo  Container running on: http://localhost:8081
echo ====================================
echo.
