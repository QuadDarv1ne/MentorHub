# MentorHub API Documentation

## Base URL

```
Production: https://api.mentorhub.app
Development: http://localhost:8000
```

## Authentication

### JWT Token

Most API endpoints require authentication using JWT (JSON Web Tokens).

**Getting a token:**

```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Using the token:**

```bash
GET /api/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Token Expiration

- Access token: 30 minutes
- Refresh token: 7 days

### Refreshing Tokens

```bash
POST /api/auth/refresh
Authorization: Bearer <refresh_token>

# Response
{
  "access_token": "new_access_token",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login with username/password |
| POST | `/api/auth/refresh` | Refresh access token |
| POST | `/api/auth/logout` | Logout (invalidate token) |
| GET | `/api/auth/me` | Get current user info |
| POST | `/api/auth/2fa/enable` | Enable two-factor auth |
| POST | `/api/auth/2fa/verify` | Verify 2FA code |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | List all users (admin) |
| GET | `/api/users/me` | Get current user profile |
| PUT | `/api/users/me` | Update current user profile |
| DELETE | `/api/users/me` | Delete account |
| GET | `/api/users/{id}` | Get user by ID |
| GET | `/api/users/{id}/mentors` | Get user's mentors |
| GET | `/api/users/{id}/sessions` | Get user's sessions |

### Mentors

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/mentors` | List all mentors |
| GET | `/api/mentors/{id}` | Get mentor details |
| POST | `/api/mentors` | Become a mentor |
| PUT | `/api/mentors/{id}` | Update mentor profile |
| DELETE | `/api/mentors/{id}` | Delete mentor profile |
| GET | `/api/mentors/{id}/reviews` | Get mentor reviews |
| GET | `/api/mentors/{id}/sessions` | Get mentor sessions |

### Sessions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sessions` | List all sessions |
| GET | `/api/sessions/my` | Get my sessions |
| GET | `/api/sessions/{id}` | Get session details |
| POST | `/api/sessions` | Create new session |
| PUT | `/api/sessions/{id}` | Update session |
| DELETE | `/api/sessions/{id}` | Cancel session |
| POST | `/api/sessions/{id}/complete` | Mark session complete |
| POST | `/api/sessions/{id}/join` | Join video session |

### Messages

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/messages` | List all messages |
| GET | `/api/messages/conversations` | Get conversation list |
| GET | `/api/messages/history/{user_id}` | Get chat history |
| POST | `/api/messages` | Send message |
| PUT | `/api/messages/{id}` | Update message |
| DELETE | `/api/messages/{id}` | Delete message |

### Payments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/payments` | List all payments |
| GET | `/api/payments/my` | Get my payments |
| GET | `/api/payments/{id}` | Get payment details |
| POST | `/api/payments` | Create payment |
| POST | `/api/payments/{id}/refund` | Refund payment |
| GET | `/api/payments/student/{student_id}` | Get student payments |
| GET | `/api/payments/mentor/{mentor_id}` | Get mentor payments |

### Courses

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/courses` | List all courses |
| GET | `/api/courses/{id}` | Get course details |
| POST | `/api/courses` | Create course (admin) |
| PUT | `/api/courses/{id}` | Update course |
| DELETE | `/api/courses/{id}` | Delete course |
| GET | `/api/courses/{id}/lessons` | Get course lessons |
| POST | `/api/courses/{id}/enroll` | Enroll in course |
| GET | `/api/stepik/courses` | Get Stepik courses |
| GET | `/api/stepik/courses/{id}` | Get Stepik course details |

### Reviews

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reviews` | List all reviews |
| GET | `/api/reviews/{id}` | Get review details |
| POST | `/api/reviews` | Create review |
| PUT | `/api/reviews/{id}` | Update review |
| DELETE | `/api/reviews/{id}` | Delete review |
| GET | `/api/courses/{id}/reviews/aggregate` | Get course rating |
| GET | `/api/mentors/{id}/reviews/aggregate` | Get mentor rating |

### Progress

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/me/progress` | Get my progress |
| GET | `/api/courses/{id}/progress/aggregate` | Get course progress stats |
| POST | `/api/progress` | Create progress entry |
| PUT | `/api/progress/{id}` | Update progress |
| DELETE | `/api/progress/{id}` | Delete progress |

### Achievements

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/achievements` | List all achievements |
| GET | `/api/achievements/my` | Get my achievements |
| POST | `/api/achievements` | Create achievement (admin) |
| PUT | `/api/achievements/{id}` | Update achievement |
| DELETE | `/api/achievements/{id}` | Delete achievement |

### Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications` | List notifications |
| GET | `/api/notifications/unread` | Get unread count |
| PUT | `/api/notifications/{id}/read` | Mark as read |
| PUT | `/api/notifications/read-all` | Mark all as read |
| DELETE | `/api/notifications/{id}` | Delete notification |
| POST | `/api/push-notifications/register` | Register device token |
| DELETE | `/api/push-notifications/unregister` | Unregister device |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/platform` | Platform-wide analytics |
| GET | `/api/analytics/user-growth` | User growth metrics |
| GET | `/api/analytics/session-stats` | Session statistics |
| GET | `/api/analytics/payment-stats` | Payment statistics |

### Stats

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats/platform` | Platform statistics |
| GET | `/api/stats/user/{user_id}` | User statistics |
| GET | `/api/stats/mentor/{mentor_id}` | Mentor statistics |

### Health & Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Basic health check |
| GET | `/health/ready` | Readiness probe |
| GET | `/health/live` | Liveness probe |
| GET | `/metrics` | Prometheus metrics |
| GET | `/api` | API information |

### Data Export (GDPR)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/export/data?format=json\|csv` | Export all user data |
| GET | `/api/export/data/summary` | Get data summary statistics |

**Export Data Response (JSON):**
```json
{
  "export_date": "2026-03-20T12:00:00Z",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "role": "student"
  },
  "sessions": [...],
  "payments": [...],
  "reviews": [...],
  "progress": [...],
  "achievements": [...],
  "messages": [...],
  "enrollments": [...]
}
```

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message here"
}
```

### Validation Errors

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

## Rate Limiting

- **Limit:** 100 requests per hour per IP
- **Headers:**
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Time when limit resets

## Pagination

Endpoints that return lists support pagination:

```bash
GET /api/mentors?page=1&size=20
```

**Parameters:**
- `page`: Page number (default: 1)
- `size`: Items per page (default: 20, max: 100)

**Response:**

```json
{
  "items": [...],
  "total": 150,
  "page": 1,
  "size": 20,
  "pages": 8
}
```

## Interactive Documentation

### Swagger UI

```
http://localhost:8000/docs
```

Features:
- Interactive API documentation
- Try out endpoints directly
- JWT authentication support
- Request/response examples

### ReDoc

```
http://localhost:8000/redoc
```

Features:
- Clean, readable documentation
- Search functionality
- Responsive design

## WebSocket API

### Chat WebSocket

```
ws://localhost:8000/ws/chat
```

**Authentication:**
```json
{
  "type": "auth",
  "token": "your_jwt_token"
}
```

**Send Message:**
```json
{
  "type": "message",
  "recipient_id": 123,
  "content": "Hello!"
}
```

## Code Examples

### Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"username": "user", "password": "pass"}
)
token = response.json()["access_token"]

# Get current user
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/users/me",
    headers=headers
)
user = response.json()
```

### JavaScript

```javascript
// Login
const loginResponse = await fetch('/api/auth/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({username: 'user', password: 'pass'})
});
const {access_token} = await loginResponse.json();

// Get current user
const userResponse = await fetch('/api/users/me', {
  headers: {'Authorization': `Bearer ${access_token}`}
});
const user = await userResponse.json();
```

### cURL

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}'

# Get current user
curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Support

- **Email:** support@mentorhub.app
- **GitHub:** https://github.com/QuadDarv1ne/MentorHub
- **Documentation:** https://mentorhub.app/docs
