# MentorHub Architecture Documentation

**Версия:** 2.0  
**Дата обновления:** 1 апреля 2026 г.  
**Статус:** Production Ready

---

## 📐 Обзор Архитектуры

MentorHub — это современная платформа для менторства, построенная на основе **микросервисной архитектуры** с элементами **сервисного слоя** (Service Layer Pattern).

### Ключевые Принципы

1. **Separation of Concerns** — разделение ответственности между слоями
2. **Dependency Injection** — внедрение зависимостей через FastAPI Depends
3. **Service Layer Pattern** — бизнес-логика вынесена в сервисы
4. **Repository Pattern** — доступ к данным через SQLAlchemy ORM
5. **CQRS Lite** — разделение команд (POST/PUT/DELETE) и запросов (GET)

---

## 🏗️ Архитектурные Слои

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │  Pages   │  │Components│  │  Hooks   │  │  Utils  │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────┘
                          ↕ HTTP/WebSocket
┌─────────────────────────────────────────────────────────┐
│                  Backend (FastAPI)                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │              API Layer (Routers)                  │   │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐  │   │
│  │  │  auth  │ │ courses│ │sessions│ │ payments │  │   │
│  │  └────────┘ └────────┘ └────────┘ └──────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
│                          ↕                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │            Service Layer (Business Logic)         │   │
│  │  ┌────────────┐ ┌──────────┐ ┌────────────────┐  │   │
│  │  │AuthServices│ │CourseSvc │ │CalendarService │  │   │
│  │  └────────────┘ └──────────┘ └────────────────┘  │   │
│  └──────────────────────────────────────────────────┘   │
│                          ↕                               │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Data Access Layer (SQLAlchemy ORM)        │   │
│  │  ┌────────┐ ┌─────────┐ ┌──────────┐ ┌────────┐ │   │
│  │  │ Models │ │Schemas  │ │Repositories│ │ Cache │ │   │
│  │  └────────┘ └─────────┘ └──────────┘ └────────┘ │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │PostgreSQL│  │  Redis   │  │  Celery  │  │  Agora  │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Структура Проекта

### Backend Структура

```
backend/
├── app/
│   ├── api/                    # API Layer (Router endpoints)
│   │   ├── auth.py            # → auth_core.py + auth_oauth.py
│   │   ├── auth_core.py       # Регистрация, логин, refresh
│   │   ├── auth_oauth.py      # OAuth Google/GitHub
│   │   ├── courses.py         # CRUD курсов
│   │   ├── sessions.py        # Бронирование сессий
│   │   ├── payments.py        # Платежи и подписки
│   │   ├── video_calls.py     # Видеозвонки (Agora)
│   │   ├── chat_rooms.py      # Групповые чаты
│   │   ├── calendar.py        # Интеграция календарей
│   │   └── ...
│   │
│   ├── services/              # Service Layer (Бизнес-логика)
│   │   ├── auth_service.py    # Логика аутентификации
│   │   ├── course_service.py  # Логика курсов
│   │   ├── chat_room_service.py # Логика чатов
│   │   ├── calendar_service.py # OAuth и календари
│   │   ├── agora_service.py   # Agora токены
│   │   ├── cache.py           # Кэширование (Redis)
│   │   └── stripe_service.py  # Платежи Stripe
│   │
│   ├── models/                # Data Layer (SQLAlchemy ORM)
│   │   ├── user.py            # Модель пользователя
│   │   ├── course.py          # Модели курсов
│   │   ├── session.py         # Модели сессий
│   │   ├── payment.py         # Модели платежей
│   │   └── ...
│   │
│   ├── schemas/               # Pydantic схемы (DTO)
│   │   ├── user.py            # Схемы пользователя
│   │   ├── course.py          # Схемы курсов
│   │   └── ...
│   │
│   ├── utils/                 # Утилиты
│   │   ├── security.py        # Хеширование, JWT
│   │   ├── auth_tokens.py     # Создание/валидация токенов
│   │   ├── sanitization.py    # Санитизация данных
│   │   └── logger.py          # Логирование
│   │
│   ├── middleware/            # Middleware
│   │   ├── rate_limiter.py    # Rate limiting
│   │   ├── security.py        # Security headers
│   │   └── request_logging.py # Логирование запросов
│   │
│   ├── tasks/                 # Background tasks (Celery)
│   │   ├── celery_tasks.py    # Email, уведомления
│   │   └── celery_config.py   # Конфигурация Celery
│   │
│   └── config.py              # Конфигурация приложения
│
├── tests/                     # Тесты
│   ├── test_auth.py           # Тесты аутентификации
│   ├── test_courses.py        # Тесты курсов
│   ├── test_integration.py    # Integration тесты
│   └── ...
│
└── alembic/                   # Миграции БД
```

### Frontend Структура

```
frontend/
├── app/                       # Next.js App Router
│   ├── (auth)/                # Auth страницы
│   ├── (dashboard)/           # Dashboard страницы
│   ├── api/                   # API Routes
│   └── ...
│
├── components/                # React компоненты
│   ├── ui/                    # UI компоненты (Button, Card)
│   ├── auth/                  # Auth компоненты
│   ├── courses/               # Course компоненты
│   └── ...
│
├── hooks/                     # Custom React hooks
│   ├── useAuth.ts            # Аутентификация
│   ├── useChat.ts            # WebSocket чат
│   ├── usePerformance.ts     # Метрики производительности
│   └── ...
│
├── lib/                       # Утилиты и API
│   ├── api/                   # API клиенты
│   ├── utils/                 # Утилиты
│   │   ├── logger.ts         # Logger с Sentry
│   │   ├── api.ts            # API клиент
│   │   └── ...
│   └── constants.ts           # Константы
│
├── types/                     # TypeScript типы
│ └── ...
│
└── public/                    # Статические файлы
    ├── sw.js                 # Service Worker
    └── manifest.json         # PWA manifest
```

---

## 🔄 Поток Данных

### 1. Аутентификация (Auth Flow)

```
┌─────────┐     ┌──────────┐     ┌─────────────┐     ┌──────────┐
│Client   │     │API Layer │     │Service Layer│     │Data Layer│
└────┬────┘     └────┬─────┘     └──────┬──────┘     └────┬─────┘
     │               │                  │                  │
     │ POST /login   │                  │                  │
     │──────────────>│                  │                  │
     │               │                  │                  │
     │               │ validate_input() │                  │
     │               │─────────────────>│                  │
     │               │                  │                  │
     │               │                  │ get_user(email)  │
     │               │                  │─────────────────>│
     │               │                  │                  │
     │               │                  │<─────────────────│
     │               │                  │     User data    │
     │               │                  │                  │
     │               │                  │ verify_password()│
     │               │                  │                  │
     │               │                  │ create_tokens()  │
     │               │                  │                  │
     │               │<─────────────────│                  │
     │               │   tokens         │                  │
     │               │                  │                  │
     │<──────────────│                  │                  │
     │  JWT tokens   │                  │                  │
     │               │                  │                  │
```

### 2. Запись на Курс (Course Enrollment)

```
┌─────────┐     ┌──────────┐     ┌─────────────┐     ┌──────────┐
│Client   │     │API Layer │     │CourseService│     │Database  │
└────┬────┘     └────┬─────┘     └──────┬──────┘     └────┬─────┘
     │               │                  │                  │
     │ POST /enroll  │                  │                  │
     │──────────────>│                  │                  │
     │               │                  │                  │
     │               │ check_mentor()   │                  │
     │               │─────────────────>│                  │
     │               │                  │                  │
     │               │                  │ SELECT course    │
     │               │                  │─────────────────>│
     │               │                  │                  │
     │               │                  │<─────────────────│
     │               │                  │   Course data    │
     │               │                  │                  │
     │               │                  │ check_enrollment()
     │               │                  │                  │
     │               │                  │ INSERT enrollment│
     │               │                  │─────────────────>│
     │               │                  │                  │
     │<──────────────│                  │                  │
     │ Enrollment    │                  │                  │
     │               │                  │                  │
```

---

## 🔐 Безопасность

### Уровни Защиты

1. **Transport Layer**
   - HTTPS/TLS для всех соединений
   - HSTS headers

2. **Authentication Layer**
   - JWT токены (access + refresh)
   - OAuth 2.0 (Google, GitHub)
   - 2FA TOTP

3. **Authorization Layer**
   - RBAC (Role-Based Access Control)
   - Permissions на уровне endpoints

4. **Input Validation**
   - Pydantic схемы
   - Санитизация данных
   - Rate limiting

5. **Data Protection**
   - Хеширование паролей (bcrypt)
   - Шифрование чувствительных данных
   - SQL injection protection (ORM)

---

## 📊 Масштабирование

### Горизонтальное Масштабирование

```
                    ┌─────────────┐
                    │ Load Balancer│
                    │   (nginx)    │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
   ┌─────▼─────┐    ┌─────▼─────┐    ┌─────▼─────┐
   │ Backend 1 │    │ Backend 2 │    │ Backend N │
   └─────┬─────┘    └─────┬─────┘    └─────┬─────┘
         │                │                │
         └────────────────┼────────────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
        ┌─────▼─────┐          ┌─────▼─────┐
        │ PostgreSQL│          │   Redis   │
        │  (Primary)│          │  (Cache)  │
        └───────────┘          └───────────┘
```

### Кэширование

1. **Redis Cache**
   - Сессионные данные
   - JWT blacklist
   - Rate limiting counters
   - API response cache

2. **HTTP Cache**
   - ETag headers
   - Last-Modified
   - Cache-Control

3. **Frontend Cache**
   - React Query cache
   - SWR cache
   - Service Worker cache

---

## 🧪 Тестирование

### Уровни Тестирования

```
┌─────────────────────────────────────┐
│         E2E Tests (Playwright)      │  ← Full user flows
├─────────────────────────────────────┤
│    Integration Tests (pytest)       │  ← API integration
├─────────────────────────────────────┤
│      Service Tests (pytest)         │  ← Business logic
├─────────────────────────────────────┤
│       Unit Tests (pytest/jest)      │  ← Functions/components
└─────────────────────────────────────┘
```

### Покрытие Кода

- **Backend:** ~80% (339 тестов)
- **Frontend:** ~75% (55 тестов)
- **Критичные пути:** 100%

---

## 📈 Мониторинг

### Метрики

1. **Performance**
   - API response time (p95, p99)
   - Database query time
   - Cache hit rate

2. **Reliability**
   - Error rate
   - Uptime
   - MTTR (Mean Time To Recovery)

3. **Business**
   - Active users
   - Course enrollments
   - Session bookings

### Инструменты

- **Prometheus** — сбор метрик
- **Grafana** — визуализация
- **Sentry** — error tracking
- **ELK Stack** — log aggregation

---

## 🚀 Деплой

### Production Environment

```yaml
Сервисы:
  - Frontend (Next.js) — 2 replicas
  - Backend (FastAPI) — 3 replicas
  - PostgreSQL 17 — primary + replica
  - Redis 7 — cluster mode
  - Celery Worker — 2 workers
  - Celery Beat — 1 scheduler
  - nginx — load balancer
  - Prometheus + Grafana — monitoring
```

### CI/CD Pipeline

```
┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌──────────┐
│  Push   │──>│  Build  │──>│  Test   │──>│  Deploy │──>│  Health  │
│  (git)  │   │(Docker) │   │(pytest) │   │ (K8s)   │   │  Check   │
└─────────┘   └─────────┘   └─────────┘   └─────────┘   └──────────┘
```

---

## 📝 Best Practices

### Код

1. **DRY (Don't Repeat Yourself)** — избегать дублирования
2. **SOLID** — принципы объектно-ориентированного дизайна
3. **KISS (Keep It Simple, Stupid)** — простота прежде всего
4. **YAGNI (You Aren't Gonna Need It)** — не добавлять лишнее

### Git

1. **Feature Branches** — одна фича = одна ветка
2. **Pull Requests** — code review обязательно
3. **Conventional Commits** — стандарт коммитов
4. **Semantic Versioning** — версионирование

### Безопасность

1. **Principle of Least Privilege** — минимальные права
2. **Defense in Depth** — многоуровневая защита
3. **Secure by Default** — безопасные настройки по умолчанию
4. **Fail Securely** — безопасная обработка ошибок

---

## 📚 Дополнительные Ресурсы

- [API Documentation](./docs/API.md)
- [Deployment Guide](./docs/DEPLOYMENT.md)
- [Contributing Guide](./CONTRIBUTING.md)
- [Security Policy](./SECURITY.md)

---

**MentorHub © 2026** — Open-source платформа для менторства
