# Analytics System

## Обзор

Система аналитики для MentorHub с метриками платформы, пользователей, курсов и revenue.

## Архитектура

```
┌─────────────┐
│   API       │
│  Endpoints  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Analytics  │
│   Service   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Database   │
│   Queries   │
└─────────────┘
```

## Возможности

### 1. Platform Analytics (Admin Only)

**Endpoint:** `GET /api/v1/analytics/platform`

**Метрики:**
- Пользователи (total, students, mentors, verified)
- Сессии (total, completed, scheduled, completion rate)
- Курсы (total, published, enrollments)
- Отзывы (total, average rating)
- Revenue (total)

**Response:**
```json
{
  "users": {
    "total": 1250,
    "students": 1000,
    "mentors": 200,
    "verified": 950,
    "verification_rate": 76.0
  },
  "sessions": {
    "total": 3500,
    "completed": 2800,
    "scheduled": 450,
    "completion_rate": 80.0
  },
  "courses": {
    "total": 120,
    "published": 100,
    "enrollments": 5400,
    "avg_enrollments_per_course": 45.0
  },
  "reviews": {
    "total": 2100,
    "average_rating": 4.65
  },
  "revenue": {
    "total": 2450000.0,
    "currency": "RUB"
  }
}
```

### 2. User Growth

**Endpoint:** `GET /api/v1/analytics/user-growth?days=30`

**Query Params:**
- `days` - период анализа (1-365)

**Response:**
```json
{
  "period_days": 30,
  "data": [
    {
      "date": "2025-11-05",
      "new_users": 12
    },
    {
      "date": "2025-11-06",
      "new_users": 18
    }
  ]
}
```

### 3. Session Analytics

**Endpoint:** `GET /api/v1/analytics/sessions?days=30`

**Response:**
```json
{
  "period_days": 30,
  "analytics": {
    "total": 450,
    "by_status": {
      "scheduled": 120,
      "completed": 280,
      "cancelled": 50
    },
    "avg_duration_minutes": 58.5,
    "top_mentors": [
      {
        "mentor_id": 5,
        "sessions": 45
      },
      {
        "mentor_id": 12,
        "sessions": 38
      }
    ]
  }
}
```

### 4. Course Performance

**Endpoint:** `GET /api/v1/analytics/courses?course_id=123`

**Response (single course):**
```json
{
  "course_id": 123,
  "course_title": "Python для начинающих",
  "enrollments": 345,
  "avg_progress": 67.8,
  "completed": 156,
  "completion_rate": 45.22,
  "avg_rating": 4.7
}
```

**Response (all courses):**
```json
{
  "courses": [
    {
      "course_id": 123,
      "course_title": "Python для начинающих",
      "enrollments": 345,
      "avg_progress": 67.8,
      "completed": 156,
      "completion_rate": 45.22,
      "avg_rating": 4.7
    }
  ]
}
```

### 5. Revenue Analytics

**Endpoint:** `GET /api/v1/analytics/revenue?days=30`

**Response:**
```json
{
  "period_days": 30,
  "analytics": {
    "total_revenue": 125000.0,
    "transaction_count": 234,
    "avg_transaction": 534.19,
    "daily_revenue": [
      {
        "date": "2025-11-05",
        "revenue": 4500.0
      },
      {
        "date": "2025-11-06",
        "revenue": 5200.0
      }
    ]
  }
}
```

### 6. User Engagement

**Endpoint:** `GET /api/v1/analytics/user/{user_id}/engagement`

**Response:**
```json
{
  "user_id": 123,
  "username": "john_doe",
  "sessions_attended": 15,
  "courses_enrolled": 4,
  "avg_progress": 72.5,
  "reviews_written": 8,
  "last_activity": "2025-12-04T10:30:00",
  "engagement_score": 78
}
```

**Engagement Score Algorithm:**
- Sessions: до 30 баллов (3 балла за сессию)
- Courses: до 25 баллов (5 баллов за курс)
- Progress: до 30 баллов (0.3 * avg_progress)
- Reviews: до 15 баллов (5 баллов за отзыв)
- **Total:** 0-100

**My Engagement:**
```bash
GET /api/v1/analytics/me/engagement
```

## Caching

Все analytics endpoints кэшируются:

| Endpoint | TTL | Invalidation |
|----------|-----|--------------|
| `/platform` | 5 min | Manual |
| `/user-growth` | 1 hour | Daily |
| `/sessions` | 10 min | On session update |
| `/courses` | 10 min | On course update |
| `/revenue` | 10 min | On payment |
| `/engagement` | 5 min | On user activity |

## Permissions

| Endpoint | Required Role |
|----------|---------------|
| Platform analytics | Admin |
| User growth | Admin |
| Session analytics | Admin |
| Course performance | Admin |
| Revenue analytics | Admin |
| User engagement | Self or Admin |
| My engagement | Authenticated |

## Frontend Integration

### React Example

```typescript
// hooks/useAnalytics.ts
import useSWR from 'swr';

export function usePlatformStats() {
  const { data, error } = useSWR(
    '/api/v1/analytics/platform',
    fetcher,
    { refreshInterval: 60000 } // Refresh every minute
  );

  return {
    stats: data,
    isLoading: !error && !data,
    isError: error
  };
}

export function useUserGrowth(days = 30) {
  const { data } = useSWR(
    `/api/v1/analytics/user-growth?days=${days}`,
    fetcher
  );

  return data;
}

export function useMyEngagement() {
  const { data } = useSWR(
    '/api/v1/analytics/me/engagement',
    fetcher
  );

  return data;
}
```

### Dashboard Component

```tsx
// components/AdminDashboard.tsx
import { usePlatformStats, useUserGrowth } from '@/hooks/useAnalytics';

export function AdminDashboard() {
  const { stats } = usePlatformStats();
  const growth = useUserGrowth(30);

  return (
    <div className="dashboard">
      <div className="stats-grid">
        <StatCard
          title="Total Users"
          value={stats?.users.total}
          change="+12%"
        />
        <StatCard
          title="Revenue"
          value={`${stats?.revenue.total} ₽`}
          change="+8%"
        />
      </div>

      <ChartComponent data={growth?.data} />
    </div>
  );
}
```

### User Profile Stats

```tsx
// components/UserStats.tsx
import { useMyEngagement } from '@/hooks/useAnalytics';

export function UserStats() {
  const engagement = useMyEngagement();

  return (
    <div className="user-stats">
      <h3>Your Engagement</h3>
      
      <ProgressCircle
        score={engagement?.engagement_score}
        label="Engagement Score"
      />

      <div className="metrics">
        <Metric label="Sessions" value={engagement?.sessions_attended} />
        <Metric label="Courses" value={engagement?.courses_enrolled} />
        <Metric label="Avg Progress" value={`${engagement?.avg_progress}%`} />
      </div>
    </div>
  );
}
```

## Testing

```bash
# Platform stats
curl http://localhost:8000/api/v1/analytics/platform \
  -H "Authorization: Bearer ADMIN_TOKEN"

# User growth (last 7 days)
curl http://localhost:8000/api/v1/analytics/user-growth?days=7 \
  -H "Authorization: Bearer ADMIN_TOKEN"

# My engagement
curl http://localhost:8000/api/v1/analytics/me/engagement \
  -H "Authorization: Bearer USER_TOKEN"
```

## Performance Optimization

### Database Indexes

```sql
-- Already created by migrations
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_sessions_created_at ON sessions(created_at);
CREATE INDEX idx_payments_created_at ON payments(created_at);
CREATE INDEX idx_course_enrollments_course_id ON course_enrollments(course_id);
CREATE INDEX idx_progress_user_id ON progress(user_id);
CREATE INDEX idx_progress_course_id ON progress(course_id);
```

### Query Optimization

Analytics service использует:
- Агрегатные функции (COUNT, AVG, SUM)
- GROUP BY для временных рядов
- Ленивую загрузку для больших датасетов
- Кэширование результатов

### Scaling

Для больших объемов данных:

1. **Materialized Views:**
```sql
CREATE MATERIALIZED VIEW daily_stats AS
SELECT 
  DATE(FROM_UNIXTIME(created_at)) as date,
  COUNT(*) as user_count,
  SUM(CASE WHEN is_verified THEN 1 ELSE 0 END) as verified_count
FROM users
GROUP BY DATE(FROM_UNIXTIME(created_at));
```

2. **Background Jobs:**
```python
# Celery task для pre-calculation
@celery_app.task
def calculate_daily_stats():
    # Calculate and cache stats
    stats = analytics.get_platform_stats()
    cache.set('platform_stats', stats, ttl=86400)
```

3. **Time-series Database:**
Для real-time метрик используйте InfluxDB или TimescaleDB.

## Monitoring

Метрики аналитики логируются:

```
✅ Analytics: Platform stats calculated in 45ms
✅ Analytics: User growth (30 days) calculated in 123ms
✅ Analytics: Cache hit for platform_stats
```

## FAQ

**Q: Почему некоторые метрики показывают 0?**

A: Убедитесь что:
1. База данных заполнена тестовыми данными
2. Пользователь имеет права доступа
3. Период `days` покрывает существующие записи

**Q: Как часто обновляются метрики?**

A: Метрики кэшируются на 5-60 минут в зависимости от endpoint. Real-time метрики требуют WebSocket или SSE.

**Q: Можно ли экспортировать данные?**

A: Да, добавьте `?format=csv` или `?format=xlsx` для экспорта (требует дополнительной реализации).

**Q: Production ready?**

A: Да, но для production рекомендуется:
1. Materialized views для больших датасетов
2. Separate analytics database (read replica)
3. Background jobs для pre-calculation
4. Time-series DB для real-time metrics
