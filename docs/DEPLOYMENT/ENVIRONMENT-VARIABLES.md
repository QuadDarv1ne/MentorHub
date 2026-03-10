# Переменные окружения для MentorHub на Render

## 📋 Минимальный набор для запуска

Эти переменные **обязательны** для работы MentorHub на Render.

### ✅ Обязательно

| Переменная | Значение | Где взять |
|------------|----------|-----------|
| `DATABASE_URL` | `postgresql://user:pass@host/db` | Автоматически из PostgreSQL |
| `SECRET_KEY` | Случайная строка 32+ символов | Автоматически (generateValue) |
| `ENVIRONMENT` | `production` | Вручную |
| `CORS_ORIGINS` | `https://your-app.onrender.com` | Вручную (ваш домен) |
| `FRONTEND_URL` | `https://your-app.onrender.com` | Вручную (ваш домен) |
| `NEXT_PUBLIC_API_BASE_URL` | `https://your-app.onrender.com/api/v1` | Вручную |
| `RENDER` | `true` | Вручную |

---

## 🔧 Настройка по шагам

### Шаг 1: Создайте сервисы

1. **PostgreSQL:**
   - Render Dashboard → **New +** → **PostgreSQL**
   - Name: `mentorhub-db`
   - Region: Frankfurt (или ваш)
   - Plan: `Starter`

2. **Backend (Web Service):**
   - Render Dashboard → **New +** → **Web Service**
   - Name: `mentorhub-backend`
   - Connect ваш репозиторий
   - Branch: `main`
   - Build Command: (пусто)
   - Start Command: `bash /app/start.sh`
   - Plan: `Starter`

---

### Шаг 2: Добавьте переменные окружения

Зайдите в **mentorhub-backend** → **Environment** → **Add Environment Variable**

#### 1. ENVIRONMENT

```
Key: ENVIRONMENT
Value: production
```

**Зачем:** Включает production режим (отключает debug, включает кэширование).

---

#### 2. SECRET_KEY

```
Key: SECRET_KEY
Value: <сгенерируйте>
```

**Сгенерировать ключ:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Пример:**
```
x8jK3mN9pL2qR5tY7wZ1aB4cD6eF8gH0iJ2kL4mN6oP8
```

**Зачем:** Подпись JWT токенов, шифрование сессий.

**Важно:** 
- Минимум 32 символа
- Не используйте одинаковый ключ в production и development
- Если используете Blueprint — `generateValue: true` создаст автоматически

---

#### 3. CORS_ORIGINS

```
Key: CORS_ORIGINS
Value: https://mentorhub-7eat.onrender.com
```

**Зачем:** Разрешает браузеру делать запросы с вашего домена.

**Формат:**
- Один домен: `https://your-app.onrender.com`
- Несколько: `https://app.com,https://www.app.com`

**Где взять ваш домен:**
- Render Dashboard → Ваш сервис → URL
- Выглядит как: `https://mentorhub-7eat.onrender.com`

---

#### 4. FRONTEND_URL

```
Key: FRONTEND_URL
Value: https://mentorhub-7eat.onrender.com
```

**Зачем:** Backend знает где находится frontend для редиректов и ссылок.

---

#### 5. NEXT_PUBLIC_API_BASE_URL

```
Key: NEXT_PUBLIC_API_BASE_URL
Value: https://mentorhub-7eat.onrender.com/api/v1
```

**Зачем:** Frontend знает куда отправлять API запросы.

**Важно:** 
- Префикс `NEXT_PUBLIC_` обязателен (Next.js)
- Должен заканчиваться на `/api/v1`

---

#### 6. RENDER

```
Key: RENDER
Value: true
```

**Зачем:** Определяет что приложение запущено на Render (для совместимости).

---

### Шаг 3: DATABASE_URL (автоматически)

Если вы создали PostgreSQL через Render и подключили его к сервису:

```
Key: DATABASE_URL
Value: <автоматически добавляется Render>
```

**Проверьте:**
1. Зайдите в **Environment**
2. `DATABASE_URL` должен быть там автоматически
3. Выглядит как: `postgresql://user:pass@host:5432/dbname`

**Если нет:**
- Зайдите в PostgreSQL Dashboard
- Скопируйте **Internal Database URL**
- Добавьте в Environment вручную

---

## 📊 Полный список всех переменных

### Обязательные (7)

```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=<32+ символов>
ENVIRONMENT=production
CORS_ORIGINS=https://your-app.onrender.com
FRONTEND_URL=https://your-app.onrender.com
NEXT_PUBLIC_API_BASE_URL=https://your-app.onrender.com/api/v1
RENDER=true
```

### Опциональные (для расширенного функционала)

#### Redis (кеширование и rate limiting)

```bash
REDIS_URL=redis://default:pass@host:6379/0
```

#### Agora (видео-звонки)

```bash
AGORA_APP_ID=your-app-id
AGORA_APP_CERTIFICATE=your-app-certificate
```

#### Stripe (платежи)

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

#### Sentry (мониторинг ошибок)

```bash
SENTRY_DSN=https://xxx@yyy.ingest.sentry.io/zzz
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
```

#### AWS S3 (хранение файлов)

```bash
AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_S3_BUCKET=your-bucket-name
AWS_REGION=us-east-1
```

#### Email (SMTP)

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@mentorhub.com
SMTP_FROM_NAME=MentorHub
```

#### SBP (Система быстрых платежей)

```bash
SBP_MERCHANT_ID=your-merchant-id
SBP_API_KEY=your-api-key
SBP_API_SECRET=your-api-secret
SBP_CALLBACK_URL=https://your-app.onrender.com/api/payments/sbp/callback
```

---

## 🚀 Проверка после настройки

### 1. Health Check

```bash
curl https://your-app.onrender.com/api/v1/health
```

**Ожидаемый ответ:**
```json
{
  "status": "healthy",
  "timestamp": 1234567890,
  "services": {
    "database": "healthy"
  }
}
```

### 2. Логи

Зайдите в **Logs** в Render Dashboard:

**Должно быть:**
```
✅ Database configured
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Если Redis подключён:**
```
✅ Redis cache connected
INFO: Redis cache enabled
```

### 3. Frontend

Откройте в браузере:
```
https://your-app.onrender.com
```

**Должна загрузиться главная страница.**

---

## 🔍 Troubleshooting

### Ошибка: "DATABASE_URL not set"

**Причина:** PostgreSQL не подключен или переменная не установлена.

**Решение:**
1. Проверьте что PostgreSQL создан
2. Зайдите в **Environment**
3. Убедитесь что `DATABASE_URL` есть
4. Если нет — скопируйте из PostgreSQL Dashboard

---

### Ошибка: "CORS origin not allowed"

**Причина:** `CORS_ORIGINS` не совпадает с доменом.

**Решение:**
1. Скопируйте точный URL из Render (без `/` в конце)
2. Обновите `CORS_ORIGINS`
3. Перезапустите сервис

---

### Ошибка: "Invalid SECRET_KEY"

**Причина:** Ключ слишком короткий или не установлен.

**Решение:**
```bash
# Сгенерируйте новый
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Должно быть минимум 32 символа.

---

### Ошибка: "Redis not available"

**Причина:** Redis не подключен.

**Решение:**
- **Вариант 1:** Игнорировать (будет работать in-memory кеш)
- **Вариант 2:** Создать Redis и добавить `REDIS_URL`

---

## 💡 Советы

### 1. Используйте группы переменных

Создайте локальный файл `.env.render`:

```bash
# Required
DATABASE_URL=postgresql://...
SECRET_KEY=...
ENVIRONMENT=production
CORS_ORIGINS=https://...
FRONTEND_URL=https://...
NEXT_PUBLIC_API_BASE_URL=https://.../api/v1
RENDER=true

# Optional (add as needed)
# REDIS_URL=redis://...
# AGORA_APP_ID=...
# STRIPE_SECRET_KEY=...
```

---

### 2. Проверяйте перед деплоем

Перед тем как нажать **Save Changes**:

- ✅ Все 7 обязательных переменных добавлены
- ✅ `DATABASE_URL` начинается с `postgresql://`
- ✅ `SECRET_KEY` минимум 32 символа
- ✅ `CORS_ORIGINS` и `FRONTEND_URL` совпадают с вашим доменом
- ✅ `NEXT_PUBLIC_API_BASE_URL` заканчивается на `/api/v1`

---

### 3. Перезапускайте после изменений

После добавления переменных:

1. **Deployments** → **Manual Deploy** → **Restart**
2. Подождите 2-3 минуты
3. Проверьте логи

---

### 4. Храните секреты безопасно

- ❌ Не коммитьте `.env` в Git
- ✅ Используйте Render Environment Variables
- ✅ Регулярно обновляйте `SECRET_KEY`
- ✅ Используйте разные ключи для dev/staging/production

---

## 📚 Дополнительные ресурсы

- [Render Environment Variables](https://render.com/docs/environment-variables)
- [Render PostgreSQL](https://render.com/docs/postgresql)
- [Render Redis](https://render.com/docs/redis)
- [MentorHub Documentation](../README.md)

---

## ✅ Чеклист

- [ ] PostgreSQL создан и подключен
- [ ] `DATABASE_URL` установлен (автоматически)
- [ ] `SECRET_KEY` сгенерирован (32+ символа)
- [ ] `ENVIRONMENT=production`
- [ ] `CORS_ORIGINS` = ваш домен
- [ ] `FRONTEND_URL` = ваш домен
- [ ] `NEXT_PUBLIC_API_BASE_URL` = ваш домен + `/api/v1`
- [ ] `RENDER=true`
- [ ] Сервис перезапущен
- [ ] Health check проходит
- [ ] Frontend загружается

**Готово!** 🎉
