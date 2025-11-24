# СБП API - Система быстрых платежей

## Обзор

Полная интеграция с СБП для приёма платежей от российских пользователей через QR-коды.

## Преимущества СБП

- ✅ **Без комиссий** для клиентов
- ✅ **Мгновенные переводы** 24/7
- ✅ **Все российские банки** (100+ банков)
- ✅ **Простая оплата** через QR-код в приложении банка
- ✅ **Высокая безопасность** - сертифицировано ЦБ РФ

---

## Эндпоинты

### 1. Создание QR-кода для оплаты

```http
POST /api/v1/payments/sbp/create-qr
Authorization: Bearer <token>
Content-Type: application/json

{
  "amount": 5000,
  "description": "Оплата сессии с ментором",
  "session_id": 1,
  "mentor_id": 2,
  "customer_phone": "+79991234567"
}
```

**Ответ:**
```json
{
  "payment_id": 5,
  "qr_id": "sbp_qr_abc123xyz",
  "qr_url": "https://qr.nspk.ru/sbp_qr_abc123xyz",
  "qr_image": "data:image/png;base64,iVBORw0KG...",
  "amount": 5000.0,
  "currency": "RUB",
  "expires_at": "2025-11-24T15:45:00",
  "status": "pending"
}
```

**Описание:**
- Создаёт QR-код для оплаты через СБП
- QR-код действителен 15 минут (по умолчанию)
- Клиент сканирует QR в приложении своего банка
- `qr_image` - base64 изображение QR-кода для отображения

---

### 2. Проверка статуса платежа

```http
GET /api/v1/payments/sbp/check-status/{payment_id}
Authorization: Bearer <token>
```

**Ответ:**
```json
{
  "payment_id": 5,
  "status": "completed",
  "amount": 5000.0,
  "sbp_status": "completed",
  "bank_name": "Сбербанк",
  "transaction_id": "sbp_txn_xyz789"
}
```

**Статусы:**
- `pending` - Ожидает оплаты
- `completed` - Оплачено
- `failed` - Не удалось
- `expired` - Время истекло

---

### 3. Список банков СБП

```http
GET /api/v1/payments/sbp/banks
```

**Ответ:**
```json
{
  "banks": [
    {
      "id": "100000000111",
      "name": "Сбербанк",
      "logo_url": "https://example.com/sber.png"
    },
    {
      "id": "100000000004",
      "name": "Тинькофф Банк",
      "logo_url": "https://example.com/tinkoff.png"
    },
    {
      "id": "100000000015",
      "name": "ВТБ",
      "logo_url": "https://example.com/vtb.png"
    }
  ]
}
```

**Описание:** Возвращает список банков для отображения пользователю.

---

### 4. Webhook от СБП

```http
POST /api/v1/payments/sbp/webhook
Content-Type: application/json
X-SBP-Signature: <signature>

{
  "event_type": "payment.completed",
  "qr_id": "sbp_qr_abc123xyz",
  "amount": 5000,
  "transaction_id": "sbp_txn_xyz789",
  "bank_name": "Сбербанк"
}
```

**Ответ:**
```json
{
  "status": "success"
}
```

---

## Конфигурация

Добавьте в `backend/.env`:

```env
# СБП (Система быстрых платежей)
SBP_MERCHANT_ID=your_merchant_id
SBP_API_KEY=your_api_key
SBP_SECRET_KEY=your_secret_key
SBP_API_URL=https://api.sbp.ru/v1
```

**Mock режим:** Если СБП не настроен, API работает в режиме mock с тестовыми QR-кодами.

---

## Workflow оплаты через СБП

```
1. Клиент нажимает "Оплатить через СБП"
   ↓
2. Backend создаёт QR-код (POST /sbp/create-qr)
   ↓
3. Frontend отображает QR-код пользователю
   ↓
4. Пользователь сканирует QR в приложении банка
   ↓
5. Пользователь подтверждает оплату в банке
   ↓
6. СБП отправляет webhook на backend
   ↓
7. Backend обновляет статус платежа → "completed"
   ↓
8. Frontend периодически проверяет статус (GET /sbp/check-status)
   ↓
9. Показывает успех и разблокирует сессию
```

---

## Тестирование

### Swagger UI
1. Откройте http://127.0.0.1:8000/docs
2. Авторизуйтесь с токеном
3. Используйте `POST /api/v1/payments/sbp/create-qr`
4. Получите QR-код и `payment_id`
5. Проверьте статус через `GET /api/v1/payments/sbp/check-status/{payment_id}`

### cURL примеры

**Создать QR-код:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/payments/sbp/create-qr" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 5000,
    "description": "Тестовый платёж",
    "session_id": 1,
    "mentor_id": 2
  }'
```

**Проверить статус:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/payments/sbp/check-status/5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Список банков:**
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/payments/sbp/banks"
```

---

## Frontend интеграция

### React/Next.js пример

```typescript
// 1. Создание QR-кода
const createSBPPayment = async (sessionId: number, mentorId: number, amount: number) => {
  const response = await fetch('/api/v1/payments/sbp/create-qr', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      amount,
      description: 'Оплата сессии с ментором',
      session_id: sessionId,
      mentor_id: mentorId,
    })
  });
  
  const data = await response.json();
  return data; // { payment_id, qr_image, qr_url, ... }
};

// 2. Отображение QR-кода
const SBPPaymentComponent = ({ qrImage, qrUrl }: { qrImage: string, qrUrl: string }) => (
  <div className="sbp-payment">
    <h3>Оплата через СБП</h3>
    <img src={qrImage} alt="QR-код для оплаты" />
    <p>Отсканируйте QR-код в приложении вашего банка</p>
    <a href={qrUrl} target="_blank">Открыть в приложении банка</a>
  </div>
);

// 3. Проверка статуса (polling)
const checkPaymentStatus = async (paymentId: number) => {
  const interval = setInterval(async () => {
    const response = await fetch(`/api/v1/payments/sbp/check-status/${paymentId}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    
    const data = await response.json();
    
    if (data.status === 'completed') {
      clearInterval(interval);
      // Показать успех
      showSuccess('Платёж успешно завершён!');
    } else if (data.status === 'failed' || data.status === 'expired') {
      clearInterval(interval);
      // Показать ошибку
      showError('Платёж не удался');
    }
  }, 3000); // Проверяем каждые 3 секунды
  
  // Останавливаем через 5 минут
  setTimeout(() => clearInterval(interval), 300000);
};
```

---

## Безопасность

- ✅ Все эндпоинты требуют JWT авторизацию (кроме списка банков)
- ✅ Проверка подписи webhook от СБП
- ✅ Валидация существования сессии и ментора
- ✅ Пользователь видит только свои платежи
- ✅ QR-коды имеют ограниченный срок действия (TTL)

---

## Обработка ошибок

| Код | Описание |
|-----|----------|
| `404` | Платёж/сессия/ментор не найден |
| `403` | Доступ запрещён (не ваш платёж) |
| `400` | Невалидные данные или QR-код не найден |
| `503` | Ошибка СБП API |

---

## Mock режим для разработки

Когда СБП не настроен:
- `create-qr` возвращает тестовый QR-код
- `check-status` автоматически помечает как `completed` через несколько секунд
- `banks` возвращает список популярных банков
- Все операции логируются с пометкой "MOCK MODE"

**Это позволяет разрабатывать и тестировать без реального подключения к СБП.**

---

## Сравнение с другими методами оплаты

| Характеристика | СБП | Stripe | Банковская карта |
|----------------|-----|--------|------------------|
| Комиссия клиенту | 0% | 0% | ~2-3% |
| Комиссия мерчанту | ~0.4-0.7% | ~2.9% + 30₽ | ~2-3% |
| Скорость зачисления | Мгновенно | 1-7 дней | 1-3 дня |
| Поддержка в РФ | ✅ Все банки | ⚠️ Ограничено | ✅ Да |
| Возвраты | ✅ Да | ✅ Да | ✅ Да |
| Регулирование | ЦБ РФ | Международное | ЦБ РФ |

---

## FAQ

**Q: Нужно ли пользователю вводить данные карты?**  
A: Нет, оплата проходит через банковское приложение без ввода данных.

**Q: Сколько времени действует QR-код?**  
A: По умолчанию 15 минут, можно настроить при создании.

**Q: Какие банки поддерживают СБП?**  
A: Более 100 банков РФ, включая Сбербанк, Тинькофф, ВТБ, Альфа-Банк и др.

**Q: Можно ли сделать возврат?**  
A: Да, используйте эндпоинт `/api/v1/payments/refund/{payment_id}`

**Q: Работает ли СБП для юридических лиц?**  
A: Да, СБП поддерживает как физические, так и юридические лица.

---

## Получение доступа к СБП

1. Зарегистрируйтесь как мерчант в любом банке-участнике СБП
2. Получите `MERCHANT_ID`, `API_KEY`, `SECRET_KEY`
3. Добавьте ключи в `.env`
4. Настройте webhook URL в личном кабинете СБП
5. Перезапустите backend

**Рекомендуемые банки для подключения:**
- Сбербанк Бизнес
- Тинькофф Бизнес
- Модульбанк
- Точка Банк

---

## Поддержка

**Документация СБП:** https://sbp.nspk.ru/  
**Swagger UI:** http://127.0.0.1:8000/docs  
**Логи:** Backend консоль или `backend/logs/app.log`

---

## ✅ Готово к использованию!

СБП интеграция полностью реализована и готова к тестированию в mock режиме.
