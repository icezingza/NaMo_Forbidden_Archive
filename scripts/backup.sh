#!/bin/bash
# Backup & Restore Script for NaMo ACC Bot
# Backs up databases, sessions, and configs for disaster recovery

set -e

BACKUP_DIR="${BACKUP_DIR:-./ backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="${POSTGRES_DB:-namo_sessions}"
DB_USER="${POSTGRES_USER:-cognitive}"
DB_HOST="${POSTGRES_HOST:-localhost}"
BACKUP_LOG="${BACKUP_DIR}/backup.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Logging function
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" >> "${BACKUP_LOG}"
    echo -e "${GREEN}✅${NC} $1"
}

error() {
    echo -e "${RED}❌ ERROR: $1${NC}" | tee -a "${BACKUP_LOG}"
    exit 1
}

# Function: Backup PostgreSQL
backup_postgres() {
    echo -e "\n${YELLOW}📦 Backing up PostgreSQL...${NC}"
    
    local pg_backup="${BACKUP_DIR}/postgres_${TIMESTAMP}.sql.gz"
    
    if ! pg_dump -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" \
        | gzip > "${pg_backup}"; then
        error "Failed to backup PostgreSQL"
    fi
    
    log "PostgreSQL backed up: $(du -h "${pg_backup}" | cut -f1)"
}

# Function: Backup Redis
backup_redis() {
    echo -e "\n${YELLOW}📦 Backing up Redis...${NC}"
    
    local redis_backup="${BACKUP_DIR}/redis_${TIMESTAMP}.rdb"
    
    if [ -f "/redis_backup/dump.rdb" ]; then
        cp /redis_backup/dump.rdb "${redis_backup}"
        log "Redis backed up: $(du -h "${redis_backup}" | cut -f1)"
    else
        log "Redis backup file not found (skipping)"
    fi
}

# Function: Backup Sessions
backup_sessions() {
    echo -e "\n${YELLOW}📦 Backing up session files...${NC}"
    
    local sessions_backup="${BACKUP_DIR}/sessions_${TIMESTAMP}.tar.gz"
    
    if [ -d "/tmp/sessions" ]; then
        tar -czf "${sessions_backup}" -C /tmp sessions
        log "Sessions backed up: $(du -h "${sessions_backup}" | cut -f1)"
    else
        log "Sessions directory not found (skipping)"
    fi
}

# Function: Backup Application Config
backup_config() {
    echo -e "\n${YELLOW}📦 Backing up configuration...${NC}"
    
    local config_backup="${BACKUP_DIR}/config_${TIMESTAMP}.tar.gz"
    
    tar -czf "${config_backup}" \
        --exclude=.git \
        --exclude=node_modules \
        --exclude=.env \
        .secrets/
    
    log "Configuration backed up: $(du -h "${config_backup}" | cut -f1)"
}

# Function: Restore PostgreSQL
restore_postgres() {
    local backup_file=$1
    
    if [ ! -f "${backup_file}" ]; then
        error "Backup file not found: ${backup_file}"
    fi
    
    echo -e "\n${YELLOW}📥 Restoring PostgreSQL from ${backup_file}...${NC}"
    
    if gunzip -c "${backup_file}" | psql -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}"; then
        log "PostgreSQL restored successfully"
    else
        error "Failed to restore PostgreSQL"
    fi
}

# Function: Restore Redis
restore_redis() {
    local backup_file=$1
    
    if [ ! -f "${backup_file}" ]; then
        error "Backup file not found: ${backup_file}"
    fi
    
    echo -e "\n${YELLOW}📥 Restoring Redis from ${backup_file}...${NC}"
    
    if cp "${backup_file}" /redis_backup/dump.rdb; then
        log "Redis restored successfully"
    else
        error "Failed to restore Redis"
    fi
}

# Function: Restore Sessions
restore_sessions() {
    local backup_file=$1
    
    if [ ! -f "${backup_file}" ]; then
        error "Backup file not found: ${backup_file}"
    fi
    
    echo -e "\n${YELLOW}📥 Restoring sessions from ${backup_file}...${NC}"
    
    rm -rf /tmp/sessions
    if tar -xzf "${backup_file}" -C /tmp; then
        log "Sessions restored successfully"
    else
        error "Failed to restore sessions"
    fi
}

# Function: Full backup
full_backup() {
    echo -e "\n${GREEN}🔄 Starting full system backup...${NC}"
    
    backup_postgres
    backup_redis
    backup_sessions
    backup_config
    
    # Cleanup old backups (keep last 7 days)
    find "${BACKUP_DIR}" -name "*.sql.gz" -mtime +7 -delete
    find "${BACKUP_DIR}" -name "*.rdb" -mtime +7 -delete
    find "${BACKUP_DIR}" -name "*.tar.gz" -mtime +7 -delete
    
    log "Full backup completed successfully"
    ls -lh "${BACKUP_DIR}"/* | tail -5
}

# Function: Show available backups
list_backups() {
    echo -e "\n${YELLOW}📋 Available backups:${NC}\n"
    ls -lhS "${BACKUP_DIR}"/ | grep -v total
}

# Main script
case "${1:-backup}" in
    backup)
        full_backup
        ;;
    restore)
        if [ -z "$2" ]; then
            echo -e "${YELLOW}Usage: $0 restore <backup_type> <backup_file>${NC}"
            echo "Types: postgres, redis, sessions"
            list_backups
            exit 1
        fi
        
        case "$2" in
            postgres) restore_postgres "$3" ;;
            redis) restore_redis "$3" ;;
            sessions) restore_sessions "$3" ;;
            *) error "Unknown restore type: $2" ;;
        esac
        ;;
    list)
        list_backups
        ;;
    *)
        echo -e "${YELLOW}Usage: $0 {backup|restore|list}${NC}"
        exit 1
        ;;
esac
