# Netlify Deployment Guide

## 📋 Требования

- Аккаунт Netlify
- Установленный Netlify CLI (опционально)

## 🚀 Быстрый старт

### Способ 1: Через Dashboard (рекомендуется)

1. **Войдите в Netlify**
   - Зайдите на [app.netlify.com](https://app.netlify.com)
   - Нажмите "Add new site" → "Import an existing project"

2. **Подключите репозиторий**
   - Выберите GitHub
   - Выберите репозиторий MentorHub
   - Укажите путь к frontend: `frontend`

3. **Настройте сборку**
   - Build command: `npm run build`
   - Publish directory: `.next`
   - Base directory: `frontend`

4. **Добавьте переменные окружения**

```env
# API URL
NEXT_PUBLIC_API_URL=https://api.mentorhub.com

# Agora
NEXT_PUBLIC_AGORA_APP_ID=your-app-id

# Environment
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
```

5. **Задеплойте**
   - Нажмите "Deploy site"

### Способ 2: Через CLI

```bash
# Установка CLI
npm install -g netlify-cli

# Аутентификация
netlify login

# Инициализация
cd frontend
netlify init

# Деплой
netlify deploy --prod
```

## 📊 Архитектура

```
┌─────────────────────────────────────────────────────┐
│              Netlify Edge Network                   │
│         (Global CDN + Serverless Functions)         │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │      Next.js Application                    │   │
│  │  ┌───────────────────────────────────────┐  │   │
│  │  │   Static Pages (SSG)                  │  │   │
│  │  │   - /                                 │  │   │
│  │  │   - /about                            │  │   │
│  │  │   - /mentors                          │  │   │
│  │  └───────────────────────────────────────┘  │   │
│  │  ┌───────────────────────────────────────┐  │   │
│  │  │   Server-Side Rendering (SSR)         │  │   │
│  │  │   - /dashboard                        │  │   │
│  │  │   - /profile                          │  │   │
│  │  └───────────────────────────────────────┘  │   │
│  │  ┌───────────────────────────────────────┐  │   │
│  │  │   API Proxy                           │  │   │
│  │  │   /api/* → backend                    │  │   │
│  │  └───────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## 🔧 Конфигурация

### netlify.toml

Основные настройки в `deploy/netlify/netlify.toml`:

```toml
[build]
command = "cd frontend && npm install && npm run build"
publish = "frontend/.next"
base = "frontend"

[build.environment]
NODE_VERSION = "18"
NEXT_TELEMETRY_DISABLED = "1"

[[redirects]]
from = "/api/*"
to = "https://api.mentorhub.com/api/:splat"
status = 200
force = true
```

### Serverless Functions

Создавайте функции в `frontend/netlify/functions/`:

```typescript
// frontend/netlify/functions/health.ts
import { Handler } from '@netlify/functions'

export const handler: Handler = async (event) => {
  return {
    statusCode: 200,
    body: JSON.stringify({ status: 'ok' }),
  }
}
```

## 🔄 Деплой

### Автоматический деплой

Netlify автоматически деплоит при:
- Пуше в main ветку
- Создании Pull Request (deploy preview)

### Ручной деплой

```bash
# Preview деплой
netlify deploy

# Production деплой
netlify deploy --prod

# Деплой с сообщением
netlify deploy --prod -m "v1.2.3 - Added new features"
```

### Деплой из CI/CD

```yaml
# .github/workflows/netlify-deploy.yml
name: Deploy to Netlify
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: cd frontend && npm install && npm run build
      - uses: nwtgck/actions-netlify@v2
        with:
          publish-dir: './frontend/.next'
          production-branch: main
          github-token: ${{ secrets.GITHUB_TOKEN }}
          deploy-message: "Deploy from GitHub Actions"
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

## 🎯 Оптимизация

### Image Optimization

Netlify автоматически оптимизирует изображения через плагин.

### Caching

```toml
# Кэш для npm
[build.environment]
NPM_CONFIG_CACHE = "/opt/build/.cache/npm"
```

### Incremental Static Regeneration (ISR)

Next.js ISR работает на Netlify автоматически.

## 📊 Мониторинг

### Netlify Dashboard

1. **Deploys** - история деплоев
2. **Analytics** - трафик и производительность
3. **Functions** - логи serverless функций

### Логи

```bash
# Логи в реальном времени
netlify logs

# Логи функций
netlify functions:log
```

## ⚠️ Troubleshooting

### Ошибка: Build failed

```bash
# Локальная сборка
cd frontend && npm run build

# Проверка логов
netlify status
```

### Ошибка: API timeout

- Используйте API proxy
- Увеличьте timeout функций
- Оптимизируйте запросы

### Ошибка: CORS

Добавьте headers в netlify.toml:

```toml
[[headers]]
for = "/api/*"
[headers.values]
Access-Control-Allow-Origin = "*"
Access-Control-Allow-Methods = "GET, POST, PUT, DELETE"
```

## 💰 Стоимость

| План | Цена | Включено |
|------|------|----------|
| Starter | $0 | 100GB bandwidth, Unlimited sites |
| Pro | $19/мес | 1TB bandwidth, Unlimited functions |
| Business | $99/мес | 2TB bandwidth, Advanced features |
| Enterprise | Custom | Unlimited |

**Примерная стоимость:**
- Starter: $0 (для пет-проектов)
- Pro: $19/месяц (для production)

## 🔗 Полезные ссылки

- [Netlify Dashboard](https://app.netlify.com)
- [Netlify Docs](https://docs.netlify.com)
- [Next.js on Netlify](https://docs.netlify.com/integrations/frameworks/next-js/)
- [Netlify CLI](https://docs.netlify.com/cli/get-started/)
