# Cloudflare Pages Deployment Guide

## 📋 Требования

- Аккаунт Cloudflare
- Установленный Wrangler CLI (опционально)

## 🚀 Быстрый старт

### Способ 1: Через Dashboard (рекомендуется)

1. **Войдите в Cloudflare Dashboard**
   - Зайдите на [dash.cloudflare.com](https://dash.cloudflare.com)
   - Перейдите в Workers & Pages

2. **Создайте проект**
   - Нажмите "Create application" → "Pages"
   - Выберите "Connect to Git"
   - Выберите репозиторий MentorHub

3. **Настройте сборку**
   - Framework preset: Next.js
   - Build command: `cd frontend && npm install && npm run build`
   - Build output directory: `.next`
   - Root directory: `frontend`

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
   - Нажмите "Save and Deploy"

### Способ 2: Через Wrangler CLI

```bash
# Установка Wrangler
npm install -g wrangler

# Аутентификация
wrangler login

# Деплой
cd frontend
wrangler pages deploy .next --project-name=mentorhub

# Production деплой
wrangler pages deploy .next --project-name=mentorhub --branch=main
```

## 📊 Архитектура

```
┌─────────────────────────────────────────────────────────┐
│           Cloudflare Edge Network                       │
│      (275+ Data Centers Worldwide)                      │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Cloudflare Pages                        │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │   Next.js Application                   │   │   │
│  │  │   - Static Assets (CDN)                 │   │   │
│  │  │   - SSR via Cloudflare Workers          │   │   │
│  │  │   - Image Optimization                  │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  │                                                 │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │   Cloudflare Workers (Functions)        │   │   │
│  │  │   - API Routes                          │   │   │
│  │  │   - Edge Functions                      │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  │                                                 │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │   Cloudflare Services                   │   │   │
│  │  │   - D1 (SQLite)                         │   │   │
│  │  │   - KV Storage                          │   │   │
│  │  │   - R2 (Object Storage)                 │   │   │
│  │  │   - Durable Objects                     │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │         Cloudflare Security                     │   │
│  │  - DDoS Protection                              │   │
│  │  - WAF (Web Application Firewall)               │   │
│  │  - SSL/TLS                                      │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 🔧 Конфигурация

### wrangler.toml

Основные настройки в `deploy/cloudflare/wrangler.toml`:

```toml
name = "mentorhub-frontend"
compatibility_date = "2024-01-01"
compatibility_flags = ["nodejs_compat"]

[pages_build_output_dir]
directory = "frontend/.next"

[functions]
directory = "frontend/functions"
nodejs_compat = true
```

### Cloudflare Workers (Functions)

Создавайте функции в `frontend/functions/`:

```typescript
// frontend/functions/api/health.ts
export async function onRequest(context) {
  return new Response(JSON.stringify({ status: 'ok' }), {
    headers: { 'Content-Type': 'application/json' },
  })
}
```

### Использование KV Storage

```typescript
// frontend/functions/api/cache.ts
export async function onRequest(context) {
  const { request, env } = context
  
  // Чтение из KV
  const cached = await env.MY_KV.get('key')
  
  // Запись в KV
  await env.MY_KV.put('key', 'value', { expirationTtl: 3600 })
  
  return new Response(cached)
}
```

## 🔄 Деплой

### Автоматический деплой

Cloudflare Pages автоматически деплоит при:
- Пуше в main ветку (production)
- Создании Pull Request (preview)

### Ручной деплой

```bash
# Preview деплой
wrangler pages deploy .next --project-name=mentorhub

# Production деплой
wrangler pages deploy .next --project-name=mentorhub --branch=main

# Деплой с окружением
wrangler pages deploy .next --project-name=mentorhub --branch=staging
```

### Деплой из CI/CD

```yaml
# .github/workflows/cloudflare-deploy.yml
name: Deploy to Cloudflare Pages
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
      - uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          command: pages deploy frontend/.next --project-name=mentorhub
```

## 🎯 Оптимизация

### Image Optimization

Cloudflare автоматически оптимизирует изображения через Cloudflare Images.

### Caching

```toml
# wrangler.toml
[[cache_rules]]
rule = "/static/*"
cache_level = "everything"
ttl = 31536000
```

### Edge Functions

Используйте Workers для выполнения кода на edge:

```typescript
// frontend/functions/middleware.ts
export async function onRequest(context) {
  const { request } = context
  
  // Проверка авторизации на edge
  const token = request.headers.get('Authorization')
  if (!token) {
    return new Response('Unauthorized', { status: 401 })
  }
  
  return context.next()
}
```

## 📊 Мониторинг

### Cloudflare Dashboard

1. **Analytics** - трафик и производительность
2. **Workers** - логи и метрики функций
3. **Security** - события безопасности

### Логи

```bash
# Логи в реальном времени
wrangler tail

# Логи с фильтром
wrangler tail --format pretty
```

## ⚠️ Troubleshooting

### Ошибка: Build failed

```bash
# Локальная сборка
cd frontend && npm run build

# Проверка логов
wrangler pages deployment list
```

### Ошибка: Function timeout

- Оптимизируйте функции
- Увеличьте timeout
- Используйте фоновые задачи

### Ошибка: KV not found

```bash
# Создайте KV namespace
wrangler kv:namespace create MY_KV

# Добавьте в wrangler.toml
[[kv_namespaces]]
binding = "MY_KV"
id = "your-namespace-id"
```

## 💰 Стоимость

| План | Цена | Включено |
|------|------|----------|
| Free | $0 | 500 requests/day, 100GB bandwidth/month |
| Pro | $5/мес | Unlimited requests, 1TB bandwidth/month |
| Business | $200/мес | 10TB bandwidth, Advanced features |
| Enterprise | Custom | Unlimited |

**Примерная стоимость:**
- Free: $0 (для пет-проектов)
- Pro: $5/месяц (для production)

## 🔗 Cloudflare Services

### D1 Database (SQLite)

```toml
# wrangler.toml
[[d1_databases]]
binding = "DB"
database_name = "mentorhub"
database_id = "your-database-id"
```

### R2 Storage (S3-compatible)

```toml
# wrangler.toml
[[r2_buckets]]
binding = "BUCKET"
bucket_name = "mentorhub-bucket"
```

### Durable Objects

```typescript
// frontend/functions/objects/counter.ts
export class Counter {
  constructor(state, env) {
    this.state = state
  }
  
  async fetch(request) {
    // Stateful logic
  }
}
```

## 🔗 Полезные ссылки

- [Cloudflare Dashboard](https://dash.cloudflare.com)
- [Cloudflare Pages Docs](https://developers.cloudflare.com/pages/)
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/)
- [Cloudflare Workers](https://developers.cloudflare.com/workers/)
