#!/bin/bash
# =====================================================
# MentorHub - Advanced Backup & Restore System
# Автоматические backups с ротацией, валидацией и сжатием
# =====================================================

set -euo pipefail

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

# Конфигурация
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="${BACKUP_DIR:-$PROJECT_DIR/backups}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"
BACKUP_MAX_COUNT="${BACKUP_MAX_COUNT:-10}"
BACKUP_COMPRESS="${BACKUP_COMPRESS:-true}"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

# =====================================================
# SETUP
# =====================================================

setup_backup_directory() {
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$BACKUP_DIR/database"
    mkdir -p "$BACKUP_DIR/configs"
    mkdir -p "$BACKUP_DIR/archive"
    log_info "Директория backups создана: $BACKUP_DIR"
}

# =====================================================
# LOGGING
# =====================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# =====================================================
# DATABASE BACKUP
# =====================================================

backup_database() {
    """Создает резервную копию базы данных"""
    log_info "Создание резервной копии базы данных..."
    
    local compose_file="${COMPOSE_FILE:-docker-compose.yml}"
    local backup_file="$BACKUP_DIR/database/mentorhub_db_${TIMESTAMP}.sql"
    
    # Проверяем запущен ли PostgreSQL
    if ! docker compose -f "$compose_file" ps postgres 2>/dev/null | grep -q "Up"; then
        log_error "PostgreSQL контейнер не запущен"
        return 1
    fi
    
    # Создаем backup
    log_info "Экспорт базы данных..."
    if docker compose -f "$compose_file" exec -T postgres pg_dumpall \
        -U "${DB_USER:-mentorhub_user}" 2>/dev/null > "$backup_file"; then
        
        log_success "База данных экспортирована: $backup_file"
        
        # Сжатие
        if [ "$BACKUP_COMPRESS" = true ] && command -v gzip &> /dev/null; then
            log_info "Сжатие backup..."
            gzip "$backup_file"
            backup_file="${backup_file}.gz"
            log_success "Backup сжат: $backup_file"
        fi
        
        # Проверка размера
        local backup_size=$(du -h "$backup_file" | awk '{print $1}')
        log_success "Размер backup: $backup_size"
        
        echo "$backup_file"
        return 0
    else
        log_error "Не удалось создать backup базы данных"
        rm -f "$backup_file" 2>/dev/null || true
        return 1
    fi
}

backup_database_direct() {
    """Прямой backup PostgreSQL через pg_dump"""
    log_info "Прямой backup PostgreSQL..."
    
    local backup_file="$BACKUP_DIR/database/mentorhub_db_${TIMESTAMP}.custom"
    
    # Загружаем переменные из .env
    if [ -f "$PROJECT_DIR/.env" ]; then
        export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs 2>/dev/null || true)
    fi
    
    # Определяем хост и порт
    local db_host="${DB_HOST:-localhost}"
    local db_port="${DB_PORT:-5432}"
    local db_user="${DB_USER:-mentorhub_user}"
    local db_name="${DB_NAME:-mentorhub}"
    
    # Проверяем доступность PostgreSQL
    if ! pg_isready -h "$db_host" -p "$db_port" > /dev/null 2>&1; then
        log_error "PostgreSQL не доступен на $db_host:$db_port"
        return 1
    fi
    
    # Создаем backup в custom формате (поддерживает частичное восстановление)
    log_info "Экспорт базы данных: $db_name"
    PGPASSWORD="${DB_PASSWORD}" pg_dump \
        -h "$db_host" \
        -p "$db_port" \
        -U "$db_user" \
        -d "$db_name" \
        -F custom \
        -Z 9 \
        -f "$backup_file" \
        --verbose 2>&1 | tail -n 20
    
    if [ $? -eq 0 ] && [ -f "$backup_file" ]; then
        log_success "Backup создан: $backup_file"
        local backup_size=$(du -h "$backup_file" | awk '{print $1}')
        log_success "Размер: $backup_size"
        echo "$backup_file"
        return 0
    else
        log_error "Не удалось создать backup"
        rm -f "$backup_file" 2>/dev/null || true
        return 1
    fi
}

# =====================================================
# CONFIG BACKUP
# =====================================================

backup_configs() {
    """Создает резервную копию конфигурационных файлов"""
    log_info "Создание резервной копии конфигурации..."
    
    local backup_file="$BACKUP_DIR/configs/mentorhub_config_${TIMESTAMP}.tar.gz"
    
    # Файлы для backup
    local configs_to_backup=(
        ".env"
        ".env.example"
        "docker-compose.yml"
        "docker-compose.dev.yml"
        "docker-compose.prod.yml"
        "nginx.conf"
        "nginx.prod.conf"
        "redis.conf"
    )
    
    local existing_configs=()
    for config in "${configs_to_backup[@]}"; do
        if [ -f "$PROJECT_DIR/$config" ]; then
            existing_configs+=("$config")
        fi
    done
    
    if [ ${#existing_configs[@]} -eq 0 ]; then
        log_warning "Конфигурационные файлы не найдены"
        return 0
    fi
    
    # Создаем архив
    log_info "Архивация ${#existing_configs[@]} конфигурационных файлов..."
    
    cd "$PROJECT_DIR"
    tar -czf "$backup_file" "${existing_configs[@]}"
    
    if [ $? -eq 0 ]; then
        log_success "Конфигурация сохранена: $backup_file"
        local backup_size=$(du -h "$backup_file" | awk '{print $1}')
        log_success "Размер: $backup_size"
        cd - > /dev/null
        echo "$backup_file"
        return 0
    else
        log_error "Не удалось создать архив конфигурации"
        cd - > /dev/null
        return 1
    fi
}

# =====================================================
# VOLUME BACKUP
# =====================================================

backup_volumes() {
    """Создает резервную копию Docker volumes"""
    log_info "Создание резервной копии Docker volumes..."
    
    local volumes=$(docker volume ls -q | grep mentorhub || true)
    
    if [ -z "$volumes" ]; then
        log_warning "Docker volumes не найдены"
        return 0
    fi
    
    for volume in $volumes; do
        log_info "Backup volume: $volume"
        local backup_file="$BACKUP_DIR/mentorhub_volume_${volume}_${TIMESTAMP}.tar.gz"
        
        # Создаем временный контейнер для backup
        docker run --rm \
            -v "$volume":/source:ro \
            -v "$BACKUP_DIR":/backup \
            alpine \
            tar -czf "/backup/$(basename "$backup_file")" -C /source .
        
        if [ $? -eq 0 ]; then
            log_success "Volume $volume сохранен"
        else
            log_error "Не удалось сохранить volume $volume"
        fi
    done
}

# =====================================================
# FULL BACKUP
# =====================================================

full_backup() {
    """Создает полную резервную копию всего проекта"""
    log_info "Создание полной резервной копии..."
    
    local backup_file="$BACKUP_DIR/mentorhub_full_${TIMESTAMP}.tar.gz"
    
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}📦 Создание полного backup MentorHub${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Backup базы данных
    echo -e "${BLUE}[1/4]${NC} Backup базы данных..."
    local db_backup=$(backup_database || backup_database_direct || echo "")
    
    if [ -n "$db_backup" ]; then
        log_success "База данных сохранена"
    else
        log_warning "Backup базы данных не удался"
    fi
    
    # Backup конфигурации
    echo -e "${BLUE}[2/4]${NC} Backup конфигурации..."
    local config_backup=$(backup_configs || echo "")
    
    if [ -n "$config_backup" ]; then
        log_success "Конфигурация сохранена"
    else
        log_warning "Backup конфигурации не удался"
    fi
    
    # Backup volumes
    echo -e "${BLUE}[3/4]${NC} Backup Docker volumes..."
    backup_volumes
    
    # Полный архив проекта
    echo -e "${BLUE}[4/4]${NC} Создание полного архива проекта..."
    log_info "Архивация файлов проекта..."
    
    cd "$PROJECT_DIR"
    tar -czf "$backup_file" \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        --exclude='.next' \
        --exclude='venv' \
        --exclude='.venv' \
        --exclude='*.pyc' \
        --exclude='.DS_Store' \
        --exclude='logs' \
        --exclude='backups' \
        .
    
    if [ $? -eq 0 ]; then
        log_success "Полный архив создан: $backup_file"
        local backup_size=$(du -h "$backup_file" | awk '{print $1}')
        log_success "Размер: $backup_size"
    else
        log_error "Не удалось создать полный архив"
    fi
    
    cd - > /dev/null
    
    echo ""
    echo -e "${GREEN}✅ Полный backup завершен!${NC}"
    echo -e "${BLUE}Файлы backup:${NC}"
    [ -n "$db_backup" ] && echo "  - Database: $db_backup"
    [ -n "$config_backup" ] && echo "  - Configs: $config_backup"
    [ -f "$backup_file" ] && echo "  - Full: $backup_file"
}

# =====================================================
# RESTORE
# =====================================================

restore_database() {
    """Восстанавливает базу данных из backup"""
    local backup_file="${1:-}"
    
    if [ -z "$backup_file" ]; then
        log_error "Укажите файл backup"
        log_info "Использование: $0 restore-database <backup_file>"
        return 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "Файл backup не найден: $backup_file"
        return 1
    fi
    
    log_info "Восстановление базы данных из: $backup_file"
    
    # Определяем тип backup
    local file_ext="${backup_file##*.}"
    
    if [[ "$file_ext" == "gz" ]]; then
        # Сжатый SQL файл
        log_info "Восстановление из сжатого SQL backup..."
        
        local compose_file="${COMPOSE_FILE:-docker-compose.yml}"
        
        # Распаковка и восстановление
        if gunzip -c "$backup_file" | docker compose -f "$compose_file" exec -T \
            postgres psql -U "${DB_USER:-mentorhub_user}" -d "${DB_NAME:-mentorhub}"; then
            log_success "База данных восстановлена"
            return 0
        else
            log_error "Не удалось восстановить базу данных"
            return 1
        fi
        
    elif [[ "$file_ext" == "sql" ]]; then
        # SQL файл
        log_info "Восстановление из SQL backup..."
        
        local compose_file="${COMPOSE_FILE:-docker-compose.yml}"
        
        if docker compose -f "$compose_file" exec -T \
            postgres psql -U "${DB_USER:-mentorhub_user}" -d "${DB_NAME:-mentorhub}" < "$backup_file"; then
            log_success "База данных восстановлена"
            return 0
        else
            log_error "Не удалось восстановить базу данных"
            return 1
        fi
        
    elif [[ "$file_ext" == "custom" ]]; then
        # Custom формат PostgreSQL
        log_info "Восстановление из custom format backup..."
        
        # Загружаем переменные
        if [ -f "$PROJECT_DIR/.env" ]; then
            export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs 2>/dev/null || true)
        fi
        
        local db_host="${DB_HOST:-localhost}"
        local db_port="${DB_PORT:-5432}"
        local db_user="${DB_USER:-mentorhub_user}"
        local db_name="${DB_NAME:-mentorhub}"
        
        # Восстановление через pg_restore
        PGPASSWORD="${DB_PASSWORD}" pg_restore \
            -h "$db_host" \
            -p "$db_port" \
            -U "$db_user" \
            -d "$db_name" \
            --clean \
            --if-exists \
            "$backup_file"
        
        if [ $? -eq 0 ]; then
            log_success "База данных восстановлена"
            return 0
        else
            log_error "Не удалось восстановить базу данных"
            return 1
        fi
    else
        log_error "Неизвестный формат backup: $file_ext"
        return 1
    fi
}

restore_configs() {
    """Восстанавливает конфигурацию из backup"""
    local backup_file="${1:-}"
    
    if [ -z "$backup_file" ]; then
        log_error "Укажите файл backup конфигурации"
        return 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "Файл backup не найден: $backup_file"
        return 1
    fi
    
    log_info "Восстановление конфигурации из: $backup_file"
    
    # Распаковка
    tar -xzf "$backup_file" -C "$PROJECT_DIR"
    
    if [ $? -eq 0 ]; then
        log_success "Конфигурация восстановлена"
        log_warning "Перезапустите сервисы для применения новой конфигурации"
        return 0
    else
        log_error "Не удалось восстановить конфигурацию"
        return 1
    fi
}

# =====================================================
# ROTATION & CLEANUP
# =====================================================

rotate_backups() {
    """Ротация backup файлов"""
    log_info "Ротация backup файлов..."
    
    # По времени
    if [ -n "$BACKUP_RETENTION_DAYS" ]; then
        log_info "Удаление backup старше $BACKUP_RETENTION_DAYS дней..."
        
        local deleted=0
        
        # Database backups
        if [ -d "$BACKUP_DIR/database" ]; then
            local old_backups=$(find "$BACKUP_DIR/database" -type f -mtime +$BACKUP_RETENTION_DAYS 2>/dev/null | wc -l || echo "0")
            if [ "$old_backups" -gt 0 ]; then
                find "$BACKUP_DIR/database" -type f -mtime +$BACKUP_RETENTION_DAYS -delete
                log_success "Удалено старых database backups: $old_backups"
                deleted=$((deleted + old_backups))
            fi
        fi
        
        # Config backups
        if [ -d "$BACKUP_DIR/configs" ]; then
            local old_backups=$(find "$BACKUP_DIR/configs" -type f -mtime +$BACKUP_RETENTION_DAYS 2>/dev/null | wc -l || echo "0")
            if [ "$old_backups" -gt 0 ]; then
                find "$BACKUP_DIR/configs" -type f -mtime +$BACKUP_RETENTION_DAYS -delete
                log_success "Удалено старых config backups: $old_backups"
                deleted=$((deleted + old_backups))
            fi
        fi
        
        log_info "Всего удалено: $deleted файлов"
    fi
    
    # По количеству
    if [ -n "$BACKUP_MAX_COUNT" ]; then
        log_info "Ограничение максимального количества backup: $BACKUP_MAX_COUNT"
        
        for dir in "$BACKUP_DIR/database" "$BACKUP_DIR/configs"; do
            if [ -d "$dir" ]; then
                local file_count=$(ls -1 "$dir"/* 2>/dev/null | wc -l || echo "0")
                
                if [ "$file_count" -gt "$BACKUP_MAX_COUNT" ]; then
                    local to_delete=$((file_count - BACKUP_MAX_COUNT))
                    ls -1t "$dir"/* 2>/dev/null | tail -n "$to_delete" | xargs rm -f
                    log_success "Удалено лишних backup из $dir: $to_delete"
                fi
            fi
        done
    fi
}

list_backups() {
    """Показывает список всех backup"""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   💾 Список backup файлов                                  ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Database backups
    echo -e "${BLUE}📦 Database Backups:${NC}"
    if [ -d "$BACKUP_DIR/database" ]; then
        ls -lhS "$BACKUP_DIR/database"/* 2>/dev/null | while read line; do
            echo "  $line"
        done || echo "  Нет backup файлов"
    else
        echo "  Директория не найдена"
    fi
    echo ""
    
    # Config backups
    echo -e "${BLUE}⚙️  Config Backups:${NC}"
    if [ -d "$BACKUP_DIR/configs" ]; then
        ls -lhS "$BACKUP_DIR/configs"/* 2>/dev/null | while read line; do
            echo "  $line"
        done || echo "  Нет backup файлов"
    else
        echo "  Директория не найдена"
    fi
    echo ""
    
    # Объем всех backup
    local total_size=$(du -sh "$BACKUP_DIR" 2>/dev/null | awk '{print $1}' || echo "0")
    echo -e "${BLUE}📊 Общий размер backup:${NC} $total_size"
    echo ""
}

# =====================================================
# VALIDATION
# =====================================================

validate_backup() {
    """Проверяет целостность backup файла"""
    local backup_file="${1:-}"
    
    if [ -z "$backup_file" ]; then
        log_error "Укажите файл backup"
        return 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "Файл backup не найден: $backup_file"
        return 1
    fi
    
    log_info "Проверка целостности backup: $backup_file"
    
    local file_ext="${backup_file##*.}"
    
    case "$file_ext" in
        gz)
            if gzip -t "$backup_file" 2>/dev/null; then
                log_success "Backup файл целостен"
                
                local file_size=$(du -h "$backup_file" | awk '{print $1}')
                log_info "Размер: $file_size"
                
                return 0
            else
                log_error "Backup файл поврежден"
                return 1
            fi
            ;;
        sql)
            if [ -s "$backup_file" ]; then
                local lines=$(wc -l < "$backup_file")
                log_success "SQL backup валиден ($lines строк)"
                return 0
            else
                log_error "SQL backup пуст или не существует"
                return 1
            fi
            ;;
        custom)
            if command -v pg_restore &> /dev/null; then
                if pg_restore --list "$backup_file" > /dev/null 2>&1; then
                    log_success "Custom format backup валиден"
                    return 0
                else
                    log_error "Custom format backup поврежден"
                    return 1
                fi
            else
                log_warning "pg_restore не установлен, пропускаем проверку"
                return 0
            fi
            ;;
        tar)
            if tar -tzf "$backup_file" > /dev/null 2>&1; then
                log_success "Tar архив валиден"
                local file_count=$(tar -tzf "$backup_file" | wc -l)
                log_info "Файлов в архиве: $file_count"
                return 0
            else
                log_error "Tar архив поврежден"
                return 1
            fi
            ;;
        *)
            log_warning "Неизвестный формат файла: $file_ext"
            return 0
            ;;
    esac
}

# =====================================================
# SCHEDULED BACKUP (для cron)
# =====================================================

scheduled_backup() {
    """Автоматический backup для cron"""
    log_info "Запуск автоматического backup..."
    
    setup_backup_directory
    
    # Создаем backup
    local db_backup=$(backup_database 2>/dev/null || backup_database_direct 2>/dev/null || echo "")
    local config_backup=$(backup_configs 2>/dev/null || echo "")
    
    # Ротация
    rotate_backups
    
    if [ -n "$db_backup" ] || [ -n "$config_backup" ]; then
        log_success "Автоматический backup завершен"
        exit 0
    else
        log_error "Автоматический backup не удался"
        exit 1
    fi
}

# =====================================================
# HELP
# =====================================================

show_help() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   💾 MentorHub Backup & Restore System                     ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Использование:${NC}"
    echo "  $0 [ACTION] [OPTIONS]"
    echo ""
    echo -e "${BLUE}Действия:${NC}"
    echo "  backup-db              Создать backup базы данных"
    echo "  backup-configs         Создать backup конфигурации"
    echo "  backup-full            Создать полный backup всего"
    echo "  restore-db <file>      Восстановить базу данных"
    echo "  restore-configs <file> Восстановить конфигурацию"
    echo "  list                   Показать список всех backup"
    echo "  validate <file>        Проверить целостность backup"
    echo "  rotate                 Ротация старых backup файлов"
    echo "  scheduled              Автоматический backup (для cron)"
    echo "  help                   Показать эту справку"
    echo ""
    echo -e "${BLUE}Переменные окружения:${NC}"
    echo "  BACKUP_DIR               Директория для backup (по умолчанию: ./backups)"
    echo "  BACKUP_RETENTION_DAYS    Дней хранения backup (по умолчанию: 7)"
    echo "  BACKUP_MAX_COUNT         Макс. количество backup (по умолчанию: 10)"
    echo "  COMPOSE_FILE             Docker Compose файл"
    echo ""
    echo -e "${BLUE}Примеры:${NC}"
    echo "  $0 backup-db                     # Backup только БД"
    echo "  $0 backup-full                   # Полный backup"
    echo "  $0 restore-db backups/database/mentorhub_db_20260404_120000.sql.gz"
    echo "  $0 validate backups/database/mentorhub_db_20260404_120000.sql.gz"
    echo ""
    echo -e "${BLUE}Cron настройка (каждый день в 2:00 AM):${NC}"
    echo "  0 2 * * * cd /path/to/MentorHub && bash scripts/backup.sh scheduled"
    echo ""
}

# =====================================================
# MAIN
# =====================================================

main() {
    setup_backup_directory
    
    local action="${1:-help}"
    shift || true
    
    case "$action" in
        backup-db)
            backup_database || backup_database_direct
            ;;
        backup-configs)
            backup_configs
            ;;
        backup-full)
            full_backup
            ;;
        restore-db)
            restore_database "${1:-}"
            ;;
        restore-configs)
            restore_configs "${1:-}"
            ;;
        list)
            list_backups
            ;;
        validate)
            validate_backup "${1:-}"
            ;;
        rotate)
            rotate_backups
            ;;
        scheduled)
            scheduled_backup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Неизвестное действие: $action"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
