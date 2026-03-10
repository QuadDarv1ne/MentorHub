# Руководство по тестированию платёжной системы MentorHub

## Обзор

MentorHub поддерживает два способа оплаты:
1. **Stripe** - для международных платежей (карты Visa/Mastercard)
2. **СБП** - для платежей в России (Система быстрых платежей)

---

## Быстрый старт

### Запуск backend:
```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Swagger UI:
http://127.0.0.1:8000/docs

---

## Тестирование СБП (Рекомендуется для РФ)

### 1. Создание QR-кода

**Endpoint:** `POST /api/v1/payments/sbp/create-qr`

**Запрос:**
```json
{
  "amount": 5000,
  "description": "Оплата сессии",
  "session_id": 1,
  "mentor_id": 2,
  "customer_phone": "+79991234567"
}
```

**Ответ:**
```json
{
  "payment_id": 5,
  "qr_id": "sbp_qr_mock_...",
  "qr_url": "https://qr.nspk.ru/...",
  "qr_image": "data:image/png;base64,...",
  "amount": 5000.0,
  "currency": "RUB",
  "expires_at": "2025-11-24T15:45:00",
  "status": "pending"
}
```

### 2. Проверка статуса платежа

**Endpoint:** `GET /api/v1/payments/sbp/check-status/{payment_id}`

**Ответ:**
```json
{
  "payment_id": 5,
  "status": "completed",
  "amount": 5000.0,
  "sbp_status": "completed",
  "bank_name": "Сбербанк",
  "transaction_id": "sbp_txn_..."
}
```

### 3. Список банков СБП

**Endpoint:** `GET /api/v1/payments/sbp/banks`

**Ответ:**
```json
{
  "banks": [
    {"id": "100000000111", "name": "Сбербанк", "logo_url": "..."},
    {"id": "100000000004", "name": "Тинькофф Банк", "logo_url": "..."},
    {"id": "100000000015", "name": "ВТБ", "logo_url": "..."}
  ]
}
```

---

## Тестирование Stripe (Международные платежи)

### 1. Создание платёжного намерения

**Endpoint:** `POST /api/v1/payments/create-intent`

**Запрос:**
```json
{
  "amount": 5000,
  "currency": "usd",
  "description": "Session payment",
  "session_id": 1,
  "mentor_id": 2
}
```

**Ответ:**
```json
{
  "client_secret": "pi_..._secret_...",
  "payment_id": 5,
  "amount": 50.0,
  "currency": "usd"
}
```

### 2. Подтверждение платежа

**Endpoint:** `POST /api/v1/payments/confirm/{payment_id}`

**Ответ:**
```json
{
  "payment_id": 5,
  "status": "completed",
  "amount": 50.0
}
```

---

## Сравнение методов оплаты

| Характеристика | СБП | Stripe |
|----------------|-----|--------|
| Регион | 🇷🇺 Россия | 🌍 Международный |
| Валюта | RUB | USD, EUR и др. |
| Комиссия | ~0.5% | ~2.9% + $0.30 |
| Скорость | Мгновенно | 1-7 дней |
| Ввод данных карты | ❌ Не нужен | ✅ Нужен |
| Mock режим | ✅ Да | ✅ Да |

---

## Workflow тестирования

### Вариант 1: СБП (для российских пользователей)

```
1. Регистрация/вход → получаем token
2. POST /sbp/create-qr → получаем QR-код
3. Отображаем QR пользователю
4. В mock режиме - сразу completed
5. GET /sbp/check-status → проверяем статус
6. Разблокируем доступ к сессии
```

### Вариант 2: Stripe (для международных платежей)

```
1. Регистрация/вход → получаем token
2. POST /create-intent → получаем client_secret
3. Используем Stripe.js на frontend (в production)
4. В mock режиме - сразу completed
5. POST /confirm → подтверждаем
6. Разблокируем доступ к сессии
```

---

## cURL примеры

### СБП

```bash
# Авторизация
TOKEN=$(curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!@#"}' \
  | jq -r '.access_token')

# Создать QR-код СБП
curl -X POST http://127.0.0.1:8000/api/v1/payments/sbp/create-qr \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000,
    "description": "Тест СБП",
    "session_id": 1,
    "mentor_id": 2
  }'

# Проверить статус
curl -X GET http://127.0.0.1:8000/api/v1/payments/sbp/check-status/5 \
  -H "Authorization: Bearer $TOKEN"

# Список банков
curl -X GET http://127.0.0.1:8000/api/v1/payments/sbp/banks
```

### Stripe

```bash
# Создать платёж Stripe
curl -X POST http://127.0.0.1:8000/api/v1/payments/create-intent \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000,
    "currency": "usd",
    "description": "Test payment",
    "session_id": 1,
    "mentor_id": 2
  }'

# Подтвердить платёж
curl -X POST http://127.0.0.1:8000/api/v1/payments/confirm/5 \
  -H "Authorization: Bearer $TOKEN"
```

---

## История платежей

**Endpoint:** `GET /api/v1/payments/history`

```bash
curl -X GET http://127.0.0.1:8000/api/v1/payments/history \
  -H "Authorization: Bearer $TOKEN"
```

**Ответ:**
```json
[
  {
    "id": 5,
    "student_id": 1,
    "mentor_id": 2,
    "session_id": 3,
    "amount": 5000.0,
    "currency": "RUB",
    "status": "completed",
    "payment_method": "sbp",
    "transaction_id": "sbp_qr_...",
    "created_at": "2025-11-24T14:30:00Z"
  },
  {
    "id": 4,
    "amount": 50.0,
    "currency": "USD",
    "status": "completed",
    "payment_method": "stripe",
    "transaction_id": "pi_...",
    "created_at": "2025-11-24T13:00:00Z"
  }
]
```

---

## Возвраты (Refunds)

**Endpoint:** `POST /api/v1/payments/refund/{payment_id}`

```bash
curl -X POST http://127.0.0.1:8000/api/v1/payments/refund/5 \
  -H "Authorization: Bearer $TOKEN"
```

**Ответ:**
```json
{
  "payment_id": 5,
  "status": "refunded",
  "refunded_amount": 5000.0
}
```

---

## Mock режим vs Production

### Mock режим (по умолчанию)

✅ Работает без реальных API ключей  
✅ Все платежи автоматически успешны  
✅ QR-коды возвращаются тестовые  
✅ Подходит для разработки и демо

### Production режим

#### Для СБП:
```env
SBP_MERCHANT_ID=your_merchant_id
SBP_API_KEY=your_api_key
SBP_SECRET_KEY=your_secret_key
```

#### Для Stripe:
```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## Проверка работоспособности

### Health Check

```bash
curl http://127.0.0.1:8000/health
```

**Ожидаемый ответ:**
```json
{
  "status": "healthy",
  "service": "MentorHub API",
  "version": "1.0.0",
  "database": "connected",
  "timestamp": "2025-11-24T14:30:00.000000"
}
```

### Список всех эндпоинтов

Откройте Swagger UI: http://127.0.0.1:8000/docs

**Платёжные эндпоинты:**
- `POST /api/v1/payments/sbp/create-qr` - Создать QR СБП
- `GET /api/v1/payments/sbp/check-status/{id}` - Проверить статус СБП
- `GET /api/v1/payments/sbp/banks` - Список банков
- `POST /api/v1/payments/sbp/webhook` - Webhook СБП
- `POST /api/v1/payments/create-intent` - Создать Stripe платёж
- `POST /api/v1/payments/confirm/{id}` - Подтвердить Stripe
- `POST /api/v1/payments/refund/{id}` - Возврат средств
- `GET /api/v1/payments/history` - История платежей
- `POST /api/v1/payments/webhook` - Webhook Stripe

---

## Частые проблемы

### ⚠️ "requests library not installed"

**Решение:**
```bash
pip install requests
```

### ⚠️ "Stripe SDK not installed"

**Решение:**
```bash
pip install stripe
```

### ✅ В Mock режиме эти библиотеки опциональны!

---

## Логирование

Backend логирует все платёжные операции:

```
INFO: Creating SBP QR code: amount=5000, order_id=5
WARNING: MOCK MODE: SBP QR code created - sbp_qr_mock_...
INFO: SBP payment status: completed
```

---

## Рекомендации для production

1. ✅ Настройте реальные API ключи СБП/Stripe
2. ✅ Включите HTTPS
3. ✅ Настройте webhook URLs
4. ✅ Добавьте мониторинг (Sentry)
5. ✅ Настройте логирование в файлы
6. ✅ Включите rate limiting
7. ✅ Добавьте email уведомления

---

## 🎯 Готово к тестированию!

**Backend:** http://127.0.0.1:8000  
**Swagger UI:** http://127.0.0.1:8000/docs  
**Документация СБП:** `backend/SBP_API.md`  
**Документация Stripe:** `backend/PAYMENTS_API.md`

**Платформа поддерживает оба способа оплаты! 🚀**
