#!/bin/bash
# =====================================================
# MentorHub Startup Script
# С автоматическим определением свободного порта
# =====================================================

set -e

echo "========================================="
echo "🔍 MentorHub Environment Check"
echo "========================================="
echo "ENVIRONMENT: ${ENVIRONMENT:-not set}"
echo "PORT: ${PORT:-not set}"
echo "DATABASE_URL: ${DATABASE_URL:-not set}"
echo "SECRET_KEY: ${SECRET_KEY:+***SET***}"
echo "RENDER: ${RENDER:-not set}"
echo "========================================="

# Проверка критических переменных для production (предупреждение, не ошибка)
if [ "${ENVIRONMENT}" = "production" ] && [ -z "${DATABASE_URL}" ]; then
    echo "⚠️ WARNING: DATABASE_URL not set in production!"
    echo "   Add DATABASE_URL in Render Environment Variables."
    echo "   See deploy/render/README.md for instructions."
    echo "   Starting anyway without database..."
fi

if [ -z "${SECRET_KEY}" ]; then
    echo "⚠️ WARNING: SECRET_KEY not set, using temporary key"
fi

# =====================================================
# ПОИСК СВОБОДНОГО ПОРТА
# =====================================================

is_port_free() {
    local port=$1
    ! (echo > /dev/tcp/localhost/$port) 2>/dev/null
}

find_free_port() {
    local start_port=$1
    local max_attempts=${2:-100}
    local port=$start_port

    while [ $port -lt $((start_port + max_attempts)) ]; do
        if is_port_free $port; then
            echo $port
            return 0
        fi
        port=$((port + 1))
    done

    echo $start_port
    return 0
}

# =====================================================
# ОПРЕДЕЛЕНИЕ ПОРТА
# =====================================================

# Render устанавливает PORT=3000 для frontend
# BACKEND_PORT используется для backend (по умолчанию 8000)
FRONTEND_PORT="${PORT:-${FRONTEND_PORT:-3000}}"
BACKEND_PORT="${BACKEND_PORT:-8000}"

echo "========================================="
echo "🔍 MentorHub Port Detection"
echo "========================================="
echo "Frontend port: $FRONTEND_PORT"
echo "Backend port: $BACKEND_PORT"

if is_port_free $FRONTEND_PORT; then
    echo "✅ Frontend port $FRONTEND_PORT is available"
else
    echo "⚠️ Frontend port $FRONTEND_PORT is in use, searching..."
    FRONTEND_PORT=$(find_free_port $((FRONTEND_PORT + 1)))
    echo "✅ Found free port: $FRONTEND_PORT"
fi

if is_port_free $BACKEND_PORT; then
    echo "✅ Backend port $BACKEND_PORT is available"
else
    echo "⚠️ Backend port $BACKEND_PORT is in use, searching..."
    BACKEND_PORT=$(find_free_port $((BACKEND_PORT + 1)))
    echo "✅ Found free port: $BACKEND_PORT"
fi

echo "========================================="
echo "🚀 Starting MentorHub..."
echo "========================================="
echo "Frontend port: $FRONTEND_PORT"
echo "Backend port:  $BACKEND_PORT"
echo "Environment:   ${ENVIRONMENT:-production}"
echo "========================================="

export PORT=$FRONTEND_PORT
export BACKEND_PORT=$BACKEND_PORT
export FRONTEND_PORT=$FRONTEND_PORT

# =====================================================
# DATABASE WAIT (опционально)
# =====================================================

if [ -n "$DATABASE_URL" ]; then
    echo "📊 Database URL configured: ${DATABASE_URL%%:*}://***@${DATABASE_URL##*@}"
    echo "⏳ Waiting for database..."
    
    # Extract host from DATABASE_URL
    DB_HOST=$(echo $DATABASE_URL | sed -E 's|.*@([^:/]+).*|\1|')
    DB_PORT=$(echo $DATABASE_URL | sed -E 's|.*:([0-9]+)/.*|\1|')
    DB_PORT=${DB_PORT:-5432}
    
    # Wait for database with timeout
    for i in $(seq 1 30); do
        if (echo > /dev/tcp/$DB_HOST/$DB_PORT) 2>/dev/null; then
            echo "✅ Database is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "⚠️ Database not ready, continuing anyway..."
        fi
        sleep 1
    done
else
    echo "⚠️ DATABASE_URL not set"
fi

echo ""
echo "🎯 Starting Backend and Frontend..."
echo ""

# Export all environment variables for child processes
export BACKEND_PORT=$BACKEND_PORT
export FRONTEND_PORT=$FRONTEND_PORT
export PGPASSWORD="${POSTGRES_PASSWORD:-}"

# Backend - запускаем с явным указанием переменных окружения
cd /app/backend
echo "🚀 Starting backend on port $BACKEND_PORT..."
PORT=$BACKEND_PORT uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --workers 1 &
BACKEND_PID=$!

# Frontend - запускаем всегда (и в Docker, и в Render)
cd /app/frontend
echo "🚀 Starting frontend on port $FRONTEND_PORT..."
PORT=$FRONTEND_PORT node server.js &
FRONTEND_PID=$!

# Ожидание завершения
wait $BACKEND_PID $FRONTEND_PID
EXIT_CODE=$?

kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true

exit $EXIT_CODE
