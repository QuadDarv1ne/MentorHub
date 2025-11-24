# 📚 MentorHub API Documentation

## Содержание

- [Аутентификация](#аутентификация)
- [Пользователи](#пользователи)
- [Менторы](#менторы)
- [Сессии](#сессии)
- [Курсы](#курсы)
- [Сообщения](#сообщения)
- [Платежи](#платежи)

---

## 🔐 Аутентификация

### Регистрация

**POST** `/api/v1/auth/register`

```json
// Request
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "Иван Иванов",
  "role": "student"
}

// Response 201
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "Иван Иванов",
  "role": "student",
  "created_at": "2025-11-24T12:00:00Z"
}
```

### Вход

**POST** `/api/v1/auth/login`

```json
// Request
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

// Response 200
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "Иван Иванов"
  }
}
```

### Обновление токена

**POST** `/api/v1/auth/refresh`

```http
Authorization: Bearer {refresh_token}
```

```json
// Response 200
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

---

## 👤 Пользователи

### Получить текущего пользователя

**GET** `/api/v1/users/me`

```http
Authorization: Bearer {access_token}
```

```json
// Response 200
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "Иван Иванов",
  "role": "student",
  "avatar_url": "https://...",
  "bio": "Изучаю Python",
  "created_at": "2025-11-24T12:00:00Z"
}
```

### Обновить профиль

**PUT** `/api/v1/users/me`

```json
// Request
{
  "full_name": "Иван Петрович Иванов",
  "bio": "Senior Python Developer",
  "phone": "+79150480249"
}

// Response 200
{
  "id": 1,
  "full_name": "Иван Петрович Иванов",
  "bio": "Senior Python Developer",
  "phone": "+79150480249"
}
```

---

## 🎓 Менторы

### Список менторов

**GET** `/api/v1/mentors?skill=python&min_price=1000&max_price=5000&page=1&limit=20`

```json
// Response 200
{
  "items": [
    {
      "id": 1,
      "user": {
        "full_name": "Петр Сидоров",
        "avatar_url": "https://..."
      },
      "title": "Senior Python Developer",
      "description": "10+ лет опыта...",
      "skills": ["Python", "Django", "FastAPI"],
      "price_per_hour": 3000,
      "rating": 4.8,
      "total_sessions": 120,
      "available": true
    }
  ],
  "total": 15,
  "page": 1,
  "pages": 1
}
```

### Детали ментора

**GET** `/api/v1/mentors/{mentor_id}`

```json
// Response 200
{
  "id": 1,
  "user": {
    "id": 2,
    "full_name": "Петр Сидоров",
    "email": "petr@example.com"
  },
  "title": "Senior Python Developer",
  "description": "Опытный разработчик...",
  "skills": ["Python", "Django", "FastAPI", "PostgreSQL"],
  "price_per_hour": 3000,
  "rating": 4.8,
  "total_sessions": 120,
  "reviews": [
    {
      "id": 1,
      "student_name": "Иван Иванов",
      "rating": 5,
      "comment": "Отличный ментор!",
      "created_at": "2025-11-20T10:00:00Z"
    }
  ]
}
```

### Стать ментором

**POST** `/api/v1/mentors/apply`

```json
// Request
{
  "title": "Senior Python Developer",
  "description": "10+ лет опыта в Python разработке",
  "skills": ["Python", "Django", "FastAPI"],
  "price_per_hour": 3000,
  "availability": {
    "monday": ["10:00-18:00"],
    "wednesday": ["14:00-20:00"]
  }
}

// Response 201
{
  "id": 1,
  "status": "pending",
  "message": "Заявка отправлена на модерацию"
}
```

---

## 📅 Сессии

### Забронировать сессию

**POST** `/api/v1/sessions`

```json
// Request
{
  "mentor_id": 1,
  "scheduled_at": "2025-11-25T15:00:00Z",
  "duration_minutes": 60,
  "topic": "Подготовка к собеседованию",
  "notes": "Нужна помощь с алгоритмами"
}

// Response 201
{
  "id": 1,
  "mentor": {
    "id": 1,
    "full_name": "Петр Сидоров"
  },
  "scheduled_at": "2025-11-25T15:00:00Z",
  "duration_minutes": 60,
  "status": "scheduled",
  "price": 3000,
  "payment_url": "https://payment.link/..."
}
```

### Мои сессии

**GET** `/api/v1/sessions?status=scheduled&page=1`

```json
// Response 200
{
  "items": [
    {
      "id": 1,
      "mentor": {
        "full_name": "Петр Сидоров",
        "avatar_url": "https://..."
      },
      "scheduled_at": "2025-11-25T15:00:00Z",
      "duration_minutes": 60,
      "status": "scheduled",
      "join_url": "https://mentorhub.ru/session/1/join"
    }
  ],
  "total": 5,
  "page": 1
}
```

### Завершить сессию

**POST** `/api/v1/sessions/{session_id}/complete`

```json
// Request
{
  "rating": 5,
  "review": "Отличная сессия!",
  "feedback": "Очень помогло с подготовкой"
}

// Response 200
{
  "id": 1,
  "status": "completed",
  "rating": 5,
  "completed_at": "2025-11-25T16:00:00Z"
}
```

---

## 📚 Курсы

### Список курсов

**GET** `/api/v1/courses?category=python&level=beginner`

```json
// Response 200
{
  "items": [
    {
      "id": 1,
      "title": "Python для начинающих",
      "description": "Базовый курс Python",
      "category": "programming",
      "level": "beginner",
      "duration_hours": 40,
      "price": 15000,
      "rating": 4.7,
      "students_count": 350
    }
  ],
  "total": 12
}
```

### Записаться на курс

**POST** `/api/v1/courses/{course_id}/enroll`

```json
// Response 201
{
  "enrollment_id": 1,
  "course": {
    "id": 1,
    "title": "Python для начинающих"
  },
  "enrolled_at": "2025-11-24T12:00:00Z",
  "progress": 0,
  "payment_url": "https://payment.link/..."
}
```

### Прогресс по курсу

**PUT** `/api/v1/courses/{course_id}/progress`

```json
// Request
{
  "completed_lessons": [1, 2, 3],
  "current_lesson": 4,
  "progress_percentage": 25
}

// Response 200
{
  "course_id": 1,
  "progress": 25,
  "completed_lessons": 3,
  "total_lessons": 12
}
```

---

## 💬 Сообщения

### Список чатов

**GET** `/api/v1/messages/chats`

```json
// Response 200
{
  "items": [
    {
      "id": 1,
      "participant": {
        "id": 2,
        "full_name": "Петр Сидоров",
        "avatar_url": "https://..."
      },
      "last_message": {
        "text": "Увидимся завтра!",
        "sent_at": "2025-11-24T18:00:00Z"
      },
      "unread_count": 2
    }
  ]
}
```

### Отправить сообщение

**POST** `/api/v1/messages`

```json
// Request
{
  "recipient_id": 2,
  "text": "Здравствуйте! Готов к завтрашней сессии"
}

// Response 201
{
  "id": 1,
  "sender_id": 1,
  "recipient_id": 2,
  "text": "Здравствуйте! Готов к завтрашней сессии",
  "sent_at": "2025-11-24T19:00:00Z",
  "read": false
}
```

---

## 💳 Платежи

### Создать платеж

**POST** `/api/v1/payments/create`

```json
// Request
{
  "session_id": 1,
  "amount": 3000,
  "payment_method": "card"
}

// Response 201
{
  "payment_id": "pm_123abc",
  "amount": 3000,
  "currency": "RUB",
  "status": "pending",
  "payment_url": "https://checkout.stripe.com/...",
  "expires_at": "2025-11-24T20:00:00Z"
}
```

### История платежей

**GET** `/api/v1/payments/history?page=1&limit=20`

```json
// Response 200
{
  "items": [
    {
      "id": "pm_123abc",
      "amount": 3000,
      "status": "succeeded",
      "description": "Сессия с Петр Сидоров",
      "created_at": "2025-11-24T12:00:00Z"
    }
  ],
  "total": 15
}
```

---

## 🔍 Коды ошибок

| Код | Описание |
|-----|----------|
| 400 | Bad Request - Неверные параметры запроса |
| 401 | Unauthorized - Требуется авторизация |
| 403 | Forbidden - Доступ запрещен |
| 404 | Not Found - Ресурс не найден |
| 422 | Unprocessable Entity - Ошибка валидации |
| 429 | Too Many Requests - Превышен лимит запросов |
| 500 | Internal Server Error - Внутренняя ошибка |

### Формат ошибки

```json
{
  "detail": "Detailed error message",
  "status_code": 400,
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

---

## 🚀 Rate Limiting

- **Анонимные запросы:** 100 запросов/час
- **Авторизованные пользователи:** 1000 запросов/час
- **Premium пользователи:** 5000 запросов/час

---

## 📡 WebSocket API

### Подключение к чату

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/chat?token=YOUR_TOKEN');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('New message:', message);
};

ws.send(JSON.stringify({
  type: 'message',
  recipient_id: 2,
  text: 'Hello!'
}));
```

---

## 🔗 Полезные ссылки

- **API Swagger:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health
- **GitHub:** https://github.com/QuadDarv1ne/MentorHub
