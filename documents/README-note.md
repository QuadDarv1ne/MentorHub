# Инструкция по запуску MentorHub

## Предварительные требования

**Перед запуском проекта убедитесь, что у вас установлены:**

- Python 3.8 или выше
- Node.js 16.0 или выше
- npm 8.0 или выше
- PostgreSQL (опционально, можно использовать SQLite для разработки)

## Структура проекта

**Проект состоит из двух основных частей:**

- `backend/` - FastAPI backend сервер
- `frontend/` - Next.js frontend приложение

## Запуск Backend

1. **Перейдите в директорию backend:**

```bash
cd backend
```

2. **Создайте и активируйте виртуальное окружение:**

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux/MacOS
python3 -m venv .venv
source .venv/bin/activate
```

3. **Установите зависимости:**

```bash
pip install -r requirements.txt
```

4. **Создайте файл `.env` в директории `backend/` со следующим содержимым:**

```env
DEBUG=True
ENVIRONMENT=development
DATABASE_URL=sqlite:///./mentorhub.db
SECRET_KEY=development-secret-key-123
CORS_ORIGINS=["http://localhost:3000","http://localhost:8000","http://127.0.0.1:3000","http://127.0.0.1:8000"]
```

5. **Запустите сервер:**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend будет доступен по адресу:** http://localhost:8000

**API документация:**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Запуск Frontend

1. Перейдите в директорию frontend:
```bash
cd frontend
```

2. Установите зависимости:
```bash
npm install
```

3. Запустите development сервер:
```bash
npm run dev
```

Frontend приложение будет доступно по адресу: http://localhost:3000

## Проверка работоспособности

### Backend API endpoints:

- Регистрация: POST http://localhost:8000/api/v1/auth/register
- Авторизация: POST http://localhost:8000/api/v1/auth/login
- Профиль пользователя: GET http://localhost:8000/api/v1/users/me

### Frontend страницы:

- Главная: http://localhost:3000
- Авторизация: http://localhost:3000/auth/login
- Регистрация: http://localhost:3000/auth/register

## Доступные команды

### Backend

```bash
# Запуск тестов
pytest tests/ -v

# Создание миграций базы данных
alembic revision --autogenerate -m "migration_name"

# Применение миграций
alembic upgrade head
```

### После добавления новых моделей

Если вы добавляете новые модели (например, модель отзывов `Review`), выполните миграции:

```bash
# Создание ревизии миграции
cd backend
alembic revision --autogenerate -m "add reviews model"

# Применение миграций
alembic upgrade head
```

### Frontend

```bash
# Запуск в режиме разработки
npm run dev

# Сборка для продакшена
npm run build

# Запуск тестов
npm test

# Проверка типов
npm run type-check

# Линтинг
npm run lint

# Форматирование кода
npm run format
```

## Troubleshooting

### Backend

1. Если возникает ошибка импорта модулей:
   - Убедитесь, что вы находитесь в виртуальном окружении
   - Проверьте, что все зависимости установлены
   - Убедитесь, что PYTHONPATH настроен правильно

2. Ошибки с базой данных:
   - Проверьте настройки подключения в `.env`
   - Убедитесь, что все миграции применены
   - При использовании PostgreSQL проверьте, что сервер запущен

### Frontend

1. Если `npm install` выдает ошибки:
   - Очистите кэш npm: `npm cache clean --force`
   - Удалите node_modules и package-lock.json
   - Повторите установку: `npm install`

2. Проблемы с подключением к backend:
   - Проверьте, что backend сервер запущен
   - Убедитесь, что CORS настроен правильно
   - Проверьте API URLs в frontend конфигурации

## Режимы работы

### Development Mode

- Backend: Автоматическая перезагрузка при изменении кода
- Frontend: Hot-reloading для быстрой разработки
- SQLite база данных для простоты настройки
- Подробные логи и отладочная информация

### Production Mode

**Для запуска в `production` режиме:**

1. **Измените настройки в `.env`:**

```env
DEBUG=False
ENVIRONMENT=production
DATABASE_URL=postgresql://user:password@localhost/mentorhub
```

2. **Используйте production сервер для backend:**

```bash
gunicorn app.main:app
```

3. **Соберите и запустите frontend:**

```bash
npm run build
npm start
```

## Упрощённый быстрый запуск

**Для Backend:**

```bash
# 1. Перейти в директорию backend
# 2. Убедиться, что все зависимости установлены
cd backend && pip install -r requirements.txt

# 3. Запустить сервер
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Для Frontend:**

```bash
# 1. Перейти в директорию frontend
# 2. Установить зависимости
cd frontend && npm install

# 3. Запустить development сервер
npm run dev
```

## Дополнительная информация

- **Документация `API`:** http://localhost:8000/docs
- **Исходный код:** https://github.com/QuadDarv1ne/MentorHub
- **Журнал изменений:** См. `CHANGELOG.md`
- **Планируемые улучшения:** См. `IMPROVEMENTS.md`
