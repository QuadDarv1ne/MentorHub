# Production Deployment Guide

## 🚀 Развертывание MentorHub в Production

### Предварительные требования

- Docker и Docker Compose установлены
- Домен настроен и указывает на ваш сервер
- SSL сертификаты (Let's Encrypt рекомендуется)
- Минимум 4GB RAM, 2 CPU cores, 20GB диска

### Шаг 1: Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
```

### Шаг 2: Клонирование репозитория

```bash
git clone https://github.com/QuadDarv1ne/MentorHub.git
cd MentorHub
```

### Шаг 3: Настройка переменных окружения

```bash
# Копирование шаблона
cp .env.production.example .env.production

# Редактирование переменных
nano .env.production
```

**Обязательно измените:**
- `POSTGRES_PASSWORD` - надежный пароль для PostgreSQL
- `REDIS_PASSWORD` - надежный пароль для Redis
- `SECRET_KEY` - случайная строка минимум 32 символа
- `SENTRY_DSN` - если используете Sentry
- `STRIPE_SECRET_KEY` - ключи Stripe для платежей
- `AWS_*` - credentials для S3 (если используете)

**Генерация SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Шаг 4: Настройка SSL (Let's Encrypt)

```bash
# Установка Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получение сертификата
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Копирование сертификатов
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/
```

### Шаг 5: Настройка Nginx

Создайте файл `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8001;
    }

    upstream frontend {
        server frontend:3000;
    }

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name your-domain.com www.your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS Server
    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # SSL Configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;

        # Security Headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;

        # API Backend
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Static files
        location /static/ {
            alias /app/static/;
        }

        location /media/ {
            alias /app/media/;
        }
    }
}
```

### Шаг 6: Запуск приложения

```bash
# Сборка и запуск контейнеров
docker-compose -f docker-compose.prod.yml up -d --build

# Проверка статуса
docker-compose -f docker-compose.prod.yml ps

# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f
```

### Шаг 7: Инициализация базы данных

```bash
# Применение миграций
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Создание администратора
docker-compose -f docker-compose.prod.yml exec backend python scripts/create_admin.py
```

### Шаг 8: Настройка автоматических бэкапов

```bash
# Добавление cron задачи для ежедневного бэкапа
crontab -e

# Добавьте строку:
0 2 * * * cd /path/to/MentorHub && docker-compose -f docker-compose.prod.yml exec -T backup /backup.sh
```

### Шаг 9: Мониторинг

```bash
# Проверка health check
curl https://your-domain.com/api/v1/health/detailed

# Мониторинг ресурсов
docker stats

# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Шаг 10: Обновление приложения

```bash
# Получение последних изменений
git pull origin main

# Пересборка и перезапуск
docker-compose -f docker-compose.prod.yml up -d --build

# Применение миграций
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

## 🔒 Безопасность

### Firewall настройка

```bash
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

### Регулярные обновления

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Обновление Docker образов
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

## 📊 Мониторинг и логи

### Просмотр логов

```bash
# Все сервисы
docker-compose -f docker-compose.prod.yml logs -f

# Только backend
docker-compose -f docker-compose.prod.yml logs -f backend

# Логи Nginx
docker-compose -f docker-compose.prod.yml logs -f nginx

# Логи базы данных
docker-compose -f docker-compose.prod.yml logs -f postgres
```

### Метрики производительности

```bash
# Использование ресурсов контейнерами
docker stats

# Размер логов
du -sh /var/lib/docker/containers/*/*-json.log
```

## 🔧 Troubleshooting

### Проблема: Контейнер не запускается

```bash
# Проверка логов
docker-compose -f docker-compose.prod.yml logs backend

# Проверка переменных окружения
docker-compose -f docker-compose.prod.yml exec backend env
```

### Проблема: База данных недоступна

```bash
# Проверка PostgreSQL
docker-compose -f docker-compose.prod.yml exec postgres psql -U mentorhub -c "SELECT 1"

# Перезапуск базы данных
docker-compose -f docker-compose.prod.yml restart postgres
```

### Проблема: Высокая нагрузка

```bash
# Масштабирование backend
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Очистка неиспользуемых ресурсов
docker system prune -a
```

## 📦 Backup и восстановление

### Создание бэкапа

```bash
# Ручной бэкап
docker-compose -f docker-compose.prod.yml exec backup /backup.sh

# Список бэкапов
ls -lh backups/
```

### Восстановление из бэкапа

```bash
# Список доступных бэкапов
docker-compose -f docker-compose.prod.yml exec backup /restore.sh list

# Восстановление последнего бэкапа
docker-compose -f docker-compose.prod.yml exec backup /restore.sh latest

# Восстановление конкретного бэкапа
docker-compose -f docker-compose.prod.yml exec backup /restore.sh restore /backups/daily/backup_20241124_120000.sql.gz
```

## 🎯 Оптимизация производительности

### PostgreSQL

```sql
-- Настройка параметров (в docker-compose.prod.yml)
command:
  - "postgres"
  - "-c"
  - "shared_buffers=256MB"
  - "-c"
  - "effective_cache_size=1GB"
  - "-c"
  - "max_connections=200"
```

### Redis

```bash
# Мониторинг использования памяти
docker-compose -f docker-compose.prod.yml exec redis redis-cli INFO memory
```

### Nginx

- Включите gzip сжатие
- Настройте кэширование статических файлов
- Используйте HTTP/2

## 📚 Дополнительные ресурсы

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [PostgreSQL Performance](https://www.postgresql.org/docs/current/performance-tips.html)
- [Nginx Optimization](https://www.nginx.com/blog/tuning-nginx/)

## 🆘 Поддержка

При возникновении проблем:
1. Проверьте логи: `docker-compose -f docker-compose.prod.yml logs -f`
2. Проверьте health checks: `/api/v1/health/detailed`
3. Откройте issue на GitHub: https://github.com/QuadDarv1ne/MentorHub/issues
