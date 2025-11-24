#!/bin/bash
# Database Restore Script
# Восстановление базы данных из резервной копии

set -e

# Configuration
BACKUP_DIR=${BACKUP_DIR:-/backups}
POSTGRES_HOST=${POSTGRES_HOST:-postgres}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_USER=${POSTGRES_USER:-mentorhub}
POSTGRES_DB=${POSTGRES_DB:-mentorhub}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to list available backups
list_backups() {
    echo -e "${YELLOW}Available backups:${NC}"
    echo "================================"
    
    echo -e "\n${GREEN}Daily backups:${NC}"
    ls -lh ${BACKUP_DIR}/daily/backup_*.gz 2>/dev/null || echo "No daily backups found"
    
    echo -e "\n${GREEN}Weekly backups:${NC}"
    ls -lh ${BACKUP_DIR}/weekly/backup_*.gz 2>/dev/null || echo "No weekly backups found"
    
    echo -e "\n${GREEN}Monthly backups:${NC}"
    ls -lh ${BACKUP_DIR}/monthly/backup_*.gz 2>/dev/null || echo "No monthly backups found"
    
    echo "================================"
}

# Function to restore from backup
restore_backup() {
    local backup_file=$1
    
    if [ ! -f "$backup_file" ]; then
        echo -e "${RED}Error: Backup file not found: $backup_file${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Restoring from backup: $backup_file${NC}"
    
    # Confirm restoration
    read -p "This will replace the current database. Are you sure? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Restoration cancelled."
        exit 0
    fi
    
    # Test backup integrity
    echo "Testing backup integrity..."
    if ! gzip -t "$backup_file"; then
        echo -e "${RED}Error: Backup file is corrupted!${NC}"
        exit 1
    fi
    
    # Create a safety backup of current database
    echo "Creating safety backup of current database..."
    SAFETY_BACKUP="${BACKUP_DIR}/pre_restore_$(date +%Y%m%d_%H%M%S).sql"
    PGPASSWORD=${POSTGRES_PASSWORD} pg_dump \
        -h ${POSTGRES_HOST} \
        -p ${POSTGRES_PORT} \
        -U ${POSTGRES_USER} \
        -d ${POSTGRES_DB} \
        -F c \
        -f "${SAFETY_BACKUP}"
    gzip "${SAFETY_BACKUP}"
    echo -e "${GREEN}Safety backup created: ${SAFETY_BACKUP}.gz${NC}"
    
    # Drop existing connections
    echo "Terminating existing connections..."
    PGPASSWORD=${POSTGRES_PASSWORD} psql \
        -h ${POSTGRES_HOST} \
        -p ${POSTGRES_PORT} \
        -U ${POSTGRES_USER} \
        -d postgres \
        -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${POSTGRES_DB}' AND pid <> pg_backend_pid();"
    
    # Drop and recreate database
    echo "Recreating database..."
    PGPASSWORD=${POSTGRES_PASSWORD} psql \
        -h ${POSTGRES_HOST} \
        -p ${POSTGRES_PORT} \
        -U ${POSTGRES_USER} \
        -d postgres \
        -c "DROP DATABASE IF EXISTS ${POSTGRES_DB};"
    
    PGPASSWORD=${POSTGRES_PASSWORD} psql \
        -h ${POSTGRES_HOST} \
        -p ${POSTGRES_PORT} \
        -U ${POSTGRES_USER} \
        -d postgres \
        -c "CREATE DATABASE ${POSTGRES_DB} WITH ENCODING='UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8';"
    
    # Restore from backup
    echo "Restoring database from backup..."
    gunzip -c "$backup_file" | PGPASSWORD=${POSTGRES_PASSWORD} pg_restore \
        -h ${POSTGRES_HOST} \
        -p ${POSTGRES_PORT} \
        -U ${POSTGRES_USER} \
        -d ${POSTGRES_DB} \
        -v \
        --no-owner \
        --no-acl
    
    echo -e "${GREEN}Database restored successfully!${NC}"
    echo -e "${YELLOW}Safety backup saved at: ${SAFETY_BACKUP}.gz${NC}"
}

# Main script
case "${1}" in
    list)
        list_backups
        ;;
    latest)
        restore_backup "${BACKUP_DIR}/latest.sql.gz"
        ;;
    restore)
        if [ -z "$2" ]; then
            echo -e "${RED}Error: Please specify backup file${NC}"
            echo "Usage: $0 restore <backup_file>"
            list_backups
            exit 1
        fi
        restore_backup "$2"
        ;;
    *)
        echo "Usage: $0 {list|latest|restore <backup_file>}"
        echo ""
        echo "Commands:"
        echo "  list              - List all available backups"
        echo "  latest            - Restore from the latest backup"
        echo "  restore <file>    - Restore from specific backup file"
        exit 1
        ;;
esac
