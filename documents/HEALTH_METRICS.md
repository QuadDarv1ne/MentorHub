# 📊 Мониторинг и метрики MentorHub

## Обзор

MentorHub использует комплексную систему мониторинга для отслеживания производительности, доступности и работоспособности приложения.

## 🏥 Health Check Endpoints

### Базовая проверка

```http
GET /api/v1/health
```

**Ответ:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-24T12:00:00.000000",
  "service": "mentorhub-api"
}
```

### Детальная проверка

```http
GET /api/v1/health/detailed
```

**Ответ:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-24T12:00:00.000000",
  "components": {
    "database": {
      "status": "healthy",
      "message": "Database connection successful"
    },
    "cache": {
      "status": "healthy",
      "message": "Redis cache operational"
    },
    "system": {
      "status": "healthy",
      "cpu_percent": 25.5,
      "memory_percent": 45.2,
      "disk_percent": 60.1
    }
  }
}
```

### Kubernetes Probes

**Readiness Probe:**
```http
GET /api/v1/health/ready
```

**Liveness Probe:**
```http
GET /api/v1/health/live
```

## 📈 Prometheus Metrics

### Доступ к метрикам

```http
GET /metrics
```

### Доступные метрики

#### Метрики запросов

- `mentorhub_requests_total{method, endpoint, http_status}` - Общее количество запросов
- `mentorhub_request_duration_seconds{method, endpoint}` - Латентность запросов (histogram)
- `mentorhub_requests_in_progress{method, endpoint}` - Запросы в процессе выполнения

#### Метрики ошибок

- `mentorhub_errors_total{method, endpoint, exception_type}` - Общее количество ошибок

#### Метрики базы данных

- `mentorhub_db_connection_pool{pool_type}` - Метрики пула подключений
  - `pool_type="size"` - Размер пула
  - `pool_type="overflow"` - Overflow
  - `pool_type="used"` - Используемых подключений

#### Метрики кэша

- `mentorhub_cache_hits_total{cache_type}` - Попадания в кэш
- `mentorhub_cache_misses_total{cache_type}` - Промахи кэша

### Пример использования с Prometheus

**prometheus.yml:**
```yaml
scrape_configs:
  - job_name: 'mentorhub'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

## 🔍 Request ID Tracking

Каждый HTTP запрос автоматически получает уникальный Request ID для отслеживания в логах.

### Заголовки

**Request:**
```http
GET /api/v1/users/me
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```http
HTTP/1.1 200 OK
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000
```

### Получение Request ID в коде

```python
from fastapi import Request
from app.middleware.request_id import get_request_id

async def my_endpoint(request: Request):
    request_id = get_request_id(request)
    logger.info(f"Processing request {request_id}")
```

## 📊 Мониторинг производительности

### Встроенный Performance Monitor

Автоматически собирает метрики:

- Время ответа по эндпоинтам
- Количество запросов
- Процент ошибок
- Системные метрики (CPU, RAM, Disk)

### Доступ к метрикам

```http
GET /api/v1/monitoring/metrics
Authorization: Bearer <admin_token>
```

## 🐳 Docker Health Checks

**Dockerfile:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1
```

**docker-compose.yml:**
```yaml
services:
  backend:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

## ☸️ Kubernetes Deployment

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mentorhub-backend
spec:
  containers:
  - name: api
    image: mentorhub-backend:latest
    ports:
    - containerPort: 8000
    
    # Liveness probe
    livenessProbe:
      httpGet:
        path: /api/v1/health/live
        port: 8000
      initialDelaySeconds: 30
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3
    
    # Readiness probe
    readinessProbe:
      httpGet:
        path: /api/v1/health/ready
        port: 8000
      initialDelaySeconds: 10
      periodSeconds: 5
      timeoutSeconds: 3
      failureThreshold: 3
```

## 📈 Grafana Dashboard

### Пример запросов для визуализации

**Request rate:**
```promql
rate(mentorhub_requests_total[5m])
```

**Error rate:**
```promql
rate(mentorhub_errors_total[5m])
```

**Average response time:**
```promql
rate(mentorhub_request_duration_seconds_sum[5m]) 
/ rate(mentorhub_request_duration_seconds_count[5m])
```

**Requests in progress:**
```promql
mentorhub_requests_in_progress
```

## 🔔 Alerting Rules

### Пример Prometheus alerts

```yaml
groups:
- name: mentorhub_alerts
  rules:
  - alert: HighErrorRate
    expr: rate(mentorhub_errors_total[5m]) > 0.05
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors/second"
  
  - alert: HighLatency
    expr: histogram_quantile(0.95, rate(mentorhub_request_duration_seconds_bucket[5m])) > 2
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High latency detected"
      description: "95th percentile latency is {{ $value }}s"
  
  - alert: ServiceDown
    expr: up{job="mentorhub"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Service is down"
      description: "MentorHub API is not responding"
```

## 🛠️ Best Practices

1. **Регулярно проверяйте health endpoints** в production
2. **Настройте автоматические alerts** для критических метрик
3. **Используйте Request ID** для отладки проблем
4. **Мониторьте тренды**, а не только текущие значения
5. **Создайте Grafana дашборды** для визуализации метрик
6. **Настройте retention policy** для метрик в Prometheus
7. **Используйте SLO/SLI** для определения целей производительности

## 📚 Связанные документы

- [MONITORING.md](./MONITORING.md) - Общий мониторинг
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Deployment инструкции
- [README.md](../README.md) - Основная документация
