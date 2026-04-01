# Quick Start - New Features (v1.1)

## 🚀 Быстрый старт с новыми возможностями

### 1. Использование Makefile

Теперь все команды доступны через Makefile:

```bash
# Показать все команды
make help

# Установить зависимости
make install

# Запустить development
make dev

# Запустить тесты с покрытием
make test-coverage

# Проверить безопасность
make security

# Форматировать код
make format

# Создать backup БД
make backup
```

### 2. Production Deployment

```bash
# Запустить production конфигурацию с PgBouncer
docker-compose -f docker-compose.prod.yml up -d

# Проверить статус
docker-compose -f docker-compose.prod.yml ps

# Посмотреть логи
docker-compose -f docker-compose.prod.yml logs -f
```

### 3. Load Testing

```bash
# Установить k6 (если еще не установлен)
# Windows: choco install k6
# macOS: brew install k6
# Linux: см. https://k6.io/docs/getting-started/installation/

# Запустить load test
make test-load

# Или напрямую
k6 run k6-load-test.js
```

### 4. Database Backup

```bash
# Создать backup
make backup

# Или напрямую
./scripts/backup.sh

# Восстановить из backup
make restore
# Введите путь к файлу backup

# Или напрямую
./scripts/restore.sh /backups/mentorhub_backup_20250116.sql.gz
```

### 5. Мониторинг

После запуска production конфигурации:

```bash
# Prometheus
http://localhost:9090

# Grafana
http://localhost:3001
Username: admin
Password: admin
```

### 6. Code Quality

```bash
# Проверить код
make lint

# Форматировать код
make format

# Запустить все проверки
make check
```

---

## 📊 Что нового?

### Безопасность
- ✅ Автоматическое сканирование при каждом push
- ✅ Dependabot обновляет зависимости автоматически
- ✅ CodeQL анализ кода

### Производительность
- ✅ PgBouncer: 3-5x улучшение работы с БД
- ✅ Redis оптимизация
- ✅ Nginx кеширование

### Надёжность
- ✅ Автоматические backup каждый день
- ✅ Health checks для всех сервисов
- ✅ Graceful shutdown

### Developer Experience
- ✅ 40+ команд в Makefile
- ✅ Улучшенная документация
- ✅ Load testing

---

## 🎯 Рекомендуемый workflow

### Development

```bash
# 1. Установить зависимости
make install

# 2. Запустить dev серверы
make dev

# 3. В другом терминале - запустить тесты
make test-coverage

# 4. Проверить код перед commit
make check
```

### Production

```bash
# 1. Запустить production
docker-compose -f docker-compose.prod.yml up -d

# 2. Создать первый backup
make backup

# 3. Проверить мониторинг
# Открыть http://localhost:9090 (Prometheus)
# Открыть http://localhost:3001 (Grafana)

# 4. Запустить load test
make test-load
```

---

## 🔧 Troubleshooting

### Проблема: Port уже занят

```bash
# Остановить все контейнеры
docker-compose down

# Или для production
docker-compose -f docker-compose.prod.yml down
```

### Проблема: Ошибка подключения к БД

```bash
# Проверить статус PostgreSQL
docker-compose ps postgres

# Посмотреть логи
docker-compose logs postgres

# Перезапустить
docker-compose restart postgres
```

### Проблема: Redis не работает

```bash
# Проверить статус
docker-compose ps redis

# Подключиться к Redis CLI
make shell-redis

# Проверить память
docker-compose exec redis redis-cli INFO memory
```

---

## 📚 Дополнительная документация

- [IMPROVEMENTS.md](IMPROVEMENTS.md) - Полное описание улучшений
- [PERFORMANCE.md](PERFORMANCE.md) - Руководство по производительности
- [CHANGELOG.md](../CHANGELOG.md) - История изменений
- [README.md](../README.md) - Основная документация

---

**Вопросы?** Создайте issue на GitHub или свяжитесь с командой.

**Last Updated:** 2025-01-16
