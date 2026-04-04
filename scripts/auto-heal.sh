#!/bin/bash
# =====================================================
# MentorHub - Auto-Heal Script
# Автоматическое восстановление упавших сервисов
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
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/auto-heal.log"
RESTART_TRACKER="$LOG_DIR/restarts.json"
MAX_RESTARTS=${MAX_RESTARTS:-5}
RESTART_WINDOW=${RESTART_WINDOW:-300}  # 5 минут
CHECK_INTERVAL=${CHECK_INTERVAL:-30}  # 30 секунд

# Compose файл
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"

# =====================================================
# ЛОГИРОВАНИЕ
# =====================================================

setup_logging() {
    mkdir -p "$LOG_DIR"
    exec > >(tee -a "$LOG_FILE") 2>&1
}

log_info() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] ${BLUE}[INFO]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1" >> "$LOG_FILE"
}

log_success() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] ${GREEN}[SUCCESS]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] $1" >> "$LOG_FILE"
}

log_warning() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] ${YELLOW}[WARNING]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARNING] $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] ${RED}[ERROR]${NC} $1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1" >> "$LOG_FILE"
}

# =====================================================
# RESTART TRACKER
# =====================================================

init_restart_tracker() {
    if [ ! -f "$RESTART_TRACKER" ]; then
        echo '{"restarts": []}' > "$RESTART_TRACKER"
        log_info "Инициализирован трекер перезапусков: $RESTART_TRACKER"
    fi
}

get_recent_restarts() {
    local container_name=$1
    
    if command -v python3 &> /dev/null; then
        python3 -c "
import json
from datetime import datetime, timedelta

try:
    with open('$RESTART_TRACKER') as f:
        data = json.load(f)
    
    cutoff = datetime.now() - timedelta(seconds=$RESTART_WINDOW)
    data['restarts'] = [r for r in data['restarts'] if datetime.fromisoformat(r['time']) > cutoff]
    
    container_restarts = [r for r in data['restarts'] if r['container'] == '$container_name']
    print(len(container_restarts))
    
    with open('$RESTART_TRACKER', 'w') as f:
        json.dump(data, f)
except Exception as e:
    print(0)
" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

record_restart() {
    local container_name=$1
    
    if command -v python3 &> /dev/null; then
        python3 -c "
import json
from datetime import datetime

try:
    with open('$RESTART_TRACKER') as f:
        data = json.load(f)
    
    data['restarts'].append({
        'container': '$container_name',
        'time': datetime.now().isoformat(),
        'action': 'auto_restart'
    })
    
    with open('$RESTART_TRACKER', 'w') as f:
        json.dump(data, f, indent=2)
except Exception as e:
    print(f'Ошибка записи перезапуска: {e}')
" 2>/dev/null || true
    fi
}

# =====================================================
# HEALTH CHECK
# =====================================================

check_container_health() {
    local container=$1
    local container_name=$(docker inspect --format='{{.Name}}' "$container" 2>/dev/null | sed 's|/||')
    local status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "unknown")
    local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "no-healthcheck")
    local restart_count=$(docker inspect --format='{{.RestartCount}}' "$container" 2>/dev/null || echo "0")
    
    # Логирование статуса
    if [[ "$status" == "running" ]]; then
        if [[ "$health" == "healthy" ]]; then
            log_success "$container_name: running, healthy (restarts: $restart_count)"
        elif [[ "$health" == "unhealthy" ]]; then
            log_warning "$container_name: running, but UNHEALTHY (restarts: $restart_count)"
            return 1
        elif [[ "$health" == "starting" ]]; then
            log_info "$container_name: running, starting..."
        else
            log_info "$container_name: running ($health)"
        fi
        return 0
    elif [[ "$status" == "exited" ]] || [[ "$status" == "dead" ]]; then
        local exit_code=$(docker inspect --format='{{.State.ExitCode}}' "$container" 2>/dev/null || echo "unknown")
        log_error "$container_name: $status (exit code: $exit_code, restarts: $restart_count)"
        return 1
    else
        log_warning "$container_name: $status"
        return 1
    fi
}

# =====================================================
# AUTO-HEAL
# =====================================================

heal_container() {
    local container=$1
    local container_name=$(docker inspect --format='{{.Name}}' "$container" 2>/dev/null | sed 's|/||')
    
    log_warning "Попытка восстановления: $container_name"
    
    # Проверяем количество недавних перезапусков
    local recent_restarts=$(get_recent_restarts "$container_name")
    
    if [ "$recent_restarts" -ge "$MAX_RESTARTS" ]; then
        log_error "$container_name превысил лимит перезапусков ($recent_restarts/$MAX_RESTARTS за последние $RESTART_WINDOW секунд)"
        log_error "Требуется ручное вмешательство!"
        
        # Отправляем алерт
        send_alert "CRITICAL: $container_name exceeded restart limit ($recent_restarts/$MAX_RESTARTS)"
        
        # Показываем последние логи контейнера
        log_info "Последние логи контейнера $container_name:"
        docker logs --tail 20 "$container" 2>&1 | while read line; do
            log_info "  $line"
        done
        
        return 1
    fi
    
    # Пытаемся перезапустить контейнер
    log_info "Перезапуск контейнера $container_name (попытка $((recent_restarts + 1))/$MAX_RESTARTS)..."
    
    if docker restart "$container" 2>/dev/null; then
        record_restart "$container_name"
        log_success "Контейнер $container_name перезапущен"
        
        # Ждем и проверяем статус
        sleep 10
        if check_container_health "$container" > /dev/null 2>&1; then
            log_success "$container_name успешно восстановлен"
            send_alert "RECOVERED: $container_name restarted successfully"
            return 0
        else
            log_warning "$container_name все еще имеет проблемы после перезапуска"
            return 1
        fi
    else
        log_error "Не удалось перезапустить контейнер $container_name"
        send_alert "ERROR: Failed to restart $container_name"
        return 1
    fi
}

# =====================================================
# NOTIFICATIONS
# =====================================================

send_alert() {
    local message="$1"
    
    log_warning "ALERT: $message"
    
    # Загружаем .env если существует
    local env_file="$PROJECT_DIR/.env"
    if [ -f "$env_file" ]; then
        export $(grep -v '^#' "$env_file" | xargs 2>/dev/null || true)
    fi
    
    # Telegram уведомление
    if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
        if [[ "$TELEGRAM_BOT_TOKEN" != "your-"* ]] && [[ -n "$TELEGRAM_BOT_TOKEN" ]]; then
            curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
                -d "chat_id=${TELEGRAM_CHAT_ID}" \
                -d "text=🚨 <b>MentorHub Auto-Heal Alert</b>%0A%0A${message}%0A%0A📅 $(date '+%Y-%m-%d %H:%M:%S')" \
                -d "parse_mode=HTML" > /dev/null 2>&1
            
            if [ $? -eq 0 ]; then
                log_info "Telegram уведомление отправлено"
            fi
        fi
    fi
    
    # Email уведомление (если настроен SMTP)
    if [ -n "${SMTP_USER:-}" ] && [ -n "${SMTP_FROM_EMAIL:-}" ]; then
        if command -v mail &> /dev/null; then
            echo "$message" | mail -s "MentorHub Alert: $(date '+%Y-%m-%d %H:%M:%S')" "${SMTP_USER:-}" 2>/dev/null || true
        fi
    fi
}

# =====================================================
# MAIN LOOP
# =====================================================

show_status() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   🔧 MentorHub Auto-Heal Monitor                           ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Конфигурация:${NC}"
    echo "  Compose файл:     $COMPOSE_FILE"
    echo "  Интервал проверки: ${CHECK_INTERVAL} секунд"
    echo "  Макс. перезапусков: $MAX_RESTARTS за $RESTART_WINDOW секунд"
    echo "  Лог файл:         $LOG_FILE"
    echo "  Трекер:           $RESTART_TRACKER"
    echo ""
}

monitor_loop() {
    log_info "Запуск цикла мониторинга (Ctrl+C для остановки)..."
    
    local iteration=0
    
    while true; do
        iteration=$((iteration + 1))
        log_info "=== Проверка #$iteration ($(date '+%H:%M:%S')) ==="
        
        # Получаем все контейнеры
        local containers=$(docker compose -f "$COMPOSE_FILE" ps -q 2>/dev/null || docker-compose -f "$COMPOSE_FILE" ps -q 2>/dev/null || true)
        
        if [ -z "$containers" ]; then
            log_warning "Нет запущенных контейнеров"
            sleep "$CHECK_INTERVAL"
            continue
        fi
        
        local issues=0
        
        for container in $containers; do
            if ! check_container_health "$container"; then
                issues=$((issues + 1))
                heal_container "$container" || true
            fi
        done
        
        if [ $issues -eq 0 ]; then
            log_success "Все сервисы работают нормально"
        else
            log_warning "Обнаружено проблем: $issues"
        fi
        
        # Ждем следующую проверку
        log_info "Следующая проверка через $CHECK_INTERVAL секунд..."
        sleep "$CHECK_INTERVAL"
    done
}

# =====================================================
# SINGLE CHECK (для cron)
# =====================================================

single_check() {
    log_info "Одиночная проверка здоровья..."
    
    local containers=$(docker compose -f "$COMPOSE_FILE" ps -q 2>/dev/null || docker-compose -f "$COMPOSE_FILE" ps -q 2>/dev/null || true)
    
    if [ -z "$containers" ]; then
        log_warning "Нет запущенных контейнеров"
        exit 1
    fi
    
    local issues=0
    
    for container in $containers; do
        if ! check_container_health "$container"; then
            issues=$((issues + 1))
            heal_container "$container" || true
        fi
    done
    
    if [ $issues -eq 0 ]; then
        log_success "Все сервисы работают нормально"
        exit 0
    else
        log_warning "Обнаружено проблем: $issues"
        exit 1
    fi
}

# =====================================================
# HELP
# =====================================================

show_help() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   🔧 MentorHub Auto-Heal Script                            ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Использование:${NC}"
    echo "  $0 [MODE] [OPTIONS]"
    echo ""
    echo -e "${BLUE}Режимы:${NC}"
    echo "  monitor            Непрерывный мониторинг (по умолчанию)"
    echo "  check              Одиночная проверка (для cron)"
    echo "  status             Показать статус"
    echo "  help               Показать эту справку"
    echo ""
    echo -e "${BLUE}Опции окружения:${NC}"
    echo "  COMPOSE_FILE       Путь к docker-compose файлу"
    echo "  MAX_RESTARTS       Макс. количество перезапусков (по умолчанию: 5)"
    echo "  RESTART_WINDOW     Окно времени в секундах (по умолчанию: 300)"
    echo "  CHECK_INTERVAL     Интервал проверки в секундах (по умолчанию: 30)"
    echo ""
    echo -e "${BLUE}Примеры:${NC}"
    echo "  $0 monitor                        # Непрерывный мониторинг"
    echo "  $0 check                          # Одиночная проверка"
    echo "  MAX_RESTARTS=3 $0 monitor         # Макс. 3 перезапуска"
    echo ""
    echo -e "${BLUE}Cron настройка (каждые 5 минут):${NC}"
    echo "  */5 * * * * cd /path/to/MentorHub && COMPOSE_FILE=docker-compose.yml bash scripts/auto-heal.sh check"
    echo ""
}

# =====================================================
# MAIN
# =====================================================

main() {
    setup_logging
    init_restart_tracker
    
    local mode="${1:-monitor}"
    
    case "$mode" in
        monitor)
            show_status
            monitor_loop
            ;;
        check)
            single_check
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Неизвестный режим: $mode"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
