#!/bin/bash
# =====================================================
# MentorHub Startup Script
# Universal startup for all cloud platforms
# Supports: Render, Railway, Fly.io, VPS, Amvera, Heroku
# =====================================================

set -e

# =====================================================
# Configuration
# =====================================================

# Backend port: приоритет у $PORT (для Render/Railway/Heroku)
# Затем BACKEND_PORT, затем дефолт 8000
BACKEND_PORT="${PORT:-${BACKEND_PORT:-8000}}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

echo "========================================="
echo "🚀 Starting MentorHub..."
echo "========================================="
echo "Backend port:  $BACKEND_PORT"
echo "Frontend port: $FRONTEND_PORT"
echo "Environment:   ${ENVIRONMENT:-production}"
echo "========================================="

# =====================================================
# Update Supervisor Configuration
# =====================================================

SUPERVISOR_CONF="/etc/supervisor/conf.d/app.conf"

if [ -f "$SUPERVISOR_CONF" ]; then
    echo "📝 Updating supervisor configuration..."

    # Заменяем плейсхолдер порта на реальное значение
    # Поддерживаем разные форматы конфигурации
    sed -i "s/%(ENV_BACKEND_PORT)s/$BACKEND_PORT/g" "$SUPERVISOR_CONF"
    sed -i "s/--port [0-9]*/--port $BACKEND_PORT/g" "$SUPERVISOR_CONF"
    sed -i "s/PORT=\"[0-9]*\"/PORT=\"$BACKEND_PORT\"/g" "$SUPERVISOR_CONF"

    echo "✅ Supervisor configuration updated"
else
    echo "⚠️ Supervisor config not found at $SUPERVISOR_CONF"
    echo "Creating inline configuration..."

    # Fallback: создаём конфигурацию на лету (для обратной совместимости)
    mkdir -p /var/log/supervisor

    cat > "$SUPERVISOR_CONF" << 'EOF'
[supervisord]
nodaemon=true
logfile=/dev/null
pidfile=/var/run/supervisord.pid
user=root
loglevel=info

[program:backend]
command=uvicorn app.main:app --host 0.0.0.0 --port BACKEND_PORT_PLACEHOLDER --workers 2 --timeout-graceful-shutdown 30
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
environment=PORT="BACKEND_PORT_PLACEHOLDER",PYTHONUNBUFFERED="1"

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

    # Заменяем плейсхолдеры
    sed -i "s/BACKEND_PORT_PLACEHOLDER/$BACKEND_PORT/g" "$SUPERVISOR_CONF"
    echo "✅ Inline supervisor configuration created"
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
echo "🎯 Starting supervisor..."
echo ""

# КРИТИЧНО: exec заменяет текущий shell процесс на supervisord
# Это позволяет сигналам SIGTERM/SIGINT достигать supervisord напрямую
# Без exec сигнал пришёл бы в shell скрипт, а не в supervisor
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
