# Heroku Deployment Guide

## 📋 Требования

- Аккаунт Heroku
- Установленный Heroku CLI
- Git

## 🚀 Быстрый старт

### 1. Установка Heroku CLI

```bash
# Windows (Chocolatey)
choco install heroku-cli

# macOS
brew install heroku/brew/heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

### 2. Аутентификация

```bash
heroku login
```

### 3. Создание приложения

```bash
cd deploy/heroku
heroku create mentorhub-your-name --region eu
```

### 4. Добавление аддонов

```bash
# PostgreSQL
heroku addons:create heroku-postgresql:essential-0

# Redis
heroku addons:create heroku-redis:mini

# Логирование
heroku addons:create papertrail:choklad

# Мониторинг ошибок
heroku addons:create sentry:developer
```

### 5. Настройка переменных окружения

```bash
# Heroku автоматически установит DATABASE_URL и REDIS_URL

# Дополнительные настройки
heroku config:set SECRET_KEY=$(openssl rand -hex 32)
heroku config:set ALGORITHM=HS256
heroku config:set ACCESS_TOKEN_EXPIRE_MINUTES=30
heroku config:set ENVIRONMENT=production

# Agora (опционально)
heroku config:set AGORA_APP_ID=your-app-id
heroku config:set AGORA_APP_CERTIFICATE=your-app-cert

# Stripe (опционально)
heroku config:set STRIPE_API_KEY=sk_test_xxx
heroku config:set STRIPE_WEBHOOK_SECRET=whsec_xxx

# AWS S3 (опционально)
heroku config:set AWS_ACCESS_KEY_ID=xxx
heroku config:set AWS_SECRET_ACCESS_KEY=xxx
heroku config:set AWS_S3_BUCKET=mentorhub-bucket

# Email (опционально)
heroku config:set SMTP_SERVER=smtp.gmail.com
heroku config:set SMTP_PORT=587
heroku config:set SMTP_USER=your-email@gmail.com
heroku config:set SMTP_PASSWORD=your-app-password
heroku config:set EMAIL_SENDER=noreply@mentorhub.com
```

### 6. Деплой

```bash
# Добавить remote
heroku git:remote -a mentorhub-your-name

# Задеплоить
git push heroku main

# Или с использованием Heroku Container Registry
heroku container:login
heroku container:push web -a mentorhub-your-name
heroku container:release web -a mentorhub-your-name
```

### 7. Запуск миграций

```bash
heroku run alembic upgrade head
```

### 8. Проверка

```bash
# Открыть приложение
heroku open

# Посмотреть логи
heroku logs --tail

# Проверить статус
heroku ps
```

## 📊 Масштабирование

```bash
# Увеличить количество web-процессов
heroku ps:scale web=2

# Увеличить размер dyno
heroku ps:type web=standard-2x
```

## 🔧 Управление

```bash
# Перезапустить приложение
heroku restart

# Запустить консоль
heroku run bash

# Запустить Python shell
heroku run python

# Выполнить команду
heroku run "python backend/scripts/seed_data.py"
```

## 📝 Логи и мониторинг

```bash
# Просмотр логов
heroku logs --tail
heroku logs --source app
heroku logs --ps web

# Метрики
heroku ps
heroku pg:info
heroku redis:info
```

## 🗄️ Работа с базой данных

```bash
# Информация о БД
heroku pg:info

# Подключиться к БД
heroku pg:psql

# Создать бэкап
heroku pg:backups:capture

# Восстановить из бэкапа
heroku pg:backups:restore b001 DATABASE_URL
```

## ⚠️ Troubleshooting

### Ошибка: H14 (Web process crashed)

```bash
heroku restart
heroku logs --tail
```

### Ошибка: R14 (Memory quota exceeded)

```bash
# Увеличить размер dyno
heroku ps:type web=standard-2x
```

### Ошибка: H12 (Request timeout)

- Оптимизировать долгие запросы
- Использовать фоновые задачи для тяжелых операций

## 💰 Стоимость (примерная)

- Dyno standard-2x: $50/месяц
- PostgreSQL essential-0: $9/месяц
- Redis mini: $5/месяц
- Papertrail: бесплатно
- Sentry: бесплатно (dev план)

**Итого:** ~$64/месяц

## 🔗 Полезные ссылки

- [Heroku Dashboard](https://dashboard.heroku.com)
- [Heroku Dev Center](https://devcenter.heroku.com)
- [Heroku Postgres](https://www.heroku.com/postgres)
- [Heroku Redis](https://www.heroku.com/redis)
