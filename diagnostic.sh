#!/bin/bash

echo "╔════════════════════════════════════════╗"
echo "║  NaMo Forbidden Archive - Diagnostic   ║"
echo "║  Status Report                         ║"
echo "╚════════════════════════════════════════╝"
echo ""

PASSED=0
FAILED=0
WARNING=0

# Function to log checks
check() {
  if eval "$1"; then
    echo "✅ $2"
    ((PASSED++))
  else
    echo "❌ $3"
    ((FAILED++))
  fi
}

warn() {
  echo "⚠️ $1"
  ((WARNING++))
}

# Checks
echo "=== ENVIRONMENT ===" && \
check "python --version > /dev/null 2>&1" "Python installed" "Python NOT found" && \
check "pip --version > /dev/null 2>&1" "pip installed" "pip NOT found" && \
check "[ -d 'venv' ]" "Virtual environment exists" "venv NOT found"

echo ""
echo "=== CONFIGURATION ===" && \
check "[ -f '.env' ]" ".env file exists" ".env NOT found" && \
check "grep -q 'OPENAI_API_KEY' .env" "OPENAI_API_KEY configured" "OPENAI_API_KEY NOT set"

echo ""
echo "=== DEPENDENCIES ===" && \
check "python -c 'import fastapi' 2>/dev/null" "FastAPI installed" "FastAPI NOT installed" && \
check "python -c 'import uvicorn' 2>/dev/null" "Uvicorn installed" "Uvicorn NOT installed" && \
check "python -c 'import openai' 2>/dev/null" "OpenAI library installed" "OpenAI library NOT installed"

echo ""
echo "=== FILES ===" && \
check "[ -f 'server.py' ]" "server.py exists" "server.py NOT found" && \
check "[ -f 'memory_service.py' ]" "memory_service.py exists" "memory_service.py NOT found"

echo ""
echo "=== GIT ===" && \
check "git status > /dev/null 2>&1" "Git repository initialized" "Git NOT initialized" && \
[ -f ".gitignore" ] && echo "✅ .gitignore exists" || warn ".gitignore NOT found"

echo ""
echo "╔════════════════════════════════════════╗"
echo "║  SUMMARY                               ║"
echo "║  ✅ Passed: $PASSED                        ║"
echo "║  ❌ Failed: $FAILED                        ║"
echo "║  ⚠️ Warnings: $WARNING                      ║"
echo "╚════════════════════════════════════════╝"

if [ $FAILED -gt 0 ]; then
  exit 1
fi
