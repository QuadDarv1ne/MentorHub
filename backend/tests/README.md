# Backend Tests - MentorHub

## 📊 Статус тестов

### Общее покрытие

| Компонент | Файл тестов | Кол-во тестов | Статус |
|-----------|------------|---------------|--------|
| Authentication | `test_auth.py` | 7 | ✅ |
| Users | `test_users.py` | 14 | ✅ |
| Courses | `test_courses.py` | 18 | ✅ |
| Sessions | `test_sessions.py` | 18 | ✅ |
| Mentors | `test_mentors.py` | 15 | ✅ |
| Email Verification | `test_email_verification.py` | 15 | ✅ |
| Notifications | `test_notifications.py` | 16 | ✅ |
| Security | `test_security.py` | 20 | ✅ |
| Progress | `test_progress.py` | 2 | ✅ |
| Reviews | `test_reviews.py` | 2 | ✅ |
| Recommendations | `test_recommendations.py` | 1 | ✅ |

**Итого: 128+ тестов**

---

## 🚀 Запуск тестов

### Все тесты
```bash
cd backend
pytest
```

### Все тесты с подробным выводом
```bash
pytest -v
```

### Конкретный файл тестов
```bash
pytest tests/test_auth.py -v
```

### Конкретный тест
```bash
pytest tests/test_auth.py::TestRegistration::test_register_success -v
```

### Тесты по маркерам
```bash
pytest -m integration -v  # Интеграционные тесты
pytest -m security -v     # Security тесты
```

---

## 📊 Coverage Report

### Запуск с покрытием
```bash
# HTML отчёт
pytest --cov=app --cov-report=html

# Terminal отчёт
pytest --cov=app --cov-report=term-missing

# XML отчёт (для CI/CD)
pytest --cov=app --cov-report=xml

# Все форматы сразу
pytest --cov=app --cov-report=html --cov-report=term-missing --cov-report=xml
```

### Целевое покрытие
```bash
# Требовать минимум 80% покрытия
pytest --cov=app --cov-fail-under=80
```

### Покрытие по модулям
```bash
# Отчёт по конкретному модулю
pytest --cov=app/api/auth.py --cov-report=term-missing
pytest --cov=app/api/users.py --cov-report=term-missing
```

### Просмотр HTML отчёта
```bash
# Открыть HTML отчёт в браузере
# Linux/Mac:
open htmlcov/index.html

# Windows:
start htmlcov\index.html
```

---

## 📁 Структура тестов

```
tests/
├── conftest.py              # Pytest fixtures и конфигурация
├── test_auth.py             # Тесты аутентификации (7 тестов)
├── test_users.py            # Тесты пользователей (14 тестов)
├── test_courses.py          # Тесты курсов (18 тестов)
├── test_sessions.py         # Тесты сессий (18 тестов)
├── test_mentors.py          # Тесты менторов (15 тестов)
├── test_email_verification.py  # Тесты email (15 тестов)
├── test_notifications.py    # Тесты уведомлений (16 тестов)
├── test_security.py         # Security тесты (20 тестов)
├── test_progress.py         # Тесты прогресса (2 теста)
├── test_recommendations.py  # Тесты рекомендаций (1 тест)
├── test_reviews.py          # Тесты отзывов (2 теста)
└── test_e2e.py              # E2E тесты (временно отключены)
```

---

## 🔧 Фикстуры

### `db_session`
Создаёт изолированную сессию SQLite для каждого теста.

```python
def test_something(db_session):
    # db_session автоматически создаёт и очищает БД
    user = User(email="test@example.com")
    db_session.add(user)
    db_session.commit()
```

### `client`
Синхронный TestClient для FastAPI приложения.

```python
def test_api_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
```

### `authenticated_headers`
Готовые заголовки с авторизационным токеном.

```python
def test_protected_endpoint(client, authenticated_headers):
    response = client.get("/api/v1/users/me", headers=authenticated_headers)
    assert response.status_code == 200
```

### `sample_user_data`
Тестовые данные пользователя с валидным паролем.

```python
def test_register(client, sample_user_data):
    response = client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 201
```

### Дополнительные фикстуры
- `sample_mentor_data` - данные ментора
- `sample_course_data` - данные курса
- `sample_session_data` - данные сессии
- `create_user` - фабрика для создания пользователей

---

## 🎯 Требования к тестам

### Покрытие кода

**Цель: 80%+ покрытия**

```bash
# Проверка достижения цели
pytest --cov=app --cov-fail-under=80
```

**Минимальные требования:**
- API endpoints: 90%+
- Business logic: 80%+
- Models: 70%+
- Utils: 60%+

### Именование тестов

```python
def test_<component>_<action>_<condition>():
    # Примеры:
    def test_register_success(): ...
    def test_login_invalid_credentials(): ...
    def test_update_profile_unauthorized(): ...
```

### Структура теста (AAA Pattern)

```python
def test_example():
    # Arrange (Подготовка)
    user_data = {"email": "test@example.com", ...}
    
    # Act (Действие)
    response = client.post("/api/v1/auth/register", json=user_data)
    
    # Assert (Проверка)
    assert response.status_code == 201
    assert response.json()["email"] == user_data["email"]
```

---

## 🔐 Security тесты

### SQL Injection
```bash
pytest tests/test_security.py::TestSQLInjection -v
```

### XSS Attacks
```bash
pytest tests/test_security.py::TestXSS -v
```

### Rate Limiting
```bash
pytest tests/test_security.py::TestRateLimiting -v
```

### Security Headers
```bash
pytest tests/test_security.py::TestSecurityHeaders -v
```

---

## 🔄 CI/CD Integration

### GitHub Actions

Тесты автоматически запускаются при:
- Push в main/develop ветки
- Pull Request
- По расписанию (nightly build)

```yaml
# .github/workflows/ci-cd.yml
- name: Run tests
  run: |
    cd backend
    pytest --cov=app --cov-report=xml --cov-fail-under=80
```

### Pre-commit хуки

```bash
# Установить pre-commit
pip install pre-commit
pre-commit install

# Запустить вручную
pre-commit run pytest
```

---

## 📈 Метрики

### Покрытие по файлам

После запуска `pytest --cov=app --cov-report=term-missing`:

```
Name                            Stmts   Miss  Cover   Missing
-------------------------------------------------------------
app/api/auth.py                   120      12    90%   45-50, 78-82
app/api/users.py                  150      18    88%   102-110, 145-150
app/api/courses.py                180      25    86%   ...
app/services/auth_service.py       80       8    90%   ...
-------------------------------------------------------------
TOTAL                            1500     150    90%
```

### Трекинг покрытия

| Версия | Покрытие | Дата |
|--------|----------|------|
| 1.0.0 | 75% | 2025-11-01 |
| 1.1.0 | 80% | 2025-12-01 |
| **Цель** | **85%** | 2026-01-01 |

---

## 🐛 Отладка тестов

### Запуск с отладочным выводом
```bash
pytest -s  # Показать print() выводы
pytest -vv # Подробный вывод
```

### Постепенный запуск
```bash
# Остановиться после первой ошибки
pytest -x

# Остановиться после N ошибок
pytest -x --maxfail=3

# Запустить последний упавший тест
pytest --lf
```

### Coverage для упавших тестов
```bash
# Запустить только изменённые тесты
pytest --ff
```

---

## 📝 Best Practices

### 1. Изоляция тестов
```python
# ✅ Хорошо: каждый тест создаёт свои данные
def test_user_creation(client, sample_user_data):
    response = client.post("/api/v1/auth/register", json=sample_user_data)
    assert response.status_code == 201

# ❌ Плохо: тесты зависят друг от друга
def test_user_creation(client):
    # Использует данные из предыдущего теста
    ...
```

### 2. Использование фикстур
```python
# ✅ Хорошо: фикстуры для общих данных
def test_update_profile(client, authenticated_headers):
    response = client.put("/api/v1/users/me", json={"bio": "New"}, headers=authenticated_headers)

# ❌ Плохо: дублирование кода
def test_update_profile(client):
    # Регистрация, вход, получение токена...
    ...
```

### 3. Параметризация
```python
# ✅ Хорошо: параметризованные тесты
@pytest.mark.parametrize("role", ["student", "mentor", "admin"])
def test_user_roles(role):
    assert role in ["student", "mentor", "admin"]

# ❌ Плохо: дублирование
def test_student_role(): ...
def test_mentor_role(): ...
def test_admin_role(): ...
```

### 4. Тестирование ошибок
```python
# ✅ Хорошо: тестирование error cases
def test_login_invalid_credentials(client):
    response = client.post("/api/v1/auth/login", json={"email": "bad", "password": "wrong"})
    assert response.status_code == 401

# ❌ Плохо: только happy path
def test_login_success(client):
    # Только успешный сценарий
    ...
```

---

## 🎓 Ресурсы

- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/explanation/fixtures.html)

---

**Последнее обновление:** 2026-03-08  
**Статус:** ✅ 128+ тестов, ~80% coverage

