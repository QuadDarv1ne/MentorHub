# Платёжный API с интеграцией Stripe

## Обзор

Полностью интегрированная система платежей с поддержкой Stripe для обработки транзакций.

## Эндпоинты

### 1. Создание платёжного намерения
```http
POST /api/v1/payments/create-intent
Authorization: Bearer <token>
Content-Type: application/json

{
  "amount": 5000,
  "currency": "usd",
  "description": "Оплата сессии",
  "session_id": 1,
  "mentor_id": 2
}
```

**Ответ:**
```json
{
  "client_secret": "pi_xxxxxxxxxxxxx_secret_xxxxxxxxxxxx",
  "payment_id": 5,
  "amount": 50.0,
  "currency": "usd"
}
```

**Описание:** Создаёт Payment Intent в Stripe и возвращает `client_secret` для завершения оплаты на клиенте.

---

### 2. Подтверждение платежа
```http
POST /api/v1/payments/confirm/{payment_id}
Authorization: Bearer <token>
```

**Ответ:**
```json
{
  "payment_id": 5,
  "status": "completed",
  "amount": 50.0
}
```

**Описание:** Проверяет статус платежа в Stripe и обновляет локальную запись.

---

### 3. Возврат платежа
```http
POST /api/v1/payments/refund/{payment_id}
Authorization: Bearer <token>
```

**Ответ:**
```json
{
  "payment_id": 5,
  "status": "refunded",
  "refunded_amount": 50.0
}
```

**Описание:** Создаёт возврат в Stripe (только для менторов/администраторов).

---

### 4. История платежей
```http
GET /api/v1/payments/history?skip=0&limit=20
Authorization: Bearer <token>
```

**Ответ:**
```json
[
  {
    "id": 5,
    "student_id": 1,
    "mentor_id": 2,
    "session_id": 3,
    "amount": 50.0,
    "currency": "usd",
    "status": "completed",
    "payment_method": "stripe",
    "transaction_id": "pi_xxxxxxxxxxxxx",
    "created_at": "2025-11-24T14:30:00Z",
    "updated_at": "2025-11-24T14:31:00Z"
  }
]
```

**Описание:** Возвращает список платежей текущего пользователя.

---

### 5. Webhook от Stripe
```http
POST /api/v1/payments/webhook
Content-Type: application/json
Stripe-Signature: <signature>

{
  "type": "payment_intent.succeeded",
  "data": {
    "object": { ... }
  }
}
```

**Ответ:**
```json
{
  "status": "success"
}
```

**Описание:** Обрабатывает webhook-события от Stripe (автоматическое обновление статуса платежей).

---

## Статусы платежей

| Статус | Описание |
|--------|----------|
| `pending` | Платёж создан, ожидает подтверждения |
| `completed` | Платёж успешно завершён |
| `failed` | Платёж не удался |
| `refunded` | Средства возвращены |

---

## Конфигурация

Добавьте в `.env`:

```env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

**Mock режим:** Если Stripe SDK не установлен или ключи не настроены, API работает в режиме mock с тестовыми данными.

---

## Установка Stripe SDK

```bash
pip install stripe
```

---

## Тестирование

### Swagger UI
Перейдите на http://127.0.0.1:8000/docs для интерактивного тестирования.

### cURL примеры

**Создать платёж:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/payments/create-intent" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000,
    "currency": "usd",
    "description": "Test payment",
    "session_id": 1,
    "mentor_id": 2
  }'
```

**Подтвердить платёж:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/payments/confirm/5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Обработка ошибок

| Код | Описание |
|-----|----------|
| `404` | Платёж/сессия/ментор не найден |
| `403` | Доступ запрещён (не ваш платёж) |
| `400` | Невалидные данные или неверный статус |
| `503` | Ошибка Stripe API |

---

## Workflow платежа

1. **Клиент**: Запрашивает `create-intent` → получает `client_secret`
2. **Клиент**: Использует Stripe.js для подтверждения платежа с `client_secret`
3. **Stripe**: Обрабатывает платёж и отправляет webhook на сервер
4. **Сервер**: Получает webhook → обновляет статус платежа в БД
5. **Клиент**: Опционально вызывает `confirm` для проверки статуса

---

## Безопасность

- ✅ Все платёжные эндпоинты требуют аутентификацию
- ✅ Проверка подписи webhook от Stripe
- ✅ Проверка прав доступа (пользователь может видеть только свои платежи)
- ✅ Менторы могут делать возвраты только для своих сессий
- ✅ Логирование всех платёжных операций

---

## Mock режим для разработки

Когда Stripe не настроен:
- `create-intent` возвращает тестовый `client_secret`
- `confirm` автоматически помечает платёж как `completed`
- `refund` успешно обрабатывается без реального возврата
- Все операции логируются с пометкой "MOCK MODE"

Это позволяет тестировать платформу без реальной интеграции Stripe.
