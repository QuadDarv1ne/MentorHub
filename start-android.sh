#!/data/data/com.termux/files/usr/bin/bash
# =====================================================
# MentorHub Android Startup Script
# Platform: Android (Termux)
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
# ПРОВЕРКА ОКРУЖЕНИЯ TORMUX
# =====================================================

echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║        🚀 MentorHub - Android (Termux)                     ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Проверка Termux
if [ ! -d "/data/data/com.termux" ]; then
    echo -e "${YELLOW}⚠ Этот скрипт предназначен для Termux${NC}"
    echo -e "${YELLOW}  Запустите его в приложении Termux на Android${NC}"
fi

# Проверка Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python не найден. Установка...${NC}"
    pkg update && pkg install python -y
fi

PYTHON_VERSION=$(python --version)
echo -e "${GREEN}✓${NC} Python: ${PYTHON_VERSION}"

# Проверка Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js не найден. Установка...${NC}"
    pkg update && pkg install nodejs -y
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

# Проверка PostgreSQL клиент
if ! command -v psql &> /dev/null; then
    echo -e "${YELLOW}⚠ PostgreSQL клиент не установлен (опционально)${NC}"
fi

echo ""

# =====================================================
# УСТАНОВКА ЗАВИСИМОСТЕЙ
# =====================================================

echo -e "${CYAN}📦 Установка зависимостей...${NC}"

# Python зависимости
echo -e "${YELLOW}⏳ Установка Python зависимостей...${NC}"
cd backend
pip install -e . --quiet
cd ..

# Node.js зависимости
echo -e "${YELLOW}⏳ Установка Node.js зависимостей...${NC}"
cd frontend
npm install --silent
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
echo -e "${CYAN}📡 Запуск Backend (FastAPI) на порту 8001...${NC}"

cd backend

# Оптимизация памяти для Android
export PYTHONMALLOC=malloc
export PYTHONDONTWRITEBYTECODE=1

# Запуск backend
PORT=8001 uvicorn app.main:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!

echo -e "${GREEN}✓${NC} Backend запущен (PID: ${BACKEND_PID})"
echo -e "   URL: ${CYAN}http://localhost:8001${NC}"
echo -e "   API Docs: ${CYAN}http://localhost:8001/docs${NC}"

cd ..

# =====================================================
# ЗАПУСК FRONTEND
# =====================================================

echo ""
echo -e "${CYAN}🎨 Запуск Frontend (Next.js) на порту 3001...${NC}"

cd frontend

# Оптимизация памяти для Android
export NODE_OPTIONS="--max-old-space-size=512"

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
echo -e "   Backend API:    ${CYAN}http://localhost:8001${NC}"
echo -e "   API Docs:       ${CYAN}http://localhost:8001/docs${NC}"
echo -e "   Frontend:       ${CYAN}http://localhost:3001${NC}"
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
