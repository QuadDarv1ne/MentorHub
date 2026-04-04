#!/bin/bash
# =====================================================
# MentorHub - Environment Variables Validation Script
# Проверяет корректность всех переменных в .env
# =====================================================

set -euo pipefail

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Счетчики ошибок
ERRORS=0
WARNINGS=0

# =====================================================
# ФУНКЦИИ
# =====================================================

log_error() {
    echo -e "${RED}❌ ERROR:${NC} $1"
    ERRORS=$((ERRORS + 1))
}

log_warning() {
    echo -e "${YELLOW}⚠️  WARNING:${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

check_required() {
    local var_name=$1
    local var_value=$2
    
    if [ -z "$var_value" ]; then
        log_error "$var_name не установлена"
        return 1
    fi
    return 0
}

check_not_default() {
    local var_name=$1
    local var_value=$2
    shift 2
    local defaults=("$@")
    
    for default in "${defaults[@]}"; do
        if [ "$var_value" = "$default" ]; then
            log_error "$var_name использует значение по умолчанию: $default"
            return 1
        fi
    done
    return 0
}

check_min_length() {
    local var_name=$1
    local var_value=$2
    local min_length=$3
    
    if [ ${#var_value} -lt $min_length ]; then
        log_error "$var_name слишком короткий (минимум $min_length символов, сейчас ${#var_value})"
        return 1
    fi
    return 0
}

check_port() {
    local var_name=$1
    local var_value=$2
    
    if ! [[ "$var_value" =~ ^[0-9]+$ ]] || [ "$var_value" -lt 1 ] || [ "$var_value" -gt 65535 ]; then
        log_error "$var_name должен быть числом от 1 до 65535 (сейчас: $var_value)"
        return 1
    fi
    return 0
}

check_url_format() {
    local var_name=$1
    local var_value=$2
    
    if [[ ! "$var_value" =~ ^https?:// ]]; then
        log_warning "$var_name не похож на URL (должен начинаться с http:// или https://)"
        return 1
    fi
    return 0
}

check_email_format() {
    local var_name=$1
    local var_value=$2
    
    if [[ ! "$var_value" =~ ^[^@]+@[^@]+\.[^@]+$ ]]; then
        log_warning "$var_name не похож на email"
        return 1
    fi
    return 0
}

# =====================================================
# ОСНОВНАЯ ЛОГИКА
# =====================================================

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   🔍 MentorHub - Environment Validation                    ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Загружаем .env файл
ENV_FILE=".env"
if [ -n "${1:-}" ]; then
    ENV_FILE="$1"
fi

if [ ! -f "$ENV_FILE" ]; then
    log_error "Файл $ENV_FILE не найден"
    exit 1
fi

echo -e "${BLUE}📄 Загрузка:${NC} $ENV_FILE"
export $(grep -v '^#' "$ENV_FILE" | xargs 2>/dev/null || true)
echo ""

echo -e "${BLUE}🔍 Валидация переменных...${NC}"
echo ""

# ==================== APPLICATION ====================
echo -e "${CYAN}[Application]${NC}"

if [ -n "${ENVIRONMENT:-}" ]; then
    case "$ENVIRONMENT" in
        development|production|staging)
            log_success "ENVIRONMENT=$ENVIRONMENT"
            ;;
        *)
            log_warning "ENVIRONMENT=$ENVIRONMENT (рекомендуется: development, production, staging)"
            ;;
    esac
else
    log_warning "ENVIRONMENT не установлена (по умолчанию: development)"
fi

[ -n "${APP_NAME:-}" ] && log_success "APP_NAME=$APP_NAME" || log_warning "APP_NAME не установлена"
[ -n "${APP_VERSION:-}" ] && log_success "APP_VERSION=$APP_VERSION" || log_warning "APP_VERSION не установлена"

echo ""

# ==================== DATABASE ====================
echo -e "${CYAN}[Database]${NC}"

check_required "DB_USER" "${DB_USER:-}"
check_required "DB_PASSWORD" "${DB_PASSWORD:-}"
check_not_default "DB_PASSWORD" "${DB_PASSWORD:-}" "change-this-password-in-production" "password" "SECURE_PASSWORD"
check_min_length "DB_PASSWORD" "${DB_PASSWORD:-}" 8
[ -n "${DB_NAME:-}" ] && log_success "DB_NAME=$DB_NAME" || log_warning "DB_NAME не установлена"
[ -n "${DB_PORT:-}" ] && check_port "DB_PORT" "${DB_PORT:-}"

if [ -n "${DATABASE_URL:-}" ]; then
    if [[ "$DATABASE_URL" =~ ^postgresql:// ]]; then
        log_success "DATABASE_URL формат корректен"
    else
        log_error "DATABASE_URL должен начинаться с postgresql://"
    fi
else
    log_error "DATABASE_URL не установлена"
fi

echo ""

# ==================== REDIS ====================
echo -e "${CYAN}[Redis]${NC}"

if [ -n "${REDIS_URL:-}" ]; then
    if [[ "$REDIS_URL" =~ ^redis:// ]]; then
        log_success "REDIS_URL формат корректен"
    else
        log_error "REDIS_URL должен начинаться с redis://"
    fi
else
    log_warning "REDIS_URL не установлена"
fi

[ -n "${REDIS_PORT:-}" ] && check_port "REDIS_PORT" "${REDIS_PORT:-}"

echo ""

# ==================== JWT ====================
echo -e "${CYAN}[JWT Authentication]${NC}"

if [ -n "${SECRET_KEY:-}" ]; then
    check_not_default "SECRET_KEY" "${SECRET_KEY:-}" \
        "change-this-secret-key-in-production-use-openssl-rand-hex-32" \
        "your-secret-key" "change-me"
    check_min_length "SECRET_KEY" "${SECRET_KEY:-}" 32
    
    if [ ${#SECRET_KEY} -ge 32 ]; then
        log_success "SECRET_KEY длина корректна (${#SECRET_KEY} символов)"
    fi
else
    log_error "SECRET_KEY не установлена"
fi

[ -n "${ALGORITHM:-}" ] && log_success "ALGORITHM=$ALGORITHM" || log_warning "ALGORITHM не установлена"
[ -n "${ACCESS_TOKEN_EXPIRE_MINUTES:-}" ] && log_success "ACCESS_TOKEN_EXPIRE_MINUTES=$ACCESS_TOKEN_EXPIRE_MINUTES"
[ -n "${REFRESH_TOKEN_EXPIRE_DAYS:-}" ] && log_success "REFRESH_TOKEN_EXPIRE_DAYS=$REFRESH_TOKEN_EXPIRE_DAYS"

echo ""

# ==================== CORS ====================
echo -e "${CYAN}[CORS]${NC}"

if [ -n "${CORS_ORIGINS:-}" ]; then
    if [[ "$CORS_ORIGINS" =~ ^http ]]; then
        log_success "CORS_ORIGINS установлена"
    else
        log_warning "CORS_ORIGINS имеет странный формат: $CORS_ORIGINS"
    fi
else
    log_warning "CORS_ORIGINS не установлена - могут быть проблемы с CORS"
fi

echo ""

# ==================== EXTERNAL SERVICES ====================
echo -e "${CYAN}[External Services]${NC}"

# Agora
if [ -n "${AGORA_APP_ID:-}" ] && [[ "$AGORA_APP_ID" != "your-"* ]]; then
    log_success "AGORA_APP_ID установлена"
else
    log_warning "AGORA_APP_ID не установлена (видеосвязь не будет работать)"
fi

# Stripe
if [ -n "${STRIPE_API_KEY:-}" ] && [[ "$STRIPE_API_KEY" != "your-"* ]]; then
    log_success "STRIPE_API_KEY установлена"
else
    log_warning "STRIPE_API_KEY не установлена (платежи не будут работать)"
fi

if [ -n "${STRIPE_WEBHOOK_SECRET:-}" ] && [[ "$STRIPE_WEBHOOK_SECRET" != "your-"* ]]; then
    log_success "STRIPE_WEBHOOK_SECRET установлена"
else
    log_warning "STRIPE_WEBHOOK_SECRET не установлена (webhooks не будут работать)"
fi

# SBP
if [ -n "${SBP_MERCHANT_ID:-}" ] && [[ "$SBP_MERCHANT_ID" != "your-"* ]]; then
    log_success "SBP_MERCHANT_ID установлена"
else
    log_warning "SBP_MERCHANT_ID не установлена (СБП платежи не будут работать)"
fi

echo ""

# ==================== EMAIL ====================
echo -e "${CYAN}[Email]${NC}"

if [ -n "${SMTP_USER:-}" ] && [[ "$SMTP_USER" != "your-"* ]]; then
    log_success "SMTP_USER установлена"
    check_email_format "SMTP_USER" "${SMTP_USER:-}"
else
    log_warning "SMTP_USER не установлена (email рассылка не будет работать)"
fi

if [ -n "${SMTP_FROM_EMAIL:-}" ]; then
    check_email_format "SMTP_FROM_EMAIL" "${SMTP_FROM_EMAIL:-}"
fi

echo ""

# ==================== MONITORING ====================
echo -e "${CYAN}[Monitoring]${NC}"

if [ -n "${SENTRY_DSN:-}" ] && [[ "$SENTRY_DSN" != "your-"* ]] && [[ -n "$SENTRY_DSN" ]]; then
    log_success "SENTRY_DSN установлена (мониторинг ошибок включен)"
else
    log_warning "SENTRY_DSN не установлена (мониторинг ошибок выключен)"
fi

if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [[ "$TELEGRAM_BOT_TOKEN" != "your-"* ]]; then
    log_success "TELEGRAM_BOT_TOKEN установлена (уведомления включены)"
else
    log_warning "TELEGRAM_BOT_TOKEN не установлена (уведомления в Telegram выключены)"
fi

echo ""

# ==================== PORTS ====================
echo -e "${CYAN}[Ports]${NC}"

[ -n "${BACKEND_PORT:-}" ] && check_port "BACKEND_PORT" "${BACKEND_PORT:-}"
[ -n "${FRONTEND_PORT:-}" ] && check_port "FRONTEND_PORT" "${FRONTEND_PORT:-}"
[ -n "${NGINX_HTTP_PORT:-}" ] && check_port "NGINX_HTTP_PORT" "${NGINX_HTTP_PORT:-}"
[ -n "${NGINX_HTTPS_PORT:-}" ] && check_port "NGINX_HTTPS_PORT" "${NGINX_HTTPS_PORT:-}"
[ -n "${PROMETHEUS_PORT:-}" ] && check_port "PROMETHEUS_PORT" "${PROMETHEUS_PORT:-}"
[ -n "${GRAFANA_PORT:-}" ] && check_port "GRAFANA_PORT" "${GRAFANA_PORT:-}"

echo ""

# ==================== ИТОГ ====================
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Валидация прошла успешно!${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Критических ошибок нет${NC}"
    echo -e "${YELLOW}⚠️  Предупреждений: $WARNINGS${NC}"
    echo ""
    echo -e "${YELLOW}Рекомендуется устранить предупреждения для оптимальной работы${NC}"
    exit 0
else
    echo -e "${RED}❌ Найдено ошибок: $ERRORS${NC}"
    echo -e "${YELLOW}⚠️  Предупреждений: $WARNINGS${NC}"
    echo ""
    echo -e "${RED}Необходимо устранить все ошибки перед запуском!${NC}"
    exit 1
fi
