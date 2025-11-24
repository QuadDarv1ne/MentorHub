# 📊 Мониторинг и производительность MentorHub

Руководство по системам мониторинга, кеширования и оптимизации производительности.

## 🎯 Обзор улучшений

### Добавленные системы:

1. **Performance Monitoring** - мониторинг производительности
2. **Caching System** - система кеширования
3. **Database Backup** - автоматическое резервное копирование
4. **Metrics API** - API для получения метрик

---

## 📈 Performance Monitoring

### Что отслеживается:

**Системные метрики:**
- CPU usage (%)
- Memory usage (%)
- Disk usage (%)
- Uptime

**Метрики приложения:**
- Общее количество запросов
- Количество ошибок
- Error rate (%)
- Requests per second
- Время ответа по endpoints
- Популярные endpoints
- Медленные endpoints

### API Endpoints:

#### Получение метрик (Admin only)

```http
GET /api/v1/admin/metrics
Authorization: Bearer <admin-token>
```

**Ответ:**
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "uptime_seconds": 3600,
  "system": {
    "cpu_percent": 45.2,
    "memory_percent": 65.8,
    "memory_used_mb": 512,
    "memory_total_mb": 1024,
    "disk_percent": 42.1,
    "disk_used_gb": 50.5,
    "disk_total_gb": 120
  },
  "application": {
    "total_requests": 15234,
    "total_errors": 23,
    "error_rate_percent": 0.15,
    "requests_per_second": 4.23
  },
  "slow_endpoints": [
    {
      "endpoint": "/api/v1/courses/search",
      "avg_ms": 1250.5,
      "max_ms": 3200.0,
      "count": 50
    }
  ],
  "popular_endpoints": [
    {
      "endpoint": "/api/v1/mentors",
      "calls": 5234
    }
  ]
}
```

#### Детальная проверка здоровья

```http
GET /api/v1/health/detailed
```

**Ответ:**
```json
{
  "status": "healthy",
  "issues": [],
  "metrics": { ... }
}
```

**Возможные статусы:**
- `healthy` - всё в порядке
- `degraded` - есть проблемы (высокая нагрузка, error rate)
- `error` - критические ошибки

#### Сброс метрик (Admin only)

```http
POST /api/v1/admin/metrics/reset
Authorization: Bearer <admin-token>
```

### Использование в коде:

#### Измерение времени выполнения:

```python
from app.utils.monitoring import measure_time

async def my_function():
    async with measure_time("database_query"):
        result = await db.execute(query)
```

#### Декоратор для функций:

```python
from app.utils.monitoring import measure_execution_time

@measure_execution_time
async def slow_operation():
    # Автоматически логирует время если > 500ms
    await heavy_computation()
```

---

## 💾 Caching System

### Возможности:

- **Redis** как основное хранилище кеша
- **In-memory** fallback при недоступности Redis
- TTL (Time To Live) для автоматического истечения
- Декораторы для простого использования
- Инвалидация кеша по паттернам

### Использование:

#### Базовые операции:

```python
from app.utils.cache import cache_manager

# Получение
value = await cache_manager.get("user:123")

# Сохранение (TTL 5 минут)
await cache_manager.set("user:123", user_data, ttl=300)

# Удаление
await cache_manager.delete("user:123")

# Очистка по паттерну
await cache_manager.clear("user:*")
```

#### Декоратор @cached:

```python
from app.utils.cache import cached, CACHE_TTL

@cached(ttl=CACHE_TTL['mentor'], key_prefix="mentor")
async def get_mentor_by_id(mentor_id: int):
    # Функция выполнится только при cache miss
    mentor = await db.query(Mentor).filter(Mentor.id == mentor_id).first()
    return mentor
```

**Параметры декоратора:**
- `ttl` - время жизни кеша в секундах
- `key_prefix` - префикс для ключа
- `skip_auth` - не учитывать user_id в ключе

#### Предустановленные TTL:

```python
CACHE_TTL = {
    'user': 600,       # 10 минут
    'mentor': 900,     # 15 минут
    'course': 1800,    # 30 минут
    'review': 300,     # 5 минут
    'stats': 60,       # 1 минута
    'session': 120,    # 2 минуты
    'list': 180,       # 3 минуты (списки)
}
```

#### Инвалидация кеша:

```python
from app.utils.cache import invalidate_cache

# После обновления ментора
await mentor_service.update_mentor(mentor_id, data)
await invalidate_cache(f"mentor:*{mentor_id}*")
```

### Пример в API endpoint:

```python
from app.utils.cache import cached, CACHE_TTL

@router.get("/mentors/{mentor_id}")
@cached(ttl=CACHE_TTL['mentor'], key_prefix="mentor_detail")
async def get_mentor(
    mentor_id: int,
    db: Session = Depends(get_db)
):
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not mentor:
        raise HTTPException(404, "Mentor not found")
    return mentor
```

---

## 💽 Database Backup

### Возможности:

- Автоматическое резервное копирование SQLite и PostgreSQL
- Загрузка backup'ов в AWS S3
- Автоматическая очистка старых backup'ов
- Восстановление из backup
- Сжатие для PostgreSQL (custom format)

### Использование:

#### Создание backup:

```bash
# Вручную
python backend/backup_database.py

# Или через код
from backup_database import DatabaseBackup

backup = DatabaseBackup()
backup_file = backup.create_backup()
```

#### Автоматический backup (cron):

```bash
# Каждый день в 3:00 AM
0 3 * * * cd /path/to/project && python backend/backup_database.py
```

#### Настройка AWS S3:

```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=mentorhub-backups
AWS_REGION=eu-west-1
```

#### Восстановление из backup:

```python
from backup_database import DatabaseBackup
from pathlib import Path

backup = DatabaseBackup()
backup_file = Path("backups/mentorhub_backup_20240115_103000.sql")
backup.restore_backup(backup_file)
```

**⚠️ ВНИМАНИЕ:** Восстановление перезапишет текущую базу данных!

### Структура backup'ов:

```
backups/
├── mentorhub_backup_20240115_030000.sql
├── mentorhub_backup_20240116_030000.sql
└── mentorhub_backup_20240117_030000.sql
```

### Хранение в S3:

```
s3://mentorhub-backups/
└── backups/
    ├── mentorhub_backup_20240115_030000.sql
    ├── mentorhub_backup_20240116_030000.sql
    └── mentorhub_backup_20240117_030000.sql
```

---

## 🔧 Настройка

### Environment Variables:

```env
# Cache
REDIS_URL=redis://localhost:6379/0

# Backup
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_S3_BUCKET=mentorhub-backups
AWS_REGION=eu-west-1

# Monitoring
SENTRY_DSN=https://...@sentry.io/...  # опционально
```

### Рекомендации для production:

1. **Monitoring:**
   - Настройте алерты при high CPU/memory
   - Мониторьте error rate
   - Отслеживайте медленные endpoints

2. **Caching:**
   - Используйте Redis в production
   - Настройте TTL в зависимости от данных
   - Инвалидируйте кеш при изменении данных

3. **Backup:**
   - Запускайте backup ежедневно через cron
   - Храните backup в S3
   - Периодически тестируйте восстановление
   - Держите минимум 7 дней backup'ов

---

## 📊 Dashboard (будущее)

Планируется добавление:
- Grafana dashboard для визуализации метрик
- Prometheus интеграция
- Alerting система
- Real-time мониторинг

---

## 🧪 Тестирование

### Проверка мониторинга:

```bash
# Получение метрик
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:8000/api/v1/admin/metrics

# Детальная проверка
curl http://localhost:8000/api/v1/health/detailed
```

### Проверка кеширования:

```python
import asyncio
from app.utils.cache import cache_manager

async def test_cache():
    # Set
    await cache_manager.set("test_key", {"value": 123}, ttl=60)
    
    # Get
    value = await cache_manager.get("test_key")
    print(value)  # {'value': 123}
    
    # Delete
    await cache_manager.delete("test_key")

asyncio.run(test_cache())
```

### Проверка backup:

```bash
# Создание тестового backup
python backend/backup_database.py

# Проверка созданных файлов
ls -lh backups/
```

---

## 📈 Best Practices

### Кеширование:

✅ **DO:**
- Кешируйте данные, которые часто читаются
- Используйте короткий TTL для динамичных данных
- Инвалидируйте кеш при обновлении данных
- Используйте осмысленные key_prefix

❌ **DON'T:**
- Не кешируйте персональные/чувствительные данные надолго
- Не забывайте про инвалидацию
- Не используйте слишком длинный TTL для часто меняющихся данных

### Мониторинг:

✅ **DO:**
- Регулярно проверяйте метрики
- Настройте алерты для критических значений
- Анализируйте медленные endpoints
- Отслеживайте error rate

❌ **DON'T:**
- Не игнорируйте предупреждения о high CPU/memory
- Не допускайте error rate > 1%

### Backup:

✅ **DO:**
- Делайте backup ежедневно
- Храните backup в отдельном хранилище (S3)
- Тестируйте восстановление
- Храните минимум 7 дней backup'ов

❌ **DON'T:**
- Не храните backup только локально
- Не забывайте удалять старые backup'ы

---

## 🆘 Troubleshooting

### Высокая нагрузка CPU:

```bash
# Проверка метрик
curl http://localhost:8000/api/v1/health/detailed

# Проверка медленных endpoints
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:8000/api/v1/admin/metrics | jq '.slow_endpoints'
```

### Redis недоступен:

Система автоматически переключится на in-memory кеш. Проверьте логи:

```bash
tail -f logs/app.log | grep "Cache"
```

### Backup failed:

```bash
# Проверьте переменные окружения
echo $DATABASE_URL
echo $AWS_S3_BUCKET

# Проверьте логи
python backend/backup_database.py 2>&1 | tee backup.log
```

---

**Версия документа:** 1.0  
**Последнее обновление:** 2024-11-24
