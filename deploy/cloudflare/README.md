# 🚀 Деплой MentorHub на Cloudflare Pages

## 📋 Архитектура

Cloudflare Pages подходит **только для frontend**. Backend нужно запускать отдельно:

```
┌─────────────────┐         ┌──────────────────┐
│  Cloudflare     │  API    │   Backend        │
│  Pages          │────────▶│   (Render/Railway)│
│  (Frontend)     │         │                  │
└─────────────────┘         └──────────────────┘
         ▲
         │
         │
┌─────────────────┐
│  Cloudflare CDN │
│  (Кэширование)  │
└─────────────────┘
```

---

## 🎯 Варианты деплоя

### Вариант 1: Cloudflare Pages + Render Backend (Рекомендуется)

**Frontend:** Cloudflare Pages (Бесплатно)
**Backend:** Render Free (Бесплатно)

**Преимущества:**
- ✅ Быстрый CDN по всему миру
- ✅ Автоматический HTTPS
- ✅ Бесплатно до 100GB bandwidth
- ✅ Instant Deploy

**Ограничения:**
- ⚠️ Только статический контент + Serverless Functions
- ⚠️ Нет WebSocket поддержки
- ⚠️ Ограничение 100ms для Functions

---

### Вариант 2: Cloudflare Workers + D1 + R2 (Полностью на Cloudflare)

**Требуется рефакторинг:**
- Backend → Cloudflare Workers (Hono framework)
- Database → Cloudflare D1 (SQLite)
- Storage → Cloudflare R2 (S3-compatible)
- Cache → Cloudflare KV

**Преимущества:**
- ✅ Полностью serverless
- ✅ Глобальная дистрибуция
- ✅ Плата только за usage

**Недостатки:**
- ⚠️ Нужен полный рефакторинг backend
- ⚠️ Ограничения Workers (15ms CPU time)
- ⚠️ Платно при большой нагрузке

---

## 📦 Вариант 1: Деплой (Frontend на Pages, Backend на Render)

### Шаг 1: Подготовка Backend на Render

1. **Убедитесь, что backend работает на Render:**
   ```
   https://mentorhub-api.onrender.com
   ```

2. **Настройте CORS в backend:**
   ```bash
   # В Render Environment Variables
   CORS_ORIGINS=https://mentorhub.pages.dev,https://yourdomain.com
   ```

---

### Шаг 2: Настройка Cloudflare Pages

#### 2.1 Через Dashboard (Простой способ)

1. **Зайдите в [Cloudflare Dashboard](https://dash.cloudflare.com/)**

2. **Workers & Pages → Create Application → Pages**

3. **Connect to Git:**
   ```
   Repository: QuadDarv1ne/MentorHub
   Branch: main
   ```

4. **Build Settings:**
   ```
   Framework preset: Next.js
   Build command: cd frontend && npm install && npm run build
   Build output directory: frontend/.next
   ```

5. **Environment Variables:**
   ```bash
   NEXT_PUBLIC_API_BASE_URL=https://mentorhub-api.onrender.com/api/v1
   NEXT_PUBLIC_SITE_URL=https://mentorhub.pages.dev
   NODE_ENV=production
   NEXT_TELEMETRY_DISABLED=1
   ```

6. **Deploy!**

---

#### 2.2 Через Wrangler CLI (Продвинутый способ)

```bash
# Установите Wrangler
npm install -g wrangler

# Логин в Cloudflare
wrangler login

# Перейдите в директорию frontend
cd frontend

# Деплой
wrangler pages deploy .next --project-name=mentorhub --branch=main
```

---

### Шаг 3: Настройка frontend для Cloudflare

#### 3.1 Обновите `frontend/next.config.js`:

```javascript
const withNextIntl = require('next-intl/plugin')('./i18n.ts');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'export', // Static export для Cloudflare Pages
  
  // Отключаем server-side features
  images: {
    unoptimized: true, // Cloudflare не поддерживает next/image
  },
  
  // Отключаем API routes (будут на backend)
  eslint: {
    ignoreDuringBuilds: true,
  },
  
  experimental: {
    serverActions: false,
  },
}

module.exports = withNextIntl(nextConfig);
```

#### 3.2 Создайте `frontend/wrangler.toml`:

```toml
name = "mentorhub-frontend"
compatibility_date = "2024-01-01"
compatibility_flags = ["nodejs_compat"]
pages_build_output_dir = ".next"

[vars]
NEXT_PUBLIC_API_BASE_URL = "https://mentorhub-api.onrender.com/api/v1"
NEXT_PUBLIC_SITE_URL = "https://mentorhub.pages.dev"
NODE_ENV = "production"
```

---

### Шаг 4: Настройка проксирования API

Cloudflare Pages не может проксировать запросы напрямую. Используйте:

#### 4.1 Вариант A: Прямые запросы с frontend

```typescript
// frontend/lib/api/client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export async function fetchAPI(endpoint: string, options?: RequestInit) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  
  return response.json();
}
```

#### 4.2 Вариант B: Cloudflare Functions (Serverless)

Создайте `frontend/functions/api/[[path]].ts`:

```typescript
// frontend/functions/api/[[path]].ts
export const onRequest: PagesFunction = async ({ request, env }) => {
  const url = new URL(request.url);
  const apiPath = url.pathname.replace('/api', '');
  
  const apiResponse = await fetch(`${env.API_BASE_URL}${apiPath}`, {
    method: request.method,
    headers: request.headers,
    body: request.body,
  });
  
  return apiResponse;
};
```

---

### Шаг 5: Деплой

```bash
# Через GitHub Actions (автоматически)
# Просто запушьте изменения в main

# Или вручную через CLI
cd frontend
npm run build
wrangler pages deploy .next --project-name=mentorhub
```

---

## 🔧 Полная миграция на Cloudflare (Вариант 2)

### Архитектура полностью на Cloudflare:

```
Frontend: Cloudflare Pages
Backend:  Cloudflare Workers (Hono)
Database: Cloudflare D1 (SQLite)
Storage:  Cloudflare R2
Cache:    Cloudflare KV
Auth:     Cloudflare Access / JWT
```

### Шаг 1: Рефакторинг Backend на Hono

```bash
# Создайте новый Workers проект
mkdir backend-workers
cd backend-workers
npm init -y
npm install hono @hono/node-server
```

```typescript
// src/index.ts
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { jwt } from 'hono/jwt';

const app = new Hono();

app.use('/api/*', cors());

app.get('/api/v1/health', (c) => {
  return c.json({ status: 'healthy' });
});

export default app;
```

### Шаг 2: Миграция Database на D1

```bash
# Создайте D1 базу
wrangler d1 create mentorhub-db

# Обновите wrangler.toml
[[d1_databases]]
binding = "DB"
database_name = "mentorhub-db"
database_id = "xxxx-xxxx-xxxx"
```

### Шаг 3: Миграция Storage на R2

```bash
# Создайте R2 bucket
wrangler r2 bucket create mentorhub-storage

# Обновите wrangler.toml
[[r2_buckets]]
binding = "STORAGE"
bucket_name = "mentorhub-storage"
```

---

## 📊 Сравнение стоимости

| Сервис | Render Free | Cloudflare Free | Cloudflare Paid |
|--------|-------------|-----------------|-----------------|
| **Frontend** | - | ✅ Бесплатно | $5/мес |
| **Backend** | ✅ 512MB RAM | ❌ Не подходит | $5/мес (Workers) |
| **Database** | ✅ 1GB | ❌ D1 платный | $5/мес (D1) |
| **Storage** | ❌ | ✅ 1GB R2 | $2/мес |
| **Bandwidth** | ✅ | ✅ 100GB | Безлимит |
| **Итого** | **$0** | **$0** | **~$17/мес** |

---

## ⚠️ Известные проблемы

### 1. Next.js Image Optimization

**Проблема:** Cloudflare не поддерживает `next/image`

**Решение:**
```javascript
// next.config.js
images: {
  unoptimized: true,
}
```

Или используйте Cloudflare Images:
```typescript
<Image 
  src="https://imagedelivery.net/xxx/abc123" 
  alt="..." 
/>
```

### 2. API Routes

**Проблема:** Cloudflare Pages не поддерживает Next.js API routes

**Решение:** Перенесите API на backend (Render) или используйте Cloudflare Functions

### 3. WebSocket

**Проблема:** Cloudflare Pages не поддерживает WebSocket

**Решение:** Используйте Cloudflare Workers с Durable Objects

### 4. Server-Side Rendering

**Проблема:** Ограниченная поддержка SSR

**Решение:** 
- Static export (`output: 'export'`)
- Или используйте Cloudflare Functions для SSR

---

## 🚀 Автоматический деплой через GitHub Actions

Создайте `.github/workflows/cloudflare-pages.yml`:

```yaml
name: Deploy to Cloudflare Pages

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Build
        run: |
          cd frontend
          npm run build
      
      - name: Deploy to Cloudflare Pages
        uses: cloudflare/wrangler-action@v3
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          command: pages deploy frontend/.next --project-name=mentorhub
```

---

## 🔐 Environment Variables

### Для Cloudflare Pages:

```bash
# .env.production
NEXT_PUBLIC_API_BASE_URL=https://mentorhub-api.onrender.com/api/v1
NEXT_PUBLIC_SITE_URL=https://mentorhub.pages.dev
NEXT_TELEMETRY_DISABLED=1
NODE_ENV=production
```

### Для Cloudflare Workers (если будете мигрировать backend):

```bash
# .dev.vars
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
JWT_SECRET=your-jwt-secret
```

---

## 📈 Мониторинг и аналитика

### Cloudflare Analytics:

1. **Dashboard → Analytics & Logs**
2. **Pages Analytics** — трафик, bandwidth
3. **Workers Analytics** — invocation count, errors

### Интеграция с Sentry:

```bash
npm install @sentry/nextjs
```

```javascript
// sentry.client.config.js
Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: 'production',
});
```

---

## ✅ Чеклист перед деплоем

- [ ] Backend работает на Render
- [ ] CORS настроен для Cloudflare домена
- [ ] NEXT_PUBLIC_API_BASE_URL установлен
- [ ] Images unoptimized (если нужно)
- [ ] API routes перенесены на backend
- [ ] Environment variables добавлены
- [ ] Тесты пройдены
- [ ] GitHub Actions настроен

---

## 🎯 Итоговая рекомендация

**Для MentorHub рекомендую:**

1. **Frontend → Cloudflare Pages** (Бесплатно, быстро)
2. **Backend → Render** (Бесплатно, работает)
3. **Database → Render PostgreSQL** (Бесплатно, 1GB)
4. **Storage → Cloudflare R2** (Бесплатно, 1GB)

Это даст:
- ✅ Быстрый CDN для frontend
- ✅ Бесплатный хостинг
- ✅ Минимальные изменения в коде
- ✅ Масштабируемость

---

**Готов помочь с настройкой!** 🚀
