#!/bin/bash
# =====================================================
# MentorHub Startup Script
# С автоматическим определением свободного порта
# =====================================================

set -e

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

if [ -n "$PORT" ]; then
    PREFERRED_PORT=$PORT
elif [ -n "$BACKEND_PORT" ]; then
    PREFERRED_PORT=$BACKEND_PORT
else
    PREFERRED_PORT=8000
fi

FRONTEND_PORT="${FRONTEND_PORT:-3000}"

echo "========================================="
echo "🔍 MentorHub Port Detection"
echo "========================================="
echo "Preferred port: $PREFERRED_PORT"

if is_port_free $PREFERRED_PORT; then
    BACKEND_PORT=$PREFERRED_PORT
    echo "✅ Port $PREFERRED_PORT is available"
else
    echo "⚠️ Port $PREFERRED_PORT is in use, searching..."
    BACKEND_PORT=$(find_free_port $((PREFERRED_PORT + 1)))
    echo "✅ Found free port: $BACKEND_PORT"
fi

echo "========================================="
echo "🚀 Starting MentorHub..."
echo "========================================="
echo "Backend port:  $BACKEND_PORT"
echo "Frontend port: $FRONTEND_PORT"
echo "Environment:   ${ENVIRONMENT:-production}"
echo "========================================="

export PORT=$BACKEND_PORT
export BACKEND_PORT=$BACKEND_PORT

# =====================================================
# ЗАПУСК
# =====================================================

echo "📊 Database URL configured: ${DATABASE_URL%%:*}://***@${DATABASE_URL##*@}" 2>/dev/null || true
echo ""
echo "🎯 Starting Backend and Frontend..."
echo ""

# Backend
cd /app/backend
uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --workers 1 &
BACKEND_PID=$!

# Frontend
cd /app/frontend
node server.js &
FRONTEND_PID=$!

# Ожидание завершения
wait -n $BACKEND_PID $FRONTEND_PID
EXIT_CODE=$?

kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
exit $EXIT_CODE
