# CI/CD Документация

## 📋 Обзор

MentorHub использует GitHub Actions для автоматизации тестирования и деплоя.

## 🔄 Workflow файлы

### 1. Backend Tests (`.github/workflows/backend-tests.yml`)

**Запускается при:**
- Push в ветки `main`, `dev`
- Pull Request в эти ветки
- Изменения в папке `backend/`

**Что делает:**
1. Поднимает PostgreSQL и Redis для тестов
2. Устанавливает Python 3.11
3. Устанавливает зависимости
4. Запускает тесты с coverage
5. Загружает отчёт в Codecov
6. Сохраняет артефакты

**Переменные окружения для тестов:**
```yaml
DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_db
REDIS_URL: redis://localhost:6379/0
SECRET_KEY: test-secret-key-for-ci-cd-pipeline
ENVIRONMENT: testing
```

---

### 2. Frontend Tests (`.github/workflows/frontend-tests.yml`)

**Запускается при:**
- Push в ветки `main`, `dev`
- Pull Request в эти ветки
- Изменения в папке `frontend/`

**Что делает:**
1. Устанавливает Node.js 18
2. Устанавливает зависимости
3. Запускает TypeScript check
4. Запускает ESLint
5. Запускает тесты с coverage
6. Собирает проект
7. Загружает отчёт в Codecov

---

### 3. CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

**Полный pipeline для production:**

**Jobs:**
1. **Code Quality** - проверка кода (Black, isort, flake8, ESLint, Prettier)
2. **Backend Tests** - тесты backend с coverage
3. **Frontend Tests** - тесты frontend с coverage
4. **Security Scan** - сканирование уязвимостей (Trivy, Bandit, npm audit)
5. **Docker Build** - сборка Docker образа
6. **Deploy Staging** - деплой на staging (при merge в `develop`)
7. **Deploy Production** - деплой на production (при merge в `main`)
8. **Notify** - уведомления о результатах

---

## 🚀 Настройка

### 1. Codecov (опционально)

Для загрузки отчётов о покрытии:

1. Зарегистрируйтесь на [Codecov](https://codecov.io/)
2. Подключите репозиторий
3. Получите токен
4. Добавьте в GitHub Secrets:
   ```
   CODECOV_TOKEN: ваш_токен
   ```

### 2. Environments (для деплоя)

Настройте окружения в GitHub:

1. Зайдите в **Settings** → **Environments**
2. Создайте:
   - `staging` - для тестового стенда
   - `production` - для production

3. Добавьте secrets для каждого окружения:
   ```
   DEPLOY_URL: https://your-app.onrender.com
   API_KEY: ваш_api_key
   ```

### 3. Secrets

Добавьте в **Settings** → **Secrets and variables** → **Actions**:

**Обязательные:**
```
CODECOV_TOKEN (опционально)
```

**Для деплоя:**
```
DEPLOY_URL
API_KEY
DOCKER_USERNAME
DOCKER_PASSWORD
```

---

## 📊 Покрытие кода

### Backend

Тесты запускаются с coverage:
```bash
pytest tests/ --cov=app --cov-report=xml
```

**Отчёт доступен:**
- В артефактах GitHub Actions
- На Codecov (если настроен)

**Цель:** 80%+ покрытия

### Frontend

Тесты запускаются с coverage:
```bash
npm run test:coverage
```

**Отчёт доступен:**
- В `frontend/coverage/`
- На Codecov (если настроен)

---

## 🔍 Мониторинг

### Статус проверок

Статус тестов отображается в:
- Pull Request checks
- Commit status
- Actions tab

### Артефакты

Сохраняются:
- Отчёты о покрытии (7 дней)
- Результаты тестов (3 дня)
- Build frontend (3 дня)

---

## 🛠️ Troubleshooting

### Тесты падают на CI/CD

**Проверьте:**
1. Логи в GitHub Actions
2. Зависимости в `requirements.txt`
3. Переменные окружения
4. Порядок тестов (не должно быть зависимостей)

### Codecov не загружает отчёт

**Проверьте:**
1. Токен в secrets
2. Путь к файлу `coverage.xml`
3. Флаг `fail_ci_if_error: false`

### Docker build fails

**Проверьте:**
1. Синтаксис Dockerfile
2. Доступность базовых образов
3. Лимиты дискового пространства

---

## 📈 Метрики

### Цели

| Метрика | Значение |
|---------|----------|
| Backend coverage | 80%+ |
| Frontend coverage | 80%+ |
| Build time | < 10 мин |
| Test time | < 5 мин |
| Deploy time | < 5 мин |

### Текущее состояние

| Метрика | Значение | Статус |
|---------|----------|--------|
| Backend coverage | TBD | 🔄 |
| Frontend coverage | TBD | 🔄 |
| Build time | ~8 мин | ✅ |
| Test time | ~5 мин | ✅ |

---

## 🎯 Best Practices

### 1. Пишите независимые тесты

```python
# ❌ Плохо: тесты зависят друг от друга
def test_create_user():
    user = create_user()

def test_update_user():
    user = get_user()  # Зависит от test_create_user
    update_user(user)

# ✅ Хорошо: каждый тест независим
def test_create_and_update_user():
    user = create_user()
    update_user(user)
```

### 2. Используйте фикстуры

```python
@pytest.fixture
def test_db():
    db = create_test_db()
    yield db
    cleanup_test_db()
```

### 3. Мокайте внешние сервисы

```python
@pytest.fixture
def mock_redis():
    with patch('redis.Redis') as mock:
        yield mock
```

### 4. Запускайте тесты локально перед push

```bash
# Backend
cd backend && pytest tests/ -v

# Frontend
cd frontend && npm test
```

---

## 📚 Дополнительные ресурсы

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Codecov Docs](https://docs.codecov.com/)
- [pytest Docs](https://docs.pytest.org/)
- [Jest Docs](https://jestjs.io/)

---

## ✅ Чеклист

- [ ] Backend tests workflow настроен
- [ ] Frontend tests workflow настроен
- [ ] Codecov подключен (опционально)
- [ ] Secrets добавлены
- [ ] Environments настроены
- [ ] Тесты запускаются локально
- [ ] Покрытие > 80%
