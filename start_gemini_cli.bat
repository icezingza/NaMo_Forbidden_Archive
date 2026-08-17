@echo off
chcp 65001 >nul
echo ===================================================
echo   Google Gemini CLI - Interactive Terminal
echo ===================================================

:: Load from .env if GEMINI_API_KEY is not already set
if "%GEMINI_API_KEY%"=="" (
    if exist .env (
        for /f "usebackq tokens=1,* delims==" %%A in (`findstr /b "GEMINI_API_KEY=" .env`) do (
            set "GEMINI_API_KEY=%%B"
        )
    )
)

if "%GEMINI_API_KEY%"=="" (
    echo [Warning] GEMINI_API_KEY is not set. Please set it in your environment or .env file.
) else (
    echo GEMINI_API_KEY loaded successfully.
)

echo Starting Gemini CLI in interactive mode...
echo.
gemini
pause
