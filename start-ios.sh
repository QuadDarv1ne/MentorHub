#!/usr/bin/bash
# =====================================================
# MentorHub iOS Startup Script
# Platform: iOS (iSH Shell)
# Запускает: Backend (FastAPI) + Frontend (Next.js)
# =====================================================

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# =====================================================
# ПРОВЕРКА ОКРУЖЕНИЯ ISH
# =====================================================

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║        🚀 MentorHub - iOS (iSH)                            ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Проверка Alpine Linux (iSH)
if [ -f /etc/alpine-release ]; then
    echo -e "${GREEN}✓${NC} iSH Shell detected (Alpine Linux)"
fi

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 не найден. Установка...${NC}"
    apk update && apk add python3 py3-pip
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓${NC} Python: ${PYTHON_VERSION}"

# Проверка Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js не найден. Установка...${NC}"
    apk update && apk add nodejs npm
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✓${NC} Node.js: ${NODE_VERSION}"

# Проверка npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm не найден${NC}"
    exit 1
fi

NPM_VERSION=$(npm --version)
echo -e "${GREEN}✓${NC} npm: ${NPM_VERSION}"

# Проверка Git
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}⚠ Git не установлен (рекомендуется для клонирования)${NC}"
fi

echo ""

# =====================================================
# УСТАНОВКА ЗАВИСИМОСТЕЙ
# =====================================================

echo -e "${CYAN}📦 Установка зависимостей...${NC}"

# Python зависимости
echo -e "${YELLOW}⏳ Установка Python зависимостей...${NC}"
cd backend
pip3 install -e . --quiet 2>/dev/null || pip3 install uvicorn fastapi python-dotenv
cd ..

# Node.js зависимости
echo -e "${YELLOW}⏳ Установка Node.js зависимостей...${NC}"
cd frontend
npm install --silent 2>/dev/null || npm install
cd ..

echo -e "${GREEN}✓${NC} Зависимости установлены"
echo ""

# =====================================================
# ЗАГРУЗКА .ENV
# =====================================================

if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ .env файл не найден. Копирование из .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠ Отредактируйте .env файл${NC}"
fi

# =====================================================
# ЗАПУСК BACKEND
# =====================================================

echo ""
echo -e "${CYAN}📡 Запуск Backend (FastAPI) на порту 8000...${NC}"

cd backend

# Оптимизация для iOS
export PYTHONDONTWRITEBYTECODE=1

# Запуск backend
PORT=8000 python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo -e "${GREEN}✓${NC} Backend запущен (PID: ${BACKEND_PID})"
echo -e "   URL: ${CYAN}http://localhost:8000${NC}"
echo -e "   API Docs: ${CYAN}http://localhost:8000/docs${NC}"

cd ..

# =====================================================
# ЗАПУСК FRONTEND
# =====================================================

echo ""
echo -e "${CYAN}🎨 Запуск Frontend (Next.js) на порту 3001...${NC}"

cd frontend

# Оптимизация памяти для iOS
export NODE_OPTIONS="--max-old-space-size=256"

# Запуск frontend
PORT=3001 npm run dev &
FRONTEND_PID=$!

echo -e "${GREEN}✓${NC} Frontend запущен (PID: ${FRONTEND_PID})"
echo -e "   URL: ${CYAN}http://localhost:3001${NC}"

cd ..

# =====================================================
# ИНФОРМАЦИЯ
# =====================================================

echo ""
echo -e "${YELLOW}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Серверы запущены${NC}"
echo ""
echo -e "${CYAN}📍 URLs:${NC}"
echo -e "   Backend API:    ${CYAN}http://localhost:8000${NC}"
echo -e "   API Docs:       ${CYAN}http://localhost:8000/docs${NC}"
echo -e "   Frontend:       ${CYAN}http://localhost:3001${NC}"
echo ""
echo -e "${YELLOW}⚠ Ограничения iSH:${NC}"
echo -e "   - Производительность ограничена эмуляцией${NC}"
echo -e "   - Рекомендуется для тестирования, не production${NC}"
echo ""
echo -e "${YELLOW}🛑 Остановка: Ctrl+C${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════════${NC}"
echo ""

# =====================================================
# ОБРАБОТКА SIGTERM/SIGINT
# =====================================================

cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Остановка сервисов...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Все сервисы остановлены"
    exit 0
}

trap cleanup SIGTERM SIGINT EXIT

# Ожидание завершения процессов
wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
