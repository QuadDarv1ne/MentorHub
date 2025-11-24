#!/bin/bash
# PostgreSQL Backup Script with Rotation
# Создает резервные копии базы данных с автоматической ротацией

set -e

# Configuration
BACKUP_DIR=${BACKUP_DIR:-/backups}
POSTGRES_HOST=${POSTGRES_HOST:-postgres}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_USER=${POSTGRES_USER:-mentorhub}
POSTGRES_DB=${POSTGRES_DB:-mentorhub}
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_KEEP_DAYS=${BACKUP_KEEP_DAYS:-7}
BACKUP_KEEP_WEEKS=${BACKUP_KEEP_WEEKS:-4}
BACKUP_KEEP_MONTHS=${BACKUP_KEEP_MONTHS:-6}

# Create backup directories
mkdir -p ${BACKUP_DIR}/{daily,weekly,monthly}

# Function to perform backup
perform_backup() {
    local backup_type=$1
    local backup_path=$2
    
    echo "Starting ${backup_type} backup..."
    
    # Create compressed backup
    PGPASSWORD=${POSTGRES_PASSWORD} pg_dump \
        -h ${POSTGRES_HOST} \
        -p ${POSTGRES_PORT} \
        -U ${POSTGRES_USER} \
        -d ${POSTGRES_DB} \
        -F c \
        -b \
        -v \
        -f "${backup_path}"
    
    # Compress with gzip
    gzip -f "${backup_path}"
    
    echo "${backup_type} backup completed: ${backup_path}.gz"
}

# Function to cleanup old backups
cleanup_backups() {
    local dir=$1
    local keep_count=$2
    
    echo "Cleaning up old backups in ${dir}..."
    
    # Keep only the specified number of most recent backups
    ls -t ${dir}/backup_*.gz 2>/dev/null | tail -n +$((keep_count + 1)) | xargs -r rm -f
    
    echo "Cleanup completed for ${dir}"
}

# Determine backup type based on day of week and month
DAY_OF_WEEK=$(date +%u)  # 1-7 (Monday-Sunday)
DAY_OF_MONTH=$(date +%d)

if [ "$DAY_OF_MONTH" -eq 1 ]; then
    # Monthly backup on the 1st of each month
    BACKUP_PATH="${BACKUP_DIR}/monthly/backup_${DATE}.sql"
    perform_backup "monthly" "$BACKUP_PATH"
    cleanup_backups "${BACKUP_DIR}/monthly" $BACKUP_KEEP_MONTHS
elif [ "$DAY_OF_WEEK" -eq 7 ]; then
    # Weekly backup on Sunday
    BACKUP_PATH="${BACKUP_DIR}/weekly/backup_${DATE}.sql"
    perform_backup "weekly" "$BACKUP_PATH"
    cleanup_backups "${BACKUP_DIR}/weekly" $BACKUP_KEEP_WEEKS
else
    # Daily backup
    BACKUP_PATH="${BACKUP_DIR}/daily/backup_${DATE}.sql"
    perform_backup "daily" "$BACKUP_PATH"
    cleanup_backups "${BACKUP_DIR}/daily" $BACKUP_KEEP_DAYS
fi

# Create a symlink to the latest backup
ln -sf "${BACKUP_PATH}.gz" "${BACKUP_DIR}/latest.sql.gz"

# Display backup info
echo "================================"
echo "Backup Information:"
echo "Date: ${DATE}"
echo "Database: ${POSTGRES_DB}"
echo "Backup file: ${BACKUP_PATH}.gz"
echo "Size: $(du -h ${BACKUP_PATH}.gz | cut -f1)"
echo "================================"

# Test backup integrity
echo "Testing backup integrity..."
if gzip -t "${BACKUP_PATH}.gz"; then
    echo "✓ Backup integrity check passed"
else
    echo "✗ Backup integrity check failed!"
    exit 1
fi

# Send notification (optional - implement webhook or email)
# curl -X POST https://your-webhook-url.com/notify \
#   -H "Content-Type: application/json" \
#   -d "{\"message\": \"Database backup completed: ${BACKUP_PATH}.gz\"}"

echo "Backup process completed successfully!"
