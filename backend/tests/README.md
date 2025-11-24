# Backend Tests

## Структура тестов

```
tests/
├── conftest.py          # Pytest fixtures и конфигурация
├── test_auth.py         # Тесты аутентификации (7 тестов)
├── test_progress.py     # Тесты прогресса (2 теста)
├── test_recommendations.py  # Тесты рекомендаций (1 тест)
├── test_reviews.py      # Тесты отзывов (2 теста)
└── test_e2e.py          # E2E тесты (временно отключены)
```

## Статус тестов

✅ **12 тестов проходят успешно**
- Authentication: 7/7 ✅
- Progress: 2/2 ✅
- Recommendations: 1/1 ✅
- Reviews: 2/2 ✅

⏸️ **E2E тесты временно отключены**
- Причина: Проблемы с `AsyncClient` фикстурой в `httpx`
- Планируется исправление после обновления зависимостей

## Запуск тестов

### Все тесты (без E2E)
```bash
cd backend
pytest
```

### Конкретный файл
```bash
pytest tests/test_auth.py -v
```

### С покрытием
```bash
pytest --cov=app --cov-report=html
```

### Быстрый запуск
```bash
pytest -q  # Quiet mode
```

## Фикстуры

### `db_session`
Создаёт изолированную сессию SQLite для каждого теста.

### `client`
Синхронный TestClient для FastAPI приложения.

### `async_client`  
Асинхронный клиент с ASGITransport (для E2E тестов).

### `sample_user_data`
Тестовые данные пользователя с валидным паролем.

## CI/CD

Тесты автоматически запускаются в GitHub Actions при каждом push:
- ✅ Black форматирование
- ✅ Flake8 линтинг  
- ✅ Pytest (12 тестов)
- ⏭️ Frontend тесты (после backend)

## Требования к паролям в тестах

Пароли должны содержать минимум 3 из 4:
- Заглавные буквы (A-Z)
- Строчные буквы (a-z)
- Цифры (0-9)
- Спецсимволы (!@#$%^&*...)

Пример: `TestPass123!`
