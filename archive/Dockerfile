# ==================== DOCKERFILE ДЛЯ RENDER (ОБЪЕДИНЁННЫЙ СЕРВИС) ====================
# Этот Dockerfile запускает backend + frontend в одном контейнере
# Render ожидает сервис на порту $PORT (пробрасывается в backend)

# ==================== FRONTEND BUILD STAGE ====================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy frontend source
COPY frontend/ ./

# Create public folder if not exists
RUN mkdir -p public

# Build frontend
RUN NEXT_TELEMETRY_DISABLED=1 npm run build

# ==================== BACKEND BUILDER ====================
FROM python:3.11-slim AS backend-builder

WORKDIR /app/backend

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --target=/app/deps -r requirements.txt

# ==================== PRODUCTION IMAGE ====================
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    supervisor \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/deps:$PYTHONPATH \
    NODE_ENV=production

# ==================== BACKEND SETUP ====================
COPY --from=backend-builder /app/deps /app/deps
COPY backend/ /app/backend/

# ==================== FRONTEND SETUP ====================
COPY --from=frontend-builder /app/frontend/.next/standalone /app/frontend/
COPY --from=frontend-builder /app/frontend/.next/static /app/frontend/.next/static
RUN mkdir -p /app/frontend/public

# ==================== STARTUP SCRIPT ====================
# Этот скрипт обрабатывает Render's $PORT и запускает оба сервиса
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Render передаёт порт через $PORT\n\
BACKEND_PORT=${PORT:-8000}\n\
FRONTEND_PORT=3000\n\
\n\
echo "========================================"\n\
echo "Starting MentorHub"\n\
echo "Backend Port: $BACKEND_PORT"\n\
echo "Frontend Port: $FRONTEND_PORT"\n\
echo "========================================"\n\
\n\
# Обновляем supervisor конфиг с правильным портом\n\
sed -i "s/--port [0-9]*/--port $BACKEND_PORT/g" /etc/supervisor/conf.d/mentorhub.conf\n\
\n\
# Запускаем supervisor\n\
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf\n\
' > /app/start.sh && chmod +x /app/start.sh

# ==================== SUPERVISOR CONFIGURATION ====================
RUN mkdir -p /var/log/supervisor /var/run/supervisor

RUN echo '[supervisord]' > /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'nodaemon=true' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'logfile=/var/log/supervisor/supervisord.log' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'pidfile=/var/run/supervisor/supervisord.pid' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'logfile_maxbytes=50MB' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'logfile_backups=10' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo '' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo '[program:backend]' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'command=python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'directory=/app/backend' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'autostart=true' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'autorestart=true' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'stderr_logfile=/var/log/supervisor/backend.err.log' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'stdout_logfile=/var/log/supervisor/backend.out.log' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'stdout_logfile_maxbytes=10MB' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'stderr_logfile_maxbytes=10MB' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo '' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo '[program:frontend]' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'command=node server.js' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'directory=/app/frontend' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'autostart=true' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'autorestart=true' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'environment=PORT="3000"' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'stderr_logfile=/var/log/supervisor/frontend.err.log' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'stdout_logfile=/var/log/supervisor/frontend.out.log' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'stdout_logfile_maxbytes=10MB' >> /etc/supervisor/conf.d/mentorhub.conf && \
    echo 'stderr_logfile_maxbytes=10MB' >> /etc/supervisor/conf.d/mentorhub.conf

# Health check - проверяем backend на порту из $PORT
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/api/v1/health || curl -f http://localhost:${PORT:-8000}/health || exit 1

# Expose ports
EXPOSE 8000 3000

# Start
CMD ["/app/start.sh"]
