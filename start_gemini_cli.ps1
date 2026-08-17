# Load GEMINI_API_KEY from .env if not already present in environment
if (-not $env:GEMINI_API_KEY) {
    if (Test-Path ".env") {
        $envLine = Get-Content ".env" | Where-Object { $_ -match "^GEMINI_API_KEY=(.+)$" }
        if ($envLine) {
            $env:GEMINI_API_KEY = ($envLine -split "=", 2)[1].Trim()
        }
    }
}

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  Google Gemini CLI - Interactive Terminal" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Cyan

if ($env:GEMINI_API_KEY) {
    Write-Host "GEMINI_API_KEY loaded successfully." -ForegroundColor Yellow
} else {
    Write-Host "[Warning] GEMINI_API_KEY is not set. Please set it in .env file." -ForegroundColor Red
}

Write-Host "Starting Gemini CLI..." -ForegroundColor Gray

# Launch Gemini CLI
gemini
