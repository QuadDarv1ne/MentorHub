# Grafana Configuration for MentorHub Monitoring

## Datasource Configuration

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      timeInterval: "15s"
      queryTimeout: "60s"
      httpMethod: "POST"

  - name: PostgreSQL
    type: postgres
    access: proxy
    url: postgres:5432
    database: mentorhub
    user: mentorhub_user
    secureJsonData:
      password: ${POSTGRES_PASSWORD}
    jsonData:
      sslmode: "disable"
      maxOpenConns: 10
      maxIdleConns: 5
      connMaxLifetime: 1800
      postgresVersion: 1600
      timescaledb: false
```

---

## Dashboard: Application Overview

```json
{
  "dashboard": {
    "title": "MentorHub - Application Overview",
    "tags": ["mentorhub", "overview"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Response Time (p50, p95, p99)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p50"
          },
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p95"
          },
          {
            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "p99"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          },
          {
            "expr": "rate(http_requests_total{status=~\"4..\"}[5m])",
            "legendFormat": "4xx errors"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Active Users",
        "type": "stat",
        "targets": [
          {
            "expr": "count(rate(user_login_total[1h]) > 0)",
            "legendFormat": "Active users"
          }
        ],
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 8}
      },
      {
        "id": 5,
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "db_pool_connections",
            "legendFormat": "Connections"
          },
          {
            "expr": "db_pool_size",
            "legendFormat": "Pool size"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16}
      },
      {
        "id": 6,
        "title": "Cache Hit Rate",
        "type": "gauge",
        "targets": [
          {
            "expr": "rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m])) * 100",
            "legendFormat": "Hit rate %"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 16}
      }
    ],
    "time": {"from": "now-1h", "to": "now"},
    "refresh": "30s"
  }
}
```

---

## Dashboard: Database Performance

```json
{
  "dashboard": {
    "title": "MentorHub - Database Performance",
    "tags": ["mentorhub", "database", "postgresql"],
    "panels": [
      {
        "id": 1,
        "title": "Query Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(pg_stat_activity_count[5m])",
            "legendFormat": "{{datname}} - {{state}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Connections by State",
        "type": "piechart",
        "targets": [
          {
            "expr": "sum by (state) (pg_stat_activity_count)",
            "legendFormat": "{{state}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "Transaction Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(pg_stat_database_xact_commit[5m])",
            "legendFormat": "Commits"
          },
          {
            "expr": "rate(pg_stat_database_xact_rollback[5m])",
            "legendFormat": "Rollbacks"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "Table Scan Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(pg_stat_user_tables_seq_scan[5m])",
            "legendFormat": "{{relname}} - seq scan"
          },
          {
            "expr": "rate(pg_stat_user_tables_idx_scan[5m])",
            "legendFormat": "{{relname}} - idx scan"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
      },
      {
        "id": 5,
        "title": "Locks",
        "type": "graph",
        "targets": [
          {
            "expr": "sum by (mode) (pg_locks_count)",
            "legendFormat": "{{mode}}"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16}
      },
      {
        "id": 6,
        "title": "Database Size",
        "type": "stat",
        "targets": [
          {
            "expr": "pg_database_size_bytes{datname=\"mentorhub\"}",
            "legendFormat": "Size"
          }
        ],
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 16}
      }
    ],
    "time": {"from": "now-6h", "to": "now"},
    "refresh": "30s"
  }
}
```

---

## Dashboard: Business Metrics

```json
{
  "dashboard": {
    "title": "MentorHub - Business Metrics",
    "tags": ["mentorhub", "business"],
    "panels": [
      {
        "id": 1,
        "title": "New Users (24h)",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(increase(user_registration_total[24h]))",
            "legendFormat": "New users"
          }
        ],
        "gridPos": {"h": 4, "w": 6, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Active Sessions (24h)",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(increase(session_created_total[24h]))",
            "legendFormat": "Sessions"
          }
        ],
        "gridPos": {"h": 4, "w": 6, "x": 6, "y": 0}
      },
      {
        "id": 3,
        "title": "Course Enrollments (24h)",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(increase(course_enrollment_total[24h]))",
            "legendFormat": "Enrollments"
          }
        ],
        "gridPos": {"h": 4, "w": 6, "x": 12, "y": 0}
      },
      {
        "id": 4,
        "title": "Revenue (24h)",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(increase(payment_success_total[24h]))",
            "legendFormat": "Revenue $"
          }
        ],
        "gridPos": {"h": 4, "w": 6, "x": 18, "y": 0}
      },
      {
        "id": 5,
        "title": "User Registrations (7d)",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(increase(user_registration_total[1d]))",
            "legendFormat": "Daily registrations"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 4}
      },
      {
        "id": 6,
        "title": "Session Bookings (7d)",
        "type": "graph",
        "targets": [
          {
            "expr": "sum(increase(session_created_total[1d]))",
            "legendFormat": "Daily sessions"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 4}
      }
    ],
    "time": {"from": "now-7d", "to": "now"},
    "refresh": "5m"
  }
}
```

---

## Alert Rules

```yaml
groups:
  - name: mentorhub_alerts
    interval: 30s
    rules:
      # ==================== AVAILABILITY ====================
      - alert: ServiceDown
        expr: up{job="mentorhub-backend"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "MentorHub backend is down"
          description: "Backend service {{ $labels.instance }} has been down for more than 1 minute"

      - alert: HighErrorRate
        expr: sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} (threshold: 5%)"

      - alert: DatabaseDown
        expr: pg_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL database is down"
          description: "Database {{ $labels.job }} is not responding"

      # ==================== PERFORMANCE ====================
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value | humanizeDuration }} (threshold: 1s)"

      - alert: SlowDatabaseQueries
        expr: rate(pg_stat_activity_count{state=\"active\"}[5m]) > 50
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High number of active database queries"
          description: "{{ $value }} active queries detected"

      - alert: DatabaseConnectionPoolExhausted
        expr: db_pool_connections / db_pool_size > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "Connection pool usage is {{ $value | humanizePercentage }}"

      # ==================== RESOURCES ====================
      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes / 1024 / 1024 > 1500
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is {{ $value | humanize }} MB (threshold: 1500 MB)"

      - alert: HighCPUUsage
        expr: rate(process_cpu_seconds_total[5m]) * 100 > 80
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is {{ $value | humanizePercentage }}"

      # ==================== BUSINESS ====================
      - alert: LowUserRegistrations
        expr: sum(increase(user_registration_total[1h])) < 5
        for: 1h
        labels:
          severity: info
        annotations:
          summary: "Low user registration rate"
          description: "Only {{ $value }} new users in the last hour"

      - alert: PaymentFailures
        expr: sum(increase(payment_failed_total[1h])) > 10
        for: 1h
        labels:
          severity: critical
        annotations:
          summary: "High payment failure rate"
          description: "{{ $value }} payment failures in the last hour"

      # ==================== CACHE ====================
      - alert: LowCacheHitRate
        expr: rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m])) * 100 < 50
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low cache hit rate"
          description: "Cache hit rate is {{ $value | humanizePercentage }} (threshold: 50%)"

      # ==================== QUEUE ====================
      - alert: CeleryQueueBacklog
        expr: celery_queue_length > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Celery queue backlog detected"
          description: "Queue length is {{ $value }} tasks"

      - alert: CeleryTaskFailures
        expr: rate(celery_task_failed_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High Celery task failure rate"
          description: "{{ $value | humanize }} task failures per second"
```

---

## Notification Channels

```yaml
apiVersion: 1

notificationChannels:
  - name: Telegram
    type: telegram
    uid: telegram_channel
    is_default: false
    send_reminder: true
    frequency: 1h
    settings:
      bot_token: ${TELEGRAM_BOT_TOKEN}
      chat_id: ${TELEGRAM_CHAT_ID}

  - name: Email
    type: email
    uid: email_channel
    is_default: true
    settings:
      addresses: admin@mentorhub.com
      single_email: true

  - name: Slack
    type: slack
    uid: slack_channel
    is_default: false
    settings:
      url: ${SLACK_WEBHOOK_URL}
      channel: "#alerts"
      username: Grafana Alerts
```

---

## Setup Instructions

### 1. Install Prometheus Exporter

```bash
# Backend metrics
pip install prometheus-client

# PostgreSQL exporter
docker run -d \
  --name postgres_exporter \
  -p 9187:9187 \
  -e DATA_SOURCE_NAME="postgresql://mentorhub_user:password@postgres:5432/mentorhub?sslmode=disable" \
  prometheuscommunity/postgres-exporter
```

### 2. Configure Prometheus

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'mentorhub-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres_exporter:9187']
```

### 3. Import Dashboards

```bash
# Import via Grafana API
curl -X POST \
  -H "Content-Type: application/json" \
  -d @dashboard-overview.json \
  http://grafana:3000/api/dashboards/db \
  -u admin:admin

# Or manually via Grafana UI:
# Dashboard → Import → Upload JSON file
```

### 4. Configure Alerts

```bash
# Add alert rules to Prometheus
kubectl apply -f alert-rules.yaml

# Or copy to Prometheus config directory
cp alert-rules.yaml /etc/prometheus/rules/
```

---

**Last Updated:** 2026-03-10
**Version:** 1.0.0
