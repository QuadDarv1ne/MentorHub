#!/bin/bash
# Скрипт для быстрой настройки проекта

set -e

echo "======================================================"
echo "🚀 Быстрая настройка MentorHub"
echo "======================================================"

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

# Создание .env файлов
echo "📝 Создание .env файлов..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✅ Создан backend/.env"
fi

if [ ! -f frontend/.env.local ]; then
    cp frontend/.env.example frontend/.env.local
    echo "✅ Создан frontend/.env.local"
fi

# Генерация SECRET_KEY
echo ""
echo "🔑 Генерация SECRET_KEY..."
SECRET_KEY=$(openssl rand -hex 32)
echo "SECRET_KEY=$SECRET_KEY" >> backend/.env
echo "✅ SECRET_KEY сгенерирован и добавлен в backend/.env"

# Запуск Docker Compose
echo ""
echo "🐳 Запуск Docker контейнеров..."
docker-compose -f docker-compose.dev.yml up -d postgres redis

# Ожидание запуска БД
echo "⏳ Ожидание запуска PostgreSQL..."
sleep 5

# Применение миграций
echo "📦 Применение миграций БД..."
cd backend
python -m alembic upgrade head || echo "⚠️  Миграции не применились (возможно, БД еще не готова)"
cd ..

# Запуск приложения
echo ""
echo "======================================================"
echo "✅ Настройка завершена!"
echo "======================================================"
echo ""
echo "📚 Следующие шаги:"
echo "  1. Отредактируйте backend/.env и frontend/.env.local"
echo "  2. Запустите: docker-compose -f docker-compose.dev.yml up"
echo "  3. Или: make dev-build"
echo ""
echo "🌐 После запуска:"
echo "  Frontend: http://localhost:3000"
echo "  Backend: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "======================================================"
