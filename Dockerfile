# =====================================================
# УНИВЕРСАЛЬНЫЙ DOCKERFILE ДЛЯ MENTORHUB
# Работает на: Render, Railway, Fly.io, VPS
# Запускает: Backend (FastAPI) + Frontend (Next.js)
# =====================================================

# ==================== STAGE 1: Frontend Build ====================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Кэшируем зависимости
COPY frontend/package*.json ./
RUN npm install --legacy-peer-deps

# Копируем исходники и собираем
COPY frontend/ ./
RUN mkdir -p public && \
    NEXT_TELEMETRY_DISABLED=1 npm run build

# ==================== STAGE 2: Production Image ====================
FROM python:3.11-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libpq5 \
    curl \
    supervisor \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NODE_ENV=production

# ==================== Backend ====================
WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# ==================== Frontend ====================
WORKDIR /app/frontend

# Копируем standalone build (включает всё необходимое)
COPY --from=frontend-builder /app/frontend/.next/standalone ./
COPY --from=frontend-builder /app/frontend/.next/static ./.next/static
RUN mkdir -p public

# ==================== Supervisor ====================
WORKDIR /app

# Создаём конфигурацию supervisor
RUN mkdir -p /var/log/supervisor

RUN echo '[supervisord]' > /etc/supervisor/conf.d/app.conf && \
    echo 'nodaemon=true' >> /etc/supervisor/conf.d/app.conf && \
    echo 'logfile=/var/log/supervisor/supervisord.log' >> /etc/supervisor/conf.d/app.conf && \
    echo 'pidfile=/var/run/supervisord.pid' >> /etc/supervisor/conf.d/app.conf && \
    echo 'user=root' >> /etc/supervisor/conf.d/app.conf && \
    echo '' >> /etc/supervisor/conf.d/app.conf && \
    echo '[program:backend]' >> /etc/supervisor/conf.d/app.conf && \
    echo 'command=uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2' >> /etc/supervisor/conf.d/app.conf && \
    echo 'directory=/app/backend' >> /etc/supervisor/conf.d/app.conf && \
    echo 'autostart=true' >> /etc/supervisor/conf.d/app.conf && \
    echo 'autorestart=true' >> /etc/supervisor/conf.d/app.conf && \
    echo 'stdout_logfile=/var/log/supervisor/backend.log' >> /etc/supervisor/conf.d/app.conf && \
    echo 'stderr_logfile=/var/log/supervisor/backend.err' >> /etc/supervisor/conf.d/app.conf && \
    echo '' >> /etc/supervisor/conf.d/app.conf && \
    echo '[program:frontend]' >> /etc/supervisor/conf.d/app.conf && \
    echo 'command=node server.js' >> /etc/supervisor/conf.d/app.conf && \
    echo 'directory=/app/frontend' >> /etc/supervisor/conf.d/app.conf && \
    echo 'environment=PORT="3000"' >> /etc/supervisor/conf.d/app.conf && \
    echo 'autostart=true' >> /etc/supervisor/conf.d/app.conf && \
    echo 'autorestart=true' >> /etc/supervisor/conf.d/app.conf && \
    echo 'stdout_logfile=/var/log/supervisor/frontend.log' >> /etc/supervisor/conf.d/app.conf && \
    echo 'stderr_logfile=/var/log/supervisor/frontend.err' >> /etc/supervisor/conf.d/app.conf

# Стартовый скрипт (обрабатывает $PORT от Render/Railway)
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'BACKEND_PORT=${PORT:-8000}' >> /app/start.sh && \
    echo 'echo "Starting MentorHub..."' >> /app/start.sh && \
    echo 'echo "Backend port: $BACKEND_PORT"' >> /app/start.sh && \
    echo 'echo "Frontend port: 3000"' >> /app/start.sh && \
    echo 'sed -i "s/--port [0-9]*/--port $BACKEND_PORT/g" /etc/supervisor/conf.d/app.conf' >> /app/start.sh && \
    echo 'exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf' >> /app/start.sh && \
    chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || curl -f http://localhost:8000/health || exit 1

# Порты (Render использует $PORT, другие платформы могут использовать стандартные)
EXPOSE 8000 3000

# Запуск
CMD ["/app/start.sh"]
