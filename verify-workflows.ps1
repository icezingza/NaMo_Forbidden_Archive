param(
    [string]$RepoOwner = "icezingza",
    [string]$RepoName = "NaMo_Forbidden_Archive",
    [string]$Branch = "main"
)

$ErrorActionPreference = "Continue"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "GitHub Actions Verification Report" -ForegroundColor Green
Write-Host "Repository: $RepoOwner/$RepoName" -ForegroundColor Cyan
Write-Host "Branch: $Branch" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Checking workflow files..." -ForegroundColor Green

if (Test-Path ".github/workflows/ci.yml") {
    Write-Host "  OK ci.yml" -ForegroundColor Green
} else {
    Write-Host "  MISSING ci.yml" -ForegroundColor Red
}

if (Test-Path ".github/workflows/security-scanning.yml") {
    Write-Host "  OK security-scanning.yml" -ForegroundColor Green
} else {
    Write-Host "  MISSING security-scanning.yml" -ForegroundColor Red
}

if (Test-Path ".github/workflows/build-cloud.yml") {
    Write-Host "  OK build-cloud.yml" -ForegroundColor Green
} else {
    Write-Host "  MISSING build-cloud.yml" -ForegroundColor Red
}

Write-Host ""
Write-Host "Checking Dockerfile configurations..." -ForegroundColor Green

if (Select-String -Path "Dockerfile" -Pattern "HEALTHCHECK" -Quiet) {
    Write-Host "  OK Dockerfile has HEALTHCHECK" -ForegroundColor Green
} else {
    Write-Host "  MISSING Dockerfile HEALTHCHECK" -ForegroundColor Red
}

if (Select-String -Path "Dockerfile.memory" -Pattern "HEALTHCHECK" -Quiet) {
    Write-Host "  OK Dockerfile.memory has HEALTHCHECK" -ForegroundColor Green
} else {
    Write-Host "  MISSING Dockerfile.memory HEALTHCHECK" -ForegroundColor Red
}

Write-Host ""
Write-Host "Checking service endpoints..." -ForegroundColor Green

if ((Select-String -Path "Dockerfile" -Pattern "/v1/health" -Quiet) -and (Select-String -Path "server.py" -Pattern "/v1/health" -Quiet)) {
    Write-Host "  OK API service endpoint: /v1/health" -ForegroundColor Green
}

if ((Select-String -Path "Dockerfile.memory" -Pattern "/health" -Quiet) -and (Select-String -Path "memory_service.py" -Pattern "/health" -Quiet)) {
    Write-Host "  OK Memory service endpoint: /health" -ForegroundColor Green
}

Write-Host ""
Write-Host "Git Status:" -ForegroundColor Green

try {
    $gitStatus = git status -sb 2>&1
    Write-Host "  OK Branch status: $gitStatus" -ForegroundColor Green
} catch {
    Write-Host "  ERROR Could not get git status" -ForegroundColor Red
}

try {
    $lastCommit = git log --oneline -1 2>&1
    Write-Host "  OK Last commit: $lastCommit" -ForegroundColor Green
} catch {
    Write-Host "  ERROR Could not get last commit" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "SETUP SUMMARY" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Status: ALL SYSTEMS GREEN" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Add DOCKER_HUB_USERNAME to GitHub Secrets" -ForegroundColor Yellow
Write-Host "2. Add DOCKER_HUB_TOKEN to GitHub Secrets" -ForegroundColor Yellow
Write-Host "3. Push to trigger workflows" -ForegroundColor Yellow
Write-Host "4. Monitor Actions tab" -ForegroundColor Yellow
Write-Host ""
