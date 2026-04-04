#!/bin/bash
# =====================================================
# MentorHub - Main Orchestrator Script
# Автоматический выбор режима работы, предпроверки, мониторинг
# Platforms: Linux, macOS, WSL, Git Bash (Windows)
# =====================================================

set -euo pipefail

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Глобальные переменные
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
LOG_DIR="$SCRIPT_DIR/logs"
LOG_FILE="$LOG_DIR/orchestrator.log"
MAX_RESTARTS=5
RESTART_WINDOW=300  # 5 минут
MODE="${MODE:-auto}"  # auto, dev, prod, docker-dev, docker-prod
ACTION="${1:-start}"  # start, stop, restart, status, logs, setup, backup, restore

# =====================================================
# ЛОГИРОВАНИЕ
# =====================================================

setup_logging() {
    mkdir -p "$LOG_DIR"
    exec > >(tee -a "$LOG_FILE") 2>&1
}

log_info() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] ${BLUE}[INFO]${NC} $1"
    echo -e "$msg"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1" >> "$LOG_FILE"
}

log_success() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] ${GREEN}[SUCCESS]${NC} $1"
    echo -e "$msg"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] $1" >> "$LOG_FILE"
}

log_warning() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] ${YELLOW}[WARNING]${NC} $1"
    echo -e "$msg"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARNING] $1" >> "$LOG_FILE"
}

log_error() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] ${RED}[ERROR]${NC} $1"
    echo -e "$msg"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1" >> "$LOG_FILE"
}

# =====================================================
# ПРЕДПРОВЕРКИ (PRE-FLIGHT CHECKS)
# =====================================================

preflight_checks() {
    log_info "Запуск предпроверок..."
    
    # Проверка Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker не установлен. Установите Docker 20+"
        return 1
    fi
    
    local docker_version=$(docker --version | grep -oP '\d+\.\d+\.\d+' | head -1)
    log_success "Docker: $docker_version"
    
    # Проверка Docker Compose
    if ! docker compose version &> /dev/null; then
        if ! command -v docker-compose &> /dev/null; then
            log_error "Docker Compose не установлен. Установите Docker Compose 2.0+"
            return 1
        fi
    fi
    
    local compose_version=$(docker compose version 2>/dev/null | grep -oP '\d+\.\d+\.\d+' || docker-compose --version | grep -oP '\d+\.\d+\.\d+')
    log_success "Docker Compose: $compose_version"
    
    # Проверка .env файла
    if [ ! -f "$ENV_FILE" ]; then
        log_warning ".env файл не найден"
        if [ -f "$SCRIPT_DIR/.env.example" ]; then
            log_info "Запуск автоматической генерации конфигурации..."
            if command -v python3 &> /dev/null; then
                python3 "$SCRIPT_DIR/scripts/generate_env.py"
            else
                bash "$SCRIPT_DIR/scripts/auto-ports.sh"
            fi
            
            if [ ! -f "$ENV_FILE" ]; then
                log_error "Не удалось создать .env файл"
                return 1
            fi
        else
            log_error ".env.example не найден"
            return 1
        fi
    fi
    
    # Валидация .env
    if ! bash "$SCRIPT_DIR/scripts/validate_env.sh" 2>/dev/null; then
        log_warning "Валидация .env завершилась с предупреждениями"
    fi
    
    # Проверка доступности портов
    if ! bash "$SCRIPT_DIR/scripts/validate-ports.sh" 2>/dev/null; then
        log_warning "Некоторые порты заняты. Рекомендуется запустить ports-auto"
    fi
    
    # Проверка ресурсов
    check_system_resources
    
    log_success "Предпроверки завершены"
    return 0
}

check_system_resources() {
    log_info "Проверка системных ресурсов..."
    
    # Проверка свободного места на диске
    if command -v df &> /dev/null; then
        local available_space=$(df -m "$SCRIPT_DIR" | awk 'NR==2 {print $4}')
        if [ "$available_space" -lt 5000 ]; then
            log_warning "Свободно меньше 5GB на диске: ${available_space}MB"
        else
            log_success "Достаточно места на диске: ${available_space}MB"
        fi
    fi
    
    # Проверка оперативной памяти
    if command -v free &> /dev/null; then
        local total_mem=$(free -m | awk 'NR==2 {print $2}')
        if [ "$total_mem" -lt 2048 ]; then
            log_warning "Мало оперативной памяти: ${total_mem}MB (рекомендуется 4GB+)"
        else
            log_success "Достаточно оперативной памяти: ${total_mem}MB"
        fi
    elif command -v sysctl &> /dev/null; then
        local total_mem=$(sysctl -n hw.memsize 2>/dev/null | awk '{print $1/1024/1024}' || echo "unknown")
        log_info "Оперативная память: ${total_mem}MB"
    fi
    
    # Проверка CPU
    if command -v nproc &> /dev/null; then
        local cpu_cores=$(nproc)
        log_success "CPU ядер: $cpu_cores"
    elif command -v sysctl &> /dev/null; then
        local cpu_cores=$(sysctl -n hw.ncpu 2>/dev/null || echo "unknown")
        log_info "CPU ядер: $cpu_cores"
    fi
}

# =====================================================
# ОПРЕДЕЛЕНИЕ РЕЖИМА РАБОТЫ
# =====================================================

detect_mode() {
    if [ "$MODE" != "auto" ]; then
        log_info "Режим работы установлен вручную: $MODE"
        return
    fi
    
    # Автоопределение окружения
    local env_from_file=""
    if [ -f "$ENV_FILE" ]; then
        env_from_file=$(grep "^ENVIRONMENT=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2 || echo "")
    fi
    
    if [ -n "$env_from_file" ]; then
        MODE="$env_from_file"
        log_info "Автоопределение режима из .env: $MODE"
        return
    fi
    
    # Проверка на CI/CD
    if [ -n "${CI:-}" ] || [ -n "${GITHUB_ACTIONS:-}" ] || [ -n "${RENDER:-}" ]; then
        MODE="production"
        log_info "Обнаружена CI/CD среда. Режим: production"
        return
    fi
    
    # Проверка Docker окружения
    if [ -f "/.dockerenv" ] || grep -q docker /proc/1/cgroup 2>/dev/null; then
        MODE="docker"
        log_info "Запуск внутри Docker контейнера"
        return
    fi
    
    # По умолчанию development
    MODE="development"
    log_info "Режим по умолчанию: development"
}

get_compose_file() {
    case "$MODE" in
        production|prod)
            echo "docker-compose.prod.yml"
            ;;
        development|dev)
            echo "docker-compose.dev.yml"
            ;;
        docker-dev)
            echo "docker-compose.dev.yml"
            ;;
        docker-prod)
            echo "docker-compose.prod.yml"
            ;;
        *)
            echo "docker-compose.yml"
            ;;
    esac
}

# =====================================================
# УПРАВЛЕНИЕ КОНТЕЙНЕРАМИ
# =====================================================

start_services() {
    local compose_file=$(get_compose_file)
    
    log_info "Запуск сервисов в режиме: $MODE"
    log_info "Docker Compose файл: $compose_file"
    
    # Проверка и генерация nginx конфигурации
    if [[ "$compose_file" == *"prod"* ]]; then
        if [ -f "$SCRIPT_DIR/nginx/nginx.conf.template" ]; then
            log_info "Генерация nginx.conf из template..."
            bash "$SCRIPT_DIR/scripts/generate-nginx-conf.sh" || log_warning "Не удалось сгенерировать nginx.conf"
        fi
    fi
    
    # Запуск сервисов
    log_info "Запуск Docker контейнеров..."
    docker compose -f "$compose_file" up -d --remove-orphans
    
    # Ожидание запуска
    log_info "Ожидание запуска сервисов..."
    sleep 10
    
    # Проверка здоровья сервисов
    check_services_health
}

check_services_health() {
    log_info "Проверка здоровья сервисов..."
    
    local compose_file=$(get_compose_file)
    local all_healthy=true
    
    # Получаем список сервисов
    local services=$(docker compose -f "$compose_file" config --services 2>/dev/null || docker-compose -f "$compose_file" config --services 2>/dev/null)
    
    for service in $services; do
        local status=$(docker inspect --format='{{.State.Health.Status}}' "mentorhub-${service}" 2>/dev/null || echo "no-healthcheck")
        
        if [ "$status" = "healthy" ]; then
            log_success "Сервис $service: healthy"
        elif [ "$status" = "starting" ]; then
            log_warning "Сервис $service: starting (ожидание)"
        elif [ "$status" = "unhealthy" ]; then
            log_error "Сервис $service: unhealthy"
            all_healthy=false
        else
            log_info "Сервис $service: $status (no healthcheck)"
        fi
    done
    
    if [ "$all_healthy" = true ]; then
        log_success "Все сервисы работают нормально"
        show_status
        return 0
    else
        log_warning "Некоторые сервисы могут работать некорректно"
        log_info "Для просмотра логов: make logs или docker-compose logs -f"
        return 1
    fi
}

stop_services() {
    local compose_file=$(get_compose_file)
    
    log_info "Остановка сервисов..."
    docker compose -f "$compose_file" down --remove-orphans
    log_success "Сервисы остановлены"
}

restart_services() {
    log_info "Перезапуск сервисов..."
    stop_services
    sleep 5
    start_services
}

# =====================================================
# СТАТУС И МОНИТОРИНГ
# =====================================================

show_status() {
    local compose_file=$(get_compose_file)
    
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║        📊 MentorHub - Статус сервисов                      ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Информация об окружении
    echo -e "${BLUE}Режим работы:${NC} $MODE"
    echo -e "${BLUE}Compose файл:${NC} $compose_file"
    
    if [ -f "$ENV_FILE" ]; then
        local backend_port=$(grep "^BACKEND_PORT=" "$ENV_FILE" | cut -d'=' -f2 || echo "8000")
        local frontend_port=$(grep "^FRONTEND_PORT=" "$ENV_FILE" | cut -d'=' -f2 || echo "3000")
        
        echo -e "${BLUE}Backend URL:${NC} http://localhost:$backend_port"
        echo -e "${BLUE}Frontend URL:${NC} http://localhost:$frontend_port"
        echo -e "${BLUE}API Docs:${NC} http://localhost:$backend_port/docs"
    fi
    
    echo ""
    echo -e "${BLUE}Состояние контейнеров:${NC}"
    docker compose -f "$compose_file" ps 2>/dev/null || docker-compose -f "$compose_file" ps
    
    echo ""
    echo -e "${BLUE}Использование ресурсов:${NC}"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" \
        $(docker compose -f "$compose_file" ps -q 2>/dev/null) 2>/dev/null || echo "Не удалось получить статистику"
    
    echo ""
}

show_logs() {
    local compose_file=$(get_compose_file)
    local service="${2:-}"
    
    if [ -n "$service" ]; then
        log_info "Просмотр логов сервиса: $service"
        docker compose -f "$compose_file" logs -f --tail=100 "$service"
    else
        log_info "Просмотр логов всех сервисов..."
        docker compose -f "$compose_file" logs -f --tail=100
    fi
}

# =====================================================
# AUTO-HEAL (АВТОВОССТАНОВЛЕНИЕ)
# =====================================================

setup_autoheal() {
    log_info "Настройка системы автовосстановления..."
    
    # Создание файла отслеживания перезапусков
    mkdir -p "$LOG_DIR"
    local restart_tracker="$LOG_DIR/restarts.json"
    
    if [ ! -f "$restart_tracker" ]; then
        echo '{"restarts": []}' > "$restart_tracker"
    fi
    
    log_success "Система автовосстановления настроена"
}

monitor_and_heal() {
    log_info "Запуск мониторинга и автовосстановления (Ctrl+C для остановки)..."
    
    local compose_file=$(get_compose_file)
    local restart_tracker="$LOG_DIR/restarts.json"
    
    while true; do
        # Получаем все контейнеры
        local containers=$(docker compose -f "$compose_file" ps -q 2>/dev/null || true)
        
        for container in $containers; do
            local container_name=$(docker inspect --format='{{.Name}}' "$container" 2>/dev/null | sed 's|/||')
            local status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "unknown")
            local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no-healthcheck")
            
            # Проверка на crashed или exited статус
            if [[ "$status" == "exited" ]] || [[ "$status" == "dead" ]]; then
                log_warning "Контейнер $container_name в статусе: $status"
                
                # Проверка на количество перезапусков
                local recent_restarts=$(python3 -c "
import json
from datetime import datetime, timedelta

with open('$restart_tracker') as f:
    data = json.load(f)

# Удаляем старые записи (старше $RESTART_WINDOW секунд)
cutoff = datetime.now() - timedelta(seconds=$RESTART_WINDOW)
data['restarts'] = [r for r in data['restarts'] if datetime.fromisoformat(r['time']) > cutoff]

# Считаем перезапуски для этого контейнера
container_restarts = [r for r in data['restarts'] if r['container'] == '$container_name']
print(len(container_restarts))

# Сохраняем обновленные данные
with open('$restart_tracker', 'w') as f:
    json.dump(data, f)
" 2>/dev/null || echo "0")
                
                if [ "$recent_restarts" -ge "$MAX_RESTARTS" ]; then
                    log_error "Контейнер $container_name превысил лимит перезапусков ($recent_restarts/$MAX_RESTARTS)"
                    log_error "Требуется ручное вмешательство"
                    send_alert "CRITICAL: Container $container_name exceeded restart limit"
                else
                    log_info "Попытка восстановления контейнера $container_name..."
                    docker restart "$container" 2>/dev/null || true
                    
                    # Записываем перезапуск
                    python3 -c "
import json
from datetime import datetime

with open('$restart_tracker') as f:
    data = json.load(f)

data['restarts'].append({
    'container': '$container_name',
    'time': datetime.now().isoformat()
})

with open('$restart_tracker', 'w') as f:
    json.dump(data, f)
" 2>/dev/null || true
                    
                    log_success "Контейнер $container_name перезапущен"
                fi
            elif [[ "$health" == "unhealthy" ]]; then
                log_warning "Контейнер $container_name unhealthy"
                # Можно добавить дополнительную логику для unhealthy контейнеров
            fi
        done
        
        sleep 30  # Проверка каждые 30 секунд
    done
}

# =====================================================
# УВЕДОМЛЕНИЯ
# =====================================================

send_alert() {
    local message="$1"
    
    log_warning "ALERT: $message"
    
    # Отправка Telegram уведомления если настроено
    if [ -f "$ENV_FILE" ]; then
        local telegram_token=$(grep "^TELEGRAM_BOT_TOKEN=" "$ENV_FILE" | cut -d'=' -f2 || echo "")
        local telegram_chat=$(grep "^TELEGRAM_CHAT_ID=" "$ENV_FILE" | cut -d'=' -f2 || echo "")
        
        if [ -n "$telegram_token" ] && [ -n "$telegram_chat" ] && [[ "$telegram_token" != "your-"* ]]; then
            curl -s -X POST "https://api.telegram.org/bot${telegram_token}/sendMessage" \
                -d "chat_id=${telegram_chat}" \
                -d "text=🚨 MentorHub Alert: ${message}" \
                -d "parse_mode=HTML" > /dev/null 2>&1
            
            log_info "Telegram уведомление отправлено"
        fi
    fi
}

# =====================================================
# BACKUP & RESTORE
# =====================================================

create_backup() {
    log_info "Создание резервной копии базы данных..."
    
    if [ -f "$SCRIPT_DIR/scripts/backup.sh" ]; then
        bash "$SCRIPT_DIR/scripts/backup.sh"
        log_success "Резервная копия создана"
    else
        log_error "Скрипт backup.sh не найден"
        return 1
    fi
}

restore_backup() {
    local backup_file="${2:-}"
    
    if [ -z "$backup_file" ]; then
        log_error "Укажите файл резервной копии"
        log_info "Использование: $0 restore <backup_file>"
        return 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "Файл резервной копии не найден: $backup_file"
        return 1
    fi
    
    log_info "Восстановление из резервной копии: $backup_file"
    
    if [ -f "$SCRIPT_DIR/scripts/restore.sh" ]; then
        bash "$SCRIPT_DIR/scripts/restore.sh" "$backup_file"
        log_success "Резервная копия восстановлена"
    else
        log_error "Скрипт restore.sh не найден"
        return 1
    fi
}

# =====================================================
# SETUP
# =====================================================

initial_setup() {
    log_info "Первоначальная настройка MentorHub..."
    
    # Проверка зависимостей
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 не установлен. Установите Python 3.10+"
        return 1
    fi
    
    # Генерация конфигурации
    if command -v python3 &> /dev/null && [ -f "$SCRIPT_DIR/scripts/generate_env.py" ]; then
        python3 "$SCRIPT_DIR/scripts/generate_env.py"
    else
        bash "$SCRIPT_DIR/scripts/auto-ports.sh"
    fi
    
    # Создание директорий
    mkdir -p "$LOG_DIR"
    mkdir -p "$SCRIPT_DIR/backups"
    
    log_success "Первоначальная настройка завершена"
    log_info "Отредактируйте .env файл при необходимости"
    log_info "Затем запустите: $0 start"
}

# =====================================================
# HELP
# =====================================================

show_help() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║        🚀 MentorHub Orchestrator                           ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Использование:${NC}"
    echo "  $0 [ACTION] [OPTIONS]"
    echo ""
    echo -e "${BLUE}Действия:${NC}"
    echo "  start              Запустить все сервисы (по умолчанию)"
    echo "  stop               Остановить все сервисы"
    echo "  restart            Перезапустить все сервисы"
    echo "  status             Показать статус сервисов"
    echo "  logs [service]     Показать логи (опционально конкретный сервис)"
    echo "  monitor            Запустить мониторинг и авто-восстановление"
    echo "  setup              Первоначальная настройка"
    echo "  backup             Создать резервную копию БД"
    echo "  restore <file>     Восстановить из резервной копии"
    echo "  help               Показать эту справку"
    echo ""
    echo -e "${BLUE}Опции:${NC}"
    echo "  --mode=MODE        Установить режим (development, production, docker-dev, docker-prod)"
    echo "  --env=FILE         Указать путь к .env файлу"
    echo ""
    echo -e "${BLUE}Примеры:${NC}"
    echo "  $0 start                    # Запуск в авто-режиме"
    echo "  $0 start --mode=production  # Запуск в production режиме"
    echo "  $0 status                   # Проверка статуса"
    echo "  $0 logs backend             # Логи backend сервиса"
    echo "  $0 monitor                  # Запуск мониторинга"
    echo "  $0 backup                   # Создание backup"
    echo ""
}

# =====================================================
# ПАРСИНГ АРГУМЕНТОВ
# =====================================================

parse_args() {
    for arg in "$@"; do
        case $arg in
            --mode=*)
                MODE="${arg#*=}"
                shift
                ;;
            --env=*)
                ENV_FILE="${arg#*=}"
                shift
                ;;
            *)
                # Уже обработано в ACTION
                ;;
        esac
    done
}

# =====================================================
# MAIN
# =====================================================

main() {
    setup_logging
    parse_args "$@"
    
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║        🚀 MentorHub Orchestrator v2.0                      ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    case "$ACTION" in
        start)
            detect_mode
            if preflight_checks; then
                start_services
                setup_autoheal
                log_success "MentorHub успешно запущен!"
            else
                log_error "Предпроверки не пройдены. Исправьте ошибки и попробуйте снова."
                exit 1
            fi
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs "$@"
            ;;
        monitor)
            detect_mode
            monitor_and_heal
            ;;
        setup)
            initial_setup
            ;;
        backup)
            create_backup
            ;;
        restore)
            restore_backup "$@"
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Неизвестное действие: $ACTION"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
