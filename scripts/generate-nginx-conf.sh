#!/bin/bash
# =====================================================
# MentorHub - Generate nginx.conf from template
# Подставляет актуальные порты из .env в nginx шаблон
# =====================================================

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}🔧 Генерация nginx.conf из template...${NC}"

# Определяем пути
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATE_FILE="$PROJECT_DIR/nginx/nginx.conf.template"
OUTPUT_FILE="$PROJECT_DIR/nginx/nginx.conf"

# Проверяем existence template
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}❌ Template не найден: $TEMPLATE_FILE${NC}"
    exit 1
fi

# Загружаем переменные из .env если существует
if [ -f "$PROJECT_DIR/.env" ]; then
    echo -e "${GREEN}✓${NC} Загрузка переменных из .env"
    export $(grep -v '^#' "$PROJECT_DIR/.env" | xargs 2>/dev/null || true)
fi

# Устанавливаем дефолты если не заданы
NGINX_HTTP_PORT="${NGINX_HTTP_PORT:-80}"
NGINX_HTTPS_PORT="${NGINX_HTTPS_PORT:-443}"
BACKEND_PORT="${BACKEND_PORT:-8001}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

# Генерируем nginx.conf
envsubst '${NGINX_HTTP_PORT} ${BACKEND_PORT} ${FRONTEND_PORT}' < "$TEMPLATE_FILE" > "$OUTPUT_FILE"

echo -e "${GREEN}✓${NC} nginx.conf сгенерирован"
echo -e "${BLUE}   Nginx HTTP port:    ${NGINX_HTTP_PORT}${NC}"
echo -e "${BLUE}   Backend port:       ${BACKEND_PORT}${NC}"
echo -e "${BLUE}   Frontend port:      ${FRONTEND_PORT}${NC}"
echo ""
echo -e "${GREEN}✅ Готово!${NC}"
