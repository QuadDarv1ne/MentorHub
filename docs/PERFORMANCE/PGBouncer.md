# PgBouncer Connection Pooling Guide

## Обзор

MentorHub использует **PgBouncer** для управления пулом соединений с PostgreSQL в production среде. Это позволяет:

- Уменьшить нагрузку на PostgreSQL при большом количестве подключений
- Улучшить производительность за счёт переиспользования соединений
- Масштабировать backend сервисы (до 3 реплик)
- Снизить latency при установлении соединений

## Архитектура

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Backend   │────▶│  PgBouncer  │────▶│  PostgreSQL │
│   (x3)      │     │  Pool: 50   │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
     │                    │                    │
     │                    │                    │
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Celery    │────▶│  PgBouncer  │────▶│  PostgreSQL │
│   Worker    │     │  Pool: 50   │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Конфигурация

### Docker Compose (production)

PgBouncer настроен в `docker-compose.prod.yml`:

```yaml
pgbouncer:
  image: bitnami/pgbouncer:latest
  environment:
    POSTGRESQL_HOST: postgres
    POSTGRESQL_PORT: 5432
    POSTGRESQL_USER: ${POSTGRES_USER:-mentorhub}
    POSTGRESQL_PASSWORD: ${POSTGRES_PASSWORD}
    POSTGRESQL_DATABASE: ${POSTGRES_DB:-mentorhub}
    PGBOUNCER_PORT: 6432
    PGBOUNCER_POOL_MODE: transaction
    PGBOUNCER_MAX_CLIENT_CONN: 1000
    PGBOUNCER_DEFAULT_POOL_SIZE: 50
    PGBOUNCER_MIN_POOL_SIZE: 10
    PGBOUNCER_RESERVE_POOL_SIZE: 25
```

### Режимы пулинга

**Transaction (рекомендуется)**:
- Соединение выделяется на время транзакции
- После COMMIT/ROLLBACK соединение возвращается в пул
- Поддерживает больше клиентов с меньшим числом соединений
- ⚠️ Не поддерживает session-level функции (например, `pg_advisory_lock`)

**Session**:
- Соединение закрепляется за клиентом на всё время подключения
- Меньшая эффективность, но полная совместимость

**Statement**:
- Соединение выделяется на время одного запроса
- Максимальная эффективность, но ограниченная совместимость

### Настройки приложения

Backend автоматически определяет PgBouncer по DATABASE_URL:

```python
# В production (Docker)
DATABASE_URL=postgresql://mentorhub:password@pgbouncer:6432/mentorhub

# Автоматическая настройка пула
DB_POOL_SIZE=5          # Уменьшен для PgBouncer
DB_MAX_OVERFLOW=10      # Уменьшен для PgBouncer
```

## Мониторинг

### Prometheus метрики

PgBouncer exporter собирает метрики:

- `pgbouncer_stats_cl_waiting` - клиенты в очереди ожидания
- `pgbouncer_stats_sv_active` - активные серверные соединения
- `pgbouncer_stats_avg_xact_time` - среднее время транзакции
- `pgbouncer_pools_server_active_conn` - активные соединения
- `pgbouncer_pools_client_active_conn` - активные клиенты

### Grafana Dashboard

Dashboard доступен на `http://localhost:3001` (порт 3001):
- PgBouncer connection pool usage
- Client waiting queue
- Transaction latency
- Server connection utilization

### Алерты

| Алерт | Условие | Критичность |
|-------|---------|-------------|
| PgBouncerDown | PgBouncer недоступен | Critical |
| PgBouncerHighClientUsage | >80% клиентов | Warning |
| PgBouncerHighServerUsage | >90% серверных соединений | Warning |
| PgBouncerHighWaitingClients | >50 клиентов в очереди | Warning |
| PgBouncerHighAvgXactTime | >1000ms среднее время | Warning |

## Локальная разработка

Для локальной разработки PgBouncer **не требуется**. Используйте прямое подключение:

```bash
# .env.local
DATABASE_URL=postgresql://mentorhub_user:password@localhost/mentorhub
```

Backend автоматически использует больший пул соединений (20/40) без PgBouncer.

## Troubleshooting

### "Too many clients" ошибка

**Проблема**: Превышен лимит подключений PostgreSQL

**Решение**:
1. Увеличьте `max_connections` в PostgreSQL
2. Уменьшите `PGBOUNCER_DEFAULT_POOL_SIZE`
3. Проверьте `pgbouncer_stats_sv_active` метрики

### Долгие транзакции

**Проблема**: `PgBouncerHighAvgXactTime` алерт

**Решение**:
1. Проверьте медленные запросы в PostgreSQL
2. Оптимизируйте N+1 queries
3. Добавьте индексы для частых запросов
4. Проверьте `pg_stat_activity` для long-running queries

### Клиенты в очереди ожидания

**Проблема**: `pgbouncer_stats_cl_waiting > 0`

**Решение**:
1. Увеличьте `PGBOUNCER_DEFAULT_POOL_SIZE`
2. Увеличьте `PGBOUNCER_RESERVE_POOL_SIZE`
3. Проверьте, не заблокированы ли соединения

## Production рекомендации

### Расчёт размера пула

Формула для расчёта оптимального размера пула:

```
pool_size = (cores * 2) + effective_spindle_count
```

Для Render Starter (1 CPU, SSD):
- `pool_size = (1 * 2) + 1 = 3`
- Рекомендуется: 5-10 соединений на реплику

Для production с 3 репликами backend:
- Общий пул: 5 × 3 = 15 соединений
- PgBouncer max_clients: 1000
- PostgreSQL max_connections: 100+

### Ресурсы

PgBouncer требует минимальные ресурсы:
- CPU: 0.25 cores
- Memory: 128-256 MB
- Network: минимальный overhead

### Безопасность

- PgBouncer не шифрует трафик (используйте SSL между сервисами)
- Не храните пароли в plaintext (используйте secrets manager)
- Ограничьте доступ к порту 6432 только для внутренних сервисов

## Ссылки

- [PgBouncer Documentation](https://www.pgbouncer.org/)
- [PgBouncer Configuration](https://www.pgbouncer.org/config.html)
- [PostgreSQL Connection Pooling Best Practices](https://wiki.postgresql.org/wiki/Number_Of_Database_Connections)
