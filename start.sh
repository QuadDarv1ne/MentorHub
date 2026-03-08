#!/bin/bash
# =====================================================
# MentorHub Startup Script
# =====================================================

set -e

# =====================================================
# ОПРЕДЕЛЕНИЕ ПОРТА
# =====================================================

if [ -n "$PORT" ]; then
    BACKEND_PORT=$PORT
elif [ -n "$BACKEND_PORT" ]; then
    BACKEND_PORT=$BACKEND_PORT
else
    BACKEND_PORT=8000
fi

FRONTEND_PORT="${FRONTEND_PORT:-3000}"

echo "========================================="
echo "🚀 Starting MentorHub..."
echo "========================================="
echo "Backend port:  $BACKEND_PORT"
echo "Frontend port: $FRONTEND_PORT"
echo "Environment:   ${ENVIRONMENT:-production}"
echo "========================================="

# Экспортируем переменные
export PORT=$BACKEND_PORT
export BACKEND_PORT=$BACKEND_PORT

# =====================================================
# Запуск Backend и Frontend
# =====================================================

echo "📊 Database URL configured: ${DATABASE_URL%%:*}://***@${DATABASE_URL##*@}" 2>/dev/null || true

echo ""
echo "🎯 Starting Backend and Frontend..."
echo ""

# Запускаем backend в фоне
cd /app/backend
uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --workers 1 &
BACKEND_PID=$!

# Запускаем frontend
cd /app/frontend
node server.js &
FRONTEND_PID=$!

# Ожидаем завершения любого из процессов
wait -n $BACKEND_PID $FRONTEND_PID
EXIT_CODE=$?

# Завершаем оба процесса
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
exit $EXIT_CODE
