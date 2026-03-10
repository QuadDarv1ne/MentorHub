# Email Verification & Password Reset

## Обзор

Система email-верификации и сброса пароля для MentorHub.

## Возможности

- ✅ Отправка email с подтверждением регистрации
- ✅ Подтверждение email по токену
- ✅ Запрос сброса пароля
- ✅ Сброс пароля по токену
- ✅ HTML шаблоны писем
- ✅ Безопасное хранение токенов (24ч для verification, 1ч для reset)

## Endpoints

### 1. Отправка verification email

```http
POST /api/v1/email/send-verification
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Письмо с подтверждением отправлено"
}
```

### 2. Подтверждение email

```http
POST /api/v1/email/verify-email
Content-Type: application/json

{
  "token": "abc123..."
}
```

**Response:**
```json
{
  "message": "Email успешно подтвержден",
  "email": "user@example.com"
}
```

### 3. Запрос сброса пароля

```http
POST /api/v1/email/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Письмо для сброса пароля отправлено"
}
```

### 4. Сброс пароля

```http
POST /api/v1/email/reset-password
Content-Type: application/json

{
  "token": "xyz789...",
  "new_password": "NewSecurePass123!"
}
```

**Response:**
```json
{
  "message": "Пароль успешно изменен",
  "email": "user@example.com"
}
```

## Конфигурация SMTP

В `.env` файле настройте параметры SMTP:

```bash
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@mentorhub.com
SMTP_FROM_NAME=MentorHub
FRONTEND_URL=http://localhost:3001
```

### Gmail настройка

1. Включите 2FA для аккаунта Google
2. Создайте App Password:
   - https://myaccount.google.com/apppasswords
3. Используйте App Password в `SMTP_PASSWORD`

### Другие провайдеры

**Yandex Mail:**
```bash
SMTP_HOST=smtp.yandex.ru
SMTP_PORT=587
```

**Mail.ru:**
```bash
SMTP_HOST=smtp.mail.ru
SMTP_PORT=587
```

**SendGrid:**
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
```

## Email Templates

Шаблоны находятся в `app/utils/email.py` и включают:

1. **Verification Email** - красивый HTML с кнопкой подтверждения
2. **Password Reset Email** - красный дизайн для безопасности
3. **Session Notification** - зеленый дизайн для напоминаний

### Кастомизация шаблонов

Отредактируйте HTML в методах:
- `send_verification_email()`
- `send_password_reset_email()`
- `send_session_notification()`

## Безопасность

✅ **Токены:**
- Генерируются через `secrets.token_urlsafe(32)` (256 бит энтропии)
- Хранятся в памяти с timestamp истечения
- Автоматически удаляются после использования

✅ **Защита от перебора:**
- Не раскрываем, существует ли email в системе
- Всегда возвращаем 200 OK

✅ **Rate Limiting:**
- Middleware автоматически ограничивает запросы

⚠️ **Production:**
В продакшене используйте Redis для хранения токенов:

```python
# Вместо in-memory словарей
verification_tokens = {}
reset_tokens = {}

# Используйте Redis
redis_client.setex(f"verify:{token}", 86400, user_email)
redis_client.setex(f"reset:{token}", 3600, user_email)
```

## Интеграция с фронтендом

### Registration flow

```typescript
// 1. Регистрация
const response = await fetch('/api/v1/auth/register', {
  method: 'POST',
  body: JSON.stringify({ email, username, password })
});

// 2. Пользователь получает email
// 3. Клик по ссылке ведет на:
// http://localhost:3001/auth/verify-email?token=abc123...

// 4. Frontend отправляет подтверждение
await fetch('/api/v1/email/verify-email', {
  method: 'POST',
  body: JSON.stringify({ token })
});
```

### Password reset flow

```typescript
// 1. Запрос сброса
await fetch('/api/v1/email/forgot-password', {
  method: 'POST',
  body: JSON.stringify({ email })
});

// 2. Email с ссылкой
// http://localhost:3001/auth/reset-password?token=xyz789...

// 3. Frontend показывает форму нового пароля
await fetch('/api/v1/email/reset-password', {
  method: 'POST',
  body: JSON.stringify({ token, new_password })
});
```

## Тестирование

### Ручное тестирование

```bash
# 1. Send verification
curl -X POST http://localhost:8000/api/v1/email/send-verification \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# 2. Verify email
curl -X POST http://localhost:8000/api/v1/email/verify-email \
  -H "Content-Type: application/json" \
  -d '{"token": "TOKEN_FROM_EMAIL"}'
```

### Pytest

```python
def test_send_verification_email(client):
    response = client.post(
        "/api/v1/email/send-verification",
        json={"email": "test@test.com"}
    )
    assert response.status_code == 200
    assert "отправлено" in response.json()["message"]

def test_verify_email(client):
    # Создаем пользователя
    user = create_test_user()
    
    # Генерируем токен
    token = "test_token"
    verification_tokens[token] = {
        "email": user.email,
        "expires_at": datetime.utcnow() + timedelta(hours=24)
    }
    
    # Подтверждаем
    response = client.post(
        "/api/v1/email/verify-email",
        json={"token": token}
    )
    assert response.status_code == 200
    assert user.is_verified == True
```

## Мониторинг

Логи email отправок:

```bash
# Успешная отправка
✅ Email sent to user@example.com: Подтверждение email - MentorHub

# Ошибка
❌ Failed to send email to user@example.com: [Errno 111] Connection refused
```

## FAQ

**Q: Почему письма не отправляются?**

A: Проверьте:
1. SMTP credentials настроены в `.env`
2. Gmail App Password создан (не обычный пароль!)
3. Firewall не блокирует порт 587
4. Логи backend для деталей ошибки

**Q: Токен истек, что делать?**

A: Запросите новый через `/send-verification` или `/forgot-password`

**Q: Можно ли использовать без SMTP?**

A: Да, в dev режиме письма будут логироваться, но не отправляться. Проверьте `email_service.send_email()` - если credentials пусты, возвращает `False` без ошибки.

**Q: Production ready?**

A: Для продакшена:
1. Переместите токены в Redis
2. Используйте SendGrid/Amazon SES вместо Gmail
3. Добавьте DKIM/SPF записи для домена
4. Rate limiting на email endpoints
