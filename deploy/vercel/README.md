# Vercel Deployment Guide

## 📋 Требования

- Аккаунт Vercel
- Установленный Vercel CLI (опционально)

## 🚀 Быстрый старт

### Способ 1: Через Dashboard (рекомендуется)

1. **Импортируйте проект**
   - Зайдите на [vercel.com](https://vercel.com)
   - Нажмите "Add New..." → "Project"
   - Импортируйте из GitHub
   - Выберите репозиторий MentorHub

2. **Настройте проект**
   - Framework Preset: Next.js
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

3. **Добавьте переменные окружения**

```env
# API URL
NEXT_PUBLIC_API_URL=https://your-backend-url.com

# Agora
NEXT_PUBLIC_AGORA_APP_ID=your-app-id

# Environment
NODE_ENV=production
```

4. **Задеплойте**
   - Нажмите "Deploy"

### Способ 2: Через CLI

```bash
# Установка CLI
npm install -g vercel

# Аутентификация
vercel login

# Деплой
cd frontend
vercel

# Production деплой
vercel --prod
```

## 📊 Архитектура

```
┌─────────────────────────────────────────┐
│            Vercel Edge Network          │
│         (Global CDN + Serverless)       │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │      Next.js Application        │   │
│  │   (Serverless Functions)        │   │
│  │                                 │   │
│  │  /api/* → Serverless Functions  │   │
│  │  /*    → Static/SSR Pages       │   │
│  └─────────────────────────────────┘   │
│                                         │
│         ┌──────────────────┐           │
│         │  External API    │           │
│         │  (Backend)       │           │
│         └──────────────────┘           │
└─────────────────────────────────────────┘
```

## 🔧 Конфигурация

### next.config.js

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'serverless',
  images: {
    domains: ['mentorhub.com', 's3.amazonaws.com'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_AGORA_APP_ID: process.env.NEXT_PUBLIC_AGORA_APP_ID,
  },
}

module.exports = nextConfig
```

## 🔄 API Proxy

Vercel может проксировать запросы к вашему backend:

```javascript
// frontend/next.config.js
module.exports = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'https://your-backend-url.com/api/:path*',
      },
    ]
  },
}
```

## 📦 Serverless Functions

Создавайте API endpoints в `frontend/pages/api/`:

```typescript
// frontend/pages/api/health.ts
import { NextApiRequest, NextApiResponse } from 'next'

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  res.status(200).json({ status: 'ok' })
}
```

## 🎯 Оптимизация

### Image Optimization

```javascript
// next.config.js
module.exports = {
  images: {
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200],
    imageSizes: [16, 32, 48, 64, 96],
  },
}
```

### Incremental Static Regeneration (ISR)

```typescript
// pages/courses/[id].tsx
export async function getStaticProps() {
  return {
    props: { ... },
    revalidate: 60, // Revalidate every 60 seconds
  }
}
```

## 📊 Мониторинг

### Vercel Analytics

1. Зайдите в проект
2. Analytics → Enable
3. Добавьте snippet в `_app.tsx`

### Speed Insights

1. Зайдите в проект
2. Speed Insights → Enable

## ⚠️ Troubleshooting

### Ошибка: Build failed

```bash
# Локальная сборка
npm run build

# Проверка логов
vercel logs
```

### Ошибка: API timeout

- Оптимизируйте функции
- Увеличьте maxDuration в vercel.json
- Используйте фоновые задачи

### Ошибка: CORS

Добавьте headers в next.config.js:

```javascript
async headers() {
  return [
    {
      source: '/api/:path*',
      headers: [
        { key: 'Access-Control-Allow-Credentials', value: 'true' },
        { key: 'Access-Control-Allow-Origin', value: '*' },
        { key: 'Access-Control-Allow-Methods', value: 'GET,DELETE,PATCH,POST,PUT' },
        { key: 'Access-Control-Allow-Headers', value: 'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version' },
      ]
    }
  ]
}
```

## 💰 Стоимость

| План | Цена | Включено |
|------|------|----------|
| Hobby | $0 | 100GB bandwidth, Unlimited deployments |
| Pro | $20/мес | 1TB bandwidth, Unlimited functions |
| Enterprise | Custom | Unlimited everything |

**Примерная стоимость:**
- Hobby: $0 (для пет-проектов)
- Pro: $20/месяц (для production)

## 🔗 Полезные ссылки

- [Vercel Dashboard](https://vercel.com/dashboard)
- [Vercel Docs](https://vercel.com/docs)
- [Next.js on Vercel](https://nextjs.org/docs/deployment)
- [Vercel CLI](https://vercel.com/docs/cli)
