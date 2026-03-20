# 🚀 MentorHub Production Deployment Script

Автоматический скрипт для развертывания MentorHub в production

## Быстрый старт

```bash
# 1. Клонировать репозиторий
git clone https://github.com/QuadDarv1ne/MentorHub.git
cd MentorHub

# 2. Сделать скрипт исполняемым
chmod +x deploy.sh

# 3. Запустить деплой
./deploy.sh
```

## Требования

- Docker 20+
- Docker Compose 2.0+
- Git
- 4GB+ RAM
- 2+ CPU cores
- 20GB+ свободного места

## Использование

### Production деплой

```bash
./deploy.sh --production
```

### Staging деплой

```bash
./deploy.sh --staging
```

### Проверка без деплоя

```bash
./deploy.sh --check
```

### Очистка

```bash
./deploy.sh --cleanup
```

## Переменные окружения

Перед запуском создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
nano .env
```

**Обязательные переменные:**
- `SECRET_KEY` — минимум 32 символа
- `POSTGRES_PASSWORD` — сложный пароль
- `CORS_ORIGINS` — ваши production домены
- `SENTRY_DSN` — опционально

## Что делает скрипт

1. ✅ Проверка зависимостей (Docker, Docker Compose)
2. ✅ Проверка `.env` файла
3. ✅ Pull свежих изменений из git
4. ✅ Build Docker образов
5. ✅ Применение миграций Alembic
6. ✅ Запуск сервисов
7. ✅ Проверка health checks
8. ✅ Вывод статуса

## Логи

```bash
# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f

# Backend логи
docker-compose -f docker-compose.prod.yml logs backend

# Ошибки
docker-compose -f docker-compose.prod.yml logs | grep ERROR
```

## Troubleshooting

### Ошибка подключения к БД

```bash
# Проверить статус БД
docker-compose -f docker-compose.prod.yml ps postgres

# Проверить логи
docker-compose -f docker-compose.prod.yml logs postgres

# Перезапустить
docker-compose -f docker-compose.prod.yml restart postgres
```

### Ошибка миграций

```bash
# Применить миграции вручную
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### Сервис не запускается

```bash
# Проверить логи
docker-compose -f docker-compose.prod.yml logs <service-name>

# Пересоздать контейнер
docker-compose -f docker-compose.prod.yml up -d --force-recreate <service-name>
```

## Monitoring

После деплоя проверьте:

```bash
# Health check
curl http://localhost:8000/health

# Prometheus metrics
curl http://localhost:9090/metrics

# Grafana dashboard
open http://localhost:3000
```

## Security Checklist

- [ ] Измените все пароли по умолчанию
- [ ] Настройте firewall (UFW)
- [ ] Установите SSL сертификаты (Let's Encrypt)
- [ ] Включите rate limiting
- [ ] Настройте backups
- [ ] Проверьте CORS настройки

## Поддержка

Документация: [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)
GitHub Issues: https://github.com/QuadDarv1ne/MentorHub/issues
