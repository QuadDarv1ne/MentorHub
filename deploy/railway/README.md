# Railway Deployment Guide

## 📋 Требования

- Аккаунт Railway
- Установленный Railway CLI (опционально)

## 🚀 Быстрый старт

### Способ 1: Через GitHub (рекомендуется)

1. **Подключите репозиторий**
   - Зайдите на [railway.app](https://railway.app)
   - Нажмите "New Project"
   - Выберите "Deploy from GitHub repo"
   - Выберите репозиторий MentorHub

2. **Настройте сервисы**

   **Backend Service:**
   - Root Directory: `backend`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2`
   - Port: 8000

   **Frontend Service:**
   - Root Directory: `frontend`
   - Start Command: `npm run start`
   - Port: 3000

   **Worker Service:**
   - Root Directory: `backend`
   - Start Command: `celery -A app.tasks worker --loglevel=info`

3. **Добавьте переменные окружения**

```env
# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database (Railway автоматически создаст PostgreSQL)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Redis (Railway автоматически создаст Redis)
REDIS_URL=${{Redis.REDIS_URL}}

# Environment
ENVIRONMENT=production
DEBUG=false

# Agora (опционально)
AGORA_APP_ID=your-app-id
AGORA_APP_CERTIFICATE=your-app-cert

# Stripe (опционально)
STRIPE_API_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx

# AWS S3 (опционально)
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_S3_BUCKET=mentorhub-bucket

# Email (опционально)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_SENDER=noreply@mentorhub.com
```

4. **Добавьте базы данных**
   - Нажмите "New" → "Database" → "PostgreSQL"
   - Нажмите "New" → "Database" → "Redis"

5. **Задеплойте**
   - Railway автоматически запустит деплой
   - Миграции запустятся автоматически

### Способ 2: Через CLI

```bash
# Установка CLI
npm install -g @railway/cli

# Аутентификация
railway login

# Инициализация проекта
railway init

# Создание проекта
railway new

# Добавление переменных окружения
railway variables set SECRET_KEY=xxx

# Деплой
railway up

# Просмотр логов
railway logs
```

## 📊 Масштабирование

Railway автоматически масштабируется в зависимости от нагрузки.

### Настройка ресурсов

1. Зайдите в настройки сервиса
2. Выберите "Settings"
3. Настройте:
   - CPU: 1-2 vCPU
   - Memory: 2-4 GB
   - Disk: 10-50 GB

## 🔧 Управление

```bash
# Перезапуск сервиса
railway restart

# Логи в реальном времени
railway logs

# Локальная разработка
railway run python backend/app/main.py

# Доступ к базе данных
railway run psql $DATABASE_URL
```

## 🗄️ Базы данных

### PostgreSQL

```bash
# Подключиться к БД
railway run psql $DATABASE_URL

# Создать бэкап
railway run pg_dump $DATABASE_URL > backup.sql

# Восстановить из бэкапа
railway run psql $DATABASE_URL < backup.sql
```

### Redis

```bash
# Подключиться к Redis
railway run redis-cli -u $REDIS_URL
```

## 🔄 CI/CD

Railway автоматически деплоит при пуше в main ветку.

### Отключение авто-деплоя

1. Settings → Deploy
2. Отключить "Auto Deploy"

### Деплой определенной ветки

```bash
railway up --branch staging
```

## ⚠️ Troubleshooting

### Ошибка: Build failed

```bash
# Проверить логи сборки
railway logs --type build

# Локальная сборка
railway run --detach
```

### Ошибка: Health check failed

- Проверьте, что приложение слушает правильный порт
- Убедитесь, что health endpoint доступен
- Увеличьте timeout health check

### Ошибка: Out of memory

- Увеличьте лимит памяти в настройках
- Оптимизируйте использование памяти в коде

## 💰 Стоимость

Railway предоставляет:
- $5 кредитов в месяц бесплатно
- $0.0000000056 за MB-сек памяти
- $0.000000025 за vCPU-сек

**Примерная стоимость:**
- Backend (2GB RAM, 1 vCPU): ~$10/месяц
- Frontend (1GB RAM, 0.5 vCPU): ~$5/месяц
- PostgreSQL (1GB): ~$5/месяц
- Redis (256MB): ~$1/месяц

**Итого:** ~$21/месяц (минус $5 кредитов = ~$16)

## 🔗 Полезные ссылки

- [Railway Dashboard](https://railway.app/dashboard)
- [Railway Docs](https://docs.railway.app)
- [Railway CLI](https://docs.railway.app/cli)
- [Railway Templates](https://railway.app/templates)
