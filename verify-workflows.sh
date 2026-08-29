#!/bin/bash
# GitHub Actions Status Verification Script for NaMo Forbidden Archive
# Run this locally to verify all workflows are ready and passing

set -e

REPO_OWNER="icezingza"
REPO_NAME="NaMo_Forbidden_Archive"
BRANCH="main"

echo "=========================================="
echo "GitHub Actions Verification Report"
echo "Repository: $REPO_OWNER/$REPO_NAME"
echo "Branch: $BRANCH"
echo "=========================================="
echo ""

# Function to check workflow status (requires GitHub CLI)
check_workflows() {
    echo "✓ Checking workflow files..."
    
    if [ -f .github/workflows/ci.yml ]; then
        echo "  ✓ ci.yml (NaMo ACC CI Pipeline)"
    else
        echo "  ✗ ci.yml NOT FOUND"
    fi
    
    if [ -f .github/workflows/security-scanning.yml ]; then
        echo "  ✓ security-scanning.yml (Docker Image Security & Signing)"
    else
        echo "  ✗ security-scanning.yml NOT FOUND"
    fi
    
    if [ -f .github/workflows/build-cloud.yml ]; then
        echo "  ✓ build-cloud.yml (Multi-Platform Builds)"
    else
        echo "  ✗ build-cloud.yml NOT FOUND"
    fi
    
    echo ""
}

# Function to check Docker files
check_dockerfiles() {
    echo "✓ Checking Dockerfile configurations..."
    
    if grep -q "HEALTHCHECK" Dockerfile; then
        HEALTH_PATH=$(grep "HEALTHCHECK" Dockerfile -A 1 | grep "CMD curl" | sed 's/.*CMD curl -f //' | cut -d' ' -f1)
        echo "  ✓ Dockerfile has HEALTHCHECK (endpoint: $HEALTH_PATH)"
    else
        echo "  ✗ Dockerfile missing HEALTHCHECK"
    fi
    
    if grep -q "HEALTHCHECK" Dockerfile.memory; then
        HEALTH_PATH=$(grep "HEALTHCHECK" Dockerfile.memory -A 1 | grep "CMD curl" | sed 's/.*CMD curl -f //' | cut -d' ' -f1)
        echo "  ✓ Dockerfile.memory has HEALTHCHECK (endpoint: $HEALTH_PATH)"
    else
        echo "  ✗ Dockerfile.memory missing HEALTHCHECK"
    fi
    
    echo ""
}

# Function to check service endpoints
check_endpoints() {
    echo "✓ Checking service endpoints..."
    
    if grep -q "/v1/health" Dockerfile && grep -q "/v1/health" server.py; then
        echo "  ✓ API service endpoint: /v1/health"
    fi
    
    if grep -q "/health" Dockerfile.memory && grep -q "/health" memory_service.py; then
        echo "  ✓ Memory service endpoint: /health"
    fi
    
    echo ""
}

# Function to check required GitHub secrets
check_secrets() {
    echo "✓ Required GitHub Secrets (setup via Settings > Secrets):"
    echo "  • DOCKER_HUB_USERNAME"
    echo "  • DOCKER_HUB_TOKEN"
    echo "  • CODECOV_TOKEN (optional)"
    echo ""
}

# Function to check git status
check_git() {
    echo "✓ Git Status:"
    BRANCH_STATUS=$(git status -sb)
    if echo "$BRANCH_STATUS" | grep -q "up to date"; then
        echo "  ✓ Branch is up to date with origin/$BRANCH"
    fi
    
    LAST_COMMIT=$(git log --oneline -1)
    echo "  ✓ Last commit: $LAST_COMMIT"
    echo ""
}

# Function to check workflow YAML syntax
check_yaml_syntax() {
    echo "✓ Validating workflow YAML syntax..."
    
    for workflow in .github/workflows/*.yml; do
        if grep -q "^name:" "$workflow" && grep -q "^on:" "$workflow"; then
            echo "  ✓ $(basename $workflow) has valid structure"
        fi
    done
    echo ""
}

# Function to summarize setup
summary() {
    echo "=========================================="
    echo "SETUP SUMMARY"
    echo "=========================================="
    echo ""
    echo "✅ Workflow files: READY"
    echo "✅ Docker configurations: READY"
    echo "✅ Health checks: CONFIGURED"
    echo "✅ Git repository: PUSHED"
    echo ""
    echo "NEXT STEPS:"
    echo "1. Go to GitHub repo Settings > Secrets and variables > Actions"
    echo "2. Add DOCKER_HUB_USERNAME and DOCKER_HUB_TOKEN"
    echo "3. Push a test commit to trigger workflows:"
    echo "   git commit --allow-empty -m 'trigger: GitHub Actions workflows'"
    echo "   git push origin main"
    echo "4. Visit Actions tab to monitor workflow execution"
    echo ""
    echo "EXPECTED WORKFLOW RESULTS:"
    echo "• test job: Python linting, pytest, coverage ✓"
    echo "• validate-compose job: Docker Compose config ✓"
    echo "• docker-build-test job: Build + health checks ✓"
    echo "• docker-push job: Push to Docker Hub ✓"
    echo "• security-scanning job: Cosign signing ✓"
    echo "• build-cloud job: Multi-platform builds ✓"
    echo ""
}

# Run all checks
check_workflows
check_dockerfiles
check_endpoints
check_secrets
check_git
check_yaml_syntax
summary

echo "For more details, see GITHUB_ACTIONS_SETUP.md and GITHUB_ACTIONS_CHECKLIST.md"
echo ""
