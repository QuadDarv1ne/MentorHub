#!/bin/bash
# =====================================================
# MentorHub - Port Validation Script
# Проверяет доступность всех портов из .env
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

check_port() {
    local port=$1
    local service_name=$2
    
    # Windows (через netstat)
    if command -v netstat &> /dev/null; then
        if netstat -an | grep -q ":${port} " 2>/dev/null; then
            echo -e "${RED}✗${NC} $service_name (порт ${YELLOW}$port${NC}) - ${RED}ЗАНЯТ${NC}"
            return 1
        fi
    fi
    
    # Linux/macOS (через ss)
    if command -v ss &> /dev/null; then
        if ss -tln | grep -q ":${port} " 2>/dev/null; then
            echo -e "${RED}✗${NC} $service_name (порт ${YELLOW}$port${NC}) - ${RED}ЗАНЯТ${NC}"
            return 1
        fi
    elif command -v lsof &> /dev/null; then
        if lsof -i :${port} &> /dev/null; then
            echo -e "${RED}✗${NC} $service_name (порт ${YELLOW}$port${NC}) - ${RED}ЗАНЯТ${NC}"
            return 1
        fi
    fi
    
    echo -e "${GREEN}✓${NC} $service_name (порт ${CYAN}$port${NC}) - свободен"
    return 0
}

# =====================================================
# ОСНОВНАЯ ЛОГИКА
# =====================================================

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║   🔍 MentorHub - Port Validation                           ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Загружаем переменные из .env
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} Загрузка из .env"
    export $(grep -v '^#' .env | xargs 2>/dev/null || true)
else
    echo -e "${YELLOW}⚠ .env не найден, используем дефолты${NC}"
fi

# Устанавливаем дефолты
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
DB_PORT="${DB_PORT:-5432}"
REDIS_PORT="${REDIS_PORT:-6379}"
NGINX_HTTP_PORT="${NGINX_HTTP_PORT:-80}"
NGINX_HTTPS_PORT="${NGINX_HTTPS_PORT:-443}"
PROMETHEUS_PORT="${PROMETHEUS_PORT:-9090}"
GRAFANA_PORT="${GRAFANA_PORT:-3001}"

echo ""
echo -e "${BLUE}📡 Проверка портов...${NC}"
echo ""

BUSY_PORTS=0

check_port $BACKEND_PORT "Backend API" || BUSY_PORTS=$((BUSY_PORTS + 1))
check_port $FRONTEND_PORT "Frontend (Next.js)" || BUSY_PORTS=$((BUSY_PORTS + 1))
check_port $DB_PORT "PostgreSQL" || BUSY_PORTS=$((BUSY_PORTS + 1))
check_port $REDIS_PORT "Redis" || BUSY_PORTS=$((BUSY_PORTS + 1))
check_port $NGINX_HTTP_PORT "Nginx HTTP" || BUSY_PORTS=$((BUSY_PORTS + 1))
check_port $NGINX_HTTPS_PORT "Nginx HTTPS" || BUSY_PORTS=$((BUSY_PORTS + 1))
check_port $PROMETHEUS_PORT "Prometheus" || BUSY_PORTS=$((BUSY_PORTS + 1))
check_port $GRAFANA_PORT "Grafana" || BUSY_PORTS=$((BUSY_PORTS + 1))

echo ""
echo -e "${YELLOW}════════════════════════════════════════════════════════════${NC}"

if [ $BUSY_PORTS -eq 0 ]; then
    echo -e "${GREEN}✅ Все порты свободны! Можно запускать.${NC}"
    echo ""
    echo -e "${CYAN}Запустите:${NC} make docker-up"
    exit 0
else
    echo -e "${RED}❌ Найдено занятыми $BUSY_PORTS порт(ов)${NC}"
    echo ""
    echo -e "${YELLOW}Варианты решения:${NC}"
    echo "  1. Остановите сервисы, использующие эти порты"
    echo "  2. Запустите ${CYAN}make ports-auto${NC} для автоподбора"
    echo "  3. Измените порты вручную в .env файле"
    exit 1
fi
