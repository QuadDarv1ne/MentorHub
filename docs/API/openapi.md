# MentorHub API Documentation

## Base URL
```
Production: https://mentorhub-7eat.onrender.com/api/v1
Development: http://localhost:8000/api/v1
```

## Authentication
Most endpoints require JWT authentication. Include the token in the `Authorization` header:
```
Authorization: Bearer <your_jwt_token>
```

---

## API Endpoints

### 🔐 Authentication (`/api/v1/auth`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/register` | Register new user | ❌ |
| POST | `/login` | Login user | ❌ |
| POST | `/refresh` | Refresh access token | ✅ |
| POST | `/logout` | Logout user | ✅ |
| GET | `/me` | Get current user | ✅ |

**Request/Response Examples:**

#### POST `/auth/register`
```json
// Request
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}

// Response (201)
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "created_at": "2026-03-10T12:00:00Z"
}
```

#### POST `/auth/login`
```json
// Request
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

// Response (200)
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer"
}
```

---

### 👥 Users (`/api/v1/users`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/{user_id}` | Get user by ID | ✅ |
| PUT | `/{user_id}` | Update user | ✅ |
| DELETE | `/{user_id}` | Delete user | ✅ |
| GET | `/` | List all users | ✅ |
| GET | `/me` | Get current user | ✅ |
| PUT | `/me` | Update current user | ✅ |

---

### 🎓 Mentors (`/api/v1/mentors`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | List all mentors | ❌ |
| GET | `/{mentor_id}` | Get mentor by ID | ❌ |
| POST | `/` | Create mentor profile | ✅ |
| PUT | `/{mentor_id}` | Update mentor | ✅ |
| DELETE | `/{mentor_id}` | Delete mentor | ✅ |
| GET | `/search` | Search mentors | ❌ |

**Query Parameters:**
- `specialization` - Filter by specialization
- `level` - Filter by level (Junior, Middle, Senior)
- `price_min` - Minimum price
- `price_max` - Maximum price

---

### 📚 Courses (`/api/v1/courses`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | List all courses | ❌ |
| GET | `/{course_id}` | Get course by ID | ❌ |
| POST | `/` | Create course | ✅ Admin |
| PUT | `/{course_id}` | Update course | ✅ Admin |
| DELETE | `/{course_id}` | Delete course | ✅ Admin |
| POST | `/{course_id}/enroll` | Enroll in course | ✅ |
| GET | `/enrolled` | Get enrolled courses | ✅ |

---

### 📅 Sessions (`/api/v1/sessions`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | List all sessions | ✅ |
| GET | `/{session_id}` | Get session by ID | ✅ |
| POST | `/` | Create session | ✅ |
| PUT | `/{session_id}` | Update session | ✅ |
| DELETE | `/{session_id}` | Cancel session | ✅ |

---

### 💬 Messages (`/api/v1/messages`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | List conversations | ✅ |
| GET | `/chat/{user_id}` | Get chat with user | ✅ |
| POST | `/` | Send message | ✅ |
| DELETE | `/{message_id}` | Delete message | ✅ |

---

### 💳 Payments (`/api/v1/payments`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/create-intent` | Create payment intent | ✅ |
| POST | `/webhook` | Payment webhook | ❌ |
| GET | `/history` | Get payment history | ✅ |
| GET | `/{payment_id}` | Get payment by ID | ✅ |

---

### 📊 Progress (`/api/v1/progress`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | Get user progress | ✅ |
| POST | `/` | Update progress | ✅ |
| GET | `/user/{user_id}` | Get user progress | ✅ |
| GET | `/course/{course_id}` | Get course progress | ✅ |

---

### ⭐ Reviews (`/api/v1/reviews`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | List all reviews | ❌ |
| POST | `/` | Create review | ✅ |
| PUT | `/{review_id}` | Update review | ✅ |
| DELETE | `/{review_id}` | Delete review | ✅ |

---

### 📈 Statistics (`/api/v1/stats`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/overview` | Get platform stats | ❌ |
| GET | `/users` | Get user statistics | ✅ Admin |
| GET | `/sessions` | Get session statistics | ✅ Admin |
| GET | `/revenue` | Get revenue statistics | ✅ Admin |

---

### 🏆 Achievements (`/api/v1/achievements`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | List all achievements | ✅ |
| POST | `/` | Create achievement | ✅ Admin |
| GET | `/user/{user_id}` | Get user achievements | ✅ |

---

### 🔔 Notifications (`/api/v1/notifications`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/` | List notifications | ✅ |
| PUT | `/{notification_id}/read` | Mark as read | ✅ |
| DELETE | `/{notification_id}` | Delete notification | ✅ |

---

### 🏥 Health Checks

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/health` | Basic health check |
| `GET /api/v1/health/detailed` | Detailed health with metrics |
| `GET /api/v1/health/ready` | Readiness check |
| `GET /api/v1/health/live` | Liveness check |
| `GET /api/v1/health/database` | Database health |

---

## Error Responses

All endpoints return consistent error format:

```json
{
  "status_code": 400,
  "message": "Error message",
  "error_code": "ERROR_CODE",
  "timestamp": "2026-03-10T12:00:00Z",
  "path": "/api/v1/endpoint"
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `HTTP_400` | 400 | Bad Request |
| `HTTP_401` | 401 | Unauthorized |
| `HTTP_403` | 403 | Forbidden |
| `HTTP_404` | 404 | Not Found |
| `HTTP_409` | 409 | Conflict |
| `HTTP_422` | 422 | Validation Error |
| `HTTP_500` | 500 | Internal Server Error |

---

## Rate Limiting

API requests are rate limited:
- **Default:** 100 requests per minute
- **Authenticated:** 200 requests per minute

Headers returned:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1647345600
```

---

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 20, max: 100)
- `sort` - Sort field (e.g., `created_at`, `name`)
- `order` - Sort order (`asc`, `desc`)

**Response:**
```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "limit": 20,
  "pages": 8
}
```

---

## WebSocket API

### Real-time Chat
```
wss://mentorhub-7eat.onrender.com/api/v1/ws/chat
```

**Authentication:**
```
wss://mentorhub-7eat.onrender.com/api/v1/ws/chat?token=<jwt_token>
```

**Message Format:**
```json
{
  "type": "message",
  "data": {
    "recipient_id": 123,
    "content": "Hello!"
  }
}
```

---

## SDK Examples

### JavaScript/TypeScript
```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'https://mentorhub-7eat.onrender.com/api/v1',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// Login
const { data } = await api.post('/auth/login', {
  email: 'user@example.com',
  password: 'password'
});

// Get mentors
const mentors = await api.get('/mentors', {
  params: { specialization: 'Python' }
});
```

### Python
```python
import requests

BASE_URL = 'https://mentorhub-7eat.onrender.com/api/v1'

# Login
response = requests.post(f'{BASE_URL}/auth/login', json={
    'email': 'user@example.com',
    'password': 'password'
})
token = response.json()['access_token']

# Get mentors
headers = {'Authorization': f'Bearer {token}'}
mentors = requests.get(f'{BASE_URL}/mentors', headers=headers)
```

---

## Swagger UI

Interactive API documentation available at:
```
https://mentorhub-7eat.onrender.com/docs
```

## ReDoc

Alternative documentation:
```
https://mentorhub-7eat.onrender.com/redoc
```
