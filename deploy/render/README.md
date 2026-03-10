# Настройка Render

## Быстрый старт

1. **Создайте PostgreSQL** в панели Render
2. **Создайте Redis** (опционально, см. [REDIS-SETUP.md](REDIS-SETUP.md))
3. **Создайте Web Service** с настройками ниже
4. **Добавьте Environment Variables**
5. **Deploy**

---

## 1. Создать PostgreSQL базу данных

В панели Render:
- New → PostgreSQL
- Database Name: `mentorhub`
- User: `mentorhub_user`
- Region: Frankfurt
- Plan: Starter

После создания скопируйте **Internal Database URL** (вид: `postgresql://user:pass@host/db`)

## 2. Создать Redis (Опционально)

⚠️ **Важно:** Redis не обязателен для работы, но рекомендуется для production.

**Варианты:**

### A. Redis на Render (Платно, $7/месяц)
- New → Redis
- Region: Frankfurt
- Plan: Starter
- Скопируйте **Internal Connection URL**

### B. Upstash Redis (Бесплатно)
- Зайдите на https://upstash.com
- Создайте бесплатный Redis
- Скопируйте **Redis URL**

### C. Без Redis (Development/Testing)
- Пропустите этот шаг
- Приложение будет использовать memory cache

📖 **Подробная инструкция:** см. [REDIS-SETUP.md](REDIS-SETUP.md)

## 3. Создать Web Service

В панели Render:
- New → Web Service
- Connect repository: MentorHub
- Region: Frankfurt
- Plan: Starter
- Docker: ✅ (используется Dockerfile)

### Environment Variables

Добавьте следующие переменные:

```bash
# Обязательно
DATABASE_URL=<Internal Database URL из шага 1>
SECRET_KEY=<сгенерируйте: openssl rand -hex 32>
ENVIRONMENT=production

# Опционально (рекомендуется)
REDIS_URL=<Redis URL из шага 2>  # Если используете Redis
NEXT_PUBLIC_API_URL=https://<ваш-domain>.onrender.com

# Опционально (сервисы)
AGORA_APP_ID=<ваш app id>           # Для видео сессий
STRIPE_SECRET_KEY=<ваш key>          # Для платежей
SENTRY_DSN=<ваш dsn>                 # Для мониторинга ошибок

# Опционально (email)
SMTP_USER=<ваш email>
SMTP_PASSWORD=<ваш password>
```

### Генерация SECRET_KEY

```bash
# Linux/Mac
openssl rand -hex 32

# Windows (PowerShell)
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

## 4. Deploy

После настройки переменных Render автоматически запустит сборку.

**Время сборки:** ~3-5 минут

## Проверка

После деплоя проверьте логи (Dashboard → Logs):

### ✅ Успешный деплой

```
✅ Database connection successful
✅ Redis cache connected  # Если Redis настроен
Environment: production
Uvicorn running on http://0.0.0.0:8000
```

### ⚠️ Redis не подключён (Нормально!)

```
ℹ️ Using memory cache (Redis not available)
```

Это **ожидаемое поведение** если Redis не настроен. См. [REDIS-SETUP.md](REDIS-SETUP.md)

### ❌ Ошибки

Если видите другие ошибки, проверьте:
- DATABASE_URL правильно скопирован
- SECRET_KEY установлен
- PORT не конфликтует (Render использует переменную PORT автоматически)

## Troubleshooting

### Health check не проходит

Проверьте логи на наличие ошибок подключения к БД.

### Redis не подключается

См. [REDIS-SETUP.md](REDIS-SETUP.md) - подробная инструкция по настройке.

### Сборка падает

- Clear Build Cache & Deploy
- Проверьте `render.yaml` в корне проекта
- Убедитесь что все переменные окружения установлены

## Обновление

После каждого push в ветку `main`:
- Автоматический деплой
- Время обновления: ~2-3 минуты

## Стоимость

- **PostgreSQL Starter**: $7/месяц
- **Redis Starter**: $7/месяц (опционально)
- **Web Service Starter**: $7/месяц
- **Итого**: $14-21/месяц

## Альтернативы

- **Railway**: https://railway.app (проще деплой, $5 кредит)
- **Fly.io**: https://fly.io (дешевле, $5-10/месяц)
- **Amvera**: https://amvera.ru (российский хостинг)

