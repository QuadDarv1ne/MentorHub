# API Documentation Generator

## Автоматическая генерация документации

MentorHub использует FastAPI встроенную систему документации с **OpenAPI (Swagger)** и **ReDoc**.

## Доступные endpoints

### Development

```
http://localhost:8000/docs       - Swagger UI (интерактивная)
http://localhost:8000/redoc      - ReDoc (красивая документация)
http://localhost:8000/openapi.json - OpenAPI schema
```

### Production

В production режиме документация отключена для безопасности.
Для включения установите `DEBUG=true` в `.env`.

## Генерация статической документации

### 1. OpenAPI Schema

Экспорт OpenAPI схемы в JSON:

```bash
cd backend
python -c "
from app.main import app
import json

with open('openapi.json', 'w') as f:
    json.dump(app.openapi(), f, indent=2)

print('✅ OpenAPI schema exported to openapi.json')
"
```

### 2. Markdown документация

Используйте `openapi-generator`:

```bash
# Установка
npm install -g @openapitools/openapi-generator-cli

# Генерация markdown
openapi-generator-cli generate \
  -i openapi.json \
  -g markdown \
  -o docs/api
```

### 3. HTML документация

```bash
# Используйте redoc-cli
npm install -g redoc-cli

# Генерация статического HTML
redoc-cli bundle openapi.json \
  -o docs/api-reference.html \
  --title "MentorHub API Documentation"
```

## Примеры использования API

### Authentication

```bash
# Регистрация
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePass123!"
  }'

# Логин
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'

# Response:
# {
#   "access_token": "eyJhbGc...",
#   "token_type": "bearer",
#   "expires_in": 1800
# }
```

### Authenticated Requests

```bash
# Получить профиль
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Обновить профиль
curl -X PUT http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "bio": "Software Developer"
  }'
```

### WebSocket

```javascript
// JavaScript/TypeScript example
const ws = new WebSocket(
  'ws://localhost:8000/ws/chat?token=YOUR_ACCESS_TOKEN'
);

ws.onopen = () => {
  console.log('Connected');
  
  // Send message
  ws.send(JSON.stringify({
    type: 'message',
    recipient_id: 2,
    content: 'Hello!'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### Analytics

```bash
# Platform stats (admin only)
curl http://localhost:8000/api/v1/analytics/platform \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"

# User growth
curl http://localhost:8000/api/v1/analytics/user-growth?days=30 \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"

# My engagement
curl http://localhost:8000/api/v1/analytics/me/engagement \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Notifications

```bash
# Get notifications
curl http://localhost:8000/api/v1/notifications?limit=20 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Unread count
curl http://localhost:8000/api/v1/notifications/unread-count \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Mark as read
curl -X POST http://localhost:8000/api/v1/notifications/123/read \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Postman Collection

Импортируйте OpenAPI schema в Postman:

1. Откройте Postman
2. Import → Link → `http://localhost:8000/openapi.json`
3. Или используйте файл `backend/postman_collection.json`

## SDK Generation

### TypeScript/JavaScript

```bash
openapi-generator-cli generate \
  -i openapi.json \
  -g typescript-axios \
  -o frontend/src/api

# Использование
import { DefaultApi } from '@/api';

const api = new DefaultApi();
const response = await api.getUsersMe();
```

### Python

```bash
openapi-generator-cli generate \
  -i openapi.json \
  -g python \
  -o python-client

# Использование
from mentorhub_client import ApiClient, DefaultApi

client = ApiClient(configuration)
api = DefaultApi(client)
```

## Rate Limits

По умолчанию:
- **100 requests per minute** для всех endpoints
- **10 requests per minute** для login/register

Headers в ответе:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1701705600
```

## Error Responses

Все ошибки возвращаются в формате:

```json
{
  "detail": "Error message",
  "status_code": 400,
  "timestamp": "2025-12-04T12:00:00Z",
  "path": "/api/v1/users/me"
}
```

## Versioning

API использует URL versioning:
- Current: `/api/v1/*`
- Future: `/api/v2/*` (когда будут breaking changes)

## CORS

Allowed origins (development):
- `http://localhost:3000`
- `http://localhost:3001`
- `http://127.0.0.1:3000`

Production origins настраиваются через `CORS_ORIGINS` env variable.

## Testing

```bash
# Healthcheck
curl http://localhost:8000/health

# Response:
# {
#   "status": "healthy",
#   "timestamp": "2025-12-04T12:00:00Z",
#   "version": "1.0.0"
# }
```

## Production URL

```
https://api.mentorhub.com/api/v1/
```

Замените `localhost:8000` на production URL в примерах выше.
