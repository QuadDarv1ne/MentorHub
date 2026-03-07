# Render Deployment Guide

## 📋 Требования

- Аккаунт Render
- GitHub репозиторий

## 🚀 Быстрый старт

### Способ 1: Через Dashboard (рекомендуется)

1. **Создайте новый проект**
   - Зайдите на [dashboard.render.com](https://dashboard.render.com)
   - Нажмите "New +" → "Blueprint"
   - Подключите GitHub репозиторий
   - Выберите файл `deploy/render/render.yaml`

2. **Настройте переменные окружения**

   Render автоматически создаст:
   - PostgreSQL базу данных
   - Redis кеш

   Необходимо добавить в Dashboard:
   ```
   SECRET_KEY=<сгенерируйте надежный ключ>
   AGORA_APP_ID=<ваш app id>
   AGORA_APP_CERTIFICATE=<ваш cert>
   STRIPE_API_KEY=<ваш ключ>
   AWS_ACCESS_KEY_ID=<ваш ключ>
   AWS_SECRET_ACCESS_KEY=<ваш секрет>
   SMTP_USER=<ваш email>
   SMTP_PASSWORD=<пароль приложения>
   ```

3. **Запустите деплой**
   - Нажмите "Apply"
   - Render автоматически создаст все сервисы

### Способ 2: Через Render CLI

```bash
# Установка CLI
npm install -g @render-cloud/cli

# Аутентификация
render login

# Деплой
render up deploy/render/render.yaml
```

## 📊 Архитектура на Render

```
┌─────────────────────────────────────────────────────┐
│                 Render Platform                     │
│                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   Backend   │  │   Frontend   │  │  Worker   │ │
│  │   (Web)     │  │   (Web)      │  │  (Worker) │ │
│  │  Port: 8000 │  │  Port: 3000  │  │           │ │
│  └──────┬──────┘  └──────┬───────┘  └─────┬─────┘ │
│         │                │                 │       │
│         └────────────────┼─────────────────┘       │
│                          │                         │
│         ┌────────────────┴────────┐               │
│         │      PostgreSQL         │               │
│         │      (Managed)          │               │
│         └─────────────────────────┘               │
│         ┌─────────────────────────┐               │
│         │       Redis             │               │
│         │      (Managed)          │               │
│         └─────────────────────────┘               │
└─────────────────────────────────────────────────────┘
```

## 🔧 Управление

### Через Dashboard

1. **Просмотр логов**
   - Зайдите в сервис
   - Вкладка "Logs"

2. **Перезапуск сервиса**
   - Зайдите в сервис
   - Кнопка "Restart"

3. **Масштабирование**
   - Settings → Instance Size
   - Выберите план (Starter, Standard, Pro)

### Через CLI

```bash
# Логи
render logs -s mentorhub-backend

# Перезапуск
render restart -s mentorhub-backend

# Деплой
render deploy -s mentorhub-backend
```

## 🗄️ Базы данных

### PostgreSQL

```bash
# Получить connection string
render db show mentorhub-db

# Подключиться
psql $(render db connection-string mentorhub-db)

# Бэкап
pg_dump $(render db connection-string mentorhub-db) > backup.sql

# Восстановление
psql $(render db connection-string mentorhub-db) < backup.sql
```

### Redis

```bash
# Получить connection string
render redis show mentorhub-redis

# Подключиться
redis-cli -u $(render redis connection-string mentorhub-redis)
```

## 🔄 CI/CD

Render автоматически деплоит при пуше в main ветку.

### Отключение авто-деплоя

1. Зайдите в сервис
2. Settings → Auto-Deploy
3. Отключите

### Деплой определенной ветки

1. Settings → Branch
2. Выберите ветку

## ⚠️ Troubleshooting

### Ошибка: Build failed

- Проверьте логи сборки
- Убедитесь, что все зависимости указаны
- Проверьте совместимость версий

### Ошибка: Health check failed

- Проверьте, что приложение запускается
- Убедитесь, что health endpoint доступен
- Проверьте логи

### Ошибка: Database connection failed

- Проверьте DATABASE_URL
- Убедитесь, что БД создана
- Проверьте network settings

## 💰 Стоимость

| Сервис | План | Стоимость/месяц |
|--------|------|----------------|
| Backend (Web) | Starter | $7 |
| Frontend (Web) | Starter | $7 |
| Worker | Starter | $7 |
| Beat | Starter | $7 |
| PostgreSQL | Starter | $7 |
| Redis | Starter | $7 |

**Итого:** ~$42/месяц

## 🎯 Оптимизация стоимости

1. Используйте один сервис для backend + frontend
2. Отключите ненужные сервисы
3. Используйте бесплатный план для dev

## 🔗 Полезные ссылки

- [Render Dashboard](https://dashboard.render.com)
- [Render Docs](https://render.com/docs)
- [Render CLI](https://render.com/docs/cli)
- [Render Pricing](https://render.com/pricing)
