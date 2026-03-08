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
    supervisor \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    NODE_ENV=production \
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

# Копируем standalone build (включает всё необходимое)
COPY --from=frontend-builder /app/frontend/.next/standalone ./
COPY --from=frontend-builder /app/frontend/.next/static ./.next/static
RUN mkdir -p public

# ==================== Supervisor Configuration ====================
WORKDIR /app

# Создаём директории
RUN mkdir -p /var/log/supervisor

# Копируем подготовленный конфигурационный файл supervisor
# Это файл должен быть в репозитории: deploy/supervisor/app.conf
COPY deploy/supervisor/app.conf /etc/supervisor/conf.d/app.conf

# ==================== Start Script ====================
# Скрипт запуска с поддержкой переменной $PORT от облачных платформ
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# ==================== Health Check ====================
# Проверка здоровья приложения
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${BACKEND_PORT}/api/v1/health || curl -f http://localhost:${BACKEND_PORT}/health || exit 1

# ==================== Ports ====================
# Render использует $PORT, другие платформы могут использовать стандартные
# Backend: 8000 (или $PORT)
# Frontend: 3000 (внутренний)
EXPOSE 8000 3000

# ==================== Entrypoint ====================
CMD ["/app/start.sh"]
