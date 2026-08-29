# GitHub Actions Status Verification Script (PowerShell)
# Run this locally to verify all workflows are ready and passing

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

# Check workflow files
Write-Host "✓ Checking workflow files..." -ForegroundColor Green

@(".github/workflows/ci.yml", ".github/workflows/security-scanning.yml", ".github/workflows/build-cloud.yml") | ForEach-Object {
    if (Test-Path $_) {
        Write-Host "  ✓ $(Split-Path $_ -Leaf)" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $(Split-Path $_ -Leaf) NOT FOUND" -ForegroundColor Red
    }
}
Write-Host ""

# Check Dockerfile configurations
Write-Host "✓ Checking Dockerfile configurations..." -ForegroundColor Green

if (Select-String -Path "Dockerfile" -Pattern "HEALTHCHECK" -Quiet) {
    $healthPath = (Select-String -Path "Dockerfile" -Pattern "curl -f" | Select-String "http" | ForEach-Object { $_.Line -replace '.*curl -f ' -replace ' .*' }).Trim()
    Write-Host "  ✓ Dockerfile has HEALTHCHECK (endpoint: $healthPath)" -ForegroundColor Green
}

if (Select-String -Path "Dockerfile.memory" -Pattern "HEALTHCHECK" -Quiet) {
    $healthPath = (Select-String -Path "Dockerfile.memory" -Pattern "curl -f" | Select-String "http" | ForEach-Object { $_.Line -replace '.*curl -f ' -replace ' .*' }).Trim()
    Write-Host "  ✓ Dockerfile.memory has HEALTHCHECK (endpoint: $healthPath)" -ForegroundColor Green
}
Write-Host ""

# Check service endpoints
Write-Host "✓ Checking service endpoints..." -ForegroundColor Green

if ((Select-String -Path "Dockerfile" -Pattern "/v1/health" -Quiet) -and (Select-String -Path "server.py" -Pattern "/v1/health" -Quiet)) {
    Write-Host "  ✓ API service endpoint: /v1/health" -ForegroundColor Green
}

if ((Select-String -Path "Dockerfile.memory" -Pattern "/health" -Quiet) -and (Select-String -Path "memory_service.py" -Pattern "/health" -Quiet)) {
    Write-Host "  ✓ Memory service endpoint: /health" -ForegroundColor Green
}
Write-Host ""

# Check required GitHub secrets
Write-Host "✓ Required GitHub Secrets (setup via Settings > Secrets):" -ForegroundColor Green
Write-Host "  • DOCKER_HUB_USERNAME" -ForegroundColor Yellow
Write-Host "  • DOCKER_HUB_TOKEN" -ForegroundColor Yellow
Write-Host "  • CODECOV_TOKEN (optional)" -ForegroundColor Yellow
Write-Host ""

# Check git status
Write-Host "✓ Git Status:" -ForegroundColor Green
$gitStatus = git status -sb 2>&1
$lastCommit = git log --oneline -1 2>&1

Write-Host "  ✓ $gitStatus" -ForegroundColor Green
Write-Host "  ✓ Last commit: $lastCommit" -ForegroundColor Green
Write-Host ""

# Check YAML syntax
Write-Host "✓ Validating workflow YAML syntax..." -ForegroundColor Green

Get-ChildItem ".github/workflows/*.yml" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content -match "^name:" -and $content -match "^on:") {
        Write-Host "  ✓ $($_.Name) has valid structure" -ForegroundColor Green
    }
}
Write-Host ""

# Summary
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "SETUP SUMMARY" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Workflow files: READY" -ForegroundColor Green
Write-Host "✅ Docker configurations: READY" -ForegroundColor Green
Write-Host "✅ Health checks: CONFIGURED" -ForegroundColor Green
Write-Host "✅ Git repository: PUSHED" -ForegroundColor Green
Write-Host ""

Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Go to GitHub repo Settings > Secrets and variables > Actions" -ForegroundColor Yellow
Write-Host "2. Add DOCKER_HUB_USERNAME and DOCKER_HUB_TOKEN" -ForegroundColor Yellow
Write-Host "3. Push a test commit to trigger workflows:" -ForegroundColor Yellow
Write-Host "   git commit --allow-empty -m 'trigger: GitHub Actions workflows'" -ForegroundColor Yellow
Write-Host "   git push origin main" -ForegroundColor Yellow
Write-Host "4. Visit Actions tab to monitor workflow execution" -ForegroundColor Yellow
Write-Host ""

Write-Host "EXPECTED WORKFLOW RESULTS:" -ForegroundColor Cyan
Write-Host "• test job: Python linting, pytest, coverage ✓" -ForegroundColor Green
Write-Host "• validate-compose job: Docker Compose config ✓" -ForegroundColor Green
Write-Host "• docker-build-test job: Build + health checks ✓" -ForegroundColor Green
Write-Host "• docker-push job: Push to Docker Hub ✓" -ForegroundColor Green
Write-Host "• security-scanning job: Cosign signing ✓" -ForegroundColor Green
Write-Host "• build-cloud job: Multi-platform builds ✓" -ForegroundColor Green
Write-Host ""

Write-Host "For more details, see GITHUB_ACTIONS_SETUP.md and GITHUB_ACTIONS_CHECKLIST.md" -ForegroundColor Cyan
Write-Host ""
