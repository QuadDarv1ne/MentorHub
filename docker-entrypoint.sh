#!/bin/bash
set -e

echo "🚀 Starting MentorHub..."

# Ожидание доступности PostgreSQL
echo "⏳ Waiting for PostgreSQL..."
until PGPASSWORD=$DB_PASSWORD psql -h "postgres" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "✅ PostgreSQL is up!"

# Ожидание доступности Redis
echo "⏳ Waiting for Redis..."
until redis-cli -h redis ping 2>/dev/null; do
  echo "Redis is unavailable - sleeping"
  sleep 2
done
echo "✅ Redis is up!"

# Применение миграций
echo "📦 Running database migrations..."
cd /app/backend
alembic upgrade head

# Запуск приложения
echo "🎉 Starting application..."
exec "$@"
