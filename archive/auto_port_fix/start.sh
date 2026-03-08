#!/bin/bash
# =====================================================
# MentorHub Startup Script
# С АВТОМАТИЧЕСКИМ ОПРЕДЕЛЕНИЕМ СВОБОДНОГО ПОРТА
# =====================================================
# Поддержка: Render, Railway, Fly.io, VPS, Amvera, Heroku
# Особенности:
#   - Автоматический поиск свободного порта
#   - Graceful shutdown
#   - Совместимость с облачными платформами
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
        if ! lsof -i :$port > /dev/null 2>&1; then
            echo $port
            return 0
        fi
        port=$((port + 1))
    done
    
    echo "ERROR: No free port found in range $start_port-$((start_port + max_attempts))" >&2
    return 1
}

is_port_available() {
    local port=$1
    ! lsof -i :$port > /dev/null 2>&1
}

wait_for_port_release() {
    local port=$1
    local timeout=${2:-30}
    local elapsed=0
    
    echo "⏳ Waiting for port $port to be released..."
    
    while [ $elapsed -lt $timeout ]; do
        if is_port_available $port; then
            echo "✅ Port $port is now available"
            return 0
        fi
        sleep 0.5
        elapsed=$((elapsed + 1))
    done
    
    echo "⚠️ Timeout waiting for port $port"
    return 1
}

# =====================================================
# ОПРЕДЕЛЕНИЕ ПОРТА
# =====================================================

# Список портов, которые нужно исключить (уже используются)
EXCLUDE_PORTS="3000 12600 19001 19005 19006 6060 6061 81"

# Приоритет порта:
# 1. Переменная окружения PORT (для облачных платформ)
# 2. BACKEND_PORT
# 3. Дефолт 8000

if [ -n "$PORT" ]; then
    PREFERRED_PORT=$PORT
elif [ -n "$BACKEND_PORT" ]; then
    PREFERRED_PORT=$BACKEND_PORT
else
    PREFERRED_PORT=8000
fi

echo "========================================="
echo "🔍 MentorHub Port Detection"
echo "========================================="
echo "Preferred port: $PREFERRED_PORT"

# Проверяем, свободен ли предпочитаемый порт
if is_port_available $PREFERRED_PORT; then
    BACKEND_PORT=$PREFERRED_PORT
    echo "✅ Port $PREFERRED_PORT is available"
else
    echo "⚠️ Port $PREFERRED_PORT is in use, searching for free port..."
    
    # Ищем свободный порт, исключая занятые
    BACKEND_PORT=""
    for port in $(seq $((PREFERRED_PORT + 1)) $((PREFERRED_PORT + 100))); do
        # Проверяем, не в списке исключений
        skip=false
        for exclude in $EXCLUDE_PORTS; do
            if [ "$port" = "$exclude" ]; then
                skip=true
                break
            fi
        done
        
        if [ "$skip" = false ] && is_port_available $port; then
            BACKEND_PORT=$port
            echo "✅ Found free port: $BACKEND_PORT"
            break
        fi
    done
    
    if [ -z "$BACKEND_PORT" ]; then
        echo "❌ ERROR: Could not find a free port!"
        exit 1
    fi
fi

FRONTEND_PORT="${FRONTEND_PORT:-3000}"

echo "========================================="
echo "🚀 Starting MentorHub..."
echo "========================================="
echo "Backend port:  $BACKEND_PORT"
echo "Frontend port: $FRONTEND_PORT"
echo "Environment:   ${ENVIRONMENT:-production}"
echo "========================================="

# Экспортируем порт для дочерних процессов
export PORT=$BACKEND_PORT
export BACKEND_PORT=$BACKEND_PORT

# =====================================================
# ОБНОВЛЕНИЕ КОНФИГУРАЦИИ SUPERVISOR
# =====================================================

SUPERVISOR_CONF="/etc/supervisor/conf.d/app.conf"

if [ -f "$SUPERVISOR_CONF" ]; then
    echo "📝 Updating supervisor configuration..."
    
    # Заменяем порт в конфигурации
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
# ЗАПУСК
# =====================================================

# Если нужно остановить конфликтующий процесс
# (раскомментировать если требуется)
# pkill -f "uvicorn.*:8000" 2>/dev/null || true

echo ""
echo "🎯 Starting supervisor..."
echo ""

# КРИТИЧНО: exec заменяет текущий shell на supervisord
# Это позволяет сигналам SIGTERM/SIGINT достигать supervisord
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
