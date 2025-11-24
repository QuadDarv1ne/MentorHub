# ===================================
# Dockerfile для Amvera (Backend Only)
# ===================================

FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements и устанавливаем зависимости
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

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
    CMD curl -f http://localhost:8000/health || exit 1

# Expose порт
EXPOSE 8000

# Создаем entrypoint скрипт
COPY <<EOF /app/entrypoint.sh
#!/bin/bash
set -e
echo "🔍 Проверка переменных окружения..."
python /app/check_env.py || echo "⚠️ Проверка пропущена"
echo "🚀 Запуск приложения на порту \${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port \${PORT:-8000}
EOF

RUN chmod +x /app/entrypoint.sh

# Запуск через entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
