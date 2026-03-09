#!/bin/bash
# =====================================================
# MentorHub Startup Script - Optimized for Render
# Исправлено: порты, line endings, hostname binding
# =====================================================

set -e

echo "========================================="
echo "🔍 MentorHub Environment Check"
echo "========================================="
echo "ENVIRONMENT: ${ENVIRONMENT:-not set}"
echo "PORT: ${PORT:-not set}"
echo "DATABASE_URL: ${DATABASE_URL:+***SET***}"
echo "SECRET_KEY: ${SECRET_KEY:+***SET***}"
echo "RENDER: ${RENDER:-not set}"
echo "========================================="

# Оптимизация памяти для Node.js (Frontend)
export NODE_OPTIONS="--max-old-space-size=256 --optimize-for-size"

# Оптимизация для Python (Backend)
export PYTHONMALLOC=malloc
export MALLOC_ARENA_MAX=2
export PYTHONDONTWRITEBYTECODE=1

# =====================================================
# ОПРЕДЕЛЕНИЕ ПОРТОВ
# =====================================================

# Render устанавливает PORT - это порт для frontend
# Backend использует внутренний порт BACKEND_PORT
export FRONTEND_PORT="${PORT:-3000}"
export BACKEND_PORT="${BACKEND_PORT:-8000}"

# Важно: hostname должен быть 0.0.0.0 для доступности извне
export HOSTNAME="0.0.0.0"

echo "========================================="
echo "🚀 Starting MentorHub..."
echo "========================================="
echo "Frontend port: $FRONTEND_PORT"
echo "Backend port:  $BACKEND_PORT"
echo "Hostname:      $HOSTNAME"
echo "Environment:   ${ENVIRONMENT:-production}"
echo "========================================="

# =====================================================
# DATABASE WAIT (опционально)
# =====================================================

if [ -n "$DATABASE_URL" ]; then
    echo "📊 Database configured"
    echo "⏳ Waiting for database..."
    
    # Extract host from DATABASE_URL
    DB_HOST=$(echo $DATABASE_URL | sed -E 's|.*@([^:/]+).*|\1|')
    DB_PORT=$(echo $DATABASE_URL | sed -E 's|.*:([0-9]+)/.*|\1|')
    DB_PORT=${DB_PORT:-5432}
    
    # Wait for database with timeout
    for i in $(seq 1 30); do
        if nc -z $DB_HOST $DB_PORT 2>/dev/null; then
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

# =====================================================
# START BACKEND
# =====================================================

echo ""
echo "🚀 Starting backend on port $BACKEND_PORT..."

if [ -d "/app/backend" ]; then
    cd /app/backend
    echo "   Backend directory: /app/backend"
    echo "   Backend URL: http://$HOSTNAME:$BACKEND_PORT"
    
    PORT=$BACKEND_PORT uvicorn app.main:app \
        --host 0.0.0.0 \
        --port $BACKEND_PORT \
        --workers 1 \
        --no-access-log \
        --loop asyncio \
        &
    BACKEND_PID=$!
    echo "   ✅ Backend started (PID: $BACKEND_PID)"
else
    echo "   ⚠️ WARNING: Backend directory not found!"
    ls -la /app/
fi

# =====================================================
# START FRONTEND
# =====================================================

echo ""
echo "🚀 Starting frontend on port $FRONTEND_PORT..."

if [ -f "/app/frontend/server.js" ]; then
    cd /app/frontend
    echo "   Frontend directory: /app/frontend"
    echo "   Frontend URL: http://$HOSTNAME:$FRONTEND_PORT"
    
    # Критически важно: PORT и HOSTNAME для Next.js standalone
    export PORT=$FRONTEND_PORT
    export HOSTNAME="0.0.0.0"
    
    node server.js &
    FRONTEND_PID=$!
    echo "   ✅ Frontend started (PID: $FRONTEND_PID)"
else
    echo "   ⚠️ WARNING: Frontend server.js not found!"
    ls -la /app/frontend/ || true
fi

echo ""
echo "✅ Services started:"
echo "   Backend PID: $BACKEND_PID on port $BACKEND_PORT"
echo "   Frontend PID: $FRONTEND_PID on port $FRONTEND_PORT"
echo ""

# =====================================================
# HEALTH CHECK LOG
# =====================================================

# Даём сервисам время запуститься
sleep 5

# Проверяем что сервисы отвечают
echo "🏥 Health check..."
curl -s http://localhost:$FRONTEND_PORT/ > /dev/null && echo "   ✅ Frontend responding" || echo "   ⚠️ Frontend not responding"
curl -s http://localhost:$BACKEND_PORT/api/v1/health > /dev/null && echo "   ✅ Backend responding" || echo "   ⚠️ Backend not responding"

echo ""
echo "🎉 MentorHub is ready!"
echo "   Public URL: ${RENDER_EXTERNAL_URL:-http://localhost:$FRONTEND_PORT}"
echo ""

# =====================================================
# KEEP ALIVE
# =====================================================

# Ожидание завершения процессов
wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true

# Если процессы завершились, держим контейнер живым
echo "⚠️ Processes ended, keeping container alive..."
tail -f /dev/null
