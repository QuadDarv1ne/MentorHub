# 🚀 Оптимизация Docker Image для MentorHub

## Обзор изменений

Оптимизированный Dockerfile для работы на Free тарифах (512MB RAM).

### 📊 Ожидаемые улучшения

| Метрика | До | После | Улучшение |
|---------|-----|-------|-----------|
| **Размер image** | ~1.2GB | ~600MB | -50% |
| **Потребление RAM** | ~400MB | ~250MB | -37% |
| **Время сборки** | ~5 мин | ~3 мин | -40% |

---

## 🔧 Применённые оптимизации

### 1. **Multi-stage сборка**

```dockerfile
# Stage 1: Frontend Builder (node:18-alpine)
# Stage 2: Backend Builder (python:3.11-alpine)
# Stage 3: Production Image (python:3.11-alpine)
```

**Преимущества:**
- Только необходимые артефакты попадают в production image
- Уменьшение размера на ~40%

### 2. **Alpine Linux вместо slim**

```dockerfile
FROM python:3.11-alpine  # Вместо python:3.11-slim
FROM node:18-alpine
```

**Преимущества:**
- Alpine: ~5MB vs slim: ~120MB
- Меньше уязвимостей безопасности
- Быстрее сборка

### 3. **Оптимизация памяти Node.js**

```dockerfile
ENV NODE_OPTIONS="--max-old-space-size=128"
```

**В start.sh:**
```bash
node --max-old-space-size=128 server.js
```

**Преимущества:**
- Ограничение памяти V8 heap до 128MB
- Предотвращение OOM ошибок на Free тарифах

### 4. **Оптимизация памяти Python**

```dockerfile
ENV PYTHONMALLOC=malloc \
    MALLOC_ARENA_MAX=2
```

**Преимущества:**
- Уменьшение fragmentation памяти
- Меньшее потребление RAM при долгой работе

### 5. **Tini для управления процессами**

```dockerfile
ENTRYPOINT ["/sbin/tini", "--"]
```

**Преимущества:**
- Правильная обработка сигналов (SIGTERM, SIGINT)
- Быстрый graceful shutdown
- Предотвращение zombie процессов

### 6. **Non-root пользователь**

```dockerfile
RUN addgroup -g 1000 appgroup && \
    adduser -u 1000 -G appgroup -D appuser

USER appuser
```

**Преимущества:**
- Безопасность (меньше привилегий)
- Соответствие best practices

### 7. **Очистка кэшей**

```dockerfile
RUN npm cache clean --force && \
    rm -rf /root/.npm /root/.node-gyp /tmp/*
```

**Преимущества:**
- Уменьшение размера image на ~100MB
- Чище image

### 8. **Оптимизация зависимостей**

```dockerfile
# Frontend: только production зависимости
RUN npm ci --legacy-peer-deps --only=production

# Backend: без кэша
RUN pip install --no-cache-dir -r requirements.txt
```

**Преимущества:**
- Меньше размер
- Быстрее установка

### 9. **Отключение телеметрии**

```dockerfile
ENV NEXT_TELEMETRY_DISABLED=1 \
    NEXT_SOURCE_MAP_DISABLED=true
```

**Преимущества:**
- Меньше размер build
- Нет лишних network запросов

### 10. **Оптимизация Uvicorn**

```bash
uvicorn app.main:app \
    --host 0.0.0.0 \
    --port $BACKEND_PORT \
    --workers 1 \
    --no-access-log \
    --loop asyncio
```

**Преимущества:**
- 1 worker вместо нескольких (экономия RAM)
- Отключён access log (меньше I/O)
- asyncio loop для лучшей производительности

---

## 📈 Сравнение размеров

### Старый Dockerfile:
```
Stage 1: node:18-alpine (~120MB)
Stage 2: python:3.11-slim (~150MB)
 + gcc, libpq-dev (~200MB)
 + nodejs (~50MB)
 + pip packages (~300MB)
 + Next.js build (~200MB)
─────────────────────────────
Итого: ~1.2GB
```

### Новый Dockerfile:
```
Stage 1: node:18-alpine (~120MB)
Stage 2: python:3.11-alpine (~50MB)
Stage 3: python:3.11-alpine (~50MB)
 + libpq, nodejs (~80MB)
 + pip packages (скопированы) (~250MB)
 + Next.js build (optimized) (~150MB)
─────────────────────────────
Итого: ~600MB
```

---

## 🔍 Мониторинг потребления памяти

### В Render:

1. Откройте **Metrics** в панели Render
2. Следите за **Memory Usage**
3. Норма: 200-300MB из 512MB

### Логи:

```bash
✅ Services started:
   Backend PID: 7 on port 8000
   Frontend PID: 8 on port 10000
   Memory: Optimized for 512MB RAM
```

---

## 🎯 Дополнительные оптимизации (опционально)

### 1. Отключить лишние middleware

Если не нужны:
```python
# В backend/app/main.py
# Отключить Prometheus metrics
# Отключить Performance monitoring
```

### 2. Уменьшить pool соединений

```python
# В backend/app/config.py
DB_POOL_SIZE: int = 5  # Вместо 20
DB_MAX_OVERFLOW: int = 2  # Вместо 40
```

### 3. Оптимизировать SQL запросы

- Добавить индексы
- Использовать select_related для Django ORM
- Избегать N+1 queries

### 4. Кэширование

```python
# В Redis или memory cache
@cache_response(timeout=300)
def get_expensive_data():
    ...
```

---

## 🚨 Troubleshooting

### OOM (Out of Memory) ошибки:

**Симптомы:**
```
Killed
npm ERR! code 137
```

**Решения:**
1. Увеличьте лимит памяти Node.js:
   ```bash
   NODE_OPTIONS="--max-old-space-size=256"
   ```

2. Или перейдите на Starter тариф ($7/мес)

### Медленная сборка:

**Решения:**
1. Кэшируйте Docker слои
2. Используйте BuildKit:
   ```bash
   DOCKER_BUILDKIT=1 docker build .
   ```

### Backend не отвечает:

**Проверьте:**
```bash
curl http://localhost:8000/api/v1/health/ready
```

**Логи:**
```bash
docker logs <container_id>
```

---

## 📚 Источники

- [Node.js Memory Limits](https://nodejs.org/api/cli.html#cli_max_old_space_size_size_in_megabytes)
- [Python Memory Management](https://docs.python.org/3/c-api/memory.html)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Alpine Linux Security](https://alpinelinux.org/about/)

---

**Последнее обновление:** 2026-03-09
**Статус:** ✅ Готово к production
