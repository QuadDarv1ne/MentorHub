#!/bin/bash
# =====================================================
# MentorHub Startup Script - Nginx Reverse Proxy
# Starts: Nginx (PORT) + Backend (8000) + Frontend (3000)
# Works with both Render and Amvera Cloud
# =====================================================

set -e

echo "========================================="
echo "MentorHub Environment Check"
echo "========================================="
echo "ENVIRONMENT: ${ENVIRONMENT:-not set}"
echo "PORT: ${PORT:-not set}"
echo "DATABASE_URL: ${DATABASE_URL:+***SET***}"
echo "SECRET_KEY: ${SECRET_KEY:+***SET***}"
echo "========================================="

# Node.js memory optimization (Frontend)
export NODE_OPTIONS="--max-old-space-size=256"

# Python optimization (Backend)
export PYTHONMALLOC=malloc
export MALLOC_ARENA_MAX=2
export PYTHONDONTWRITEBYTECODE=1

# =====================================================
# PORT DEFINITION
# =====================================================

# Use PORT from environment (set by Render/Amvera) or default to 8000
export NGINX_PORT="${PORT:-8000}"
export BACKEND_PORT="8001"
export FRONTEND_PORT="3000"

# Host must be 0.0.0.0 for external access
export HOSTNAME="0.0.0.0"

echo "========================================="
echo "Starting MentorHub..."
echo "========================================="
echo "Nginx port:    $NGINX_PORT (external)"
echo "Backend port:  $BACKEND_PORT (internal)"
echo "Frontend port: $FRONTEND_PORT (internal)"
echo "Hostname:      $HOSTNAME"
echo "Environment:   ${ENVIRONMENT:-production}"
echo "========================================="

# =====================================================
# DATABASE WAIT (optional)
# =====================================================

if [ -n "$DATABASE_URL" ]; then
    echo "Database configured"
    echo "Waiting for database..."

    # Extract host from DATABASE_URL
    DB_HOST=$(echo $DATABASE_URL | sed -E 's|.*@([^:/]+).*|\1|')
    DB_PORT=$(echo $DATABASE_URL | sed -E 's|.*:([0-9]+)/.*|\1|')
    DB_PORT=${DB_PORT:-5432}

    # Wait for database with timeout
    for i in $(seq 1 30); do
        if nc -z $DB_HOST $DB_PORT 2>/dev/null; then
            echo "Database is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            echo "Database not ready, continuing anyway..."
        fi
        sleep 1
    done
else
    echo "DATABASE_URL not set"
fi

# =====================================================
# START BACKEND (on port 8000)
# =====================================================

echo ""
echo "Starting backend on port $BACKEND_PORT..."

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
    echo "   Backend started (PID: $BACKEND_PID)"
else
    echo "   WARNING: Backend directory not found!"
    ls -la /app/
    exit 1
fi

# =====================================================
# START FRONTEND (on port 3000)
# =====================================================

echo ""
echo "Starting frontend on port $FRONTEND_PORT..."

if [ -f "/app/frontend/server.js" ]; then
    cd /app/frontend
    echo "   Frontend directory: /app/frontend"
    echo "   Frontend URL: http://$HOSTNAME:$FRONTEND_PORT"

    export PORT=$FRONTEND_PORT
    export HOSTNAME="0.0.0.0"

    node server.js &
    FRONTEND_PID=$!
    echo "   Frontend started (PID: $FRONTEND_PID)"
else
    echo "   WARNING: Frontend server.js not found!"
    echo "   Checking /app/frontend:"
    ls -la /app/frontend/ || true
    exit 1
fi

# =====================================================
# START NGINX (on external PORT)
# =====================================================

echo ""
echo "Starting nginx on port $NGINX_PORT..."

# Check that nginx.conf exists
if [ ! -f "/etc/nginx/nginx.conf" ]; then
    echo "   ERROR: nginx.conf not found!"
    exit 1
fi

# Prepare nginx configuration - replace port 8000 with actual PORT
sed -i "s/listen 8000;/listen $NGINX_PORT;/g" /etc/nginx/nginx.conf
sed -i "s/listen \[::\]:8000;/listen [::]:$NGINX_PORT;/g" /etc/nginx/nginx.conf

echo "   Nginx configuration updated for port $NGINX_PORT"
echo "   Nginx URL: http://$HOSTNAME:$NGINX_PORT"

# Test nginx configuration before starting
if ! nginx -t 2>&1; then
    echo "   ERROR: nginx configuration test failed!"
    cat /etc/nginx/nginx.conf
    exit 1
fi

# Start nginx
nginx -g "daemon off;" &
NGINX_PID=$!
echo "   Nginx started (PID: $NGINX_PID)"

# =====================================================
# HEALTH CHECK LOG
# =====================================================

echo ""
echo "Services started:"
echo "   Backend PID:  $BACKEND_PID on port $BACKEND_PORT"
echo "   Frontend PID: $FRONTEND_PID on port $FRONTEND_PORT"
echo "   Nginx PID:    $NGINX_PID on port $NGINX_PORT (external)"
echo ""

# Give services time to start
sleep 8

# Check that services are responding
echo "Health check..."

# Check backend
if curl -s http://localhost:$BACKEND_PORT/api/v1/health > /dev/null 2>&1; then
    echo "   Backend responding"
else
    echo "   Backend not responding"
fi

# Check frontend
if curl -s http://localhost:$FRONTEND_PORT/ > /dev/null 2>&1; then
    echo "   Frontend responding"
else
    echo "   Frontend not responding"
fi

# Check nginx (external port)
if curl -s http://localhost:$NGINX_PORT/nginx-health > /dev/null 2>&1; then
    echo "   Nginx responding"
elif curl -s http://localhost:$NGINX_PORT/api/v1/health > /dev/null 2>&1; then
    echo "   Nginx proxy working (API accessible)"
else
    echo "   Nginx not responding on port $NGINX_PORT"
    echo "   Checking nginx error log:"
    cat /var/log/nginx/error.log 2>/dev/null || echo "   No error log available"
fi

echo ""
echo "MentorHub is ready!"
echo "   Public URL: http://localhost:$NGINX_PORT"
echo "   API URL:    http://localhost:$NGINX_PORT/api/v1"
echo ""

# =====================================================
# KEEP ALIVE
# =====================================================

# Signal handler for child processes
cleanup() {
    echo "Stopping services..."
    kill $BACKEND_PID $FRONTEND_PID $NGINX_PID 2>/dev/null || true
    wait $BACKEND_PID $FRONTEND_PID $NGINX_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGTERM SIGINT EXIT

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID $NGINX_PID 2>/dev/null || true

# If processes ended, keep container alive
echo "Processes ended, keeping container alive..."
tail -f /dev/null
