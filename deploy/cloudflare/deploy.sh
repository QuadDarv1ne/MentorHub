#!/bin/bash
# =====================================================
# Cloudflare Pages Deploy Script для MentorHub
# =====================================================

set -e

echo "========================================="
echo "🚀 MentorHub - Cloudflare Pages Deploy"
echo "========================================="

# Проверка Wrangler
if ! command -v wrangler &> /dev/null; then
    echo "❌ Wrangler не установлен. Установите:"
    echo "   npm install -g wrangler"
    exit 1
fi

# Проверка авторизации
if ! wrangler whoami &> /dev/null; then
    echo "⚠️  Требуется авторизация в Cloudflare"
    wrangler login
fi

# Переход в директорию frontend
cd "$(dirname "$0")/../frontend"

echo ""
echo "📦 Установка зависимостей..."
npm ci --legacy-peer-deps

echo ""
echo "🔨 Сборка frontend..."
export NEXT_TELEMETRY_DISABLED=1
npm run build

echo ""
echo "🚀 Деплой на Cloudflare Pages..."

# Деплой
wrangler pages deploy .next \
    --project-name=mentorhub \
    --branch=main \
    --commit-dirty=true

echo ""
echo "✅ Деплой завершён!"
echo ""
echo "📊 Проверить статус:"
echo "   https://dash.cloudflare.com/?to=/:account/pages/view/mentorhub"
echo ""
echo "🌐 Сайт доступен по адресу:"
echo "   https://mentorhub.pages.dev"
echo ""
