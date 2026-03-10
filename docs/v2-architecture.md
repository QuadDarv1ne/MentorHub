# MentorHub v2.0 - Расширенная документация

## 🚀 Что нового в версии 2.0

### Основные улучшения:
- **Real-time чат** между студентами и менторами
- **Система уведомлений** с 15+ типами уведомлений  
- **Email верификация** с HTML шаблонами
- **Background tasks** с Celery
- **Расширенное логирование** запросов
- **Усиленная безопасность** для продакшена

---

## 📱 Frontend Components

### 1. Чат (WebSocket)

#### ChatWidget.tsx
Плавающий виджет чата с real-time сообщениями

**Props:**
```typescript
interface ChatWidgetProps {
  recipientId: number      // ID получателя
  recipientName: string    // Имя получателя
  isOpen: boolean         // Состояние видимости
  onClose: () => void     // Callback закрытия
}
```

**Функциональность:**
- Real-time обмен сообщениями
- Индикатор печати (typing)
- Отметки о прочтении
- Онлайн статус
- Автоматическая прокрутка

#### ChatButton.tsx
Кнопка для открытия чата

**Props:**
```typescript
interface ChatButtonProps {
  recipientId: number
  recipientName: string
}
```

### 2. Email верификация

#### EmailVerification.tsx
Страница верификации email с красивым UI

**Функциональность:**
- Автоматическая верификация по токену
- Повторная отправка письма
- Обработка ошибок
- Переадресация после успеха

#### ForgotPassword.tsx
Форма восстановления пароля

**Функциональность:**
- Запрос сброса пароля
- Отправка инструкций на email
- Обратный отсчет времени действия ссылки

### 3. Уведомления

#### NotificationCenter.tsx
Центр уведомлений в хедере

**Функциональность:**
- Фильтрация по статусу
- Массовые операции
- Автоматическое обновление
- Анимированные переходы

---

## 🔧 Backend API

### Email Endpoints

#### POST `/api/v1/email/send-verification`
Отправка письма верификации

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Verification email sent",
  "expires_in_hours": 24
}
```

#### POST `/api/v1/email/verify-email`
Верификация email по токену

**Request:**
```json
{
  "token": "verification_token_here"
}
```

#### POST `/api/v1/email/forgot-password`
Запрос восстановления пароля

**Request:**
```json
{
  "email": "user@example.com"
}
```

#### POST `/api/v1/email/reset-password`
Сброс пароля

**Request:**
```json
{
  "token": "reset_token_here",
  "new_password": "new_secure_password"
}
```

### WebSocket Endpoints

#### WS `ws://localhost:8000/ws/chat`
Real-time чат

**Authentication:**
Query parameter: `?token=JWT_TOKEN`

**Incoming Messages:**
```json
// Отправка сообщения
{
  "type": "message",
  "recipient_id": 123,
  "content": "Hello!"
}

// Индикатор печати
{
  "type": "typing",
  "recipient_id": 123
}

// Отметка о прочтении
{
  "type": "read",
  "message_id": 456
}
```

**Outgoing Messages:**
```json
// Полученное сообщение
{
  "type": "message",
  "id": 456,
  "sender_id": 789,
  "sender_username": "john_doe",
  "content": "Hello!",
  "timestamp": "2025-12-04T12:00:00"
}

// Индикатор печати
{
  "type": "typing",
  "user_id": 789,
  "username": "john_doe"
}
```

#### GET `/api/v1/ws/online-users`
Список онлайн пользователей

### Notification Endpoints

#### GET `/api/v1/notifications`
Получение уведомлений пользователя

**Query Parameters:**
- `page` (int, default: 1)
- `size` (int, default: 20)
- `type` (string, enum)
- `is_read` (boolean)

#### GET `/api/v1/notifications/unread-count`
Количество непрочитанных уведомлений

#### POST `/api/v1/notifications/{id}/read`
Отметить уведомление как прочитанное

#### POST `/api/v1/notifications/mark-all-read`
Отметить все как прочитанные

#### DELETE `/api/v1/notifications/{id}`
Удалить уведомление

#### DELETE `/api/v1/notifications/clear-all`
Очистить все уведомления

---

## 🛡️ Безопасность

### Middleware

#### SecurityHeadersMiddleware
Добавляет HTTP заголовки безопасности:
- Strict-Transport-Security
- X-Content-Type-Options
- X-Frame-Options
- Content-Security-Policy
- И другие

#### RateLimitMiddleware
Ограничение частоты запросов (по умолчанию 60/минуту)

#### RequestSizeLimiterMiddleware
Ограничение размера тела запроса (по умолчанию 10MB)

#### AuditLoggingMiddleware
Аудит критических операций

### Production Config

Файл: `app/config_prod.py`

**Ключевые настройки:**
- `DEBUG = False`
- `ALLOWED_HOSTS` для продакшена
- Настройки пула соединений БД
- Параметры безопасности Redis/Celery
- Лимиты запросов и размеров файлов

---

## 🧪 Тестирование

### Новые тесты:

#### `test_email_verification.py`
- Тесты email верификации
- Тесты восстановления пароля
- Интеграционные тесты

#### `test_websocket_chat.py`
- Тесты WebSocket подключения
- Тесты обмена сообщениями
- Тесты индикаторов печати

#### `test_notifications.py`
- Тесты CRUD операций с уведомлениями
- Тесты фильтрации и пагинации
- Тесты массовых операций

### Запуск тестов:
```bash
cd backend
pytest tests/test_email_verification.py -v
pytest tests/test_websocket_chat.py -v
pytest tests/test_notifications.py -v
```

---

## 📊 Мониторинг

### Health Checks

#### `/health`
Базовая проверка здоровья

#### `/health/detailed`
Детальная информация с системными метриками

#### `/health/ready`
Проверка готовности к работе

#### `/health/live`
Проверка жизнеспособности

### Metrics
Доступны стандартные метрики Prometheus через `/metrics`

---

## 🚀 Deployment

### Production Requirements:

1. **Environment Variables:**
```env
# Основные
SECRET_KEY=your-super-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://localhost:6379/0

# Email (SendGrid рекомендуется)
SMTP_HOST=smtp.sendgrid.net
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

2. **Services:**
- PostgreSQL (основная БД)
- Redis (кэш, очереди)
- Celery workers
- Celery beat scheduler

3. **Process Management:**
```bash
# Backend API
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Celery worker
celery -A app.tasks.celery_tasks worker --loglevel=info

# Celery beat
celery -A app.tasks.celery_tasks beat --loglevel=info
```

---

## 📈 Производительность

### Оптимизации:

1. **Connection Pooling:**
   - БД: pool_size=20, max_overflow=30
   - Redis: connection pooling встроено

2. **Caching:**
   - Redis для сессий
   - Кэширование часто запрашиваемых данных

3. **Async Processing:**
   - Email отправка через Celery
   - Background tasks для тяжелых операций

4. **Rate Limiting:**
   - Защита от DDoS
   - Fair usage policy

---

## 🐛 Troubleshooting

### Частые проблемы:

1. **WebSocket connection failed:**
   - Проверьте JWT токен
   - Убедитесь что сервер запущен
   - Проверьте CORS настройки

2. **Email not sending:**
   - Проверьте SMTP credentials
   - Убедитесь что Celery worker запущен
   - Проверьте логи Celery

3. **Notifications not appearing:**
   - Проверьте подключение к Redis
   - Убедитесь что пользователь авторизован
   - Проверьте права доступа

### Логирование:
- `INFO` уровень для обычных операций
- `WARNING` для потенциальные проблемы
- `ERROR` для реальных ошибок
- `AUDIT` для критических операций

---

## 📞 Support

Для вопросов и поддержки:
- GitHub Issues: [repo/issues](https://github.com/your-repo/issues)
- Email: support@mentorhub.ru
- Документация: [docs.mentorhub.ru](https://docs.mentorhub.ru)

---

**Happy coding!** 🚀