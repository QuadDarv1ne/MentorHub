#!/bin/bash
# PostgreSQL Restore Script for MentorHub
# Restores database from backup file

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backup file is provided
if [ -z "$1" ]; then
    echo -e "${RED}Usage: $0 <backup_file>${NC}"
    echo -e "${YELLOW}Available backups:${NC}"
    ls -lh /backups/mentorhub_backup_*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "${BACKUP_FILE}" ]; then
    echo -e "${RED}Error: Backup file not found: ${BACKUP_FILE}${NC}"
    exit 1
fi

echo -e "${YELLOW}[$(date)] WARNING: This will replace the current database!${NC}"
echo -e "${YELLOW}[$(date)] Backup file: ${BACKUP_FILE}${NC}"
read -p "Are you sure you want to continue? (yes/no): " CONFIRM

if [ "${CONFIRM}" != "yes" ]; then
    echo -e "${RED}[$(date)] Restore cancelled${NC}"
    exit 0
fi

echo -e "${GREEN}[$(date)] Starting database restore...${NC}"

# Drop existing connections
echo -e "${YELLOW}[$(date)] Terminating existing connections...${NC}"
psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '${PGDATABASE}' AND pid <> pg_backend_pid();" || true

# Drop and recreate database
echo -e "${YELLOW}[$(date)] Recreating database...${NC}"
dropdb --if-exists "${PGDATABASE}"
createdb "${PGDATABASE}"

# Restore backup
echo -e "${GREEN}[$(date)] Restoring from backup...${NC}"
if gunzip -c "${BACKUP_FILE}" | pg_restore -d "${PGDATABASE}" --no-owner --no-acl; then
    echo -e "${GREEN}[$(date)] Database restored successfully!${NC}"
else
    echo -e "${RED}[$(date)] Restore failed!${NC}"
    exit 1
fi

# Run migrations (optional)
# echo -e "${YELLOW}[$(date)] Running migrations...${NC}"
# alembic upgrade head

echo -e "${GREEN}[$(date)] Restore process completed!${NC}"
