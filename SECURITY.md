# 🔒 Безопасность MentorHub

Комплексная защита платформы от различных видов атак и уязвимостей.

## 📋 Содержание

1. [Обзор системы безопасности](#обзор-системы-безопасности)
2. [Защита от атак](#защита-от-атак)
3. [Аутентификация и авторизация](#аутентификация-и-авторизация)
4. [Безопасность данных](#безопасность-данных)
5. [Мониторинг и логирование](#мониторинг-и-логирование)
6. [Конфигурация](#конфигурация)

---

## 🛡️ Обзор системы безопасности

MentorHub использует многоуровневую систему защиты:

### Уровни защиты

1. **Frontend Security**
   - Route Guards (защита страниц)
   - JWT token validation
   - Automatic redirects для неавторизованных пользователей
   - HTTPS only в production

2. **Backend Security**
   - Advanced Security Middleware
   - Input sanitization и validation
   - SQL injection protection
   - XSS protection
   - CSRF protection
   - Rate limiting
   - Brute-force protection

3. **Database Security**
   - Password hashing (bcrypt)
   - Prepared statements (SQLAlchemy ORM)
   - Encrypted sensitive data

4. **Network Security**
   - CORS configuration
   - Security headers
   - TLS/SSL encryption

---

## 🚫 Защита от атак

### 1. SQL Injection Protection

**Механизмы защиты:**
- SQLAlchemy ORM (prepared statements)
- Pattern detection в middleware
- Input sanitization

```python
# Детектирование SQL injection паттернов
SQL_PATTERNS = [
    r"(\bunion\b.*\bselect\b)",
    r"(\bor\b\s+\d+\s*=\s*\d+)",
    r"(\bdrop\b\s+\btable\b)",
    r"(\bexec\b\s*\()",
    # ... и другие
]
```

**Что блокируется:**
- `UNION SELECT` атаки
- Boolean-based blind SQL injection
- Time-based SQL injection
- `DROP TABLE` и другие DDL команды

### 2. XSS (Cross-Site Scripting) Protection

**Механизмы защиты:**
- HTML entity escaping
- Script tag detection
- Content-Security-Policy headers
- Input sanitization

```python
# Паттерны XSS
XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"onerror\s*=",
    r"onload\s*=",
    # ... и другие
]
```

**Что блокируется:**
- `<script>` tags
- Event handlers (`onerror`, `onload`)
- JavaScript в URL (`javascript:`)
- Inline event attributes

### 3. CSRF (Cross-Site Request Forgery) Protection

**Механизмы защиты:**
- CSRF tokens для всех state-changing операций
- Token validation
- SameSite cookies
- Origin checking

```python
# Использование CSRF protection
from app.utils.security import csrf_protection

# Генерация токена
token = csrf_protection.generate_token(user_id=1)

# Валидация токена
is_valid = csrf_protection.validate_token(token, user_id=1)
```

### 4. Brute-Force Protection

**Механизмы защиты:**
- Ограничение попыток входа (5 попыток)
- Временная блокировка (15 минут)
- Rate limiting
- IP-based tracking

```python
# Пример защиты от brute-force
if brute_force_protection.is_locked(email):
    remaining = brute_force_protection.get_lockout_time_remaining(email)
    raise HTTPException(
        status_code=429,
        detail=f"Слишком много попыток. Подождите {remaining} секунд"
    )
```

**Настройки:**
- Максимум попыток: `5`
- Длительность блокировки: `900 секунд (15 минут)`
- Автоматическая очистка: `каждый час`

### 5. Clickjacking Protection

**Механизмы защиты:**
- `X-Frame-Options: DENY` header
- `Content-Security-Policy: frame-ancestors 'none'`

### 6. Directory Traversal Protection

**Механизмы защиты:**
- Path traversal detection
- Блокировка `../` последовательностей
- Whitelist разрешенных путей

---

## 🔐 Аутентификация и авторизация

### JWT Authentication

**Характеристики:**
- Алгоритм: `HS256`
- Access token lifetime: `60 минут`
- Refresh token lifetime: `7 дней`
- Автоматическое обновление токенов

**Структура токена:**
```json
{
  "sub": "user_id",
  "email": "user@example.com",
  "role": "user",
  "exp": 1234567890,
  "iat": 1234567890
}
```

### Password Security

**Требования к паролям:**
- Минимум 8 символов
- Максимум 128 символов
- Заглавные и строчные буквы
- Цифры
- Специальные символы

**Оценка силы пароля:**
- Слабый (0-40): недопустимо
- Средний (40-70): допустимо
- Сильный (70-90): рекомендуется
- Очень сильный (90-100): отлично

**Хеширование:**
- Алгоритм: `bcrypt`
- Work factor: `12` (автоматически)
- Уникальная соль для каждого пароля

### Role-Based Access Control (RBAC)

**Роли пользователей:**
- `student` - базовая роль
- `mentor` - роль ментора
- `admin` - административная роль

**Пример проверки прав:**
```python
from app.dependencies import get_current_user, require_role

@router.get("/admin/users")
async def get_users(
    current_user: User = Depends(require_role(UserRole.ADMIN))
):
    # Только администраторы
    pass
```

---

## 💾 Безопасность данных

### Хранение чувствительных данных

**Шифрование:**
- Пароли: `bcrypt hashing`
- API ключи: `SHA-256 hashing`
- Платёжные данные: не хранятся (используются токены)

### Санитизация входных данных

**Email санитизация:**
```python
sanitized_email = sanitize_email(user_input)
# Результат: lowercase, trimmed, validated
```

**Username санитизация:**
```python
sanitized_username = sanitize_username(user_input)
# Разрешены: a-z, A-Z, 0-9, _, -
```

**Общая санитизация:**
```python
sanitized_text = sanitize_string(user_input)
# HTML entities escaped, dangerous chars removed
```

### Валидация данных

**Pydantic schemas:**
```python
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
```

---

## 📊 Мониторинг и логирование

### Security Logging

**Что логируется:**
- Неудачные попытки входа
- Блокировки аккаунтов
- SQL injection попытки
- XSS попытки
- Подозрительные запросы
- Rate limit violations

**Формат логов:**
```
2024-01-15 10:30:45 - security - WARNING - SQL injection attempt detected from IP: 192.168.1.100
2024-01-15 10:31:00 - security - WARNING - Account locked due to multiple failed attempts: user@example.com
```

### Sentry Integration

**Production monitoring:**
```python
if SENTRY_AVAILABLE and settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1,
    )
```

---

## ⚙️ Конфигурация

### Environment Variables

```bash
# JWT Settings
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Security Settings
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
CORS_ORIGINS=http://localhost:3001,https://yourdomain.com
ENVIRONMENT=production

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### Security Headers

**Автоматически устанавливаемые заголовки:**

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### Rate Limiting Configuration

**По умолчанию:**
- Глобальный лимит: `60 запросов/минуту` на IP
- Login endpoint: `5 попыток/15 минут`
- Register endpoint: `3 регистрации/час`

---

## 🧪 Тестирование безопасности

### Ручное тестирование

**SQL Injection:**
```bash
# Попытка SQL injection
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com OR 1=1--", "password": "test"}'

# Ожидаемый результат: 400 Bad Request
```

**XSS:**
```bash
# Попытка XSS атаки
curl -X POST http://localhost:8000/api/v1/users/update \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"full_name": "<script>alert(\"XSS\")</script>"}'

# Ожидаемый результат: 400 Bad Request или sanitized input
```

**Brute-Force:**
```bash
# 6 неудачных попыток входа
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/v1/auth/login \
    -d '{"email": "test@test.com", "password": "wrong"}'
done

# Ожидаемый результат: 429 Too Many Requests на 6-й попытке
```

---

## 📚 Best Practices

### Для разработчиков

1. **Всегда используйте параметризованные запросы**
   ```python
   # ✅ Правильно
   user = db.query(User).filter(User.email == email).first()
   
   # ❌ Неправильно
   user = db.execute(f"SELECT * FROM users WHERE email = '{email}'")
   ```

2. **Санитизируйте все пользовательские данные**
   ```python
   from app.utils.sanitization import sanitize_string
   
   clean_input = sanitize_string(user_input)
   ```

3. **Проверяйте права доступа на каждом endpoint**
   ```python
   @router.get("/admin/data")
   async def get_admin_data(
       current_user: User = Depends(require_role(UserRole.ADMIN))
   ):
       pass
   ```

4. **Используйте HTTPS в production**
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
   }
   ```

### Для пользователей

1. **Используйте сильные пароли**
   - Минимум 8 символов
   - Комбинация букв, цифр, спецсимволов
   - Не используйте распространённые пароли

2. **Включите 2FA (когда станет доступно)**

3. **Не делитесь токенами доступа**

4. **Регулярно меняйте пароль**

---

## 🆘 Reporting Security Issues

Если вы обнаружили уязвимость в системе безопасности:

1. **НЕ создавайте публичный issue**
2. Отправьте email: `security@mentorhub.com`
3. Укажите:
   - Описание уязвимости
   - Шаги для воспроизведения
   - Потенциальное влияние
   - Предложения по исправлению (опционально)

Мы ответим в течение 48 часов и исправим критические уязвимости в течение 7 дней.

---

## 📖 Дополнительные ресурсы

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

---

**Последнее обновление:** 2024-01-15  
**Версия документа:** 1.0
