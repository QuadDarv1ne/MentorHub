# Настройка Render

## 1. Создать PostgreSQL базу данных

В панели Render:
- New → PostgreSQL
- Database Name: `mentorhub`
- User: `mentorhub_user`
- Region: Frankfurt
- Plan: Starter

После создания скопируйте **Internal Database URL** (вид: `postgresql://user:pass@host/db`)

## 2. Создать Redis

В панели Render:
- New → Redis
- Region: Frankfurt
- Plan: Starter

После создания скопируйте **Internal Connection URL** (вид: `redis://host:6379/0`)

## 3. Создать Web Service

В панели Render:
- New → Web Service
- Connect repository: MentorHub
- Region: Frankfurt
- Plan: Starter

### Environment Variables

Добавьте следующие переменные:

```
# Обязательно
DATABASE_URL=<Internal Database URL из шага 1>
REDIS_URL=<Internal Connection URL из шага 2>
SECRET_KEY=<сгенерируйте: openssl rand -hex 32>
ENVIRONMENT=production
RENDER=true

# Опционально
AGORA_APP_ID=
AGORA_APP_CERTIFICATE=
STRIPE_API_KEY=
STRIPE_WEBHOOK_SECRET=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
SMTP_USER=
SMTP_PASSWORD=
NEXT_PUBLIC_API_URL=https://<ваш-domain>
```

## 4. Deploy

После настройки переменных Render автоматически запустит сборку.

## Проверка

После деплоя проверьте логи:
- ✅ `DATABASE_URL configured`
- ✅ `Database connection successful`
- ✅ `Environment: production`
