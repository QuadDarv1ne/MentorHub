#!/bin/bash
# =====================================================
# MentorHub Startup Script - Nginx Reverse Proxy
# Запускает: Nginx (PORT) + Backend (8000) + Frontend (3000)
# =====================================================

set -e

echo "========================================="
echo "🔍 MentorHub Environment Check"
echo "========================================="
echo "ENVIRONMENT: ${ENVIRONMENT:-not set}"
echo "PORT: ${PORT:-not set} (Render выделяет этот порт)"
echo "DATABASE_URL: ${DATABASE_URL:+***SET***}"
echo "SECRET_KEY: ${SECRET_KEY:+***SET***}"
echo "RENDER: ${RENDER:-not set}"
echo "========================================="

# Оптимизация памяти для Node.js (Frontend)
export NODE_OPTIONS="--max-old-space-size=256"

# Оптимизация для Python (Backend)
export PYTHONMALLOC=malloc
export MALLOC_ARENA_MAX=2
export PYTHONDONTWRITEBYTECODE=1

# =====================================================
# ОПРЕДЕЛЕНИЕ ПОРТОВ
# =====================================================

# Render устанавливает PORT - nginx будет слушать на этом порту
# Backend и Frontend работают на внутренних портах
export NGINX_PORT="${PORT:-8000}"
export BACKEND_PORT="8000"
export FRONTEND_PORT="3000"

# Важно: hostname должен быть 0.0.0.0 для доступности извне
export HOSTNAME="0.0.0.0"

echo "========================================="
echo "🚀 Starting MentorHub..."
echo "========================================="
echo "Nginx port:    $NGINX_PORT (external - Render PORT)"
echo "Backend port:  $BACKEND_PORT (internal)"
echo "Frontend port: $FRONTEND_PORT (internal)"
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
# START BACKEND (на порту 8000)
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
    exit 1
fi

# =====================================================
# START FRONTEND (на порту 3000)
# =====================================================

echo ""
echo "🚀 Starting frontend on port $FRONTEND_PORT..."

if [ -f "/app/frontend/server.js" ]; then
    cd /app/frontend
    echo "   Frontend directory: /app/frontend"
    echo "   Frontend URL: http://$HOSTNAME:$FRONTEND_PORT"

    export PORT=$FRONTEND_PORT
    export HOSTNAME="0.0.0.0"

    node server.js &
    FRONTEND_PID=$!
    echo "   ✅ Frontend started (PID: $FRONTEND_PID)"
else
    echo "   ⚠️ WARNING: Frontend server.js not found!"
    echo "   Checking /app/frontend:"
    ls -la /app/frontend/ || true
    exit 1
fi

# =====================================================
# START NGINX (на порту Render)
# =====================================================

echo ""
echo "🚀 Starting nginx on port $NGINX_PORT..."

# Подготавливаем nginx конфигурацию - заменяем порт 8000 на актуальный PORT
sed -i "s/listen 8000;/listen $NGINX_PORT;/g" /etc/nginx/nginx.conf
sed -i "s/listen \[::\]:8000;/listen [::]:$NGINX_PORT;/g" /etc/nginx/nginx.conf

echo "   Nginx configuration updated for port $NGINX_PORT"
echo "   Nginx URL: http://$HOSTNAME:$NGINX_PORT"

# Запускаем nginx
nginx -g "daemon off;" &
NGINX_PID=$!
echo "   ✅ Nginx started (PID: $NGINX_PID)"

# =====================================================
# HEALTH CHECK LOG
# =====================================================

echo ""
echo "✅ Services started:"
echo "   Backend PID:  $BACKEND_PID on port $BACKEND_PORT"
echo "   Frontend PID: $FRONTEND_PID on port $FRONTEND_PORT"
echo "   Nginx PID:    $NGINX_PID on port $NGINX_PORT (external)"
echo ""

# Даём сервисам время запуститься
sleep 8

# Проверяем что сервисы отвечают
echo "🏥 Health check..."

# Проверка backend
if curl -s http://localhost:$BACKEND_PORT/api/v1/health > /dev/null 2>&1; then
    echo "   ✅ Backend responding"
else
    echo "   ⚠️ Backend not responding"
fi

# Проверка frontend
if curl -s http://localhost:$FRONTEND_PORT/ > /dev/null 2>&1; then
    echo "   ✅ Frontend responding"
else
    echo "   ⚠️ Frontend not responding"
fi

# Проверка nginx (external port)
if curl -s http://localhost:$NGINX_PORT/nginx-health > /dev/null 2>&1; then
    echo "   ✅ Nginx responding"
elif curl -s http://localhost:$NGINX_PORT/api/v1/health > /dev/null 2>&1; then
    echo "   ✅ Nginx proxy working (API accessible)"
else
    echo "   ⚠️ Nginx not responding on port $NGINX_PORT"
fi

echo ""
echo "🎉 MentorHub is ready!"
echo "   Public URL: ${RENDER_EXTERNAL_URL:-http://localhost:$NGINX_PORT}"
echo "   API URL:    ${RENDER_EXTERNAL_URL:-http://localhost:$NGINX_PORT}/api/v1"
echo ""

# =====================================================
# KEEP ALIVE
# =====================================================

# Ожидание завершения процессов
wait $BACKEND_PID $FRONTEND_PID $NGINX_PID 2>/dev/null || true

# Если процессы завершились, держим контейнер живым
echo "⚠️ Processes ended, keeping container alive..."
tail -f /dev/null
