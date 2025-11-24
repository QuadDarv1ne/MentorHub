# ===================================
# Multi-stage Dockerfile для Production
# Оптимизирован для минимального размера
# ===================================

# ============ STAGE 1: Builder ============
FROM python:3.11-slim AS builder

WORKDIR /build

# Установка только build зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем в отдельную директорию
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --user --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# ============ STAGE 2: Production ============
FROM python:3.11-slim

WORKDIR /app

# Установка только runtime зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Копируем Python пакеты из builder
COPY --from=builder /root/.local /root/.local

# Добавляем в PATH
ENV PATH=/root/.local/bin:$PATH

# Копируем backend код
COPY backend/ .

# Делаем скрипт проверки исполняемым
RUN chmod +x check_env.py 2>/dev/null || true

# Создаем non-root пользователя
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Переменные окружения
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    DATABASE_URL=${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/mentorhub}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Expose порт
EXPOSE 8000

# Создаем entrypoint скрипт
COPY <<EOF /app/entrypoint.sh
#!/bin/bash
set -e

echo "=========================================="
echo "🔍 Проверка переменных окружения"
echo "=========================================="

# Проверка DATABASE_URL
if [ -z "\${DATABASE_URL}" ]; then
    echo "❌ ERROR: DATABASE_URL не установлена!"
    echo "💡 Установите переменную DATABASE_URL в настройках Amvera"
    exit 1
else
    # Маскируем пароль в выводе
    MASKED_URL=\$(echo "\${DATABASE_URL}" | sed 's/:\/\/[^:]*:[^@]*@/:\/\/***:***@/')
    echo "✅ DATABASE_URL: \${MASKED_URL}"
fi

# Проверка SECRET_KEY
if [ -z "\${SECRET_KEY}" ]; then
    echo "❌ ERROR: SECRET_KEY не установлен!"
    echo "💡 Установите переменную SECRET_KEY в настройках Amvera"
    exit 1
else
    echo "✅ SECRET_KEY: \${SECRET_KEY:0:10}..."
fi

echo "✅ ENVIRONMENT: \${ENVIRONMENT:-not-set}"
echo "=========================================="

echo "🚀 Запуск приложения на порту \${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port \${PORT:-8000}
EOF

RUN chmod +x /app/entrypoint.sh

# Запуск через entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
