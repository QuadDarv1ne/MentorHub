# MentorHub

**Платформа для профессионального менторства и карьерного развития в IT**

![MentorHub](https://img.shields.io/badge/status-in%20development-yellow) ![License](https://img.shields.io/badge/license-MIT-blue) ![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen) ![React](https://img.shields.io/badge/react-18%2B-blue)

## 📋 Оглавление

- [Описание](#описание)
- [Возможности](#возможности)
- [Технический стек](#технический-стек)
- [Архитектура](#архитектура)
- [Установка и запуск](#установка-и-запуск)
- [Структура проекта](#структура-проекта)
- [API Документация](#api-документация)
- [Использование](#использование)
- [Дорожная карта](#дорожная-карта)
- [Вклад](#вклад)
- [Лицензия](#лицензия)
- [Контакты](#контакты)

---

## 📝 Описание

**MentorHub** — это современная платформа для соединения опытных IT-специалистов (менторов) с людьми, стремящимися развивать свои навыки и построить карьеру в сфере информационных технологий. Платформа предоставляет полный набор инструментов для обучения, менторства и карьерного развития.

### Проблема

Многие люди, желающие войти в IT или повысить свой уровень, сталкиваются с:
- Отсутствием структурированного пути обучения
- Недостатком практического опыта
- Сложностью подготовки к собеседованиям
- Низкой эффективностью самостоятельного обучения

### Решение

MentorHub объединяет менторов и студентов в единую экосистему, предоставляя:
- Персональное менторство от опытных специалистов
- Структурированные курсы и материалы
- Практику на реальных проектах
- Помощь при подготовке к собеседованиям
- Сопровождение на испытательном сроке

---

## ✨ Возможности

### Для студентов

- 👤 **Персональный профиль** — создание портфолио и отслеживание прогресса
- 🔍 **Поиск менторов** — фильтрация по специальности, опыту и отзывам
- 📅 **Система бронирования** — удобное расписание занятий
- 💬 **Встроенный чат** — коммуникация с менторами между сессиями
- 🎥 **Видеоконференции** — проведение занятий один-на-один
- 📚 **Курсы и материалы** — доступ к обучающему контенту
- 📊 **Отслеживание прогресса** — визуализация улучшений и достижений
- 🏆 **Рейтинг и достижения** — мотивирующая система
- 📝 **Подготовка к собеседованиям** — специальные материалы и мок-интервью

### Для менторов

- 🎓 **Профиль ментора** — демонстрация опыта и достижений
- 📅 **Управление расписанием** — гибкое планирование доступности
- 👥 **Управление студентами** — список активных учеников и их прогресс
- 📈 **Аналитика** — статистика по занятиям, рейтинги, отзывы
- 💰 **Система оплаты** — безопасный способ получения вознаграждения
- 📱 **Инструменты преподавания** — материалы, задания, проверка работ
- ⭐ **Система отзывов** — отзывы от студентов для повышения репутации

### Для администратора

- 🛠️ **Управление контентом** — добавление курсов, редактирование материалов
- 👤 **Модерация пользователей** — проверка менторов, управление учётными записями
- 💳 **Управление платежами** — комиссии, выплаты, финансовые отчёты
- 📊 **Аналитика платформы** — статистика по пользователям, доход, активность
- 🔔 **Система уведомлений** — отправка важных сообщений пользователям

---

## 🛠️ Технический стек

### Frontend

| Технология | Версия | Назначение |
|-----------|--------|-----------|
| **Next.js** | 14+ | Full-stack React фреймворк |
| **React** | 18+ | UI компоненты |
| **TypeScript** | 5+ | Типизация кода |
| **Tailwind CSS** | 3+ | Стилизация |
| **Redux Toolkit** | 1.9+ | Управление состоянием |
| **Axios** | 1.4+ | HTTP клиент |
| **React Query** | 3+ | Кеширование данных |
| **WebSocket** | - | Real-time коммуникация |

### Backend

| Технология | Версия | Назначение |
|-----------|--------|-----------|
| **Python** | 3.9+ | Язык программирования |
| **FastAPI** | 0.100+ | Web фреймворк |
| **SQLAlchemy** | 2.0+ | ORM |
| **Pydantic** | 2.0+ | Валидация данных |
| **PostgreSQL** | 13+ | Основная БД |
| **Redis** | 6+ | Кеш и сессии |
| **Celery** | 5+ | Асинхронные задачи |
| **JWT** | - | Аутентификация |

### Дополнительно

| Технология | Назначение |
|-----------|-----------|
| **Docker** | Контейнеризация |
| **Docker Compose** | Оркестрирование контейнеров |
| **Agora SDK** | Видеоконференции |
| **Stripe/Yandex.Kassa** | Платежи |
| **AWS S3** | Хранение файлов |
| **Nginx** | Reverse proxy |

---

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│  ┌──────────────┐  ┌──────────┐  ┌────────────────────┐ │
│  │   Pages      │  │Components│  │ Redux State Store  │ │
│  └──────────────┘  └──────────┘  └────────────────────┘ │
└────────────────────┬──────────────────────────────────────┘
                     │ HTTP/WebSocket
┌────────────────────┴──────────────────────────────────────┐
│                   API Gateway (Nginx)                     │
└────────────────────┬──────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│              Backend (FastAPI)                              │
│  ┌──────────────┐  ┌──────────┐  ┌────────────────────┐   │
│  │ Auth Routes  │  │API Routes│  │WebSocket Handler  │   │
│  └──────────────┘  └──────────┘  └────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Business Logic & Services                   │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────┬──────────────────────┬────────────────────┘
                 │                      │
    ┌────────────┴────────┐   ┌────────┴──────────┐
    │                     │   │                   │
┌───▼───┐        ┌──────▼─┐  │  ┌──────────┐ ┌──▼───┐
│PostgreSQL      │ Redis  │  │  │   Celery │ │ AWS  │
│                │        │  │  │          │ │  S3  │
└────────────────┴────────┘  │  └──────────┘ └──────┘
                             │
                    ┌────────┴──────────┐
                    │  External APIs    │
                    │  ├─ Agora SDK     │
                    │  ├─ Stripe        │
                    │  └─ Email Service │
                    └───────────────────┘
```

---

## 🚀 Установка и запуск

### Предварительные требования

- Python 3.9+
- Node.js 16+
- Docker & Docker Compose
- Git
- PostgreSQL 13+ (или используйте Docker)
- Redis (или используйте Docker)

### Клонирование репозитория

```bash
git clone https://github.com/yourusername/mentorhub.git
cd mentorhub
```

### Установка Backend

```bash
# Перейти в папку backend
cd backend

# Создать виртуальное окружение
python -m venv venv

# Активировать виртуальное окружение
# На Linux/Mac:
source venv/bin/activate
# На Windows:
venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Создать .env файл
cp .env.example .env
# Отредактировать .env с вашими настройками

# Запустить миграции БД
alembic upgrade head

# Запустить сервер
uvicorn app.main:app --reload
```

Backend будет доступен на `http://localhost:8000`

### Установка Frontend

```bash
# Перейти в папку frontend
cd frontend

# Установить зависимости
npm install

# Создать .env.local файл
cp .env.example .env.local
# Отредактировать .env.local с вашими настройками

# Запустить dev сервер
npm run dev
```

Frontend будет доступен на `http://localhost:3000`

### Использование Docker Compose

Для удобства можно запустить всё через Docker:

```bash
# Из корневой папки проекта
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка контейнеров
docker-compose down
```

### Переменные окружения (.env)

**Backend (.env)**
```
DATABASE_URL=postgresql://user:password@localhost/mentorhub
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

AGORA_APP_ID=your-agora-app-id
AGORA_APP_CERTIFICATE=your-agora-cert

STRIPE_API_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_S3_BUCKET=mentorhub-bucket

EMAIL_SENDER=noreply@mentorhub.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**Frontend (.env.local)**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AGORA_APP_ID=your-agora-app-id
```

---

## 📁 Структура проекта

```
mentorhub/
├── backend/
│   ├── app/
│   │   ├── main.py                 # Entry point приложения
│   │   ├── config.py               # Конфигурация
│   │   ├── dependencies.py         # Зависимости
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py            # Маршруты аутентификации
│   │   │   ├── users.py           # Маршруты пользователей
│   │   │   ├── mentors.py         # Маршруты менторов
│   │   │   ├── courses.py         # Маршруты курсов
│   │   │   ├── sessions.py        # Маршруты сессий
│   │   │   ├── messages.py        # Маршруты сообщений
│   │   │   └── payments.py        # Маршруты платежей
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── mentor.py
│   │   │   ├── course.py
│   │   │   ├── session.py
│   │   │   ├── message.py
│   │   │   └── payment.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── mentor.py
│   │   │   ├── course.py
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── mentor_service.py
│   │   │   ├── course_service.py
│   │   │   ├── session_service.py
│   │   │   └── payment_service.py
│   │   ├── tasks/
│   │   │   ├── email.py           # Celery задачи для email
│   │   │   ├── notifications.py   # Уведомления
│   │   │   └── ...
│   │   ├── websockets/
│   │   │   └── chat_handler.py    # WebSocket для чата
│   │   └── utils/
│   │       ├── security.py
│   │       ├── validators.py
│   │       └── helpers.py
│   ├── migrations/                 # Alembic миграции
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_mentors.py
│   │   └── ...
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx             # Root layout
│   │   ├── page.tsx               # Home page
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   ├── register/page.tsx
│   │   │   └── ...
│   │   ├── (dashboard)/
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── mentors/page.tsx
│   │   │   ├── courses/page.tsx
│   │   │   ├── sessions/page.tsx
│   │   │   ├── chat/page.tsx
│   │   │   └── profile/page.tsx
│   │   ├── api/                   # API routes
│   │   │   └── ...
│   │   └── ...
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   ├── Navigation.tsx
│   │   │   └── ...
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── ...
│   │   ├── mentors/
│   │   │   ├── MentorCard.tsx
│   │   │   ├── MentorList.tsx
│   │   │   └── MentorProfile.tsx
│   │   ├── sessions/
│   │   │   ├── SessionBooking.tsx
│   │   │   ├── VideoCall.tsx
│   │   │   └── ...
│   │   └── ...
│   ├── lib/
│   │   ├── api.ts                 # API клиент
│   │   ├── auth.ts                # Auth логика
│   │   ├── agora.ts               # Agora интеграция
│   │   └── utils.ts
│   ├── store/
│   │   ├── authSlice.ts
│   │   ├── mentorSlice.ts
│   │   └── ...
│   ├── styles/
│   │   └── globals.css
│   ├── public/
│   │   └── ...
│   ├── package.json
│   ├── tsconfig.json
│   ├── Dockerfile
│   ├── .env.example
│   └── next.config.js
│
├── docker-compose.yml
├── Makefile                        # Команды для разработки
├── README.md
└── .gitignore
```

---

## 📚 API Документация

### Swagger Documentation

После запуска backend, документация доступна по адресу:
```
http://localhost:8000/docs
```

### Основные endpoints

#### Аутентификация
```
POST   /api/v1/auth/register        # Регистрация
POST   /api/v1/auth/login           # Вход
POST   /api/v1/auth/refresh         # Обновить токен
POST   /api/v1/auth/logout          # Выход
```

#### Пользователи
```
GET    /api/v1/users/me             # Текущий пользователь
PUT    /api/v1/users/me             # Обновить профиль
GET    /api/v1/users/{user_id}      # Получить пользователя
```

#### Менторы
```
GET    /api/v1/mentors              # Список менторов
GET    /api/v1/mentors/{mentor_id}  # Информация ментора
POST   /api/v1/mentors/apply        # Применить как ментор
PUT    /api/v1/mentors/{mentor_id}  # Обновить профиль ментора
GET    /api/v1/mentors/{id}/reviews # Отзывы ментора
```

#### Сессии
```
GET    /api/v1/sessions             # Мои сессии
POST   /api/v1/sessions             # Забронировать сессию
GET    /api/v1/sessions/{session_id}# Информация сессии
PUT    /api/v1/sessions/{id}        # Обновить сессию
DELETE /api/v1/sessions/{id}        # Отменить сессию
POST   /api/v1/sessions/{id}/complete # Завершить сессию
```

#### Курсы
```
GET    /api/v1/courses              # Список курсов
GET    /api/v1/courses/{course_id}  # Информация курса
POST   /api/v1/courses/{id}/enroll  # Записаться на курс
```

#### Сообщения
```
GET    /api/v1/messages/chats       # Список чатов
GET    /api/v1/messages/chats/{id}  # История чата
POST   /api/v1/messages             # Отправить сообщение
```

#### Платежи
```
POST   /api/v1/payments/create      # Создать платёж
POST   /api/v1/payments/webhook     # Webhook платежа
GET    /api/v1/payments/history     # История платежей
```

---

## 💻 Использование

### Регистрация как студент

1. Перейдите на главную страницу
2. Нажмите "Зарегистрироваться"
3. Выберите роль "Студент"
4. Заполните информацию о себе
5. Подтвердите email
6. Завершите регистрацию

### Поиск ментора

1. Перейдите в раздел "Менторы"
2. Используйте фильтры (специальность, опыт, цена)
3. Посмотрите профиль ментора и отзывы
4. Нажмите "Забронировать"
5. Выберите удобное время
6. Оплатите сессию

### Проведение сессии

1. За 15 минут до начала перейдите в "Мои сессии"
2. Нажмите "Присоединиться"
3. Позвольте доступ к камере и микрофону
4. Общайтесь с менторов через видео
5. После завершения оставьте отзыв

### Регистрация как ментор

1. Зарегистрируйтесь как пользователь
2. Перейдите в профиль
3. Нажмите "Стать ментором"
4. Заполните информацию о своем опыте
5. Добавьте фото и описание
6. Дождитесь одобрения администратора
7. Начните принимать студентов

---

## 🗺️ Дорожная карта

### MVP (v1.0) - Q1 2025
- [x] Основная структура проекта
- [x] Аутентификация и авторизация
- [x] Профили пользователей и менторов
- [ ] Поиск и фильтрация менторов
- [ ] Система бронирования сессий
- [ ] Видеоконференции через Agora
- [ ] Встроенный чат
- [ ] Система оплаты (Stripe)

### V1.1 - Q2 2025
- [ ] Курсы и материалы
- [ ] Система отзывов и рейтинги
- [ ] Email уведомления
- [ ] Профиль ментора с аналитикой
- [ ] Система выплат менторам
- [ ] Mobile версия

### V1.2 - Q3 2025
- [ ] Групповые сессии
- [ ] Цифровые сертификаты
- [ ] Интеграция с календарём (Google, Outlook)
- [ ] Автоматические напоминания
- [ ] Экспорт данных
- [ ] Интеграция с соцсетями

### V2.0 - Q4 2025
- [ ] AI-ассистент для подготовки
- [ ] Мок-интервью с записью
- [ ] Маркетплейс услуг
- [ ] Корпоративные аккаунты
- [ ] Интеграция с HRM системами
- [ ] Мобильное приложение (iOS/Android)

---

## 🤝 Вклад

Мы приветствуем вклад от сообщества! Если вы хотите помочь:

1. **Форкните репозиторий**
```bash
git clone https://github.com/yourusername/mentorhub.git
cd mentorhub
git checkout -b feature/your-feature-name
```

2. **Внесите свои изменения**
```bash
git add .
git commit -m "Add: описание ваших изменений"
```

3. **Отправьте Pull Request**
```bash
git push origin feature/your-feature-name
```

### Стандарты кода

- Используйте PEP 8 для Python
- Используйте Prettier для JavaScript/TypeScript
- Напишите тесты для новых функций
- Обновите документацию

### Баг репорты

**Если нашли баг, создайте Issue с:**

- Описанием проблемы
- Шагами для воспроизведения
- Ожидаемым и актуальным поведением
- Скриншотами (если применимо)

---

## 📄 Лицензия

Этот проект лицензирован под MIT License — см. файл [LICENSE](LICENSE) для деталей.

---

## 📞 Контакты

- **Email:** support@mentorhub.com
- **Website:** https://mentorhub.com
- **Telegram:** @mentorhub_support
- **Twitter:** @MentorHubApp

### Социальные сети

- [GitHub](https://github.com/mentorhub)
- [LinkedIn](https://linkedin.com/company/mentorhub)
- [Twitter](https://twitter.com/MentorHubApp)
- [Telegram Community](https://t.me/mentorhub_community)

---

## 🙏 Благодарности

Спасибо всем, кто помогает развивать MentorHub и верит в нашу миссию сделать IT-образование доступнее!

---

**Made with ❤️ by MentorHub Team**

*Последнее обновление: 02/11/2025*
