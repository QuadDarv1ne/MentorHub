#!/bin/bash
# PostgreSQL Backup Script for MentorHub
# Performs daily backups with retention policy

set -e

# Configuration
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/mentorhub_backup_${TIMESTAMP}.sql.gz"
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-7}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}[$(date)] Starting PostgreSQL backup...${NC}"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Perform backup
if pg_dump -Fc -Z9 | gzip > "${BACKUP_FILE}"; then
    echo -e "${GREEN}[$(date)] Backup completed successfully: ${BACKUP_FILE}${NC}"
    
    # Get backup size
    BACKUP_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo -e "${GREEN}[$(date)] Backup size: ${BACKUP_SIZE}${NC}"
else
    echo -e "${RED}[$(date)] Backup failed!${NC}"
    exit 1
fi

# Remove old backups
echo -e "${YELLOW}[$(date)] Cleaning up old backups (retention: ${RETENTION_DAYS} days)...${NC}"
find "${BACKUP_DIR}" -name "mentorhub_backup_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete

# Count remaining backups
BACKUP_COUNT=$(find "${BACKUP_DIR}" -name "mentorhub_backup_*.sql.gz" -type f | wc -l)
echo -e "${GREEN}[$(date)] Total backups: ${BACKUP_COUNT}${NC}"

# Optional: Upload to S3 (uncomment if needed)
# if [ -n "${AWS_ACCESS_KEY_ID}" ] && [ -n "${AWS_SECRET_ACCESS_KEY}" ]; then
#     echo -e "${YELLOW}[$(date)] Uploading backup to S3...${NC}"
#     aws s3 cp "${BACKUP_FILE}" "s3://${S3_BUCKET}/backups/" --storage-class STANDARD_IA
#     echo -e "${GREEN}[$(date)] Backup uploaded to S3${NC}"
# fi

echo -e "${GREEN}[$(date)] Backup process completed!${NC}"
