#!/bin/bash
# =====================================================
# MentorHub Startup Script
# С АВТОМАТИЧЕСКИМ ОПРЕДЕЛЕНИЕМ СВОБОДНОГО ПОРТА
# =====================================================
# Работает на: Render, Railway, Fly.io, VPS, Amvera, Heroku
# =====================================================

set -e

# =====================================================
# ФУНКЦИЯ ПОИСКА СВОБОДНОГО ПОРТА
# =====================================================

find_free_port() {
    local start_port=$1
    local max_attempts=${2:-100}
    local port=$start_port
    
    while [ $port -lt $((start_port + max_attempts)) ]; do
        # Проверяем, свободен ли порт
        if ! (echo > /dev/tcp/localhost/$port) 2>/dev/null; then
            # Порт закрыт = свободен для биндинга
            echo $port
            return 0
        fi
        port=$((port + 1))
    done
    
    # Fallback - возвращаем start_port если не нашли
    echo $start_port
    return 0
}

is_port_free() {
    local port=$1
    # Порт свободен если соединение не удаётся
    ! (echo > /dev/tcp/localhost/$port) 2>/dev/null
}

# =====================================================
# ОПРЕДЕЛЕНИЕ ПОРТА
# =====================================================

# Приоритет порта:
# 1. $PORT (устанавливается Render и другими облачными платформами)
# 2. $BACKEND_PORT
# 3. Дефолт 8000

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

# Проверяем, свободен ли предпочитаемый порт
if is_port_free $PREFERRED_PORT; then
    BACKEND_PORT=$PREFERRED_PORT
    echo "✅ Port $PREFERRED_PORT is available"
else
    echo "⚠️ Port $PREFERRED_PORT is in use, searching for free port..."
    
    # Ищем свободный порт
    BACKEND_PORT=$(find_free_port $((PREFERRED_PORT + 1)))
    
    # Порты которые нужно пропустить (заняты другими сервисами)
    for skip_port in 3000 3001 5432 6379; do
        if [ "$BACKEND_PORT" = "$skip_port" ]; then
            BACKEND_PORT=$((BACKEND_PORT + 1))
        fi
    done
    
    echo "✅ Found free port: $BACKEND_PORT"
fi

echo "========================================="
echo "🚀 Starting MentorHub..."
echo "========================================="
echo "Backend port:  $BACKEND_PORT"
echo "Frontend port: $FRONTEND_PORT"
echo "Environment:   ${ENVIRONMENT:-production}"
echo "========================================="

# Экспортируем порт для supervisor
export PORT=$BACKEND_PORT
export BACKEND_PORT=$BACKEND_PORT

# =====================================================
# Update Supervisor Configuration
# =====================================================

SUPERVISOR_CONF="/etc/supervisor/conf.d/app.conf"

if [ -f "$SUPERVISOR_CONF" ]; then
    echo "📝 Updating supervisor configuration..."

    # Заменяем плейсхолдер порта на реальное значение
    sed -i "s/%(ENV_BACKEND_PORT)s/$BACKEND_PORT/g" "$SUPERVISOR_CONF"
    sed -i "s/--port [0-9]*/--port $BACKEND_PORT/g" "$SUPERVISOR_CONF"
    sed -i "s/PORT=\"[0-9]*\"/PORT=\"$BACKEND_PORT\"/g" "$SUPERVISOR_CONF"

    echo "✅ Supervisor configuration updated with port $BACKEND_PORT"
else
    echo "⚠️ Supervisor config not found at $SUPERVISOR_CONF"
    echo "Creating inline configuration..."

    mkdir -p /var/log/supervisor

    cat > "$SUPERVISOR_CONF" << EOF
[supervisord]
nodaemon=true
logfile=/dev/null
pidfile=/var/run/supervisord.pid
user=root
loglevel=info

[program:backend]
command=uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT --workers 2 --timeout-graceful-shutdown 30
directory=/app/backend
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stopwaitsecs=35
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
environment=PORT="$BACKEND_PORT",PYTHONUNBUFFERED="1"

[program:frontend]
command=node server.js
directory=/app/frontend
environment=PORT="3000",NODE_ENV="production"
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stopwaitsecs=20
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
EOF

    echo "✅ Inline supervisor configuration created with port $BACKEND_PORT"
fi

# =====================================================
# Database Connection (опционально)
# =====================================================

if [ -n "$DATABASE_URL" ]; then
    echo "📊 Database URL configured: ${DATABASE_URL%%:*}://***@${DATABASE_URL##*@}"
fi

# =====================================================
# Start Supervisor
# =====================================================

echo ""
echo "🎯 Starting supervisor on port $BACKEND_PORT..."
echo ""

exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
