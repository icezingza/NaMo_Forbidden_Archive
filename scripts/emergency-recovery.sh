#!/bin/bash
# Emergency Recovery Procedures for NaMo ACC Bot
# Handles system failures, data recovery, and incident response

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-./backups}"
LOG_FILE="/var/log/namo-recovery.log"
ALERT_EMAIL="${ALERT_EMAIL:-admin@example.com}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "${LOG_FILE}"
}

alert() {
    echo "🚨 ALERT: $1" | tee -a "${LOG_FILE}"
    # Send email alert (requires mail configured)
    # echo "$1" | mail -s "NaMo ACC Emergency Alert" "${ALERT_EMAIL}"
}

error() {
    echo -e "${RED}❌ ERROR: $1${NC}" | tee -a "${LOG_FILE}"
    exit 1
}

# =========================
# HEALTH CHECK & DIAGNOSTICS
# =========================

health_check() {
    echo -e "\n${BLUE}🔍 Running Health Check...${NC}\n"
    
    local unhealthy=0
    
    # Check Docker
    if ! docker ps &> /dev/null; then
        echo -e "${RED}❌ Docker daemon not responding${NC}"
        unhealthy=$((unhealthy + 1))
    else
        echo -e "${GREEN}✅ Docker daemon OK${NC}"
    fi
    
    # Check container status
    if ! docker ps | grep -q "namo-acc"; then
        echo -e "${RED}❌ NaMo ACC container not running${NC}"
        unhealthy=$((unhealthy + 1))
    else
        echo -e "${GREEN}✅ NaMo ACC container running${NC}"
    fi
    
    # Check database
    if ! docker exec postgres-container pg_isready &> /dev/null; then
        echo -e "${RED}❌ PostgreSQL not responding${NC}"
        unhealthy=$((unhealthy + 1))
    else
        echo -e "${GREEN}✅ PostgreSQL OK${NC}"
    fi
    
    # Check Redis
    if ! docker exec redis-container redis-cli ping &> /dev/null; then
        echo -e "${RED}❌ Redis not responding${NC}"
        unhealthy=$((unhealthy + 1))
    else
        echo -e "${GREEN}✅ Redis OK${NC}"
    fi
    
    # Check API endpoint
    if ! curl -f http://localhost:8080/health &> /dev/null; then
        echo -e "${RED}❌ API endpoint not responding${NC}"
        unhealthy=$((unhealthy + 1))
    else
        echo -e "${GREEN}✅ API endpoint OK${NC}"
    fi
    
    echo ""
    if [ $unhealthy -eq 0 ]; then
        echo -e "${GREEN}✅ All systems healthy${NC}"
        return 0
    else
        echo -e "${RED}⚠️  $unhealthy system(s) unhealthy${NC}"
        return 1
    fi
}

# =========================
# CONTAINER RECOVERY
# =========================

restart_container() {
    local container=$1
    
    echo -e "\n${YELLOW}🔄 Restarting container: ${container}${NC}"
    
    docker stop "${container}" 2>/dev/null || true
    sleep 2
    docker start "${container}"
    
    sleep 3
    if docker ps | grep -q "${container}"; then
        echo -e "${GREEN}✅ Container restarted successfully${NC}"
        log "Container ${container} restarted"
    else
        error "Failed to restart container ${container}"
    fi
}

restart_all_services() {
    echo -e "\n${YELLOW}🔄 Restarting all services...${NC}"
    
    docker compose down
    sleep 5
    docker compose up -d
    
    sleep 10
    health_check
}

# =========================
# DATABASE RECOVERY
# =========================

restore_database() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        echo -e "${YELLOW}Available backups:${NC}"
        ls -lh "${BACKUP_DIR}"/*.sql.gz | tail -10
        read -p "Enter backup filename: " backup_file
    fi
    
    if [ ! -f "${BACKUP_DIR}/${backup_file}" ]; then
        error "Backup file not found: ${backup_file}"
    fi
    
    echo -e "\n${YELLOW}📥 Restoring database from ${backup_file}...${NC}"
    
    # Stop application
    docker compose down
    
    # Restore database
    gunzip -c "${BACKUP_DIR}/${backup_file}" | docker compose exec -T postgres psql -U cognitive -d namo_sessions
    
    # Restart services
    docker compose up -d
    
    echo -e "${GREEN}✅ Database restored${NC}"
    log "Database restored from ${backup_file}"
}

# =========================
# SESSION RECOVERY
# =========================

recover_sessions() {
    local backup_file=$1
    
    echo -e "\n${YELLOW}📥 Recovering sessions...${NC}"
    
    if [ ! -f "${backup_file}" ]; then
        error "Backup file not found: ${backup_file}"
    fi
    
    # Backup current sessions
    if [ -d "/tmp/sessions" ]; then
        tar -czf "/tmp/sessions_backup_$(date +%s).tar.gz" /tmp/sessions
    fi
    
    # Restore sessions
    rm -rf /tmp/sessions
    tar -xzf "${backup_file}" -C /tmp
    
    echo -e "${GREEN}✅ Sessions recovered${NC}"
    log "Sessions recovered from backup"
}

# =========================
# INCIDENT RESPONSE
# =========================

handle_high_memory() {
    echo -e "\n${RED}🚨 HIGH MEMORY USAGE DETECTED${NC}"
    
    # Get current memory usage
    local mem_usage=$(docker stats namo-acc --no-stream | tail -1 | awk '{print $7}')
    echo "Current memory: $mem_usage"
    
    alert "High memory usage: $mem_usage"
    
    # Restart container
    restart_container "namo-acc"
    
    # Clear Redis cache
    echo -e "${YELLOW}Clearing Redis cache...${NC}"
    docker exec redis-container redis-cli FLUSHALL
    
    log "Memory incident handled"
}

handle_high_cpu() {
    echo -e "\n${RED}🚨 HIGH CPU USAGE DETECTED${NC}"
    
    local cpu_usage=$(docker stats namo-acc --no-stream | tail -1 | awk '{print $3}')
    echo "Current CPU: $cpu_usage"
    
    alert "High CPU usage: $cpu_usage"
    
    # Check logs for errors
    docker logs namo-acc --tail 50
    
    log "CPU incident handled"
}

handle_disk_space() {
    echo -e "\n${RED}🚨 LOW DISK SPACE DETECTED${NC}"
    
    local disk_usage=$(df / | tail -1 | awk '{print $5}')
    echo "Disk usage: $disk_usage"
    
    alert "Low disk space: $disk_usage"
    
    # Clean Docker caches
    echo -e "${YELLOW}Cleaning Docker system...${NC}"
    docker system prune -f
    
    # Archive old logs
    echo -e "${YELLOW}Archiving old logs...${NC}"
    find ./logs -name "*.log" -mtime +30 -exec gzip {} \;
    
    log "Disk space incident handled"
}

# =========================
# ROLLBACK PROCEDURES
# =========================

rollback_to_checkpoint() {
    local checkpoint=$1
    
    echo -e "\n${YELLOW}⏮️  Rolling back to checkpoint: ${checkpoint}${NC}"
    
    if [ ! -d "checkpoints/${checkpoint}" ]; then
        error "Checkpoint not found: ${checkpoint}"
    fi
    
    # Backup current state
    cp -r projects-NaMo-Forbidden-Archive "backup_before_rollback_$(date +%s)"
    
    # Restore checkpoint
    cp -r "checkpoints/${checkpoint}"/* .
    
    # Restart services
    restart_all_services
    
    log "Rolled back to checkpoint: ${checkpoint}"
}

# =========================
# MAIN MENU
# =========================

show_menu() {
    echo -e "\n${BLUE}NaMo ACC Bot - Emergency Recovery Menu${NC}"
    echo "========================================"
    echo "1. Health Check"
    echo "2. Restart All Services"
    echo "3. Restart Specific Container"
    echo "4. Restore Database from Backup"
    echo "5. Recover Sessions"
    echo "6. Handle High Memory"
    echo "7. Handle High CPU"
    echo "8. Handle Low Disk Space"
    echo "9. Rollback to Checkpoint"
    echo "10. View Incident Log"
    echo "0. Exit"
    echo "========================================"
}

main() {
    while true; do
        show_menu
        read -p "Select option [0-10]: " choice
        
        case $choice in
            1) health_check ;;
            2) restart_all_services ;;
            3) 
                read -p "Enter container name: " container
                restart_container "$container"
                ;;
            4) restore_database ;;
            5)
                read -p "Enter backup file path: " backup
                recover_sessions "$backup"
                ;;
            6) handle_high_memory ;;
            7) handle_high_cpu ;;
            8) handle_disk_space ;;
            9)
                read -p "Enter checkpoint name: " cp
                rollback_to_checkpoint "$cp"
                ;;
            10) tail -50 "${LOG_FILE}" ;;
            0) echo "Exiting..."; exit 0 ;;
            *) echo "Invalid option" ;;
        esac
    done
}

# If no argument provided, show menu
if [ $# -eq 0 ]; then
    main
else
    # Otherwise execute specific command
    case $1 in
        health) health_check ;;
        restart) restart_all_services ;;
        restore-db) restore_database "$2" ;;
        recover-sessions) recover_sessions "$2" ;;
        *) echo "Unknown command: $1"; exit 1 ;;
    esac
fi
