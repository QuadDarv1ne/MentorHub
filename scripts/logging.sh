#!/bin/bash
# =====================================================
# MentorHub - Advanced Logging and Monitoring System
# Система логирования с ротацией, фильтрацией и мониторингом
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

# Конфигурация
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="${LOG_DIR:-$PROJECT_DIR/logs}"
LOG_MAX_SIZE="${LOG_MAX_SIZE:-100M}"  # Максимальный размер лог файла
LOG_MAX_FILES="${LOG_MAX_FILES:-10}"  # Максимальное количество файлов ротации
LOG_LEVEL="${LOG_LEVEL:-INFO}"  # Уровень логирования

# =====================================================
# LOGGING FUNCTIONS
# =====================================================

setup_log_directory() {
    mkdir -p "$LOG_DIR"
    mkdir -p "$LOG_DIR/archive"
    mkdir -p "$LOG_DIR/metrics"
}

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local color=""
    
    case "$level" in
        DEBUG) color="$MAGENTA" ;;
        INFO) color="$BLUE" ;;
        SUCCESS) color="$GREEN" ;;
        WARNING) color="$YELLOW" ;;
        ERROR) color="$RED" ;;
        CRITICAL) color="$RED" ;;
        *) color="$NC" ;;
    esac
    
    # Вывод в консоль с цветами
    echo -e "${color}[$timestamp] [$level]${NC} $message"
    
    # Запись в лог файл (без цветов)
    echo "[$timestamp] [$level] $message" >> "$LOG_DIR/orchestrator.log"
}

log_debug() {
    if [[ "$LOG_LEVEL" == "DEBUG" ]]; then
        log "DEBUG" "$@"
    fi
}

log_info() {
    log "INFO" "$@"
}

log_success() {
    log "SUCCESS" "$@"
}

log_warning() {
    log "WARNING" "$@"
}

log_error() {
    log "ERROR" "$@"
}

log_critical() {
    log "CRITICAL" "$@"
}

# =====================================================
# LOG ROTATION
# =====================================================

rotate_logs() {
    """Ротация лог файлов"""
    log_info "Запуск ротации лог файлов..."
    
    local log_files=("$LOG_DIR"/*.log)
    
    for log_file in "${log_files[@]}"; do
        if [ ! -f "$log_file" ]; then
            continue
        fi
        
        local file_size=$(stat -f%z "$log_file" 2>/dev/null || stat -c%s "$log_file" 2>/dev/null || echo "0")
        local max_size_bytes=$(echo "$LOG_MAX_SIZE" | sed 's/M/*1024*1024/' | sed 's/G/*1024*1024*1024/' | bc 2>/dev/null || echo "104857600")
        
        if [ "$file_size" -gt "$max_size_bytes" ]; then
            log_info "Ротация файла: $(basename "$log_file") ($file_size bytes)"
            
            # Сжимаем и перемещаем в архив
            local base_name=$(basename "$log_file" .log)
            local timestamp=$(date '+%Y%m%d_%H%M%S')
            local archive_file="$LOG_DIR/archive/${base_name}_${timestamp}.log"
            
            mv "$log_file" "$archive_file"
            
            # Сжатие
            if command -v gzip &> /dev/null; then
                gzip "$archive_file"
                log_success "Сжат: ${archive_file}.gz"
            fi
            
            # Создаем новый пустой лог файл
            touch "$log_file"
            log_success "Создан новый лог файл: $(basename "$log_file")"
        fi
    done
    
    # Удаляем старые архивы
    clean_old_archives
}

clean_old_archives() {
    """Удаляет старые архивные логи"""
    log_info "Очистка старых архивов (старше $LOG_MAX_FILES файлов)..."
    
    local archive_count=$(ls -1 "$LOG_DIR/archive/"*.log.gz 2>/dev/null | wc -l || echo "0")
    
    if [ "$archive_count" -gt "$LOG_MAX_FILES" ]; then
        local to_delete=$((archive_count - LOG_MAX_FILES))
        ls -1t "$LOG_DIR/archive/"*.log.gz 2>/dev/null | tail -n "$to_delete" | xargs rm -f
        log_success "Удалено старых архивов: $to_delete"
    fi
}

# =====================================================
# LOG VIEWER
# =====================================================

view_logs() {
    """Просмотр логов с фильтрацией"""
    local service="${1:-}"
    local level="${2:-}"
    local lines="${3:-100}"
    local follow="${4:-false}"
    
    local log_file="$LOG_DIR/orchestrator.log"
    
    if [ -n "$service" ]; then
        log_file="$LOG_DIR/${service}.log"
    fi
    
    if [ ! -f "$log_file" ]; then
        log_error "Лог файл не найден: $log_file"
        return 1
    fi
    
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   📄 Просмотр логов: $(basename "$log_file")${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    if [ -n "$level" ]; then
        echo -e "${BLUE}Фильтр по уровню:${NC} $level"
    fi
    echo -e "${BLUE}Количество строк:${NC} $lines"
    echo ""
    
    if [ "$follow" = true ]; then
        # Режим реального времени
        if [ -n "$level" ]; then
            tail -f "$log_file" | grep --color=always "\[$level\]"
        else
            tail -f "$log_file"
        fi
    else
        # Статический просмотр
        if [ -n "$level" ]; then
            tail -n "$lines" "$log_file" | grep --color=always "\[$level\]"
        else
            tail -n "$lines" "$log_file"
        fi
    fi
}

search_logs() {
    """Поиск в логах"""
    local pattern="$1"
    local service="${2:-}"
    local case_sensitive="${3:-false}"
    
    local log_file="$LOG_DIR/orchestrator.log"
    
    if [ -n "$service" ]; then
        log_file="$LOG_DIR/${service}.log"
    fi
    
    if [ ! -f "$log_file" ]; then
        log_error "Лог файл не найден: $log_file"
        return 1
    fi
    
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   🔍 Поиск: '$pattern'${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    local grep_opts="-i"
    if [ "$case_sensitive" = true ]; then
        grep_opts=""
    fi
    
    grep $grep_opts --color=always "$pattern" "$log_file" | head -n 100
    
    local match_count=$(grep $grep_opts -c "$pattern" "$log_file" 2>/dev/null || echo "0")
    echo ""
    echo -e "${BLUE}Найдено совпадений:${NC} $match_count"
}

# =====================================================
# METRICS COLLECTION
# =====================================================

collect_metrics() {
    """Сбор метрик системы"""
    log_info "Сбор метрик системы..."
    
    local metrics_file="$LOG_DIR/metrics/system_$(date '+%Y%m%d').json"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # CPU Usage
    local cpu_usage="0"
    if command -v top &> /dev/null; then
        cpu_usage=$(top -l 1 | awk '/^CPU usage/ {print $4}' 2>/dev/null || echo "0")
    fi
    
    # Memory Usage
    local mem_total=0
    local mem_used=0
    local mem_percent="0"
    
    if command -v free &> /dev/null; then
        mem_total=$(free -m | awk 'NR==2 {print $2}')
        mem_used=$(free -m | awk 'NR==2 {print $3}')
        mem_percent=$((mem_used * 100 / mem_total))
    fi
    
    # Disk Usage
    local disk_total=0
    local disk_used=0
    local disk_percent="0"
    
    if command -v df &> /dev/null; then
        disk_total=$(df -m "$(pwd)" | awk 'NR==2 {print $2}')
        disk_used=$(df -m "$(pwd)" | awk 'NR==2 {print $3}')
        disk_percent=$(df -h "$(pwd)" | awk 'NR==2 {print $5}' | tr -d '%')
    fi
    
    # Docker Containers
    local containers_total=0
    local containers_running=0
    local containers_stopped=0
    
    if command -v docker &> /dev/null; then
        containers_total=$(docker ps -a --format '{{.ID}}' | wc -l || echo "0")
        containers_running=$(docker ps --format '{{.ID}}' | wc -l || echo "0")
        containers_stopped=$((containers_total - containers_running))
    fi
    
    # Записываем метрики
    cat > "$metrics_file" << EOF
{
  "timestamp": "$timestamp",
  "cpu": {
    "usage_percent": "$cpu_usage"
  },
  "memory": {
    "total_mb": $mem_total,
    "used_mb": $mem_used,
    "usage_percent": $mem_percent
  },
  "disk": {
    "total_mb": $disk_total,
    "used_mb": $disk_used,
    "usage_percent": $disk_percent
  },
  "docker": {
    "total_containers": $containers_total,
    "running_containers": $containers_running,
    "stopped_containers": $containers_stopped
  }
}
EOF
    
    log_success "Метрики сохранены: $metrics_file"
}

show_metrics() {
    """Показывает последние метрики"""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   📊 Текущие метрики системы                               ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Показываем текуую статистику
    echo -e "${BLUE}CPU:${NC}"
    if command -v top &> /dev/null; then
        top -l 1 | grep -E "CPU usage" 2>/dev/null || echo "  N/A"
    fi
    echo ""
    
    echo -e "${BLUE}Memory:${NC}"
    if command -v free &> /dev/null; then
        free -h | grep -E "Mem:" 2>/dev/null || echo "  N/A"
    elif command -v vm_stat &> /dev/null; then
        vm_stat 2>/dev/null || echo "  N/A"
    fi
    echo ""
    
    echo -e "${BLUE}Disk:${NC}"
    df -h "$(pwd)" 2>/dev/null | grep -v "^Filesystem" || echo "  N/A"
    echo ""
    
    echo -e "${BLUE}Docker Containers:${NC}"
    if command -v docker &> /dev/null; then
        echo "  Всего: $(docker ps -a --format '{{.ID}}' | wc -l || echo '0')"
        echo "  Запущено: $(docker ps --format '{{.ID}}' | wc -l || echo '0')"
        echo "  Остановлено: $(docker ps -a --filter 'status=exited' --format '{{.ID}}' | wc -l || echo '0')"
    else
        echo "  Docker не установлен"
    fi
    echo ""
}

# =====================================================
# REAL-TIME MONITORING
# =====================================================

monitor_dashboard() {
    """Мониторинг в реальном времени"""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   📈 MentorHub Real-time Monitor (Ctrl+C для выхода)       ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    while true; do
        clear
        echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${CYAN}║   📈 MentorHub Real-time Monitor                           ║${NC}"
        echo -e "${CYAN}║   $(date '+%Y-%m-%d %H:%M:%S')                                    ║${NC}"
        echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        
        # CPU
        echo -e "${BLUE}CPU Usage:${NC}"
        if command -v top &> /dev/null; then
            top -l 1 | grep -E "CPU usage" 2>/dev/null | awk '{print "  " $0}' || echo "  N/A"
        fi
        echo ""
        
        # Memory
        echo -e "${BLUE}Memory Usage:${NC}"
        if command -v free &> /dev/null; then
            free -h | grep -E "Mem:" 2>/dev/null | awk '{print "  Total: " $2 ", Used: " $3 ", Free: " $4}' || echo "  N/A"
        fi
        echo ""
        
        # Disk
        echo -e "${BLUE}Disk Usage:${NC}"
        df -h "$(pwd)" 2>/dev/null | grep -v "^Filesystem" | awk '{print "  Total: " $2 ", Used: " $3 ", Available: " $4 ", Usage: " $5}' || echo "  N/A"
        echo ""
        
        # Docker
        echo -e "${BLUE}Docker Containers:${NC}"
        if command -v docker &> /dev/null; then
            docker ps --format "  {{.Names}}: {{.Status}}" 2>/dev/null || echo "  N/A"
        else
            echo "  Docker не установлен"
        fi
        echo ""
        
        # Recent Logs
        echo -e "${BLUE}Recent Errors (last 5):${NC}"
        if [ -f "$LOG_DIR/orchestrator.log" ]; then
            tail -n 100 "$LOG_DIR/orchestrator.log" | grep -E "\[ERROR\]|\[CRITICAL\]" | tail -n 5 | while read line; do
                echo -e "  ${RED}$line${NC}"
            done
            
            if [ $(tail -n 100 "$LOG_DIR/orchestrator.log" | grep -c -E "\[ERROR\]|\[CRITICAL\]") -eq 0 ]; then
                echo -e "  ${GREEN}Нет ошибок${NC}"
            fi
        else
            echo "  Логи не найдены"
        fi
        echo ""
        
        sleep 5
    done
}

# =====================================================
# LOG ANALYSIS
# =====================================================

analyze_logs() {
    """Анализ логов на наличие проблем"""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   🔍 Анализ логов                                          ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    local log_file="$LOG_DIR/orchestrator.log"
    
    if [ ! -f "$log_file" ]; then
        log_error "Лог файл не найден: $log_file"
        return 1
    fi
    
    # Статистика по уровням
    echo -e "${BLUE}Статистика по уровням логов:${NC}"
    local total_lines=$(wc -l < "$log_file")
    local error_count=$(grep -c "\[ERROR\]" "$log_file" 2>/dev/null || echo "0")
    local warning_count=$(grep -c "\[WARNING\]" "$log_file" 2>/dev/null || echo "0")
    local success_count=$(grep -c "\[SUCCESS\]" "$log_file" 2>/dev/null || echo "0")
    
    echo "  Всего записей:     $total_lines"
    echo -e "  ${GREEN}SUCCESS:${NC} $success_count"
    echo -e "  ${YELLOW}WARNING:${NC} $warning_count"
    echo -e "  ${RED}ERROR:${NC}   $error_count"
    echo ""
    
    # Последние ошибки
    if [ "$error_count" -gt 0 ]; then
        echo -e "${RED}Последние 10 ошибок:${NC}"
        grep "\[ERROR\]" "$log_file" | tail -n 10 | while read line; do
            echo -e "  ${RED}$line${NC}"
        done
        echo ""
    fi
    
    # Частые предупреждения
    if [ "$warning_count" -gt 0 ]; then
        echo -e "${YELLOW}Топ-5 частых предупреждений:${NC}"
        grep "\[WARNING\]" "$log_file" | awk -F'] ' '{print $2}' | sort | uniq -c | sort -nr | head -n 5 | while read count msg; do
            echo "  $count x $msg"
        done
        echo ""
    fi
    
    # Рекомендации
    echo -e "${BLUE}Рекомендации:${NC}"
    if [ "$error_count" -gt 10 ]; then
        echo -e "  ${RED}⚠ Много ошибок! Проверьте логи и устраните проблемы${NC}"
    fi
    if [ "$warning_count" -gt 20 ]; then
        echo -e "  ${YELLOW}⚠ Много предупреждений - рекомендуется оптимизировать конфигурацию${NC}"
    fi
    if [ "$error_count" -eq 0 ] && [ "$warning_count" -lt 5 ]; then
        echo -e "  ${GREEN}✓ Логи в хорошем состоянии${NC}"
    fi
}

# =====================================================
# HELP
# =====================================================

show_help() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   📄 MentorHub Logging & Monitoring System                 ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Использование:${NC}"
    echo "  $0 [ACTION] [OPTIONS]"
    echo ""
    echo -e "${BLUE}Действия:${NC}"
    echo "  view [service] [level] [lines] [follow]  Просмотр логов"
    echo "  search <pattern> [service]               Поиск в логах"
    echo "  metrics                                  Показать метрики системы"
    echo "  collect                                  Собрать метрики"
    echo "  monitor                                  Мониторинг в реальном времени"
    echo "  analyze                                  Анализ логов"
    echo "  rotate                                   Ротация лог файлов"
    echo "  help                                     Показать эту справку"
    echo ""
    echo -e "${BLUE}Примеры:${NC}"
    echo "  $0 view backend ERROR 50          # Последние 50 ERROR из backend"
    echo "  $0 view '' '' 100 true            # Follow режим для всех логов"
    echo "  $0 search 'timeout' backend        # Поиск 'timeout' в backend логах"
    echo "  $0 monitor                         # Real-time мониторинг"
    echo "  $0 analyze                         # Анализ всех логов"
    echo ""
}

# =====================================================
# MAIN
# =====================================================

main() {
    setup_log_directory
    
    local action="${1:-help}"
    shift || true
    
    case "$action" in
        view)
            view_logs "${1:-}" "${2:-}" "${3:-100}" "${4:-false}"
            ;;
        search)
            search_logs "${1:-}" "${2:-}" "${3:-false}"
            ;;
        metrics)
            show_metrics
            ;;
        collect)
            collect_metrics
            ;;
        monitor)
            monitor_dashboard
            ;;
        analyze)
            analyze_logs
            ;;
        rotate)
            rotate_logs
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
