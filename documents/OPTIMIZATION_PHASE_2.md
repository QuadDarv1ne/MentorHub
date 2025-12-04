# 🔧 Внедрение оптимизаций Performance - Версия 2

Документация по новым оптимизациям, добавленным во второй итерации улучшения проекта.

## 📋 Содержание

1. [N+1 Query Prevention](#n1-query-prevention)
2. [Database Profiling](#database-profiling)
3. [Image Optimization](#image-optimization)
4. [Performance Metrics](#performance-metrics)

---

## 🔍 N+1 Query Prevention

### Проблема

```python
# ❌ Плохо - N+1 проблема
mentors = db.query(Mentor).all()  # 1 запрос
for mentor in mentors:
    user = mentor.user  # N запросов (по одному для каждого ментора!)
```

### Решение: joinedload

```python
from sqlalchemy.orm import joinedload

# ✅ Хорошо - все данные загружаются в одном запросе
mentors = db.query(Mentor).options(joinedload(Mentor.user)).all()
```

### Реализованные оптимизации

**backend/app/api/mentors.py:**
```python
@router.get("/", response_model=List[MentorResponse])
@cached(ttl=CACHE_TTL['mentor'], key_prefix="mentors_list")
async def get_mentors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), ...):
    # joinedload предотвращает N+1 запросы
    mentors = db.query(Mentor).options(joinedload(Mentor.user)).offset(skip).limit(limit).all()
    return mentors
```

**backend/app/api/courses.py:**
```python
@router.get("/{course_id}", response_model=CourseWithLessonsResponse)
@cached(ttl=CACHE_TTL['course'], key_prefix="course_detail")
async def get_course(course_id: int, db: Session = Depends(get_db), ...):
    # Загружаем instructor и lessons вместе с курсом
    course = db.query(Course).options(
        joinedload(Course.instructor),
        joinedload(Course.lessons)
    ).filter(Course.id == course_id).first()
```

### Ожидаемое улучшение

- **50-100+ запросов → 1-2 запроса**
- **Database query time: -95%**
- **API Response time: -80-90%**

---

## 📊 Database Profiling

### QueryProfiler Утилита

Отслеживание и анализ всех SQL запросов:

```python
from app.utils.profiling import query_profiler, ProfileContext, explain_query

# Использование контекста профилирования
with ProfileContext("Get mentors with users") as profile:
    mentors = db.query(Mentor).options(joinedload(Mentor.user)).all()
# Автоматически выведет статистику по запросам
```

### Обнаружение N+1 Проблем

```python
from app.utils.profiling import find_n_plus_one_queries

#找出повторяющиеся запросы
n_plus_one = find_n_plus_one_queries(db, threshold=10)
if n_plus_one:
    print("N+1 запросы обнаружены:")
    for query, count in n_plus_one.items():
        print(f"  {count}x - {query[:100]}")
```

### EXPLAIN ANALYZE

```python
from app.utils.profiling import explain_query

# Анализ плана выполнения запроса
result = explain_query(db, "SELECT * FROM users WHERE email = 'test@example.com'")
print(result)
# Выведет план выполнения из PostgreSQL
```

### Логирование Медленных Запросов

```python
from app.database import engine
from app.utils.profiling import setup_query_logging

# Включить логирование всех запросов > 100ms
setup_query_logging(engine)
```

### API Endpoints для Профилирования

```python
# В main.py можно добавить endpoint для профилирования в dev режиме
@app.get("/debug/profiling")
async def get_profiling_stats():
    """Получить статистику по запросам (только dev)"""
    return query_profiler.get_summary()
```

---

## 🖼️ Image Optimization

### OptimizedImage Компонент

```tsx
import { OptimizedImage } from '@/lib/utils/imageOptimization'

// Базовое использование
<OptimizedImage
  src="/course-image.jpg"
  alt="Course"
  width={400}
  height={300}
  priority={false}
/>

// С blur placeholder
<OptimizedImage
  src="/course-image.jpg"
  alt="Course"
  width={400}
  height={300}
  placeholder="blur"
  blurDataURL={blurImageUrl}
/>

// С responsive sizes
<OptimizedImage
  src="/course-image.jpg"
  alt="Course"
  width={400}
  height={300}
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 400px"
/>
```

### LazyImageGallery

```tsx
import { LazyImageGallery } from '@/lib/utils/imageOptimization'

const images = [
  { src: '/img1.jpg', alt: 'Image 1', width: 300, height: 300 },
  { src: '/img2.jpg', alt: 'Image 2', width: 300, height: 300 },
  { src: '/img3.jpg', alt: 'Image 3', width: 300, height: 300 },
]

<LazyImageGallery
  images={images}
  columns={3}
  gap={4}
/>
// Первые 3 изображения загружаются с приоритетом, остальные - lazy loading
```

### ResponsiveImage

```tsx
import { ResponsiveImage } from '@/lib/utils/imageOptimization'

<ResponsiveImage
  mobileSrc="/hero-mobile.jpg"
  tabletSrc="/hero-tablet.jpg"
  desktopSrc="/hero-desktop.jpg"
  alt="Hero"
/>
```

### useImagePreloader

```tsx
import { useImagePreloader } from '@/lib/utils/imageOptimization'

export default function CoursePage() {
  const { preloadImages } = useImagePreloader()

  useEffect(() => {
    // Предзагрузить изображения перед отображением
    preloadImages([
      '/course1.jpg',
      '/course2.jpg',
      '/course3.jpg',
    ])
  }, [])
}
```

### IMAGE_OPTIMIZATION Constants

```tsx
import { IMAGE_OPTIMIZATION } from '@/lib/utils/imageOptimization'

// Использование predefined sizes
console.log(IMAGE_OPTIMIZATION.SIZES.mobile)    // 360
console.log(IMAGE_OPTIMIZATION.SIZES.tablet)    // 768
console.log(IMAGE_OPTIMIZATION.SIZES.desktop)   // 1200

// Использование aspect ratios
console.log(IMAGE_OPTIMIZATION.ASPECT_RATIOS.card)    // '4/3'
console.log(IMAGE_OPTIMIZATION.ASPECT_RATIOS.hero)    // '2/1'

// Использование quality settings
console.log(IMAGE_OPTIMIZATION.QUALITY.thumbnail)  // 60
console.log(IMAGE_OPTIMIZATION.QUALITY.hero)       // 85
```

### Оптимизация Best Practices

```tsx
// ❌ Плохо - полный размер, высокое качество
<img src="/course.jpg" alt="Course" />

// ✅ Хорошо
<OptimizedImage
  src="/course.jpg"
  alt="Course"
  width={400}
  height={300}
  priority={false}
  sizes="(max-width: 640px) 100vw, 400px"
  placeholder="blur"
/>
```

---

## 📈 Performance Metrics

### Ожидаемые Улучшения

| Метрика | До | После | Улучшение |
|---------|-----|--------|------------|
| API Response Time | 500-1000ms | 50-100ms | **-80-90%** |
| Database Query Count | 50-100+ | 2-5 | **-95%** |
| Image Load Time | 2-5s | 0.5-1s | **-80%** |
| Initial Page Load | 3-5s | 1-2s | **-60%** |
| First Contentful Paint | 2-3s | 0.5-1s | **-75%** |

### Мониторинг

Используйте Prometheus метрики для отслеживания:

```python
from app.utils.prometheus import REQUEST_DURATION, ERROR_COUNT

# Автоматически отслеживается через middleware
# Смотрите /metrics endpoint
```

### Performance Checklist

- [x] N+1 queries устранены (joinedload)
- [x] Database индексы добавлены (12 индексов)
- [x] API кеширование реализовано (Redis)
- [x] Frontend lazy loading включен
- [x] Image optimization добавлена
- [x] Database profiling утилита создана
- [ ] Load testing (JMeter/K6)
- [ ] Frontend performance audit (Lighthouse)
- [ ] Database query analysis (EXPLAIN ANALYZE)
- [ ] Backend profiling (cProfile, py-spy)

---

## 🚀 Развертывание

### 1. Backend

```bash
# Применить миграции с индексами
alembic upgrade head

# Включить query logging в production (если нужно)
# в app/main.py добавить:
from app.utils.profiling import setup_query_logging
from app.database import engine
setup_query_logging(engine)
```

### 2. Frontend

```bash
# Убедиться что Next.js Image Optimization включен
# В next.config.js проверить:
// images: {
//   unoptimized: false,
//   domains: ['your-api-domain.com'],
// }

npm run build
npm start
```

### 3. Мониторинг

```bash
# Проверить метрики Prometheus
curl http://localhost:8000/metrics

# Смотрете slow queries в логах
tail -f logs/app.log | grep "Slow query"
```

---

## 📚 Дополнительные Ресурсы

- [SQLAlchemy Relationship Loading](https://docs.sqlalchemy.org/en/20/orm/loading_relationships.html)
- [Next.js Image Optimization](https://nextjs.org/docs/basic-features/image-optimization)
- [PostgreSQL EXPLAIN](https://www.postgresql.org/docs/current/sql-explain.html)
- [Web Performance APIs](https://developer.mozilla.org/en-US/docs/Web/API/Performance)
