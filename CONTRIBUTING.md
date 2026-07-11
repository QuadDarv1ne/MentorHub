# Руководство по внесению вклада в MentorHub

Спасибо за ваш интерес к развитию MentorHub! Мы приветствуем вклад от сообщества и ценим ваше время и усилия.

## 📋 Оглавление

- [Кодекс поведения](#кодекс-поведения)
- [Как внести вклад](#как-внести-вклад)
- [Процесс разработки](#процесс-разработки)
- [Стандарты кода](#стандарты-кода)
- [Тестирование](#тестирование)
- [Коммиты и Pull Requests](#коммиты-и-pull-requests)
- [Сообщение об ошибках](#сообщение-об-ошибках)
- [Предложение новых функций](#предложение-новых-функций)

---

## 🤝 Кодекс поведения

Участвуя в этом проекте, вы соглашаетесь соблюдать наш [Кодекс поведения](CODE_OF_CONDUCT.md). Пожалуйста, будьте уважительны и профессиональны во всех взаимодействиях.

### Основные принципы:

- **Уважение** — ценим различные точки зрения и опыт
- **Конструктивность** — фокусируемся на решениях, а не на проблемах
- **Профессионализм** — поддерживаем высокие стандарты общения
- **Инклюзивность** — приветствуем всех независимо от опыта и бэкграунда

---

## 🚀 Как внести вклад

### Типы вклада, которые мы принимаем:

- 🐛 **Исправление багов** — помогите нам улучшить стабильность
- ✨ **Новые функции** — добавьте новые возможности платформе
- 📝 **Документация** — улучшите или переведите документацию
- 🎨 **Дизайн** — предложите улучшения UI/UX
- 🧪 **Тесты** — повысьте покрытие тестами
- 🔧 **Инфраструктура** — оптимизируйте CI/CD и deployment

### Шаги для начала:

1. **Форкните репозиторий**
   ```bash
   git clone https://github.com/QuadDarv1ne/MentorHub.git
   cd MentorHub
   ```

2. **Создайте ветку для вашей работы**
   ```bash
   git checkout -b feature/your-feature-name
   # или
   git checkout -b fix/bug-description
   ```

3. **Установите зависимости**
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
   ```

4. **Внесите изменения** и протестируйте их локально

5. **Закоммитьте изменения**
   ```bash
   git add .
   git commit -m "feat: добавлена новая функция X"
   ```

6. **Отправьте изменения в ваш форк**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Создайте Pull Request** на GitHub

---

## 💻 Процесс разработки

### Настройка окружения

#### Backend разработка

```bash
cd backend

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Настроить .env файл
cp .env.example .env
# Отредактируйте .env с вашими настройками

# Запустить миграции
alembic upgrade head

# Запустить сервер
uvicorn app.main:app --reload
```

#### Frontend разработка

```bash
cd frontend

# Установить зависимости
npm install

# Настроить .env.local
cp .env.example .env.local
# Отредактируйте .env.local

# Запустить dev сервер
npm run dev
```

### Структура веток

- `main` — стабильная production версия
- `develop` — основная ветка разработки
- `feature/*` — новые функции
- `fix/*` — исправления багов
- `hotfix/*` — критические исправления для production
- `release/*` — подготовка к релизу

### Рабочий процесс

1. Всегда создавайте новую ветку от `develop`
2. Регулярно синхронизируйтесь с основной веткой
3. Тестируйте изменения локально
4. Создавайте Pull Request в `develop`
5. Ждите код-ревью от мейнтейнеров

---

## 📏 Стандарты кода

### Python (Backend)

Следуйте [PEP 8](https://peps.python.org/pep-0008/) стайл гайду:

```python
# ✅ Хорошо
def calculate_total_price(items: list[Item]) -> Decimal:
    """
    Вычисляет общую стоимость товаров.
    
    Args:
        items: Список товаров
        
    Returns:
        Общая стоимость
    """
    return sum(item.price for item in items)


# ❌ Плохо
def calc(i):
    return sum([x.p for x in i])
```

**Инструменты:**
- `black` — форматирование кода
- `flake8` — линтер
- `mypy` — проверка типов
- `isort` — сортировка импортов

```bash
# Запустить проверки
black .
flake8 .
mypy .
isort .
```

### TypeScript/React (Frontend)

Следуйте [Airbnb Style Guide](https://github.com/airbnb/javascript):

```typescript
// ✅ Хорошо
interface UserProps {
  name: string
  email: string
  role: UserRole
}

export function UserCard({ name, email, role }: UserProps) {
  return (
    <div className="user-card">
      <h3>{name}</h3>
      <p>{email}</p>
      <span>{role}</span>
    </div>
  )
}

// ❌ Плохо
export function card(props: any) {
  return <div>{props.n}</div>
}
```

**Инструменты:**
- `ESLint` — линтер
- `Prettier` — форматирование
- `TypeScript` — типизация

```bash
# Запустить проверки
npm run lint
npm run type-check
npm run format
```

### Общие правила

1. **Именование**
   - Используйте понятные, описательные имена
   - Избегайте сокращений (кроме общепринятых)
   - Используйте camelCase для переменных/функций
   - Используйте PascalCase для классов/компонентов

2. **Комментарии**
   - Пишите комментарии для сложной логики
   - Используйте docstrings для функций/классов
   - Избегайте очевидных комментариев

3. **Функции**
   - Одна функция — одна ответственность
   - Максимум 50 строк на функцию
   - Явные типы для параметров и возврата

4. **Файлы**
   - Максимум 300 строк на файл
   - Логическое группирование кода
   - Один компонент/класс на файл

---

## 🧪 Тестирование

### Backend тесты (pytest)

```bash
cd backend

# Запустить все тесты
pytest

# Запустить с покрытием
pytest --cov=app --cov-report=html

# Запустить конкретный тест
pytest tests/test_auth.py::test_login_success
```

**Структура тестов:**

```python
import pytest
from app.services.auth_service import AuthService

class TestAuthService:
    """Тесты для сервиса аутентификации."""
    
    @pytest.fixture
    def auth_service(self):
        return AuthService()
    
    def test_login_with_valid_credentials(self, auth_service):
        """Тест успешного входа с правильными учетными данными."""
        # Arrange
        email = "test@example.com"
        password = "securepassword"
        
        # Act
        result = auth_service.login(email, password)
        
        # Assert
        assert result.success is True
        assert result.token is not None
```

### Frontend тесты (Jest + React Testing Library)

```bash
cd frontend

# Запустить все тесты
npm test

# Запустить с покрытием
npm run test:coverage

# Запустить в watch режиме
npm run test:watch
```

**Структура тестов:**

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { LoginForm } from './LoginForm'

describe('LoginForm', () => {
  it('должен отображать форму входа', () => {
    render(<LoginForm />)
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /войти/i })).toBeInTheDocument()
  })
  
  it('должен валидировать email', async () => {
    render(<LoginForm />)
    
    const emailInput = screen.getByLabelText(/email/i)
    fireEvent.change(emailInput, { target: { value: 'invalid' } })
    
    expect(await screen.findByText(/некорректный email/i)).toBeInTheDocument()
  })
})
```

### Минимальное покрытие

- Backend: **80%+**
- Frontend: **70%+**

---

## 📝 Коммиты и Pull Requests

### Формат коммитов (Conventional Commits)

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Типы коммитов:**

- `feat`: Новая функция
- `fix`: Исправление бага
- `docs`: Изменения в документации
- `style`: Форматирование, пропущенные точки с запятой и т.д.
- `refactor`: Рефакторинг кода
- `perf`: Улучшение производительности
- `test`: Добавление тестов
- `chore`: Обновление зависимостей, конфигурации и т.д.

**Примеры:**

```bash
feat(auth): добавлена двухфакторная аутентификация

Реализована возможность включения 2FA через SMS или TOTP.
Добавлены новые эндпоинты API и UI компоненты.

Closes #123
```

```bash
fix(payment): исправлена ошибка при обработке платежа

Устранена проблема с неправильным расчетом комиссии
при использовании промокода.

Fixes #456
```

### Pull Request Guidelines

**Название PR:**
```
[Type] Brief description (#issue-number)
```

**Пример:**
```
[Feature] Add password strength indicator (#234)
```

**Шаблон описания PR:**

```markdown
## Описание
Краткое описание изменений и мотивация.

## Тип изменений
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Тестирование
Опишите тесты, которые вы провели.

## Чеклист
- [ ] Код следует стандартам проекта
- [ ] Код прошёл self-review
- [ ] Добавлены комментарии к сложным участкам
- [ ] Обновлена документация
- [ ] Нет новых предупреждений
- [ ] Добавлены тесты
- [ ] Все тесты проходят локально
- [ ] Зависимости обновлены (если применимо)

## Скриншоты (если применимо)
Добавьте скриншоты для визуальных изменений.

## Связанные Issues
Closes #123
Related to #456
```

---

## 🐛 Сообщение об ошибках

### Перед созданием Issue

1. Проверьте, не существует ли уже подобный Issue
2. Убедитесь, что используете последнюю версию
3. Проверьте [FAQ](docs/FAQ.md) и [документацию](README.md)

### Шаблон Bug Report

```markdown
**Описание бага**
Четкое и краткое описание проблемы.

**Шаги для воспроизведения**
1. Перейти на '...'
2. Нажать на '...'
3. Прокрутить вниз до '...'
4. Увидеть ошибку

**Ожидаемое поведение**
Что должно было произойти.

**Актуальное поведение**
Что произошло на самом деле.

**Скриншоты**
При необходимости добавьте скриншоты.

**Окружение:**
- OS: [e.g. Windows 10]
- Browser: [e.g. Chrome 120]
- Version: [e.g. v1.2.3]

**Дополнительный контекст**
Любая другая информация о проблеме.

**Логи**
```
Вставьте соответствующие логи здесь
```
```

---

## 💡 Предложение новых функций

### Перед созданием Feature Request

1. Убедитесь, что функция еще не предложена
2. Проверьте [дорожную карту](README.md#дорожная-карта)
3. Рассмотрите, соответствует ли функция целям проекта

### Шаблон Feature Request

```markdown
**Описание функции**
Четкое и краткое описание того, что вы хотите.

**Проблема, которую решает**
Опишите проблему, которую вы пытаетесь решить.

**Предлагаемое решение**
Опишите, как вы видите реализацию этой функции.

**Альтернативы**
Опишите альтернативные решения, которые вы рассматривали.

**Примеры из других проектов**
Если подобная функция есть в других проектах, укажите их.

**Дополнительный контекст**
Добавьте любой другой контекст или скриншоты.
```

---

## 🎯 Приоритеты разработки

### Высокий приоритет

- Критические баги безопасности
- Исправления, влияющие на всех пользователей
- Потеря данных или крэши

### Средний приоритет

- Улучшение производительности
- Новые функции из дорожной карты
- Улучшение UX

### Низкий приоритет

- Косметические изменения
- Рефакторинг без функциональных изменений
- Незначительные оптимизации

---

## 📚 Ресурсы для разработчиков

### Документация

- [README.md](README.md) — основная документация
- [AUTHENTICATION.md](AUTHENTICATION.md) — система аутентификации
- [API Documentation](http://localhost:8001/docs) — Swagger docs

### Полезные ссылки

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)

### Инструменты

- [GitHub Issues](https://github.com/QuadDarv1ne/MentorHub/issues)
- [GitHub Projects](https://github.com/QuadDarv1ne/MentorHub/projects)
- [Discussions](https://github.com/QuadDarv1ne/MentorHub/discussions)

---

## 🏆 Признание вклада

Мы ценим каждый вклад в проект! Все контрибьюторы будут упомянуты в:

- [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Release notes
- Специальный раздел на сайте (планируется)

---

## 📞 Получить помощь

Если у вас есть вопросы:

- 💬 [GitHub Discussions](https://github.com/QuadDarv1ne/MentorHub/discussions)
- 📧 Email: [maksimqwe42@mail.ru](mailto:maksimqwe42@mail.ru)
- 📱 Telegram: [@quadd4rv1n7](https://t.me/quadd4rv1n7)

---

**Спасибо за ваш вклад в развитие MentorHub! 🎉**

Вместе мы делаем IT-образование доступнее для всех.
