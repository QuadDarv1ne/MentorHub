#!/bin/bash
# =====================================================
# MentorHub Development Startup Script
# Platforms: Linux, macOS, WSL
# Запускает: Backend (FastAPI) + Frontend (Next.js)
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
echo -e "${CYAN}║        🚀 MentorHub - Development Mode                     ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 не найден. Установите Python 3.10+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python: ${PYTHON_VERSION}"

# Проверка Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js не найден. Установите Node.js 18+${NC}"
    exit 1
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

# Проверка uvicorn
if ! python3 -m uvicorn --version &> /dev/null; then
    echo -e "${YELLOW}⚠ Uvicorn не найден. Установка...${NC}"
    pip3 install uvicorn[standard] fastapi
fi

echo ""

# =====================================================
# ЗАГРУЗКА .ENV
# =====================================================

if [ -f .env ]; then
    echo -e "${GREEN}✓${NC} Загрузка переменных из .env"
    export $(grep -v '^#' .env | xargs)
fi

# =====================================================
# ЗАПУСК BACKEND
# =====================================================

echo ""
echo -e "${CYAN}📡 Запуск Backend (FastAPI) на порту 8000...${NC}"

cd backend

# Установка зависимостей Python если нужно
if [ ! -d "__pycache__" ] || [ ! -f "pyproject.toml" ]; then
    echo -e "${YELLOW}⚠ Установка Python зависимостей...${NC}"
    pip3 install -e . 2>/dev/null || true
fi

# Запуск backend в фоне
PORT=8000 uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

echo -e "${GREEN}✓${NC} Backend запущен (PID: ${BACKEND_PID})"
echo -e "   URL: ${CYAN}http://127.0.0.1:8000${NC}"
echo -e "   API Docs: ${CYAN}http://127.0.0.1:8000/docs${NC}"

cd ..

# =====================================================
# ЗАПУСК FRONTEND
# =====================================================

echo ""
echo -e "${CYAN}🎨 Запуск Frontend (Next.js) на порту 3001...${NC}"

cd frontend

# Установка зависимостей Node.js если нужно
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠ Установка Node.js зависимостей...${NC}"
    npm install
fi

# Запуск frontend в фоне
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
echo -e "   Backend API:    ${CYAN}http://127.0.0.1:8000${NC}"
echo -e "   API Docs:       ${CYAN}http://127.0.0.1:8000/docs${NC}"
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
