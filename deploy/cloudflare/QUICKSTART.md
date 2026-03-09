# 🚀 Cloudflare Pages - Быстрый старт

## 📋 Что нужно

1. **Аккаунт Cloudflare** (бесплатно)
2. **Backend на Render** (или другом сервисе)
3. **Wrangler CLI**

---

## ⚡ Быстрый деплой (5 минут)

### Шаг 1: Установите Wrangler

```bash
npm install -g wrangler
```

### Шаг 2: Авторизуйтесь в Cloudflare

```bash
wrangler login
```

Откроется браузер для авторизации.

### Шаг 3: Запустите деплой

**Windows (PowerShell):**
```powershell
.\deploy\cloudflare\deploy.ps1
```

**Linux/Mac:**
```bash
./deploy/cloudflare/deploy.sh
```

**Или вручную:**
```bash
cd frontend
npm install
npm run build
wrangler pages deploy .next --project-name=mentorhub
```

---

## 🔐 Настройка Environment Variables

После первого деплоя, зайдите в **Cloudflare Dashboard**:

1. **Workers & Pages** → **mentorhub** → **Settings**
2. **Environment Variables** → **Add Variable**

Добавьте:

```bash
NEXT_PUBLIC_API_BASE_URL=https://mentorhub-api.onrender.com/api/v1
NEXT_PUBLIC_SITE_URL=https://mentorhub.pages.dev
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
```

---

## 🌐 Доступ к сайту

После деплоя сайт доступен по адресу:

```
https://mentorhub.pages.dev
```

Или используйте **кастомный домен**:

1. **Custom Domains** → **Add Custom Domain**
2. Введите ваш домен (например, `mentorhub.com`)
3. Следуйте инструкциям для обновления DNS

---

## 🔄 Автоматический деплой (GitHub Actions)

### Настройка:

1. **В GitHub Repository:**
   - Settings → Secrets and variables → Actions

2. **Добавьте Secrets:**

```bash
# Cloudflare API Token (с правами Pages:Deploy)
CLOUDFLARE_API_TOKEN=your_token_here

# Cloudflare Account ID
CLOUDFLARE_ACCOUNT_ID=your_account_id_here
```

**Где получить:**
- API Token: https://dash.cloudflare.com/profile/api-tokens
- Account ID: https://dash.cloudflare.com (справа внизу)

3. **Запушьте в main:**

```bash
git push origin main
```

GitHub Actions автоматически задеплоит на Cloudflare Pages!

---

## 📊 Мониторинг

### Cloudflare Dashboard:

1. **Analytics** → трафик, bandwidth, requests
2. **Deployments** → история деплоев
3. **Settings** → конфигурация

### Логи деплоя:

```bash
wrangler pages deployment list --project-name=mentorhub
```

---

## ⚠️ Важные заметки

### 1. Backend должен быть отдельно

Cloudflare Pages — только для frontend!

**Backend запустите на:**
- Render (бесплатно)
- Railway (бесплатно)
- Fly.io (бесплатно)
- Ваш VPS

### 2. Настройте CORS на backend

```bash
# В Render Environment Variables
CORS_ORIGINS=https://mentorhub.pages.dev,https://yourdomain.com
```

### 3. Next.js ограничения

Cloudflare Pages не поддерживает:
- `next/image` (используйте `unoptimized: true`)
- API routes (перенесите на backend)
- WebSocket (используйте Cloudflare Workers)

---

## 🆘 Troubleshooting

### Ошибка: "Wrangler not found"

```bash
npm install -g wrangler
wrangler login
```

### Ошибка: "Build failed"

Проверьте логи:
```bash
cd frontend
npm run build 2>&1 | tee build.log
```

### Ошибка: "CORS error" в браузере

Настройте CORS на backend:
```bash
CORS_ORIGINS=https://mentorhub.pages.dev
```

### Сайт показывает 404

Проверьте, что `.next` директория существует:
```bash
ls -la frontend/.next
```

---

## 💰 Стоимость

**Cloudflare Pages (Free):**
- ✅ 100GB bandwidth / месяц
- ✅ 500 builds / месяц
- ✅ Неограниченные requests
- ✅ Бесплатный SSL

**Итого: $0/мес** для большинства проектов!

---

## 📚 Документация

- [Cloudflare Pages Docs](https://developers.cloudflare.com/pages/)
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/)
- [Next.js на Cloudflare](https://developers.cloudflare.com/pages/framework-guides/deploy-a-nextjs-site/)

---

**Готово! Ваш MentorHub на Cloudflare Pages!** 🎉
