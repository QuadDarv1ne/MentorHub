# Background Tasks with Celery

## Обзор

Асинхронные фоновые задачи для MentorHub используя Celery + Redis.

## Возможности

- ✅ Асинхронная отправка email
- ✅ Периодические задачи (Celery Beat)
- ✅ Напоминания о сессиях
- ✅ Генерация статистики
- ✅ Очистка истекших токенов
- ✅ Retry логика
- ✅ Мониторинг задач

## Установка

### 1. Redis

```bash
# Windows (через WSL или Docker)
docker run -d -p 6379:6379 redis:alpine

# Linux
sudo apt install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis
```

### 2. Celery

```bash
pip install celery redis
```

## Структура

```
backend/
  app/
    tasks/
      celery_tasks.py  # Определения задач
      __init__.py
```

## Запуск

### Development

```bash
# Terminal 1: Celery Worker
cd backend
celery -A app.tasks.celery_tasks worker --loglevel=info

# Terminal 2: Celery Beat (периодические задачи)
celery -A app.tasks.celery_tasks beat --loglevel=info

# Terminal 3: Backend API
uvicorn app.main:app --reload
```

### Production

```bash
# Celery Worker (4 воркера)
celery -A app.tasks.celery_tasks worker \
  --loglevel=info \
  --concurrency=4 \
  --max-tasks-per-child=1000

# Celery Beat
celery -A app.tasks.celery_tasks beat --loglevel=info
```

### Docker Compose

```yaml
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  celery-worker:
    build: ./backend
    command: celery -A app.tasks.celery_tasks worker --loglevel=info
    depends_on:
      - redis
      - db
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - DATABASE_URL=postgresql://user:pass@db/mentorhub

  celery-beat:
    build: ./backend
    command: celery -A app.tasks.celery_tasks beat --loglevel=info
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
```

## Tasks

### 1. Email Tasks

#### Send Verification Email

```python
from app.tasks.celery_tasks import send_verification_email_task

# Вызов из API
send_verification_email_task.delay(
    email="user@example.com",
    username="john_doe",
    token="abc123..."
)
```

#### Send Password Reset Email

```python
send_password_reset_email_task.delay(
    email="user@example.com",
    username="john_doe",
    token="xyz789..."
)
```

#### Send Session Reminder

```python
send_session_reminder_task.delay(
    email="student@example.com",
    username="alice",
    session_date="04.12.2025 15:00",
    mentor_name="Bob Smith",
    session_link="https://mentorhub.com/sessions/123"
)
```

### 2. Periodic Tasks

#### Cleanup Expired Tokens (Daily)

```python
@celery_app.task(name="cleanup_expired_tokens")
def cleanup_expired_tokens():
    """Очистка истекших verification и reset токенов"""
    # Выполняется каждый день в 3:00
    ...
```

#### Generate Daily Stats (Daily)

```python
@celery_app.task(name="generate_daily_stats")
def generate_daily_stats():
    """Генерация ежедневной статистики"""
    # Выполняется каждый день в 1:00
    # Подсчитывает: новых пользователей, сессий, курсов
    ...
```

#### Send Session Reminders (Hourly)

```python
@celery_app.task(name="send_session_reminders")
def send_session_reminders():
    """Отправка напоминаний о сессиях через 1 час"""
    # Выполняется каждый час
    # Находит сессии, которые начнутся через 1 час
    ...
```

## Configuration

### Settings (app/config.py)

```python
# Celery Configuration
CELERY_BROKER_URL: str = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
CELERY_TASK_SERIALIZER: str = "json"
CELERY_RESULT_SERIALIZER: str = "json"
CELERY_ACCEPT_CONTENT: List[str] = ["json"]
CELERY_TIMEZONE: str = "UTC"
```

### Beat Schedule (celery_tasks.py)

```python
celery_app.conf.beat_schedule = {
    "cleanup-expired-tokens-daily": {
        "task": "cleanup_expired_tokens",
        "schedule": timedelta(days=1),  # Каждый день
    },
    "generate-daily-stats": {
        "task": "generate_daily_stats",
        "schedule": timedelta(days=1),
    },
    "send-session-reminders-hourly": {
        "task": "send_session_reminders",
        "schedule": timedelta(hours=1),  # Каждый час
    },
}
```

## Integration with API

### Example: Email Verification

```python
# app/api/email_verification.py

from app.tasks.celery_tasks import send_verification_email_task

@router.post("/send-verification")
async def send_verification_email(
    request: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user or user.is_verified:
        return {"message": "Email отправлен"}
    
    # Генерируем токен
    token = secrets.token_urlsafe(32)
    verification_tokens[token] = {
        "email": user.email,
        "expires_at": datetime.utcnow() + timedelta(hours=24)
    }
    
    # АСИНХРОННАЯ ОТПРАВКА через Celery
    send_verification_email_task.delay(
        email=user.email,
        username=user.username,
        token=token
    )
    
    return {"message": "Письмо отправлено"}
```

### Example: Session Reminder

```python
# app/api/sessions.py

from app.tasks.celery_tasks import send_session_reminder_task

@router.post("/sessions")
async def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Создаем сессию
    session = Session(**session_data.dict())
    db.add(session)
    db.commit()
    
    # Планируем напоминание за 1 час
    remind_time = session.scheduled_at - timedelta(hours=1)
    
    send_session_reminder_task.apply_async(
        args=[
            student.email,
            student.username,
            session.scheduled_at.strftime("%d.%m.%Y %H:%M"),
            mentor.full_name,
            f"{settings.FRONTEND_URL}/sessions/{session.id}"
        ],
        eta=remind_time  # Execute at specific time
    )
    
    return session
```

## Advanced Features

### 1. Retry Logic

```python
@celery_app.task(
    name="send_email_with_retry",
    bind=True,
    max_retries=3,
    default_retry_delay=60  # 1 minute
)
def send_email_with_retry(self, email, subject, content):
    try:
        email_service.send_email(email, subject, content)
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
```

### 2. Task Chaining

```python
from celery import chain

# Последовательное выполнение
result = chain(
    task1.s(arg1),
    task2.s(),
    task3.s()
).apply_async()
```

### 3. Task Groups

```python
from celery import group

# Параллельное выполнение
job = group([
    send_email_task.s(user1.email),
    send_email_task.s(user2.email),
    send_email_task.s(user3.email),
])
result = job.apply_async()
```

### 4. Task Routing

```python
# Разные очереди для разных типов задач
celery_app.conf.task_routes = {
    'send_email_*': {'queue': 'email'},
    'generate_stats_*': {'queue': 'analytics'},
    '*': {'queue': 'default'},
}

# Запуск воркеров для разных очередей
celery -A app.tasks.celery_tasks worker -Q email
celery -A app.tasks.celery_tasks worker -Q analytics
```

## Monitoring

### Flower (Web UI)

```bash
# Install
pip install flower

# Run
celery -A app.tasks.celery_tasks flower

# Open http://localhost:5555
```

Features:
- ✅ Real-time задачи
- ✅ Статистика воркеров
- ✅ Task history
- ✅ Task retry/revoke
- ✅ Графики производительности

### CLI Monitoring

```bash
# Статус воркеров
celery -A app.tasks.celery_tasks inspect active

# Статистика
celery -A app.tasks.celery_tasks inspect stats

# Registered tasks
celery -A app.tasks.celery_tasks inspect registered

# Активные задачи
celery -A app.tasks.celery_tasks inspect active
```

### Logs

```python
# В задаче
import logging
logger = logging.getLogger(__name__)

@celery_app.task
def my_task():
    logger.info("Task started")
    # ...
    logger.info("Task completed")
```

## Error Handling

### Dead Letter Queue

```python
# Настройка для failed tasks
celery_app.conf.task_reject_on_worker_lost = True
celery_app.conf.task_acks_late = True

# Custom error handler
@celery_app.task(bind=True, max_retries=3)
def my_task(self):
    try:
        # Task logic
        pass
    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        # Notify admin
        send_admin_notification.delay(f"Task {self.name} failed")
        raise
```

### Sentry Integration

```python
import sentry_sdk
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",
    integrations=[CeleryIntegration()]
)
```

## Best Practices

✅ **Idempotency:**
```python
# Task можно запустить несколько раз без побочных эффектов
@celery_app.task
def idempotent_task(user_id):
    user = db.query(User).filter(User.id == user_id).first()
    if user.email_sent:
        return  # Уже отправлено
    send_email(user.email)
    user.email_sent = True
    db.commit()
```

✅ **Small Tasks:**
```python
# Плохо: одна большая задача
@celery_app.task
def process_all_users():
    users = db.query(User).all()
    for user in users:
        heavy_computation(user)

# Хорошо: много маленьких задач
@celery_app.task
def process_user(user_id):
    user = db.query(User).get(user_id)
    heavy_computation(user)

# Запуск
for user_id in user_ids:
    process_user.delay(user_id)
```

✅ **Timeouts:**
```python
@celery_app.task(
    time_limit=300,      # Hard limit: 5 minutes
    soft_time_limit=240  # Soft limit: 4 minutes
)
def long_task():
    try:
        # Task logic
        pass
    except SoftTimeLimitExceeded:
        # Cleanup
        pass
```

## Production Deployment

### Systemd Service (Linux)

```ini
# /etc/systemd/system/celery-worker.service
[Unit]
Description=Celery Worker
After=network.target

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/var/www/mentorhub/backend
ExecStart=/usr/local/bin/celery -A app.tasks.celery_tasks worker \
  --loglevel=info \
  --logfile=/var/log/celery/worker.log \
  --pidfile=/var/run/celery/worker.pid

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start celery-worker
sudo systemctl enable celery-worker
```

### Supervisor (Alternative)

```ini
# /etc/supervisor/conf.d/celery.conf
[program:celery-worker]
command=celery -A app.tasks.celery_tasks worker --loglevel=info
directory=/var/www/mentorhub/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/worker.log
```

## FAQ

**Q: Redis vs RabbitMQ?**

A: Redis проще, RabbitMQ надежнее. Для большинства случаев Redis достаточно.

**Q: Сколько воркеров нужно?**

A: Начните с `CPU_COUNT * 2`. Мониторьте и увеличивайте по необходимости.

**Q: Как тестировать Celery задачи?**

A:
```python
# Pytest
def test_send_email_task(mocker):
    mock_send = mocker.patch('app.utils.email.email_service.send_email')
    send_verification_email_task("test@test.com", "user", "token")
    mock_send.assert_called_once()

# Или запускай синхронно в тестах
celery_app.conf.task_always_eager = True
```

**Q: Production ready?**

A: Для продакшена:
1. Используйте RabbitMQ вместо Redis (optional)
2. Настройте monitoring (Flower, Sentry)
3. Используйте отдельные очереди
4. Настройте max_tasks_per_child для предотвращения memory leaks
5. Логируйте в ELK/Grafana
