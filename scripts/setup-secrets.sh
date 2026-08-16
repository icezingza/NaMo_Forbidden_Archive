#!/bin/bash
# Setup secrets management for NaMo ACC Bot
# Creates encrypted secrets for production deployment

set -e

echo "🔐 NaMo ACC Bot - Secrets Management Setup"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Config
SECRETS_DIR=".secrets"
SECRETS_FILE="${SECRETS_DIR}/.env.production"
SECRETS_ENCRYPTED="${SECRETS_DIR}/.env.production.enc"

# Create secrets directory
mkdir -p "${SECRETS_DIR}"
chmod 700 "${SECRETS_DIR}"

# Function to prompt and store secret
store_secret() {
    local key=$1
    local prompt=$2
    local default=$3
    
    read -sp "${prompt} [default: ${default}]: " value
    echo
    if [ -z "$value" ]; then
        value="$default"
    fi
    echo "${key}=${value}" >> "${SECRETS_FILE}"
}

# Remove existing secrets file
rm -f "${SECRETS_FILE}"

echo -e "\n${YELLOW}Enter your secrets:${NC}\n"

# Core Secrets
store_secret "TELEGRAM_BOT_TOKEN" "Telegram Bot Token (from @BotFather)" "[REQUIRED]"
store_secret "GEMINI_API_KEY" "Google Gemini API Key" "[REQUIRED]"

# Database Secrets
store_secret "POSTGRES_PASSWORD" "PostgreSQL Password" "cognitive_secure_pass_$(date +%s)"
store_secret "REDIS_PASSWORD" "Redis Password" "redis_secure_pass_$(date +%s)"
store_secret "NEO4J_PASSWORD" "Neo4j Password" "neo4j_secure_pass_$(date +%s)"

# Backup & Recovery
store_secret "BACKUP_ENCRYPTION_KEY" "Backup Encryption Key" "$(openssl rand -base64 32)"
store_secret "S3_ACCESS_KEY" "AWS S3 Access Key (optional)" ""
store_secret "S3_SECRET_KEY" "AWS S3 Secret Key (optional)" ""

# Application Settings
store_secret "GRAFANA_PASSWORD" "Grafana Admin Password" "grafana_admin_$(date +%s | cut -c5-)"
store_secret "JWT_SECRET" "JWT Secret for API Auth" "$(openssl rand -base64 32)"

# Security
store_secret "SENTRY_DSN" "Sentry DSN for error tracking (optional)" ""
store_secret "WEBHOOK_SECRET" "Webhook Secret for validation" "$(openssl rand -base64 32)"

# Set permissions
chmod 600 "${SECRETS_FILE}"

echo -e "\n${GREEN}✅ Secrets saved to: ${SECRETS_FILE}${NC}"
echo -e "${YELLOW}⚠️  IMPORTANT: Add to .gitignore (don't commit!)${NC}\n"

# Encrypt secrets (optional)
if command -v gpg &> /dev/null; then
    read -p "Encrypt secrets with GPG? (y/n) [n]: " encrypt_choice
    if [ "$encrypt_choice" = "y" ]; then
        gpg --symmetric --cipher-algo AES256 "${SECRETS_FILE}" -o "${SECRETS_ENCRYPTED}"
        echo -e "${GREEN}✅ Secrets encrypted to: ${SECRETS_ENCRYPTED}${NC}"
        echo -e "${YELLOW}Store the passphrase securely!${NC}"
    fi
fi

# Create .env.example
echo -e "\n📝 Creating .env.example...\n"
cat > "${SECRETS_DIR}/.env.example" << 'EOF'
# =========================
# REQUIRED SECRETS
# =========================
TELEGRAM_BOT_TOKEN=your_token_here
GEMINI_API_KEY=your_key_here

# =========================
# DATABASE PASSWORDS
# =========================
POSTGRES_PASSWORD=secure_password_here
REDIS_PASSWORD=secure_password_here
NEO4J_PASSWORD=secure_password_here

# =========================
# BACKUP & RECOVERY
# =========================
BACKUP_ENCRYPTION_KEY=encryption_key_here
S3_ACCESS_KEY=
S3_SECRET_KEY=

# =========================
# APPLICATION
# =========================
GRAFANA_PASSWORD=admin_password_here
JWT_SECRET=jwt_secret_here

# =========================
# MONITORING & SECURITY
# =========================
SENTRY_DSN=
WEBHOOK_SECRET=webhook_secret_here

# =========================
# SETTINGS
# =========================
DEBUG=false
LOG_DIR=./logs
USE_GCS=false
GCS_BUCKET_NAME=
BACKUP_INTERVAL=86400
EOF

echo -e "${GREEN}✅ Created .env.example${NC}\n"

# Print security recommendations
echo -e "${YELLOW}📋 SECURITY RECOMMENDATIONS:${NC}"
echo "1. Add .secrets/ to .gitignore"
echo "2. Use GitHub Secrets for CI/CD"
echo "3. Rotate secrets regularly"
echo "4. Use a secrets manager (AWS Secrets Manager, HashiCorp Vault)"
echo "5. Enable audit logging for secret access"
echo "6. Backup secrets securely"
echo ""

# Create .gitignore entry
if ! grep -q "\.secrets/" .gitignore 2>/dev/null; then
    echo ".secrets/" >> .gitignore
    echo -e "${GREEN}✅ Added .secrets/ to .gitignore${NC}"
fi

echo -e "${GREEN}🎉 Secrets setup complete!${NC}\n"
