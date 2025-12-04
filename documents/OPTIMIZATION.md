# 🚀 Оптимизация и производительность MentorHub

Документация по оптимизации производительности приложения MentorHub.

## 📋 Содержание

1. [Общие рекомендации](#общие-рекомендации)
2. [Backend оптимизация](#backend-оптимизация)
3. [Frontend оптимизация](#frontend-оптимизация)
4. [Database оптимизация](#database-оптимизация)
5. [Кеширование](#кеширование)
6. [Мониторинг](#мониторинг)

---

## 🎯 Общие рекомендации

### Производительность

- **Response time**: < 200ms для 95% запросов
- **Database queries**: Максимум 3-5 запросов на API endpoint
- **Cache hit rate**: > 80% для часто используемых данных
- **CPU utilization**: < 70% в нормальных условиях
- **Memory**: < 80% от выделенного

### Targets

```
API Response Time Distribution:
- 50th percentile: < 50ms
- 95th percentile: < 200ms
- 99th percentile: < 500ms

Error Rate: < 0.1%
```

---

## ⚙️ Backend оптимизация

### 1. Кеширование API endpoints

Использование Redis для кеширования часто используемых данных:

```python
from app.utils.cache import cached, CACHE_TTL

@router.get("/mentors/{mentor_id}")
@cached(ttl=CACHE_TTL['mentor'], key_prefix="mentor_detail")
async def get_mentor(mentor_id: int, db: Session = Depends(get_db)):
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not mentor:
        raise HTTPException(404, "Mentor not found")
    return mentor
```

**Кеш TTL по умолчанию:**
- user: 600 сек (10 мин)
- mentor: 900 сек (15 мин)
- course: 1800 сек (30 мин)
- review: 300 сек (5 мин)
- stats: 60 сек (1 мин)

### 2. Database optimization

#### N+1 Query Prevention

```python
# ❌ Плохо - N+1 проблема
mentors = db.query(Mentor).all()
for mentor in mentors:
    user = mentor.user  # Отдельный запрос для каждого ментора

# ✅ Хорошо - используем joinedload
from sqlalchemy.orm import joinedload

mentors = db.query(Mentor).options(
    joinedload(Mentor.user)
).all()
```

#### Index Usage

```python
# Создание индексов для часто используемых полей
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_mentor_user_id ON mentors(user_id);
CREATE INDEX idx_session_status ON sessions(status);
CREATE INDEX idx_payment_user_id ON payments(user_id);
```

### 3. Query optimization

```python
# ❌ Плохо - SELECT *
query = "SELECT * FROM users WHERE email = %s"

# ✅ Хорошо - выбираем только нужные поля
query = "SELECT id, email, username FROM users WHERE email = %s"

# ✅ Используем пагинацию
mentors = db.query(Mentor).offset(0).limit(20).all()

# ✅ Используем фильтры на уровне БД
active_users = db.query(User).filter(User.is_active == True).all()
```

### 4. Connection pooling

```python
# В config.py уже оптимизировано:
DB_POOL_SIZE: int = 20
DB_MAX_OVERFLOW: int = 40
```

Это означает:
- 20 постоянных соединений с БД
- До 40 дополнительных соединений при пиковой нагрузке
- Всего максимум 60 соединений

### 5. Rate limiting

```python
from app.middleware.rate_limiter import rate_limit_dependency

@router.get("/api/endpoint")
async def my_endpoint(rate_limit: bool = Depends(rate_limit_dependency)):
    # Защита от DDoS и abuse
    return {"status": "ok"}
```

Параметры (в config.py):
- Requests per minute: 100
- Block duration: 3600 sec (1 hour)

---

## 🎨 Frontend оптимизация

### 1. Code splitting и lazy loading

```tsx
import dynamic from 'next/dynamic'

// Динамический импорт компонента
const HeavyComponent = dynamic(() => import('@/components/Heavy'), {
  loading: () => <div>Loading...</div>,
  ssr: false
})

export default function Page() {
  return <HeavyComponent />
}
```

### 2. Image optimization

```tsx
import Image from 'next/image'

// ✅ Правильно - используем Next.js Image component
<Image
  src="/course-image.jpg"
  alt="Course"
  width={300}
  height={200}
  priority={false}
  loading="lazy"
/>

// ❌ Неправильно - обычный img tag
<img src="/course-image.jpg" alt="Course" />
```

### 3. Component memoization

```tsx
import { memo } from 'react'

// Мемоизация компонента для предотвращения ненужных re-renders
const MentorCard = memo(({ mentor }) => {
  return (
    <div className="card">
      <h3>{mentor.name}</h3>
      <p>{mentor.bio}</p>
    </div>
  )
})

export default MentorCard
```

### 4. Debounce for expensive operations

```tsx
import { useCallback } from 'react'
import { debounce } from '@/lib/utils/performance'

export default function SearchMentors() {
  const handleSearch = useCallback(
    debounce((query: string) => {
      // API запрос только после 300ms без ввода
      api.search(query)
    }, 300),
    []
  )

  return (
    <input
      placeholder="Search mentors..."
      onChange={(e) => handleSearch(e.target.value)}
    />
  )
}
```

### 5. Virtual scrolling для больших списков

```tsx
import { FixedSizeList } from 'react-window'

export default function MentorsList({ mentors }) {
  return (
    <FixedSizeList
      height={600}
      itemCount={mentors.length}
      itemSize={80}
    >
      {({ index, style }) => (
        <div style={style}>
          <MentorCard mentor={mentors[index]} />
        </div>
      )}
    </FixedSizeList>
  )
}
```

---

## 🗄️ Database оптимизация

### Индексы

```sql
-- Для быстрого поиска по email
CREATE INDEX idx_user_email ON users(email);

-- Для фильтрации по статусу
CREATE INDEX idx_session_status ON sessions(status);

-- Композитный индекс
CREATE INDEX idx_user_active_email ON users(is_active, email);

-- Для сортировки
CREATE INDEX idx_session_created_at ON sessions(created_at DESC);
```

### EXPLAIN PLAN

```sql
-- Анализ производительности запроса
EXPLAIN ANALYZE
SELECT u.id, u.email, m.specialization
FROM users u
JOIN mentors m ON u.id = m.user_id
WHERE u.is_active = true
ORDER BY m.rating DESC;
```

### Connection pooling monitoring

```python
# В мониторинг API
from app.utils.monitoring import get_pool_metrics

pool_metrics = {
    "pool_size": 20,
    "max_overflow": 40,
    "connected": 18,
    "available": 12,
    "overflow": 2
}
```

---

## 💾 Кеширование

### Redis vs Memory cache

```python
# Redis используется для:
# - Session data
# - User data
# - API responses
# - Real-time updates

# Memory cache используется для:
# - Конфигурация приложения
# - Статические данные
# - Временные данные
```

### Cache invalidation

```python
from app.utils.cache import invalidate_cache

# При обновлении ментора - инвалидируем кеш
async def update_mentor(mentor_id: int, data: dict):
    # ... обновляем в БД ...
    await invalidate_cache(f"mentor:{mentor_id}")
    return updated_mentor
```

### Cache statistics

```python
from app.utils.cache import cache_manager

stats = cache_manager.get_stats()
print(stats)
# {
#     "hits": 15234,
#     "misses": 3456,
#     "hit_rate": "81.5%"
# }
```

---

## 📊 Мониторинг

### Prometheus метрики

```python
from app.utils.prometheus import (
    REQUEST_DURATION,
    ERROR_COUNT,
    CACHE_HITS,
    DATABASE_QUERY_DURATION
)

# Отслеживание медленных запросов
slow_requests = db.query(Request).filter(
    Request.duration > 1.0  # > 1 second
).all()

# Отслеживание ошибок
error_rate = ERROR_COUNT / REQUEST_COUNT

# Отслеживание попаданий в кеш
cache_hit_rate = CACHE_HITS / (CACHE_HITS + CACHE_MISSES)
```

### Health checks

```
GET /health - базовый health check
GET /health/deep - глубокая проверка (БД, Redis, etc)
GET /metrics - Prometheus метрики
```

---

## 🔍 Профилирование и анализ

### Backend profiling

```bash
# Установка профайлера
pip install py-spy

# Профилирование приложения
py-spy record -o profile.svg -- python -m uvicorn app.main:app
```

### Frontend performance

```javascript
// Использование Performance API
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.log(`${entry.name}: ${entry.duration}ms`);
  }
});

observer.observe({ entryTypes: ["measure", "navigation"] });
```

---

## ✅ Performance Checklist

- [ ] Все часто используемые данные кешированы
- [ ] N+1 queries устранены
- [ ] Индексы созданы для часто используемых полей
- [ ] Компоненты мемоизированы
- [ ] Изображения оптимизированы
- [ ] Code splitting реализован
- [ ] Rate limiting включен
- [ ] Мониторинг настроен
- [ ] Cache hit rate > 80%
- [ ] Response time < 200ms для 95% запросов

---

## 📚 Дополнительные ресурсы

- [Django Performance Guide](https://docs.djangoproject.com/en/stable/topics/db/optimization/)
- [Next.js Performance](https://nextjs.org/learn/foundations/how-nextjs-works)
- [PostgreSQL Optimization](https://www.postgresql.org/docs/current/queries.html)
- [Redis Best Practices](https://redis.io/docs/manual/client-side-caching/)
