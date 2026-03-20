#!/bin/bash
# =====================================================
# MentorHub Production Startup Script
# Platforms: Linux, macOS, WSL
# Запускает: Docker Compose (все сервисы)
# =====================================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# =====================================================
# ПРОВЕРКА ОКРУЖЕНИЯ
# =====================================================

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║        🚀 MentorHub - Production Mode                      ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker не найден. Установите Docker${NC}"
    exit 1
fi

DOCKER_VERSION=$(docker --version)
echo -e "${GREEN}✓${NC} Docker: ${DOCKER_VERSION}"

# Проверка Docker Compose
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose не найден${NC}"
    exit 1
fi

COMPOSE_VERSION=$(docker compose version)
echo -e "${GREEN}✓${NC} Docker Compose: ${COMPOSE_VERSION}"

echo ""

# =====================================================
# ЗАГРУЗКА .ENV
# =====================================================

if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env файл не найден. Копирование из .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠ Отредактируйте .env файл и запустите скрипт снова${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Загрузка переменных из .env"
export $(grep -v '^#' .env | xargs)

# Проверка обязательных переменных
if [ -z "$SECRET_KEY" ]; then
    echo -e "${RED}❌ SECRET_KEY не установлен в .env${NC}"
    exit 1
fi

if [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}❌ DB_PASSWORD не установлен в .env${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Все обязательные переменные установлены"

# =====================================================
# ЗАПУСК DOCKER COMPOSE
# =====================================================

echo ""
echo -e "${CYAN}🐳 Запуск Docker Compose сервисов...${NC}"
echo ""

# Остановка старых контейнеров
echo -e "${YELLOW}⏳ Остановка существующих сервисов...${NC}"
docker compose -f docker-compose.prod.yml down 2>/dev/null || true

# Запуск сервисов
echo -e "${CYAN}🚀 Запуск сервисов в production режиме...${NC}"
docker compose -f docker-compose.prod.yml up -d --build

# =====================================================
# ПРОВЕРКА СТАТУСА
# =====================================================

echo ""
echo -e "${CYAN}📊 Проверка статуса сервисов...${NC}"
echo ""

sleep 5

docker compose -f docker-compose.prod.yml ps

# =====================================================
# ИНФОРМАЦИЯ
# =====================================================

echo ""
echo -e "${YELLOW}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ MentorHub запущен в production режиме${NC}"
echo ""
echo -e "${CYAN}📍 URLs:${NC}"
echo -e "   Frontend:       ${CYAN}http://localhost${NC}"
echo -e "   Backend API:    ${CYAN}http://localhost/api/v1${NC}"
echo -e "   API Docs:       ${CYAN}http://localhost/docs${NC}"
echo -e "   Grafana:        ${CYAN}http://localhost:3001${NC}"
echo -e "   Prometheus:     ${CYAN}http://localhost:9090${NC}"
echo ""
echo -e "${YELLOW}🛑 Остановка:${NC}"
echo -e "   ${CYAN}docker compose -f docker-compose.prod.yml down${NC}"
echo ""
echo -e "${YELLOW}📋 Логи:${NC}"
echo -e "   ${CYAN}docker compose -f docker-compose.prod.yml logs -f${NC}"
echo ""
echo -e "${YELLOW}════════════════════════════════════════════════════════════${NC}"
echo ""
