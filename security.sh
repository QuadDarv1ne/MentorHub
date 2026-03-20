#!/bin/bash

# MentorHub Security Hardening Script
# Автоматическая настройка безопасности для production

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Генерация безопасного SECRET_KEY
generate_secret_key() {
    log_info "Генерация SECRET_KEY..."
    openssl rand -hex 32
}

# Генерация безопасного пароля
generate_password() {
    log_info "Генерация безопасного пароля..."
    openssl rand -base64 32
}

# Настройка firewall
setup_firewall() {
    log_info "Настройка firewall (UFW)..."
    
    if ! command -v ufw &> /dev/null; then
        log_warning "UFW не установлен. Пропускаем..."
        return
    fi
    
    # Сброс правил
    ufw --force reset
    
    # Разрешение SSH
    ufw allow 22/tcp comment 'SSH'
    
    # Разрешение HTTP/HTTPS
    ufw allow 80/tcp comment 'HTTP'
    ufw allow 443/tcp comment 'HTTPS'
    
    # Включение firewall
    ufw --force enable
    
    log_success "Firewall настроен"
    ufw status
}

# Настройка SSL (Let's Encrypt)
setup_ssl() {
    log_info "Настройка SSL сертификатов..."
    
    if [ ! -f .env ]; then
        log_error ".env файл не найден"
        exit 1
    fi
    
    # Чтение домена из .env
    DOMAIN=$(grep "CORS_ORIGINS" .env | head -1 | sed 's/.*https:\/\/\([^,/]*\).*/\1/')
    
    if [ -z "$DOMAIN" ] || [ "$DOMAIN" = "yourdomain.com" ]; then
        log_warning "Домен не настроен. Пропускаем SSL..."
        return
    fi
    
    log_info "Домен: $DOMAIN"
    
    # Установка Certbot
    if ! command -v certbot &> /dev/null; then
        log_info "Установка Certbot..."
        apt-get update && apt-get install -y certbot python3-certbot-nginx
    fi
    
    # Получение сертификата
    log_info "Получение SSL сертификата..."
    certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --email admin@"$DOMAIN"
    
    log_success "SSL сертификат установлен"
}

# Проверка security настроек
check_security() {
    log_info "Проверка security настроек..."
    
    ERRORS=0
    
    # Проверка SECRET_KEY
    if grep -q "SECRET_KEY=.*change-me\|SECRET_KEY=.*your-secret" .env 2>/dev/null; then
        log_error "SECRET_KEY не настроен!"
        ERRORS=$((ERRORS + 1))
    fi
    
    # Проверка пароля БД
    if grep -q "POSTGRES_PASSWORD=.*password\|POSTGRES_PASSWORD=.*SECURE_PASSWORD" .env 2>/dev/null; then
        log_error "POSTGRES_PASSWORD не настроен!"
        ERRORS=$((ERRORS + 1))
    fi
    
    # Проверка DEBUG
    if grep -q "DEBUG=True" .env 2>/dev/null; then
        log_error "DEBUG должен быть False в production!"
        ERRORS=$((ERRORS + 1))
    fi
    
    # Проверка CORS
    if grep -q "CORS_ORIGINS=.*localhost" .env 2>/dev/null; then
        log_warning "CORS разрешает localhost в production"
    fi
    
    if [ $ERRORS -eq 0 ]; then
        log_success "Все security проверки пройдены"
    else
        log_error "Найдено ошибок: $ERRORS"
        exit 1
    fi
}

# Создание .env файла
create_env() {
    log_info "Создание .env файла..."
    
    if [ -f .env ]; then
        log_warning ".env уже существует. Создаем .env.backup..."
        cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    fi
    
    # Генерация секретов
    SECRET_KEY=$(generate_secret_key)
    POSTGRES_PASSWORD=$(generate_password)
    GRAFANA_PASSWORD=$(generate_password)
    
    # Создание файла
    cat > .env << EOF
# ==================== APPLICATION ====================
APP_NAME=MentorHub API
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=production

# ==================== SERVER ====================
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# ==================== DATABASE ====================
POSTGRES_USER=mentorhub
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=mentorhub
DATABASE_URL=postgresql://\$POSTGRES_USER:\$POSTGRES_PASSWORD@pgbouncer:6432/\$POSTGRES_DB

# ==================== REDIS ====================
REDIS_URL=redis://redis:6379/0

# ==================== JWT AUTHENTICATION ====================
SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ==================== CORS ====================
CORS_ORIGINS=https://yourdomain.com

# ==================== RATE LIMITING ====================
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100
RATE_LIMIT_AUTH=10

# ==================== SECURITY ====================
TRUSTED_HOSTS=yourdomain.com
ALLOWED_HOSTS=yourdomain.com,localhost

# ==================== SENTRY ====================
SENTRY_DSN=

# ==================== PAYMENTS ====================
STRIPE_SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
SBP_MOCK_MODE=False

# ==================== GRAFANA ====================
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=$GRAFANA_PASSWORD

# ==================== AWS S3 ====================
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=
EOF

    log_success ".env файл создан"
    log_warning "Отредактируйте .env файл:"
    log_warning "  - Установите CORS_ORIGINS"
    log_warning "  - Добавьте SENTRY_DSN (опционально)"
    log_warning "  - Добавьте STRIPE ключи"
    log_warning "  - Добавьте AWS ключи (опционально)"
}

# Main
main() {
    echo ""
    echo "========================================"
    echo "  MentorHub Security Hardening"
    echo "========================================"
    echo ""
    
    case ${1:-check} in
        --generate-env)
            create_env
            ;;
        --firewall)
            setup_firewall
            ;;
        --ssl)
            setup_ssl
            ;;
        --check)
            check_security
            ;;
        --all)
            create_env
            check_security
            setup_firewall
            setup_ssl
            ;;
        --help)
            echo "MentorHub Security Hardening Script"
            echo ""
            echo "Использование:"
            echo "  ./security.sh [OPTIONS]"
            echo ""
            echo "Опции:"
            echo "  --generate-env  Создать .env файл с безопасными настройками"
            echo "  --firewall      Настроить firewall (UFW)"
            echo "  --ssl           Настроить SSL (Let's Encrypt)"
            echo "  --check         Проверить security настройки"
            echo "  --all           Выполнить все проверки и настройки"
            echo "  --help          Показать эту справку"
            exit 0
            ;;
        *)
            log_error "Неизвестная опция: $1"
            exit 1
            ;;
    esac
}

main
