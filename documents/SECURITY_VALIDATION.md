# 🛡️ Безопасность и валидация MentorHub

## Обзор

Комплексная система обработки ошибок и валидации данных для повышения безопасности и надежности API.

## 🎯 Новые возможности

### 1. Централизованная обработка ошибок
### 2. Продвинутые валидаторы
### 3. Rate Limiting (уже реализован)
### 4. Стандартизированные ответы об ошибках

---

## 🚨 Обработка ошибок (Error Handlers)

### Типы обработчиков

#### HTTP Exceptions
Автоматическая обработка всех HTTP ошибок (404, 403, 401 и т.д.)

**Пример ответа:**
```json
{
  "status_code": 404,
  "message": "User not found",
  "error_code": "HTTP_404",
  "path": "/api/v1/users/999",
  "timestamp": "2025-11-24T12:00:00.000000"
}
```

#### Validation Errors
Детальная информация об ошибках валидации данных

**Пример ответа:**
```json
{
  "status_code": 422,
  "message": "Validation error",
  "error_code": "VALIDATION_ERROR",
  "detail": [
    {
      "field": "email",
      "message": "value is not a valid email address",
      "type": "value_error.email"
    },
    {
      "field": "age",
      "message": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt"
    }
  ],
  "path": "/api/v1/users",
  "timestamp": "2025-11-24T12:00:00.000000"
}
```

#### Database Errors
Обработка ошибок базы данных с защитой от утечек информации

**Пример ответа (Integrity Error):**
```json
{
  "status_code": 409,
  "message": "Database integrity error",
  "error_code": "INTEGRITY_ERROR",
  "detail": "A record with this data already exists or violates database constraints",
  "path": "/api/v1/users",
  "timestamp": "2025-11-24T12:00:00.000000"
}
```

#### General Exceptions
Отлов всех неожиданных ошибок с детальным логированием

**Production:**
```json
{
  "status_code": 500,
  "message": "Internal server error",
  "error_code": "INTERNAL_ERROR",
  "path": "/api/v1/users",
  "timestamp": "2025-11-24T12:00:00.000000"
}
```

**Development:**
```json
{
  "status_code": 500,
  "message": "division by zero",
  "error_code": "ZeroDivisionError",
  "detail": "Traceback (most recent call last):\n  File ...",
  "path": "/api/v1/users",
  "timestamp": "2025-11-24T12:00:00.000000"
}
```

### Использование в коде

```python
from app.utils.error_handlers import register_error_handlers

# В main.py
app = FastAPI()
register_error_handlers(app)
```

---

## ✅ Валидаторы (Validators)

### Email Validation

```python
from app.utils.validators import validate_email

email = validate_email("user@example.com")
# Raises HTTPException if invalid
```

**Проверки:**
- Формат RFC 5322
- Максимальная длина 254 символа
- Автоматическая нормализация (lowercase, strip)

### Phone Validation

```python
from app.utils.validators import validate_phone

phone = validate_phone("+1234567890")
# E.164 format
```

**Проверки:**
- Формат E.164 (международный стандарт)
- Удаление пробелов и дефисов
- От 2 до 15 цифр

### Username Validation

```python
from app.utils.validators import validate_username

username = validate_username("john_doe")
# Raises HTTPException if invalid
```

**Проверки:**
- 3-32 символа
- Только буквы, цифры, подчеркивания, дефисы
- Проверка зарезервированных имен (admin, root, system)

### URL Validation

```python
from app.utils.validators import validate_url

url = validate_url("https://example.com")
```

**Проверки:**
- Валидный HTTP/HTTPS URL
- Максимум 2048 символов
- Поддержка портов и путей

### Input Sanitization

```python
from app.utils.validators import sanitize_input

clean_text = sanitize_input(user_input, max_length=500)
```

**Защита от:**
- SQL Injection
- XSS (Cross-Site Scripting)
- Превышение максимальной длины

**Детектируемые паттерны:**
- SQL ключевые слова (SELECT, DROP, INSERT и т.д.)
- SQL комментарии (--, /*, #)
- HTML/JavaScript теги (<script>, <iframe>)
- Event handlers (onclick, onerror)

### Password Strength

```python
from app.utils.validators import validate_password_strength

validate_password_strength("MySecure123!")
# Raises HTTPException if weak
```

**Требования:**
- Минимум 8 символов
- Максимум 128 символов
- Хотя бы одна цифра
- Хотя бы одна буква
- Рекомендуется спецсимвол

### Pagination Validation

```python
from app.utils.validators import validate_pagination

page, limit = validate_pagination(page=1, limit=20, max_limit=100)
```

**Проверки:**
- page >= 1
- limit >= 1
- limit <= max_limit

---

## 📊 Rate Limiting

### Конфигурация

**В main.py:**
```python
from app.middleware.rate_limit import RateLimitMiddleware

app.add_middleware(
    RateLimitMiddleware,
    max_requests=100,     # Максимум запросов
    time_window=60,       # За 60 секунд
    exclude_paths=["/health", "/metrics", "/docs"]
)
```

### Заголовки ответа

Каждый ответ содержит информацию о лимитах:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 85
X-RateLimit-Reset: 1700832060
```

### Ответ при превышении лимита

**HTTP 429 Too Many Requests:**
```json
{
  "detail": "Too many requests. Please try again later."
}
```

**Headers:**
```http
Retry-After: 60
```

### Административные функции

```python
from app.middleware.rate_limit import RateLimitMiddleware

# Очистка лимита для конкретного IP
middleware.clear_ip("192.168.1.1")

# Очистка всех лимитов
middleware.clear_all()
```

---

## 🔒 Лучшие практики

### 1. Валидация пользовательского ввода

**Всегда валидируйте:**
```python
from app.utils.validators import sanitize_input, validate_email

# ❌ ПЛОХО
def create_user(email: str, bio: str):
    user = User(email=email, bio=bio)
    
# ✅ ХОРОШО
def create_user(email: str, bio: str):
    email = validate_email(email)
    bio = sanitize_input(bio, max_length=500)
    user = User(email=email, bio=bio)
```

### 2. Использование в Pydantic схемах

```python
from pydantic import BaseModel, field_validator
from app.utils.validators import validate_email, sanitize_input

class UserCreate(BaseModel):
    email: str
    bio: str
    
    @field_validator('email')
    def validate_email_field(cls, v):
        return validate_email(v)
    
    @field_validator('bio')
    def validate_bio_field(cls, v):
        return sanitize_input(v, max_length=500)
```

### 3. Обработка ошибок в эндпоинтах

```python
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

@router.post("/users")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Создание пользователя
        new_user = User(**user.dict())
        db.add(new_user)
        db.commit()
        return new_user
    except IntegrityError:
        # Автоматически обрабатывается error_handlers
        raise
```

### 4. Логирование безопасности

```python
import logging

logger = logging.getLogger(__name__)

# Логируем подозрительную активность
if suspicious_activity_detected:
    logger.warning(
        f"Suspicious activity: {activity_type} | "
        f"IP: {client_ip} | "
        f"User: {user_id}"
    )
```

---

## 🧪 Тестирование

### Тест валидаторов

```python
import pytest
from app.utils.validators import validate_email, sanitize_input
from fastapi import HTTPException

def test_email_validation():
    # Валидный email
    assert validate_email("user@example.com") == "user@example.com"
    
    # Невалидный email
    with pytest.raises(HTTPException):
        validate_email("invalid-email")

def test_sql_injection_prevention():
    # SQL injection attempt
    malicious_input = "'; DROP TABLE users; --"
    
    with pytest.raises(HTTPException):
        sanitize_input(malicious_input)
```

### Тест error handlers

```python
from fastapi.testclient import TestClient

def test_validation_error_format(client: TestClient):
    response = client.post("/api/v1/users", json={"email": "invalid"})
    
    assert response.status_code == 422
    assert "error_code" in response.json()
    assert response.json()["error_code"] == "VALIDATION_ERROR"
```

---

## 📈 Мониторинг безопасности

### Метрики для отслеживания

1. **Количество заблокированных запросов (Rate Limit)**
2. **Детектированные SQL injection попытки**
3. **Детектированные XSS попытки**
4. **Ошибки валидации по типам**
5. **IP адреса с подозрительной активностью**

### Пример Prometheus query

```promql
# Rate limit blocks
rate(mentorhub_rate_limit_blocks_total[5m])

# Validation errors
rate(mentorhub_validation_errors_total[5m])
```

---

## 🔧 Конфигурация

### Environment Variables

```bash
# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_MAX_REQUESTS=100
RATE_LIMIT_TIME_WINDOW=60

# Validation
MAX_INPUT_LENGTH=10000
STRICT_PASSWORD_VALIDATION=true

# Error Reporting
SENTRY_DSN=https://...
LOG_LEVEL=INFO
```

---

## 🆘 Troubleshooting

### Проблема: Слишком много 429 ошибок

**Решение:**
1. Увеличьте `max_requests` в Rate Limiting
2. Добавьте IP в whitelist
3. Проверьте логи на подозрительную активность

### Проблема: Валидные данные отклоняются

**Решение:**
1. Проверьте регулярные выражения в validators.py
2. Убедитесь в правильном формате данных
3. Проверьте логи для деталей ошибки

### Проблема: Утечка информации в ошибках

**Решение:**
1. Убедитесь что `ENVIRONMENT=production`
2. Проверьте что error_handlers корректно скрывают детали
3. Настройте Sentry для детального логирования

---

## 📚 Связанные документы

- [MONITORING.md](./MONITORING.md) - Мониторинг и метрики
- [HEALTH_METRICS.md](./HEALTH_METRICS.md) - Health checks
- [AUTHENTICATION.md](../AUTHENTICATION.md) - Аутентификация
