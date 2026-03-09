# =====================================================
# УНИВЕРСАЛЬНЫЙ DOCKERFILE ДЛЯ MENTORHUB
# Работает на: Render, Railway, Fly.io, VPS, Amvera, Heroku
# Запускает: Backend (FastAPI) + Frontend (Next.js)
# С исправленным Graceful Shutdown
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
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Переменные окружения (могут быть переопределены в Render)
ARG DATABASE_URL
ARG REDIS_URL
ARG SECRET_KEY
ARG ENVIRONMENT=production
ARG RENDER=true

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NODE_ENV=production \
    DATABASE_URL=${DATABASE_URL} \
    REDIS_URL=${REDIS_URL} \
    SECRET_KEY=${SECRET_KEY} \
    ENVIRONMENT=${ENVIRONMENT} \
    RENDER=${RENDER} \
    # Default ports (can be overridden by $PORT)
    BACKEND_PORT=8000 \
    FRONTEND_PORT=3000

# ==================== Backend ====================
WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# ==================== Frontend ====================
WORKDIR /app/frontend

# Копируем standalone build (включает server.js в package/server.js)
COPY --from=frontend-builder /app/frontend/.next/standalone ./
COPY --from=frontend-builder /app/frontend/.next/static ./.next/static
COPY --from=frontend-builder /app/frontend/public ./public

# ==================== Start Script ====================
# Скрипт запуска с поддержкой переменной $PORT от облачных платформ
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# ==================== Environment Setup ====================
# Для Render: PORT должен быть 8000 (backend only)
ENV BACKEND_PORT=8000 \
    FRONTEND_PORT=3000

# ==================== Health Check ====================
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${BACKEND_PORT}/api/v1/health/ready || exit 1

# ==================== Ports ====================
EXPOSE 8000 3000

# ==================== Entrypoint ====================
CMD ["/app/start.sh"]
