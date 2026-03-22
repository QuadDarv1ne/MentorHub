# OpenAPI/Swagger Документация MentorHub

## Обзор

MentorHub предоставляет полнофункциональный REST API с автоматической OpenAPI документацией.

## Доступ к документации

После запуска сервера документация доступна по следующим адресам:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Аутентификация

Большинство endpoints требуют JWT аутентификации.

### Получение токена

```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

Ответ:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Использование токена

Добавьте токен в заголовок Authorization:

```bash
Authorization: Bearer <your_access_token>
```

### Обновление токена

```bash
POST /api/auth/refresh
Headers:
  Authorization: Bearer <your_refresh_token>
```

## Основные endpoints

### Пользователи

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/users/me` | Получить профиль текущего пользователя |
| PUT | `/api/users/me` | Обновить профиль текущего пользователя |
| GET | `/api/users/{user_id}` | Получить пользователя по ID |

### Менторы

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/mentors/` | Получить список менторов |
| GET | `/api/mentors/{mentor_id}` | Получить ментора по ID |
| POST | `/api/mentors/` | Создать профиль ментора |
| PUT | `/api/mentors/{mentor_id}` | Обновить профиль ментора |
| DELETE | `/api/mentors/{mentor_id}` | Удалить профиль ментора |

### Сессии

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/sessions/` | Получить список сессий |
| GET | `/api/sessions/{session_id}` | Получить сессию по ID |
| POST | `/api/sessions/` | Забронировать сессию |
| PUT | `/api/sessions/{session_id}` | Обновить сессию |
| DELETE | `/api/sessions/{session_id}` | Отменить сессию |

### Курсы

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/courses/` | Получить список курсов |
| GET | `/api/courses/{course_id}` | Получить курс с уроками |
| POST | `/api/courses/` | Создать курс (менторы) |
| PUT | `/api/courses/{course_id}` | Обновить курс |
| DELETE | `/api/courses/{course_id}` | Удалить курс |
| POST | `/api/courses/{course_id}/enroll` | Записаться на курс |

### Платежи

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/payments/` | Получить список платежей |
| GET | `/api/payments/{payment_id}` | Получить платёж по ID |
| POST | `/api/payments/` | Создать платёж |
| POST | `/api/payments/{payment_id}/refund` | Вернуть платёж |

### Сообщения

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/api/messages/` | Получить список сообщений |
| POST | `/api/messages/` | Отправить сообщение |
| PUT | `/api/messages/{message_id}/read` | Отметить как прочитанное |

### WebSocket

Подключение к WebSocket для real-time общения:

```
ws://localhost:8000/ws?token=<your_jwt_token>
```

## Rate Limiting

API имеет ограничения на количество запросов:

- **100 запросов в час** на IP адрес для анонимных endpoints
- **60 запросов в минуту** на пользователя для аутентифицированных endpoints

При превышении лимита возвращается ответ `429 Too Many Requests`.

## Коды ошибок

| Код | Описание |
|-----|----------|
| 200 | Успешный запрос |
| 201 | Ресурс создан |
| 400 | Некорректный запрос |
| 401 | Неавторизован |
| 403 | Доступ запрещён |
| 404 | Ресурс не найден |
| 429 | Превышен лимит запросов |
| 500 | Внутренняя ошибка сервера |

## Примеры использования

### Python (requests)

```python
import requests

# Логин
response = requests.post('http://localhost:8000/api/auth/login', json={
    'email': 'user@example.com',
    'password': 'password123'
})
token = response.json()['access_token']

# Получение профиля
headers = {'Authorization': f'Bearer {token}'}
profile = requests.get('http://localhost:8000/api/users/me', headers=headers)
print(profile.json())
```

### JavaScript (fetch)

```javascript
// Логин
const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        email: 'user@example.com',
        password: 'password123'
    })
});
const {access_token} = await loginResponse.json();

// Получение профиля
const profileResponse = await fetch('http://localhost:8000/api/users/me', {
    headers: {'Authorization': `Bearer ${access_token}`}
});
const profile = await profileResponse.json();
```

### cURL

```bash
# Логин
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Получение профиля
curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer <token>"
```

## Двухфакторная аутентификация

### Настройка 2FA

```bash
POST /api/auth/2fa/setup
Headers:
  Authorization: Bearer <your_token>

Response:
{
  "qr_code_url": "otpauth://totp/...",
  "secret": "JBSWY3DPEHPK3PXP",
  "backup_codes": ["12345678", "87654321", ...]
}
```

### Подтверждение 2FA

```bash
POST /api/auth/2fa/verify
Headers:
  Authorization: Bearer <your_token>
Content-Type: application/json

{
  "code": "123456"
}
```

## Уведомления

### Push уведомления

Регистрация устройства для push уведомлений:

```bash
POST /api/push-notifications/register
Headers:
  Authorization: Bearer <your_token>
Content-Type: application/json

{
  "device_token": "fcm_device_token",
  "device_type": "android"
}
```

## Экспорт данных (GDPR)

### Экспорт в PDF

```bash
GET /api/export/pdf
Headers:
  Authorization: Bearer <your_token>

Response: application/pdf файл
```

### Экспорт в Excel

```bash
GET /api/export/excel
Headers:
  Authorization: Bearer <your_token>

Response: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet файл
```

## Health Checks

### Основная проверка

```bash
GET /health
```

Ответ:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-22T12:00:00Z"
}
```

### Подробная проверка

```bash
GET /health/detailed
```

Ответ включает статус всех сервисов:
- Database
- Redis
- Cache
- External services

## Мониторинг

### Prometheus метрики

```bash
GET /metrics
```

Метрики включают:
- Количество запросов
- Время ответа
- Ошибки
- Использование ресурсов

## Поддержка

Для вопросов по API создайте issue на GitHub или обратитесь к документации в `/docs`.
