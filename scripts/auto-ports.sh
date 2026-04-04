#!/bin/bash
# =====================================================
# MentorHub - Automatic Port Detection Script
# Автоматически находит свободные порты и генерирует .env
# Platforms: Linux, macOS, WSL, Git Bash (Windows)
# =====================================================

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

# =====================================================
# ФУНКЦИИ
# =====================================================

# Проверка доступности порта
# Возвращает 0 если порт свободен, 1 если занят
check_port() {
    local port=$1
    
    # Windows (через netstat)
    if command -v netstat &> /dev/null; then
        if netstat -an | grep -q ":${port} " 2>/dev/null; then
            return 1
        fi
    fi
    
    # Linux/macOS (через ss или lsof)
    if command -v ss &> /dev/null; then
        if ss -tln | grep -q ":${port} " 2>/dev/null; then
            return 1
        fi
    elif command -v lsof &> /dev/null; then
        if lsof -i :${port} &> /dev/null; then
            return 1
        fi
    fi
    
    # Fallback: пробуем привязаться к порту
    if command -v python3 &> /dev/null; then
        python3 -c "
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind(('127.0.0.1', ${port}))
    s.close()
    exit(0)
except:
    s.close()
    exit(1)
" 2>/dev/null || return 1
    fi
    
    return 0
}

# Найти первый свободный порт начиная с базового
find_free_port() {
    local base_port=$1
    local port=$base_port
    local max_attempts=100
    
    for i in $(seq 1 $max_attempts); do
        if check_port $port; then
            echo $port
            return 0
        fi
        port=$((base_port + i))
    done
    
    echo -e "${RED}❌ Не удалось найти свободный порт в диапазоне ${base_port}-$((base_port + max_attempts))${NC}" >&2
    return 1
}

# =====================================================
# ОПРЕДЕЛЕНИЕ ПОРТОВ
# =====================================================

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   🔍 MentorHub - Automatic Port Detection                  ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Базовые порты (можно переопределить через аргументы)
DEFAULT_BACKEND_PORT=8000
DEFAULT_FRONTEND_PORT=3000
DEFAULT_DB_PORT=5432
DEFAULT_REDIS_PORT=6379
DEFAULT_NGINX_HTTP_PORT=80
DEFAULT_NGINX_HTTPS_PORT=443
DEFAULT_PROMETHEUS_PORT=9090
DEFAULT_GRAFANA_PORT=3001

echo -e "${BLUE}📡 Поиск свободных портов...${NC}"

# Определяем порты
if check_port $DEFAULT_BACKEND_PORT; then
    BACKEND_PORT=$DEFAULT_BACKEND_PORT
    echo -e "${GREEN}✓${NC} Backend port:  ${CYAN}$BACKEND_PORT${NC} (default)"
else
    BACKEND_PORT=$(find_free_port $DEFAULT_BACKEND_PORT)
    echo -e "${YELLOW}⚠${NC} Backend port:  ${CYAN}$BACKEND_PORT${NC} (auto-detected, default $DEFAULT_BACKEND_PORT busy)"
fi

if check_port $DEFAULT_FRONTEND_PORT; then
    FRONTEND_PORT=$DEFAULT_FRONTEND_PORT
    echo -e "${GREEN}✓${NC} Frontend port: ${CYAN}$FRONTEND_PORT${NC} (default)"
else
    FRONTEND_PORT=$(find_free_port $DEFAULT_FRONTEND_PORT)
    echo -e "${YELLOW}⚠${NC} Frontend port: ${CYAN}$FRONTEND_PORT${NC} (auto-detected, default $DEFAULT_FRONTEND_PORT busy)"
fi

if check_port $DEFAULT_DB_PORT; then
    DB_PORT=$DEFAULT_DB_PORT
    echo -e "${GREEN}✓${NC} Database port: ${CYAN}$DB_PORT${NC} (default)"
else
    DB_PORT=$(find_free_port $DEFAULT_DB_PORT)
    echo -e "${YELLOW}⚠${NC} Database port: ${CYAN}$DB_PORT${NC} (auto-detected, default $DEFAULT_DB_PORT busy)"
fi

if check_port $DEFAULT_REDIS_PORT; then
    REDIS_PORT=$DEFAULT_REDIS_PORT
    echo -e "${GREEN}✓${NC} Redis port:    ${CYAN}$REDIS_PORT${NC} (default)"
else
    REDIS_PORT=$(find_free_port $DEFAULT_REDIS_PORT)
    echo -e "${YELLOW}⚠${NC} Redis port:    ${CYAN}$REDIS_PORT${NC} (auto-detected, default $DEFAULT_REDIS_PORT busy)"
fi

# Nginx порты требуют привилегий (< 1024)
# Проверяем root (Linux/macOS) или админ (Windows)
IS_ROOT=false
if [ "$(id -u)" -eq 0 ] 2>/dev/null; then
    IS_ROOT=true
elif command -v whoami &> /dev/null && [ "$(whoami)" = "Administrator" ] 2>/dev/null; then
    IS_ROOT=true
fi

# Проверяем можно ли использовать порты < 1024
if [ "$IS_ROOT" = true ]; then
    NGINX_HTTP_PORT=$DEFAULT_NGINX_HTTP_PORT
    NGINX_HTTPS_PORT=$DEFAULT_NGINX_HTTPS_PORT
    echo -e "${GREEN}✓${NC} Nginx HTTP:    ${CYAN}$NGINX_HTTP_PORT${NC} (default)"
    echo -e "${GREEN}✓${NC} Nginx HTTPS:   ${CYAN}$NGINX_HTTPS_PORT${NC} (default)"
else
    # Без root используем порты > 1024
    if check_port 8080; then
        NGINX_HTTP_PORT=8080
    else
        NGINX_HTTP_PORT=$(find_free_port 8080)
    fi
    
    if check_port 8443; then
        NGINX_HTTPS_PORT=8443
    else
        NGINX_HTTPS_PORT=$(find_free_port 8443)
    fi
    
    echo -e "${YELLOW}⚠${NC} Nginx HTTP:    ${CYAN}$NGINX_HTTP_PORT${NC} (default 80, no root)"
    echo -e "${YELLOW}⚠${NC} Nginx HTTPS:   ${CYAN}$NGINX_HTTPS_PORT${NC} (default 443, no root)"
fi

if check_port $DEFAULT_PROMETHEUS_PORT; then
    PROMETHEUS_PORT=$DEFAULT_PROMETHEUS_PORT
    echo -e "${GREEN}✓${NC} Prometheus:    ${CYAN}$PROMETHEUS_PORT${NC} (default)"
else
    PROMETHEUS_PORT=$(find_free_port $DEFAULT_PROMETHEUS_PORT)
    echo -e "${YELLOW}⚠${NC} Prometheus:    ${CYAN}$PROMETHEUS_PORT${NC} (auto-detected)"
fi

if check_port $DEFAULT_GRAFANA_PORT; then
    GRAFANA_PORT=$DEFAULT_GRAFANA_PORT
    echo -e "${GREEN}✓${NC} Grafana:       ${CYAN}$GRAFANA_PORT${NC} (default)"
else
    GRAFANA_PORT=$(find_free_port $DEFAULT_GRAFANA_PORT)
    echo -e "${YELLOW}⚠${NC} Grafana:       ${CYAN}$GRAFANA_PORT${NC} (auto-detected)"
fi

echo ""

# =====================================================
# ГЕНЕРАЦИЯ .env ФАЙЛА
# =====================================================

echo -e "${BLUE}📝 Генерация .env файла...${NC}"

# Проверяем существует ли .env
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠ Файл .env уже существует. Создать .env.auto?${NC}"
    ENV_FILE=".env.auto"
else
    ENV_FILE=".env"
fi

# Генерируем SECRET_KEY и DB_PASSWORD кроссплатформенно
generate_random_string() {
    local length=${1:-16}
    if command -v openssl &> /dev/null; then
        openssl rand -hex $((length / 2)) | head -c $length
    elif command -v python3 &> /dev/null; then
        python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range($length)))"
    elif command -v python &> /dev/null; then
        python -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range($length)))"
    else
        # Fallback: используем /dev/urandom если доступен
        if [ -f /dev/urandom ]; then
            head -c $length /dev/urandom | tr -dc 'a-zA-Z0-9' | head -c $length
        else
            echo "random_$(date +%s)_$$"
        fi
    fi
}

if [ -n "$SECRET_KEY" ]; then
    GENERATED_SECRET_KEY="$SECRET_KEY"
else
    GENERATED_SECRET_KEY=$(generate_random_string 64)
fi

# Генерируем пароль для БД
DB_PASSWORD_RANDOM=$(generate_random_string 20)

# Создаём .env файл
cat > "$ENV_FILE" << EOF
# =====================================================
# MentorHub - Auto-generated Configuration
# Generated: $(date '+%Y-%m-%d %H:%M:%S')
# =====================================================

# ==================== APPLICATION ====================
APP_NAME=MentorHub API
APP_VERSION=1.0.0
DEBUG=False
ENVIRONMENT=development

# ==================== SERVER ====================
HOST=0.0.0.0
PORT=$BACKEND_PORT

# ==================== PORTS ====================
BACKEND_PORT=$BACKEND_PORT
FRONTEND_PORT=$FRONTEND_PORT
DB_PORT=$DB_PORT
REDIS_PORT=$REDIS_PORT
NGINX_HTTP_PORT=$NGINX_HTTP_PORT
NGINX_HTTPS_PORT=$NGINX_HTTPS_PORT
PROMETHEUS_PORT=$PROMETHEUS_PORT
GRAFANA_PORT=$GRAFANA_PORT

# ==================== DATABASE ====================
DB_USER=mentorhub_user
DB_PASSWORD=dev_$DB_PASSWORD_RANDOM
DB_NAME=mentorhub_dev
DATABASE_URL=postgresql://mentorhub_user:\${DB_PASSWORD}@localhost:\${DB_PORT}/\${DB_NAME}
DB_ECHO=False
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# ==================== REDIS ====================
REDIS_URL=redis://localhost:\${REDIS_PORT}/0
REDIS_HOST=localhost
REDIS_PORT=\${REDIS_PORT}
REDIS_DB=0

# ==================== JWT AUTHENTICATION ====================
SECRET_KEY=$GENERATED_SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ==================== CORS ====================
CORS_ORIGINS=http://localhost:\${FRONTEND_PORT},http://localhost:\${BACKEND_PORT},http://127.0.0.1:\${FRONTEND_PORT},http://127.0.0.1:\${BACKEND_PORT}

# ==================== AGORA VIDEO ====================
AGORA_APP_ID=your-agora-app-id
AGORA_APP_CERTIFICATE=your-agora-certificate

# ==================== STRIPE PAYMENTS ====================
STRIPE_API_KEY=your-stripe-api-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret
STRIPE_MOCK_MODE=True

# ==================== SBP ====================
SBP_MERCHANT_ID=your-sbp-merchant-id
SBP_API_KEY=your-sbp-api-key
SBP_API_SECRET=your-sbp-api-secret
SBP_CALLBACK_URL=http://localhost:\${BACKEND_PORT}/api/payments/sbp/callback
SBP_MOCK_MODE=True

# ==================== EMAIL ====================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@mentorhub.com
SMTP_FROM_NAME=MentorHub

# ==================== FRONTEND ====================
NEXT_PUBLIC_API_BASE_URL=http://localhost:\${BACKEND_PORT}/api/v1
NEXT_PUBLIC_SITE_URL=http://localhost:\${FRONTEND_PORT}
NEXT_PUBLIC_API_URL=http://localhost:\${BACKEND_PORT}

# ==================== MONITORING ====================
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin

# ==================== OPTIONAL ====================
SENTRY_DSN=
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=
EOF

echo -e "${GREEN}✓${NC} Файл ${CYAN}$ENV_FILE${NC} создан"
echo ""

# =====================================================
# ВЫВОД ИНФОРМАЦИИ
# =====================================================

echo -e "${YELLOW}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Порты успешно настроены${NC}"
echo ""
echo -e "${CYAN}📍 Services URLs:${NC}"
echo -e "   Backend API:    ${CYAN}http://localhost:$BACKEND_PORT${NC}"
echo -e "   API Docs:       ${CYAN}http://localhost:$BACKEND_PORT/docs${NC}"
echo -e "   Frontend:       ${CYAN}http://localhost:$FRONTEND_PORT${NC}"
echo -e "   Database:       ${CYAN}localhost:$DB_PORT${NC}"
echo -e "   Redis:          ${CYAN}localhost:$REDIS_PORT${NC}"
echo -e "   Nginx HTTP:     ${CYAN}http://localhost:$NGINX_HTTP_PORT${NC}"
echo -e "   Prometheus:     ${CYAN}http://localhost:$PROMETHEUS_PORT${NC}"
echo -e "   Grafana:        ${CYAN}http://localhost:$GRAFANA_PORT${NC}"
echo ""

if [ "$ENV_FILE" = ".env.auto" ]; then
    echo -e "${YELLOW}⚠ Используется файл .env.auto (основной .env сохранён)${NC}"
    echo -e "${YELLOW}  Для использования: скопируйте содержимое в .env${NC}"
fi

echo -e "${YELLOW}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}🚀 Теперь запустите:${NC}"
echo -e "   ${CYAN}make docker-up${NC}  или  ${CYAN}docker-compose up -d${NC}"
echo ""
