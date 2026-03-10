# Деплой MentorHub на Render

## 📋 Обзор

Эта инструкция поможет вам развернуть MentorHub на платформе [Render](https://render.com/).

## 🔧 Предварительные требования

1. Аккаунт на Render (можно войти через GitHub)
2. Репозиторий проекта на GitHub/GitLab
3. Домен (опционально, для production)

## 🚀 Быстрый старт

### Способ 1: Автоматический деплой (рекомендуется)

1. **Подключите репозиторий к Render:**
   - Зайдите в [Render Dashboard](https://dashboard.render.com/)
   - Нажмите **New +** → **Blueprint**
   - Подключите ваш GitHub/GitLab репозиторий
   - Выберите репозиторий с `render.yaml`

2. **Render автоматически создаст:**
   - ✅ Backend сервис (Python)
   - ✅ Frontend сервис (Next.js)
   - ✅ PostgreSQL базу данных
   - ✅ Redis кеш
   - ✅ Все необходимые переменные окружения

3. **Настройте переменные окружения:**
   После развёртывания добавьте в backend сервис:
   ```
   SECRET_KEY=<сгенерируйте надёжный ключ>
   ```

4. **Готово!** Сервис доступен по URL: `https://mentorhub-backend-xxxx.onrender.com`

### Способ 2: Ручная настройка

Если автоматическое развёртывание не сработало:

#### 1. Создайте Backend сервис

1. В Dashboard нажмите **New +** → **Web Service**
2. Подключите ваш репозиторий
3. Настройте:
   ```yaml
   Name: mentorhub-backend
   Region: Frankfurt (или ближайший к вам)
   Branch: main
   Root Directory: (оставьте пустым)
   Runtime: Python 3
   Build Command: (оставьте пустым)
   Start Command: bash /app/start.sh
   ```

4. Выберите тариф:
   - **Free** — для тестирования (засыпает через 15 мин бездействия)
   - **Starter** ($7/мес) — для production

#### 2. Добавьте PostgreSQL

1. В Dashboard нажмите **New +** → **PostgreSQL**
2. Настройте:
   ```yaml
   Name: mentorhub-db
   Region: Frankfurt (тот же что и backend)
   Database: mentorhub
   User: mentorhub_user
   Plan: Starter
   ```

3. После создания скопируйте **Internal Database URL**

#### 3. Добавьте Redis

1. В Dashboard нажмите **New +** → **Redis**
2. Настройте:
   ```yaml
   Name: mentorhub-redis
   Region: Frankfurt (тот же что и backend)
   Plan: Starter
   Max Memory Policy: allkeys-lru
   ```

3. После создания скопируйте **Internal Database URL**

#### 4. Настройте переменные окружения

В настройках backend сервиса перейдите в **Environment** и добавьте:

```bash
# Database
DATABASE_URL=postgresql://mentorhub_user:password@host:5432/mentorhub

# Redis
REDIS_URL=redis://user:password@host:port/db

# Security
SECRET_KEY=<сгенерируйте: python -c "import secrets; print(secrets.token_urlsafe(32))">

# Application
ENVIRONMENT=production
DEBUG=False

# Frontend URL
NEXT_PUBLIC_API_URL=https://mentorhub-backend-xxxx.onrender.com
```

#### 5. Deploy

1. Нажмите **Save Changes**
2. Render автоматически начнёт сборку и деплой
3. Первый деплой займёт ~5-10 минут

## 📊 Мониторинг

### Проверка здоровья

После деплоя проверьте:

```bash
# Health check
curl https://mentorhub-backend-xxxx.onrender.com/api/v1/health

# Detailed health check
curl https://mentorhub-backend-xxxx.onrender.com/api/v1/health/detailed
```

### Логи

- Зайдите в настройки сервиса → **Logs**
- Включите **Real-time logs** для отладки

### Метрики

- Перейдите в **Metrics** для просмотра:
  - CPU usage
  - Memory usage
  - Request count
  - Response time

## 🔍 Troubleshooting

### Ошибка: "Redis not available"

**Симптомы:**
```
WARNING:app.services.cache:⚠️ Redis not available, using memory cache
```

**Решение:**
1. Проверьте что Redis сервис создан и запущен
2. Скопируйте **Internal Database URL** из панели Redis
3. Добавьте переменную `REDIS_URL` в backend сервис
4. Перезапустите backend (**Manual Deploy** → **Restart**)

См. подробную инструкцию: [DEPLOYMENT-REDIS-RENDER.md](documents/DEPLOYMENT-REDIS-RENDER.md)

### Ошибка: "Database not ready"

**Решение:**
1. Проверьте статус PostgreSQL в панели Render
2. Убедитесь что `DATABASE_URL` правильный
3. Проверьте что регион БД совпадает с регионом backend

### Ошибка: "Address already in use"

**Решение:**
1. Убедитесь что `PORT` не установлен в переменных окружения
2. Render автоматически устанавливает PORT
3. Проверьте `start.sh` — он должен использовать `${PORT:-3000}`

### Ошибка: "Build failed"

**Возможные причины:**
- Недостаточно памяти на Free тарифе
- Ошибки зависимостей в requirements.txt

**Решение:**
1. Переключитесь на Starter тариф
2. Проверьте логи сборки
3. Убедитесь что все зависимости указаны в requirements.txt

### Frontend не загружается

**Проверьте:**
1. `NEXT_PUBLIC_API_URL` установлен правильно
2. Frontend build прошёл успешно
3. В логах нет ошибок сборки Next.js

## 💰 Стоимость

| Компонент | Тариф | Цена/мес |
|-----------|-------|----------|
| Backend (Starter) | 512 MB RAM | $7 |
| PostgreSQL (Starter) | 256 MB | $7 |
| Redis (Starter) | 256 MB | $7 |
| **Итого** | | **$21/мес** |

Для экономии можно использовать Free тарифы для тестирования ($0), но они засыпают при бездействии.

## 🔐 Безопасность

### Обязательно настройте:

1. **SECRET_KEY** — сгенерируйте надёжный ключ:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **CORS_ORIGINS** — укажите ваш домен:
   ```
   CORS_ORIGINS=https://yourdomain.com
   ```

3. **Environment variables** — храните секреты в панели Render, не в репозитории!

### Рекомендуется:

- Включить **Private Networking** между сервисами
- Настроить **IP Allow List** для базы данных
- Использовать **Custom Domain** с HTTPS

## 📈 Масштабирование

### Когда масштабировать:

- CPU > 80% в течение 5 минут
- Memory > 85%
- Response time > 500ms
- Error rate > 1%

### Как масштабировать:

1. Зайдите в настройки сервиса
2. Измените **Plan** на более мощный
3. Сохраните — Render автоматически применит изменения

### Доступные тарифы:

| Тариф | RAM | CPU | Цена |
|-------|-----|-----|------|
| Starter | 512 MB | 0.5 | $7 |
| Standard | 2 GB | 1.0 | $25 |
| Pro | 4 GB | 2.0 | $50 |

## 🔄 CI/CD

Render автоматически деплоит при:

- Push в branch `main`
- Pull request (можно настроить preview)
- Ручном триггере в панели

### Настройка auto-deploy:

1. Settings → **Auto-Deploy** → **Enabled**
2. Branch: `main`
3. Сохраните

## 📚 Дополнительные ресурсы

- [Render Documentation](https://render.com/docs)
- [Render Pricing](https://render.com/pricing)
- [Render Community](https://community.render.com/)
- [MentorHub Documentation](../README.md)

## ✅ Чеклист после деплоя

- [ ] Backend отвечает на `/api/v1/health`
- [ ] Frontend загружается по URL
- [ ] Redis подключён (проверить логи)
- [ ] База данных подключена
- [ ] SECRET_KEY установлен
- [ ] CORS настроен
- [ ] Логи в порядке
- [ ] Метрики в норме
- [ ] Домен настроен (если используете)

## 🆘 Поддержка

Если возникли проблемы:

1. Проверьте логи в панели Render
2. Поищите в [документации Render](https://render.com/docs)
3. Спросите в [Render Community](https://community.render.com/)
4. Создайте issue в репозитории проекта
