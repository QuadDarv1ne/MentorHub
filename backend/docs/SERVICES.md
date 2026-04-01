# Backend Services Documentation

**Версия:** 1.0  
**Дата:** 1 апреля 2026 г.  
**Статус:** Production Ready

---

## 📚 Обзор

MentorHub использует **Service Layer Pattern** для разделения бизнес-логики от API endpoints.

### Преимущества

- ✅ **Separation of Concerns** — бизнес-логика отделена от HTTP layer
- ✅ **Testability** — сервисы легко тестировать независимо
- ✅ **Reusability** — сервисы переиспользуются в разных endpoint'ах
- ✅ **Maintainability** — изменения в логике в одном месте

---

## 📁 Структура Сервисов

```
backend/app/services/
├── agora_service.py         # Видеозвонки (Agora)
├── calendar_service.py      # Календари (Google, Outlook)
├── chat_room_service.py     # Чат-комнаты
├── course_service.py        # Курсы и уроки
├── stripe_service.py        # Платежи (Stripe)
├── subscription_service.py  # Подписки
├── cache.py                 # Кэширование (Redis)
└── __init__.py
```

---

## 🔧 Сервисы

### 1. AgoraService

**Файл:** `agora_service.py` (80 строк)

**Назначение:** Генерация токенов для видеозвонков через Agora

**Методы:**
```python
agora_service.generate_token(channel, uid, role, expiration)
agora_service.get_app_id()
agora_service.is_available()
```

**Пример использования:**
```python
from app.services.agora_service import agora_service

token = agora_service.generate_token(
    channel="call_123",
    uid=1,
    role="publisher",
    expiration=3600
)
```

---

### 2. CourseService

**Файл:** `course_service.py` (187 строк)

**Назначение:** Управление курсами и уроками

**Методы:**
```python
service.create_course(user, course_data)
service.update_course(course_id, user, course_data)
service.create_lesson(course_id, user, lesson_data)
service.update_lesson(lesson_id, user, lesson_data)
service.get_user_enrollments(user_id)
service.get_similar_courses(course, limit)
service.check_mentor_access(user, instructor_id)
```

**Пример:**
```python
from app.services.course_service import CourseService

service = CourseService(db)
course = service.create_course(current_user, course_data)
```

---

### 3. ChatRoomService

**Файл:** `chat_room_service.py` (175 строк)

**Назначение:** Управление чат-комнатами и сообщениями

**Методы:**
```python
service.create_chat_room(user, room_data)
service.get_user_rooms(user_id, skip, limit)
service.get_room_by_id(room_id, user_id)
service.add_member(room_id, member_id)
service.remove_member(room_id, member_id)
service.send_message(room_id, user, message_data)
service.get_room_messages(room_id, user_id, skip, limit)
```

---

### 4. CalendarService

**Файл:** `calendar_service.py` (273 строки)

**Назначение:** Интеграция с Google Calendar и Outlook

**Компоненты:**
- `GoogleCalendarService` — Google OAuth
- `MicrosoftCalendarService` — Microsoft OAuth
- `CalendarService` — основная логика

**Методы:**
```python
service.get_sync_status(provider)
service.save_google_tokens(tokens, calendar_id)
service.save_microsoft_tokens(tokens, calendar_id)
service.disconnect_calendar(provider)
service.get_events(start_date, end_date)
service.sync_sessions_to_calendar()
service.sync_video_calls_to_calendar()
```

---

### 5. SubscriptionService

**Файл:** `subscription_service.py` (197 строк)

**Назначение:** Управление подписками пользователей

**Методы:**
```python
service.get_plans()
service.get_plan(tier)
service.get_user_subscription(user_id)
service.create_subscription(user, tier, stripe_subscription_id)
service.activate_subscription(subscription_id)
service.cancel_subscription(subscription_id, user_id)
service.reactivate_subscription(subscription_id, user_id)
service.expire_subscription(subscription_id)
service.upgrade_subscription(subscription_id, user_id, new_tier)
service.get_subscription_stats(user_id)
```

**Тарифные планы:**
- **Basic** — $9.99/мес, 14 дней trial
- **Pro** — $29.99/мес, 14 дня trial
- **Premium** — $99.99/мес, 7 дней trial

---

### 6. StripeService

**Файл:** `stripe_service.py` (существующий)

**Назначение:** Обработка платежей через Stripe

**Методы:**
```python
stripe_service.create_customer(email, name, metadata)
stripe_service.create_checkout_session(customer_id, price_id, ...)
stripe_service.refund_payment(payment_intent_id)
stripe_service.handle_webhook_event(event_data)
```

---

### 7. Cache Service

**Файл:** `cache.py` (существующий)

**Назначение:** Кэширование данных в Redis

**Декораторы:**
```python
@cached(ttl=300, key_prefix="users")
async def get_users():
    ...

@cache_response(ttl=600)
async def get_expensive_data():
    ...
```

**Функции:**
```python
await cache.get(key)
await cache.set(key, value, ttl)
await cache.delete(key)
await invalidate_cache(pattern)
```

---

## 📝 Использование в API

### Пример: Courses API

```python
from fastapi import APIRouter, Depends
from app.services.course_service import CourseService
from app.dependencies import get_db

router = APIRouter()

def _get_course_service(db = Depends(get_db)):
    return CourseService(db)

@router.get("/", response_model=List[CourseResponse])
async def get_courses(
    skip: int = 0,
    limit: int = 100,
    service: CourseService = Depends(_get_course_service)
):
    courses = db.query(Course).offset(skip).limit(limit).all()
    return courses

@router.post("/", response_model=CourseResponse)
async def create_course(
    course: CourseCreate,
    current_user: User = Depends(get_current_user),
    service: CourseService = Depends(_get_course_service)
):
    try:
        return service.create_course(current_user, course)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## 🧪 Тестирование Сервисов

### Unit Tests

```python
def test_course_service_create_course(db_session, test_user):
    service = CourseService(db_session)
    
    course_data = CourseCreate(
        title="Test Course",
        description="Test",
        category="Programming"
    )
    
    course = service.create_course(test_user, course_data)
    
    assert course.title == "Test Course"
    assert course.instructor_id == test_user.id
```

### Integration Tests

```python
def test_subscription_flow(client, test_user):
    # Get plans
    response = client.get("/api/v1/subscriptions/plans")
    assert response.status_code == 200
    
    # Create subscription
    response = client.post(
        "/api/v1/subscriptions/create",
        json={"tier": "pro"},
        headers=auth_headers
    )
    assert response.status_code == 200
```

---

## 🔐 Безопасность

### Проверка Прав Доступа

```python
# В сервисе
def check_mentor_access(self, user: User, course_instructor_id: int) -> bool:
    mentor = self.db.query(Mentor).filter(Mentor.user_id == user.id).first()
    return mentor is not None and mentor.id == course_instructor_id

# В API
@router.put("/{course_id}")
async def update_course(course_id: int, ...):
    if not service.check_mentor_access(current_user, course.instructor_id):
        raise HTTPException(status_code=403, detail="Access denied")
```

### Валидация Данных

```python
# Санитизация в сервисе
def _sanitize_course_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    sanitized = {}
    for key, value in data.items():
        if key in ["title", "description", "category"] and value is not None:
            sanitized_value = sanitize_text_field(value)
            if not is_safe_string(sanitized_value):
                raise ValueError(f"Invalid characters in {key}")
            sanitized[key] = sanitized_value
        else:
            sanitized[key] = value
    return sanitized
```

---

## 📈 Метрики Сервисов

| Сервис | Строк | Методов | Используется в API |
|--------|-------|---------|-------------------|
| AgoraService | 80 | 3 | video_calls.py |
| CourseService | 187 | 8 | courses.py |
| ChatRoomService | 175 | 9 | chat_rooms.py |
| CalendarService | 273 | 12 | calendar.py |
| SubscriptionService | 197 | 11 | subscriptions.py |
| StripeService | ~200 | 8 | payments.py, subscriptions.py |
| Cache | ~150 | 6 | Все API |

---

## 🚀 Расширение

### Создание Нового Сервиса

1. **Создать файл** `backend/app/services/new_service.py`

2. **Определить класс:**
```python
class NewService:
    def __init__(self, db: Session):
        self.db = db
    
    def do_something(self, user_id: int):
        # Бизнес-логика
        pass
```

3. **Использовать в API:**
```python
def _get_service(db = Depends(get_db)):
    return NewService(db)

@router.get("/something")
async def get_something(service: NewService = Depends(_get_service)):
    return service.do_something(current_user.id)
```

---

## 📞 Поддержка

**Документация:** [ARCHITECTURE.md](./ARCHITECTURE.md)  
**API Documentation:** [API.md](./API.md)  
**Tests:** `backend/tests/`

---

**MentorHub © 2026** — Open-source платформа для менторства
