# Настройка Redis для Render

## Проблема

При деплое на Render вы можете увидеть в логах:

```
WARNING:app.services.cache:⚠️ Redis not available, using memory cache: Error -2 connecting to redis:6379. Name does not resolve.
```

Это означает, что Redis сервис не подключён или URL указан неверно.

## Решение

### Вариант 1: Render Redis (Рекомендуется)

1. **Создайте Redis сервис в Render:**
   - Зайдите в [Render Dashboard](https://dashboard.render.com/)
   - Нажмите **New** → **Redis**
   - Выберите тариф (бесплатный `Free` для тестирования)
   - Дайте имя (например, `mentorhub-redis`)
   - Нажмите **Create Database**

2. **Получите Redis URL:**
   - После создания зайдите в настройки Redis сервиса
   - Найдите **Internal Database URL** или **External Database URL**
   - Скопируйте URL (выглядит как: `redis://user:password@host:port/db`)

3. **Добавьте переменную окружения в Backend сервис:**
   - Зайдите в настройки вашего backend сервиса на Render
   - Перейдите в раздел **Environment**
   - Добавьте переменную:
     ```
     Key: REDIS_URL
     Value: redis://user:password@host:port/db
     ```
   - Нажмите **Save Changes**

4. **Перезапустите сервис:**
   - В настройках backend нажмите **Manual Deploy** или **Restart**

### Вариант 2: Redis от сторонних провайдеров

Если не хотите использовать Render Redis, можно подключить внешний:

#### Upstash Redis (Бесплатно, serverless)

1. Зарегистрируйтесь на [Upstash](https://upstash.com/)
2. Создайте новый Redis кластер
3. Скопируйте **REST URL** или **TCP URL**
4. Добавьте в Environment переменную `REDIS_URL`

#### Redis Cloud

1. Зарегистрируйтесь на [Redis Cloud](https://redis.com/try-free/)
2. Создайте бесплатную базу данных
3. Скопируйте **Public endpoint**
4. Добавьте в Environment переменную `REDIS_URL`

## Проверка подключения

После настройки проверьте логи:

```
✅ Redis client initialized with URL: redis://***:***@host:port/0
INFO: Redis cache enabled
```

Если видите это — Redis подключён успешно!

## Fallback режим

Если Redis недоступен, MentorHub автоматически переключается на **in-memory cache**. 

**Важно:** В production всегда используйте Redis, потому что:
- In-memory cache не работает между репликами backend
- Кеш сбрасывается при перезапуске контейнера
- Нет возможности масштабирования

## Переменные окружения

| Переменная | Описание | Пример |
|------------|----------|--------|
| `REDIS_URL` | Полный URL подключения | `redis://user:pass@host:6379/0` |
| `REDIS_HOST` | Хост Redis (если не используете URL) | `redis` |
| `REDIS_PORT` | Порт Redis | `6379` |
| `REDIS_DB` | Номер базы данных | `0` |

## Troubleshooting

### Ошибка: "Name does not resolve"

**Причина:** Используется hostname `redis`, который недоступен в Render

**Решение:** Используйте полный `REDIS_URL` из панели Render

### Ошибка: "Authentication failed"

**Причина:** Неверный пароль или URL

**Решение:** 
1. Проверьте `REDIS_URL` в панели Render
2. Убедитесь, что скопировали полный URL с паролем
3. Перезапустите сервис

### Ошибка: "Connection refused"

**Причина:** Redis сервис не запущен или недоступен

**Решение:**
1. Проверьте статус Redis сервиса в панели Render
2. Убедитесь, что используете **Internal Database URL** для сервисов в той же сети Render
3. Проверьте firewall настройки

## Стоимость

| Провайдер | Тариф | Память | Цена |
|-----------|-------|--------|------|
| Render | Free | 25 MB | $0/мес |
| Render | Starter | 256 MB | $7/мес |
| Upstash | Free | 256 MB | $0/мес |
| Redis Cloud | Free | 30 MB | $0/мес |

## Рекомендации

1. **Для разработки:** Используйте бесплатный тариф Render или Upstash
2. **Для production:** Upgrade до платного тарифа для большей памяти
3. **Мониторинг:** Настройте алерты при 80% использовании памяти
4. **Бэкапы:** Render автоматически делает бэкапы
