# Backend Services Documentation

## Overview

The backend provides various services to support the MentorHub platform functionality.

## Services

### Email Service (`services/email.py`)

Handles email notifications to users.

**Methods:**
- `send_email(to_email, subject, body, html=False)` - Send generic email
- `send_welcome_email(email, name)` - Welcome new users
- `send_session_confirmation(email, topic, time)` - Confirm session booking
- `send_session_reminder(email, topic, link, time_until)` - Remind about upcoming session

**Configuration:**
Required environment variables:
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@mentorhub.com
```

**Usage:**
```python
from app.services.email import email_service

email_service.send_welcome_email('user@example.com', 'John Doe')
```

### Notification Service (`services/notifications.py`)

Unified notification system supporting multiple channels.

**Notification Types:**
- `welcome` - New user registration
- `session_confirmed` - Session booking confirmed
- `session_reminder` - Upcoming session reminder
- `session_cancelled` - Session cancellation
- `new_message` - New message received
- `payment_received` - Payment processed

**Usage:**
```python
from app.services.notifications import notification_service

await notification_service.send_notification(
    user_email='user@example.com',
    notification_type='session_confirmed',
    data={
        'topic': 'React Hooks',
        'scheduled_time': '2024-02-20 15:00'
    },
    channels=['email']
)
```

### Cache Service (`services/cache.py`)

Caching layer with Redis support (falls back to memory cache).

**Methods:**
- `get(key)` - Get cached value
- `set(key, value, ttl=3600)` - Cache value with TTL
- `delete(key)` - Remove from cache
- `clear()` - Clear all cache
- `exists(key)` - Check if key exists

**Decorator:**
```python
from app.services.cache import cached

@cached(ttl=600, key_prefix="user")
def get_user(user_id: int):
    return db.query(User).filter(User.id == user_id).first()
```

**Configuration:**
```env
REDIS_URL=redis://localhost:6379/0
```

## Middleware

### Rate Limiting (`middleware/rate_limit.py`)

Prevents API abuse with token bucket algorithm.

**Configuration:**
```python
from app.middleware.rate_limit import RateLimitMiddleware

app.add_middleware(
    RateLimitMiddleware,
    max_requests=100,      # Max requests
    time_window=60,        # Per 60 seconds
    exclude_paths=['/health', '/docs']
)
```

**Response Headers:**
- `X-RateLimit-Limit` - Maximum requests allowed
- `X-RateLimit-Remaining` - Requests remaining
- `X-RateLimit-Reset` - Timestamp when limit resets

**Error Response (429):**
```json
{
  "status_code": 429,
  "message": "Too many requests. Please try again later."
}
```

## API Endpoints

### Statistics (`/api/v1/stats`)

Platform and user statistics endpoints.

#### GET `/stats/platform`
Get overall platform statistics (public, cached 5 minutes).

**Response:**
```json
{
  "total_users": 1000,
  "total_mentors": 150,
  "total_students": 850,
  "total_sessions": 2500,
  "platform_name": "MentorHub",
  "version": "1.0.0"
}
```

#### GET `/stats/user` 🔒
Get current user's statistics (requires authentication).

**Response:**
```json
{
  "user_id": 1,
  "email": "user@example.com",
  "is_mentor": true,
  "created_at": "2024-01-01T00:00:00",
  "mentor_stats": {
    "total_sessions": 50,
    "completed_sessions": 45
  }
}
```

#### GET `/stats/dashboard` 🔒
Get dashboard statistics for current user (requires authentication).

**Response:**
```json
{
  "total_courses": 5,
  "in_progress": 2,
  "completed": 3,
  "total_sessions": 10,
  "upcoming_sessions": 2,
  "completed_sessions": 8,
  "total_reviews": 5,
  "average_rating": 4.5
}
```

## Error Handling

All services include comprehensive error handling and logging.

**Example:**
```python
try:
    result = email_service.send_email(...)
    if result:
        logger.info("Email sent successfully")
    else:
        logger.warning("Email sending failed")
except Exception as e:
    logger.error(f"Email error: {e}")
```

## Logging

All services use Python's logging module:

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Service initialized")
logger.warning("Service degraded")
logger.error("Service failed", exc_info=True)
```

Log levels:
- `INFO` - Normal operations
- `WARNING` - Degraded service or configuration issues
- `ERROR` - Service failures
- `DEBUG` - Detailed debugging information

## Best Practices

1. **Always use services through dependency injection:**
```python
from app.services.email import email_service

# In your route handler
email_service.send_email(...)
```

2. **Cache expensive operations:**
```python
@cached(ttl=600)
def expensive_query():
    return db.query(...).all()
```

3. **Handle service failures gracefully:**
```python
try:
    email_service.send_email(...)
except Exception as e:
    # Log error but don't fail the request
    logger.error(f"Email failed: {e}")
    # Continue with success response
```

4. **Use async/await for I/O operations:**
```python
async def send_notification(...):
    await notification_service.send_notification(...)
```

5. **Monitor rate limits:**
```python
# Check headers in response
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

## Environment Variables

Required configuration:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost/mentorhub

# Redis (optional, falls back to memory)
REDIS_URL=redis://localhost:6379/0

# Email (optional, logs if not configured)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@mentorhub.com

# Security
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

## Testing

Test services in isolation:

```python
from app.services.cache import cache_service

def test_cache_service():
    # Set value
    cache_service.set('test_key', {'data': 'value'}, ttl=60)
    
    # Get value
    result = cache_service.get('test_key')
    assert result == {'data': 'value'}
    
    # Delete value
    cache_service.delete('test_key')
    assert cache_service.get('test_key') is None
```

## Performance

- **Caching** reduces database load by 70-90%
- **Rate limiting** prevents abuse and ensures fair resource allocation
- **Async operations** improve concurrency and response times
- **Connection pooling** optimizes database connections

## Security

- Rate limiting prevents brute force attacks
- Email service validates recipients
- Cache service sanitizes keys
- All services log security events

## Monitoring

Monitor service health:

```python
# Check service availability
GET /health

# Check readiness (Kubernetes)
GET /ready
```

Services include health checks for:
- Database connectivity
- Redis connectivity (if configured)
- SMTP connectivity (if configured)
