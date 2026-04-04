#!/bin/bash
# =====================================================
# MentorHub - Unified Notification System
# Система уведомлений через Telegram, Email и Webhook
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
NOTIFICATION_LOG="$PROJECT_DIR/logs/notifications.log"

# =====================================================
# SETUP
# =====================================================

setup_notification_log() {
    mkdir -p "$(dirname "$NOTIFICATION_LOG")"
    touch "$NOTIFICATION_LOG"
}

# =====================================================
# LOAD CONFIG
# =====================================================

load_config() {
    """Загружает конфигурацию уведомлений"""
    local env_file="$PROJECT_DIR/.env"
    
    if [ -f "$env_file" ]; then
        export $(grep -v '^#' "$env_file" | xargs 2>/dev/null || true)
    fi
    
    # Telegram
    TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
    TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"
    TELEGRAM_ENABLED="${TELEGRAM_ENABLED:-true}"
    
    # Email
    SMTP_HOST="${SMTP_HOST:-smtp.gmail.com}"
    SMTP_PORT="${SMTP_PORT:-587}"
    SMTP_USER="${SMTP_USER:-}"
    SMTP_PASSWORD="${SMTP_PASSWORD:-}"
    EMAIL_FROM="${SMTP_FROM_EMAIL:-noreply@mentorhub.com}"
    EMAIL_TO="${NOTIFY_EMAIL_TO:-$SMTP_USER}"
    EMAIL_ENABLED="${EMAIL_ENABLED:-true}"
    
    # Webhook
    WEBHOOK_URL="${NOTIFY_WEBHOOK_URL:-}"
    WEBHOOK_ENABLED="${WEBHOOK_ENABLED:-true}"
    
    # Общие настройки
    NOTIFY_ON_ERROR="${NOTIFY_ON_ERROR:-true}"
    NOTIFY_ON_SUCCESS="${NOTIFY_ON_SUCCESS:-true}"
    NOTIFY_ON_DEPLOY="${NOTIFY_ON_DEPLOY:-true}"
    NOTIFY_ON_BACKUP="${NOTIFY_ON_BACKUP:-true}"
    MIN_ALERT_LEVEL="${MIN_ALERT_LEVEL:-WARNING}"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
}

# =====================================================
# LOGGING
# =====================================================

log_notification() {
    """Записывает уведомление в лог"""
    local level=$1
    local channel=$2
    local message=$3
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] [$level] [$channel] $message" >> "$NOTIFICATION_LOG"
}

# =====================================================
# TELEGRAM NOTIFICATIONS
# =====================================================

send_telegram() {
    """Отправляет уведомление через Telegram"""
    if [ "$TELEGRAM_ENABLED" != "true" ]; then
        return 0
    fi
    
    if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
        return 0
    fi
    
    if [[ "$TELEGRAM_BOT_TOKEN" == "your-"* ]]; then
        return 0
    fi
    
    local level=$1
    local title=$2
    local message=$3
    local emoji=""
    local color=""
    
    case "$level" in
        INFO) emoji="ℹ️"; color="🔵" ;;
        SUCCESS) emoji="✅"; color="🟢" ;;
        WARNING) emoji="⚠️"; color="🟡" ;;
        ERROR) emoji="❌"; color="🔴" ;;
        CRITICAL) emoji="🚨"; color="🔴" ;;
        *) emoji="📢"; color="⚪" ;;
    esac
    
    local text="${emoji} <b>${title}</b>

${message}

📅 $(date '+%Y-%m-%d %H:%M:%S')
🖥️ Хост: $(hostname 2>/dev/null || echo 'unknown')"
    
    # Отправка через Telegram Bot API
    local response=$(curl -s -w "\n%{http_code}" -X POST \
        "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${TELEGRAM_CHAT_ID}" \
        -d "text=${text}" \
        -d "parse_mode=HTML" \
        -d "disable_web_page_preview=true" \
        --max-time 10 2>/dev/null)
    
    local http_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        log_notification "$level" "Telegram" "$title - отправлено"
        return 0
    else
        log_notification "$level" "Telegram" "$title - ошибка (HTTP $http_code)"
        return 1
    fi
}

send_telegram_test() {
    """Отправляет тестовое сообщение в Telegram"""
    echo -e "${BLUE}📤 Отправка тестового сообщения в Telegram...${NC}"
    
    if send_telegram "INFO" "🧪 Test Message" "Это тестовое сообщение от MentorHub"; then
        echo -e "${GREEN}✓ Тестовое сообщение отправлено${NC}"
        return 0
    else
        echo -e "${RED}✗ Не удалось отправить тестовое сообщение${NC}"
        return 1
    fi
}

# =====================================================
# EMAIL NOTIFICATIONS
# =====================================================

send_email() {
    """Отправляет уведомление через Email"""
    if [ "$EMAIL_ENABLED" != "true" ]; then
        return 0
    fi
    
    if [ -z "$SMTP_USER" ] || [ -z "$SMTP_PASSWORD" ] || [ -z "$EMAIL_TO" ]; then
        return 0
    fi
    
    if [[ "$SMTP_USER" == "your-"* ]]; then
        return 0
    fi
    
    local level=$1
    local title=$2
    local message=$3
    
    local subject="[MentorHub] [$level] $title"
    
    local body="MentorHub Notification
========================

Level: $level
Title: $title
Time: $(date '+%Y-%m-%d %H:%M:%S')
Host: $(hostname 2>/dev/null || echo 'unknown')

Message:
$message

========================
MentorHub Automated Notification System"
    
    # Отправка через mail или sendmail
    if command -v mail &> /dev/null; then
        echo "$body" | mail \
            -s "$subject" \
            -r "$EMAIL_FROM" \
            "$EMAIL_TO" 2>/dev/null
        
        if [ $? -eq 0 ]; then
            log_notification "$level" "Email" "$title - отправлено"
            return 0
        fi
    fi
    
    # Альтернатива: отправка через curl и SMTP API
    if command -v curl &> /dev/null; then
        # Используем curl с SMTP
        curl -s --url "smtp://${SMTP_HOST}:${SMTP_PORT}" \
            --ssl-reqd \
            --mail-from "$EMAIL_FROM" \
            --mail-rcpt "$EMAIL_TO" \
            --upload-file <(echo -e "From: $EMAIL_FROM\nTo: $EMAIL_TO\nSubject: $subject\n\n$body") \
            --user "${SMTP_USER}:${SMTP_PASSWORD}" \
            --max-time 10 2>/dev/null
        
        if [ $? -eq 0 ]; then
            log_notification "$level" "Email" "$title - отправлено"
            return 0
        fi
    fi
    
    log_notification "$level" "Email" "$title - ошибка отправки"
    return 1
}

send_email_test() {
    """Отправляет тестовое Email сообщение"""
    echo -e "${BLUE}📤 Отправка тестового Email сообщения...${NC}"
    
    if send_email "INFO" "Test Message" "Это тестовое сообщение от MentorHub"; then
        echo -e "${GREEN}✓ Тестовое Email сообщение отправлено${NC}"
        return 0
    else
        echo -e "${RED}✗ Не удалось отправить тестовое Email сообщение${NC}"
        return 1
    fi
}

# =====================================================
# WEBHOOK NOTIFICATIONS
# =====================================================

send_webhook() {
    """Отправляет уведомление через Webhook"""
    if [ "$WEBHOOK_ENABLED" != "true" ]; then
        return 0
    fi
    
    if [ -z "$WEBHOOK_URL" ]; then
        return 0
    fi
    
    if [[ "$WEBHOOK_URL" == "your-"* ]]; then
        return 0
    fi
    
    local level=$1
    local title=$2
    local message=$3
    
    local payload=$(cat << EOF
{
  "service": "MentorHub",
  "level": "$level",
  "title": "$title",
  "message": "$message",
  "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "host": "$(hostname 2>/dev/null || echo 'unknown')",
  "environment": "${ENVIRONMENT:-unknown}"
}
EOF
)
    
    local response=$(curl -s -w "\n%{http_code}" -X POST \
        "$WEBHOOK_URL" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        --max-time 10 2>/dev/null)
    
    local http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        log_notification "$level" "Webhook" "$title - отправлено"
        return 0
    else
        log_notification "$level" "Webhook" "$title - ошибка (HTTP $http_code)"
        return 1
    fi
}

send_webhook_test() {
    """Отправляет тестовое Webhook сообщение"""
    echo -e "${BLUE}📤 Отправка тестового Webhook сообщения...${NC}"
    
    if send_webhook "INFO" "Test Message" "Это тестовое сообщение от MentorHub"; then
        echo -e "${GREEN}✓ Тестовое Webhook сообщение отправлено${NC}"
        return 0
    else
        echo -e "${RED}✗ Не удалось отправить тестовое Webhook сообщение${NC}"
        return 1
    fi
}

# =====================================================
# UNIFIED NOTIFICATION
# =====================================================

notify() {
    """Отправляет уведомление через все настроенные каналы"""
    local level="${1:-INFO}"
    local title="${2:-Notification}"
    local message="${3:-}"
    
    # Проверка минимального уровня
    case "$MIN_ALERT_LEVEL" in
        DEBUG) local min_level=0 ;;
        INFO) local min_level=1 ;;
        WARNING) local min_level=2 ;;
        ERROR) local min_level=3 ;;
        CRITICAL) local min_level=4 ;;
        *) local min_level=1 ;;
    esac
    
    case "$level" in
        DEBUG) local msg_level=0 ;;
        INFO) local msg_level=1 ;;
        WARNING) local msg_level=2 ;;
        ERROR) local msg_level=3 ;;
        CRITICAL) local msg_level=4 ;;
        *) local msg_level=1 ;;
    esac
    
    if [ "$msg_level" -lt "$min_level" ]; then
        return 0
    fi
    
    # Проверка типа уведомления
    case "$level" in
        ERROR|CRITICAL)
            if [ "$NOTIFY_ON_ERROR" != "true" ]; then
                return 0
            fi
            ;;
        SUCCESS)
            if [ "$NOTIFY_ON_SUCCESS" != "true" ]; then
                return 0
            fi
            ;;
    esac
    
    echo -e "${BLUE}📢 Отправка уведомления: [$level] $title${NC}"
    
    local sent_count=0
    local failed_count=0
    
    # Telegram
    if send_telegram "$level" "$title" "$message"; then
        sent_count=$((sent_count + 1))
    else
        failed_count=$((failed_count + 1))
    fi
    
    # Email
    if send_email "$level" "$title" "$message"; then
        sent_count=$((sent_count + 1))
    else
        failed_count=$((failed_count + 1))
    fi
    
    # Webhook
    if send_webhook "$level" "$title" "$message"; then
        sent_count=$((sent_count + 1))
    else
        failed_count=$((failed_count + 1))
    fi
    
    echo -e "${GREEN}✓ Отправлено каналов: $sent_count${NC}"
    if [ $failed_count -gt 0 ]; then
        echo -e "${YELLOW}⚠ Ошибок: $failed_count${NC}"
    fi
    
    return 0
}

# =====================================================
# SPECIFIC NOTIFICATIONS
# =====================================================

notify_deploy() {
    """Уведомление о деплое"""
    if [ "$NOTIFY_ON_DEPLOY" != "true" ]; then
        return 0
    fi
    
    local environment="${1:-unknown}"
    local status="${2:-success}"
    local version="${3:-unknown}"
    
    local level="SUCCESS"
    if [ "$status" = "failed" ]; then
        level="ERROR"
    fi
    
    notify "$level" "🚀 Deployment" "Environment: $environment
Version: $version
Status: $status
Time: $(date '+%Y-%m-%d %H:%M:%S')"
}

notify_backup() {
    """Уведомление о backup"""
    if [ "$NOTIFY_ON_BACKUP" != "true" ]; then
        return 0
    fi
    
    local status="${1:-success}"
    local size="${2:-unknown}"
    local duration="${3:-unknown}"
    
    local level="SUCCESS"
    if [ "$status" = "failed" ]; then
        level="ERROR"
    fi
    
    notify "$level" "💾 Backup" "Status: $status
Size: $size
Duration: $duration
Time: $(date '+%Y-%m-%d %H:%M:%S')"
}

notify_error() {
    """Уведомление об ошибке"""
    local service="${1:-unknown}"
    local error="${2:-unknown}"
    local details="${3:-}"
    
    notify "ERROR" "❌ Error in $service" "Error: $error
Service: $service
Details: $details
Time: $(date '+%Y-%m-%d %H:%M:%S')"
}

notify_system_status() {
    """Уведомление о статусе системы"""
    local status="${1:-healthy}"
    local services="${2:-}"
    local metrics="${3:-}"
    
    local level="SUCCESS"
    if [ "$status" = "degraded" ]; then
        level="WARNING"
    elif [ "$status" = "unhealthy" ]; then
        level="ERROR"
    fi
    
    notify "$level" "📊 System Status: $status" "Services:
$services

Metrics:
$metrics
Time: $(date '+%Y-%m-%d %H:%M:%S')"
}

# =====================================================
# TEST ALL CHANNELS
# =====================================================

test_all() {
    """Тестирует все каналы уведомлений"""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   🧪 Testing All Notification Channels                     ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    load_config
    
    echo -e "${BLUE}Конфигурация:${NC}"
    echo "  Telegram: $([ -n "$TELEGRAM_BOT_TOKEN" ] && [ "$TELEGRAM_BOT_TOKEN" != "your-"* ] && echo "✓ настроен" || echo "✗ не настроен')"
    echo "  Email: $([ -n "$SMTP_USER" ] && [ "$SMTP_USER" != "your-"* ] && echo "✓ настроен" || echo "✗ не настроен')"
    echo "  Webhook: $([ -n "$WEBHOOK_URL" ] && [ "$WEBHOOK_URL" != "your-"* ] && echo "✓ настроен" || echo "✗ не настроен')"
    echo ""
    
    local success=0
    local failed=0
    
    echo -e "${BLUE}Тестирование каналов:${NC}"
    
    if send_telegram_test; then
        success=$((success + 1))
    else
        failed=$((failed + 1))
    fi
    
    if send_email_test; then
        success=$((success + 1))
    else
        failed=$((failed + 1))
    fi
    
    if send_webhook_test; then
        success=$((success + 1))
    else
        failed=$((failed + 1))
    fi
    
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ Успешно: $success${NC}"
    if [ $failed -gt 0 ]; then
        echo -e "${RED}✗ Не успешно: $failed${NC}"
    fi
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
}

# =====================================================
# SHOW NOTIFICATION LOGS
# =====================================================

show_notification_logs() {
    """Показывает лог уведомлений"""
    if [ ! -f "$NOTIFICATION_LOG" ]; then
        echo -e "${YELLOW}⚠ Лог уведомлений не найден${NC}"
        return
    fi
    
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   📄 Notification Logs                                     ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    tail -n 50 "$NOTIFICATION_LOG"
}

# =====================================================
# HELP
# =====================================================

show_help() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   📢 MentorHub Notification System                         ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Использование:${NC}"
    echo "  $0 [ACTION] [OPTIONS]"
    echo ""
    echo -e "${BLUE}Действия:${NC}"
    echo "  send <level> <title> <message>   Отправить уведомление"
    echo "  deploy <env> <status> [version]  Уведомление о деплое"
    echo "  backup <status> [size] [duration] Уведомление о backup"
    echo "  error <service> <error> [details] Уведомление об ошибке"
    echo "  status <status> [services] [metrics] Статус системы"
    echo "  test                             Тестировать все каналы"
    echo "  logs                             Показать лог уведомлений"
    echo "  help                             Показать эту справку"
    echo ""
    echo -e "${BLUE}Переменные окружения (.env):${NC}"
    echo "  TELEGRAM_BOT_TOKEN       Токен бота Telegram"
    echo "  TELEGRAM_CHAT_ID         ID чата Telegram"
    echo "  TELEGRAM_ENABLED         Включить Telegram (true/false)"
    echo "  SMTP_USER                Email для отправки"
    echo "  SMTP_PASSWORD            Пароль email"
    echo "  NOTIFY_EMAIL_TO          Email получателя"
    echo "  EMAIL_ENABLED            Включить Email (true/false)"
    echo "  NOTIFY_WEBHOOK_URL       URL Webhook для уведомлений"
    echo "  WEBHOOK_ENABLED          Включить Webhook (true/false)"
    echo "  NOTIFY_ON_ERROR          Уведомлять об ошибках (true/false)"
    echo "  NOTIFY_ON_SUCCESS        Уведомлять об успехе (true/false)"
    echo "  NOTIFY_ON_DEPLOY         Уведомлять о деплое (true/false)"
    echo "  NOTIFY_ON_BACKUP         Уведомлять о backup (true/false)"
    echo "  MIN_ALERT_LEVEL          Минимальный уровень (DEBUG/INFO/WARNING/ERROR/CRITICAL)"
    echo ""
    echo -e "${BLUE}Примеры:${NC}"
    echo "  $0 send WARNING 'High Memory' 'Memory usage at 85%'"
    echo "  $0 deploy production success v1.2.3"
    echo "  $0 backup success 1.2GB 45s"
    echo "  $0 error backend 'Connection timeout' 'Database unreachable'"
    echo "  $0 test"
    echo ""
}

# =====================================================
# MAIN
# =====================================================

main() {
    setup_notification_log
    load_config
    
    local action="${1:-help}"
    shift || true
    
    case "$action" in
        send)
            notify "${1:-INFO}" "${2:-Notification}" "${3:-}"
            ;;
        deploy)
            notify_deploy "${1:-unknown}" "${2:-success}" "${3:-unknown}"
            ;;
        backup)
            notify_backup "${1:-success}" "${2:-unknown}" "${3:-unknown}"
            ;;
        error)
            notify_error "${1:-unknown}" "${2:-unknown}" "${3:-}"
            ;;
        status)
            notify_system_status "${1:-healthy}" "${2:-}" "${3:-}"
            ;;
        test)
            test_all
            ;;
        logs)
            show_notification_logs
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}❌ Неизвестное действие: $action${NC}"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
