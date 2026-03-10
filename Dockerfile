# =====================================================
# ОПТИМИЗИРОВАННЫЙ DOCKERFILE ДЛЯ MENTORHUB
# Fix: start.sh и порты для Render (2026-03-09)
# =====================================================

# ==================== STAGE 1: Frontend Build ====================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Кэширование зависимостей
COPY frontend/package*.json ./

# Устанавливаем все зависимости (включая dev для сборки)
RUN npm install --legacy-peer-deps

COPY frontend/ ./

# Отключаем телеметрию и source maps для меньшего размера
ENV NEXT_TELEMETRY_DISABLED=1 \
    NEXT_SOURCE_MAP_DISABLED=true

RUN npm run build

# Очищаем кэш npm
RUN npm cache clean --force

# ==================== STAGE 2: Backend Build ====================
FROM python:3.11-alpine AS backend-builder

WORKDIR /app

# Устанавливаем только необходимые зависимости
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev

COPY backend/requirements.txt ./

# Устанавливаем зависимости без кэша
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==================== STAGE 3: Production Image ====================
FROM python:3.11-alpine

# Минимальный набор пакетов
RUN apk add --no-cache \
    libpq \
    nodejs \
    curl \
    tini \
    bash

# Создаём не-root пользователя для безопасности
RUN addgroup -g 1000 appgroup && \
    adduser -u 1000 -G appgroup -D appuser

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NODE_ENV=production \
    PYTHONMALLOC=malloc \
    MALLOC_ARENA_MAX=2

# Копируем зависимости backend
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Копируем backend код
COPY backend/ ./backend/

# Копируем frontend build (standalone)
WORKDIR /app
COPY --from=frontend-builder /app/frontend/.next/standalone ./frontend
COPY --from=frontend-builder /app/frontend/.next/static ./frontend/.next/static
COPY --from=frontend-builder /app/frontend/public ./frontend/public

# Копируем скрипт запуска и конвертируем line endings
WORKDIR /app
COPY start.sh ./start.sh
RUN sed -i 's/\r$//' start.sh && chmod +x start.sh

# Устанавливаем владельца на appuser
RUN chown -R appuser:appgroup /app

USER appuser

# Переменные окружения по умолчанию
ENV BACKEND_PORT=8000 \
    FRONTEND_PORT=3000 \
    HOSTNAME=0.0.0.0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-3000}/ || curl -f http://localhost:${BACKEND_PORT}/api/v1/health || exit 1

EXPOSE 3000 8000

# Запускаем через bash
CMD ["bash", "-c", "/app/start.sh"]
