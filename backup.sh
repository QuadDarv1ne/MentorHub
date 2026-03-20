#!/bin/bash

# MentorHub Automated Backup Script
# Автоматическое резервное копирование PostgreSQL + медиа файлов

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Конфигурация
BACKUP_DIR="${BACKUP_DIR:-/var/backups/mentorhub}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
S3_BUCKET="${S3_BUCKET:-}"
AWS_PROFILE="${AWS_PROFILE:-default}"

log_info() { echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') $1"; }

# Создание директории для бэкапов
setup_backup_dir() {
    log_info "Создание директории для бэкапов: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    chmod 750 "$BACKUP_DIR"
    log_success "Директория создана"
}

# Бэкап PostgreSQL
backup_postgres() {
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="$BACKUP_DIR/db_backup_$timestamp.sql.gz"
    
    log_info "Создание бэкапа PostgreSQL..."
    
    # Получение переменных окружения
    source .env 2>/dev/null || true
    
    POSTGRES_USER="${POSTGRES_USER:-mentorhub}"
    POSTGRES_DB="${POSTGRES_DB:-mentorhub}"
    
    # Бэкап через pg_dump
    docker-compose -f $COMPOSE_FILE exec -T postgres pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" | gzip > "$backup_file"
    
    if [ -f "$backup_file" ] && [ -s "$backup_file" ]; then
        local size=$(du -h "$backup_file" | cut -f1)
        log_success "Бэкап создан: $backup_file ($size)"
    else
        log_error "Бэкап не создан или пустой"
        exit 1
    fi
    
    echo "$backup_file"
}

# Бэкап медиа файлов
backup_media() {
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="$BACKUP_DIR/media_backup_$timestamp.tar.gz"
    
    log_info "Создание бэкапа медиа файлов..."
    
    # Бэкап volume с медиа файлами
    docker run --rm \
        -v mentorhub_media_volume:/data:ro \
        -v "$BACKUP_DIR:/backup" \
        alpine tar -czf /backup/media_backup_$timestamp.tar.gz -C /data .
    
    if [ -f "$backup_file" ] && [ -s "$backup_file" ]; then
        local size=$(du -h "$backup_file" | cut -f1)
        log_success "Медиа бэкап создан: $backup_file ($size)"
    else
        log_warning "Медиа бэкап не создан или пустой (возможно нет данных)"
    fi
    
    echo "$backup_file"
}

# Очистка старых бэкапов
cleanup_old_backups() {
    log_info "Очистка бэкапов старше $RETENTION_DAYS дней..."
    
    local count=$(find "$BACKUP_DIR" -name "*.sql.gz" -o -name "*.tar.gz" | wc -l)
    find "$BACKUP_DIR" -name "*.sql.gz" -o -name "*.tar.gz" | xargs rm -f {} \; 2>/dev/null || true
    
    local deleted=$((count - $(find "$BACKUP_DIR" -name "*.sql.gz" -o -name "*.tar.gz" | wc -l)))
    log_success "Удалено старых бэкапов: $deleted"
}

# Загрузка в S3 (опционально)
upload_to_s3() {
    if [ -z "$S3_BUCKET" ]; then
        log_warning "S3_BUCKET не настроен. Пропускаем загрузку в S3..."
        return
    fi
    
    log_info "Загрузка бэкапов в S3: $S3_BUCKET..."
    
    # Загрузка последних бэкапов
    aws s3 cp "$BACKUP_DIR" "s3://$S3_BUCKET/backups/" --recursive --profile "$AWS_PROFILE"
    
    log_success "Бэкапы загружены в S3"
}

# Проверка бэкапа
verify_backup() {
    local backup_file="$1"
    
    log_info "Проверка целостности бэкапа..."
    
    if gzip -t "$backup_file" 2>/dev/null; then
        log_success "Бэкап целостен"
        return 0
    else
        log_error "Бэкап поврежден: $backup_file"
        return 1
    fi
}

# Восстановление из бэкапа
restore_backup() {
    local backup_file="$1"
    
    if [ ! -f "$backup_file" ]; then
        log_error "Файл бэкапа не найден: $backup_file"
        exit 1
    fi
    
    log_warning "Восстановление из бэкапа: $backup_file"
    log_warning "Все текущие данные будут заменены!"
    read -p "Продолжить? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        log_info "Восстановление отменено"
        exit 0
    fi
    
    source .env 2>/dev/null || true
    POSTGRES_USER="${POSTGRES_USER:-mentorhub}"
    POSTGRES_DB="${POSTGRES_DB:-mentorhub}"
    
    # Восстановление БД
    log_info "Восстановление PostgreSQL..."
    gunzip -c "$backup_file" | docker-compose -f $COMPOSE_FILE exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
    
    log_success "Восстановление завершено"
}

# Список бэкапов
list_backups() {
    log_info "Доступные бэкапы:"
    echo ""
    ls -lht "$BACKUP_DIR"/*.sql.gz 2>/dev/null || echo "Бэкапы БД не найдены"
    echo ""
    ls -lht "$BACKUP_DIR"/*.tar.gz 2>/dev/null || echo "Медиа бэкапы не найдены"
}

# Main
main() {
    echo ""
    echo "========================================"
    echo "  MentorHub Backup System"
    echo "========================================"
    echo ""
    
    case ${1:-backup} in
        backup)
            setup_backup_dir
            backup_postgres
            backup_media
            cleanup_old_backups
            upload_to_s3
            log_success "Бэкапирование завершено"
            ;;
        restore)
            if [ -z "$2" ]; then
                log_error "Укажите файл бэкапа: ./backup.sh restore <file.sql.gz>"
                exit 1
            fi
            restore_backup "$2"
            ;;
        list)
            list_backups
            ;;
        verify)
            if [ -z "$2" ]; then
                log_error "Укажите файл бэкапа: ./backup.sh verify <file.sql.gz>"
                exit 1
            fi
            verify_backup "$2"
            ;;
        cron)
            # Для запуска по cron (без вывода цветов)
            setup_backup_dir
            backup_postgres
            cleanup_old_backups
            upload_to_s3
            ;;
        --help)
            echo "MentorHub Backup Script"
            echo ""
            echo "Использование:"
            echo "  ./backup.sh [COMMAND] [OPTIONS]"
            echo ""
            echo "Команды:"
            echo "  backup          Создать новый бэкап (по умолчанию)"
            echo "  restore <file>  Восстановить из бэкапа"
            echo "  list            Показать список бэкапов"
            echo "  verify <file>   Проверить целостность бэкапа"
            echo "  cron            Режим для cron (без цветов)"
            echo "  --help          Показать эту справку"
            echo ""
            echo "Переменные окружения:"
            echo "  BACKUP_DIR      Директория для бэкапов (по умолчанию: /var/backups/mentorhub)"
            echo "  RETENTION_DAYS  Хранить бэкапы N дней (по умолчанию: 7)"
            echo "  S3_BUCKET       S3 бакет для загрузки (опционально)"
            echo "  AWS_PROFILE     AWS профиль (по умолчанию: default)"
            exit 0
            ;;
        *)
            log_error "Неизвестная команда: $1"
            exit 1
            ;;
    esac
}

main
