# 🚀 Production Deployment Guide

## 📋 Предварительные требования

### Системные требования:
- Ubuntu 20.04+ или CentOS 8+
- Python 3.9+
- Node.js 18+
- Docker и Docker Compose
- 4GB RAM минимум
- 2 CPU cores

### Сервисы:
- PostgreSQL 13+
- Redis 6+
- Nginx

---

## 🏗️ Архитектура продакшена

```
Internet
    ↓
Nginx (SSL Termination, Load Balancing)
    ↓
Backend API (FastAPI + Uvicorn)
    ↓
PostgreSQL ←→ Redis ←→ Celery Workers
    ↓
Frontend (Next.js Static Export)
```

---

## 🔧 Шаги деплоя

### 1. Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y \
    python3-pip python3-dev python3-venv \
    postgresql postgresql-contrib \
    redis-server \
    nginx \
    supervisor \
    git \
    docker.io docker-compose

# Добавление пользователя для приложения
sudo adduser mentorhub
sudo usermod -aG docker mentorhub
sudo usermod -aG www-data mentorhub
```

### 2. Настройка базы данных

```bash
# Создание базы данных и пользователя
sudo -u postgres psql << EOF
CREATE DATABASE mentorhub_prod;
CREATE USER mentorhub WITH PASSWORD 'strong_password_here';
GRANT ALL PRIVILEGES ON DATABASE mentorhub_prod TO mentorhub;
ALTER USER mentorhub CREATEDB;
EOF

# Настройка прав доступа
sudo -u postgres psql -c "ALTER DATABASE mentorhub_prod OWNER TO mentorhub;"
```

### 3. Клонирование репозитория

```bash
# Переключение под пользователя mentorhub
sudo su - mentorhub

# Клонирование проекта
git clone https://github.com/your-org/mentorhub.git
cd mentorhub

# Создание директорий
mkdir -p logs staticfiles media backups
```

### 4. Настройка окружения

Создайте файл `.env` в корне проекта:

```env
# Основные настройки
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-very-long-secret-key-here-change-this
ALLOWED_HOSTS=mentorhub.ru,www.mentorhub.ru,localhost,127.0.0.1

# База данных
DATABASE_URL=postgresql://mentorhub:strong_password_here@localhost:5432/mentorhub_prod

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email (SendGrid рекомендуется)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_FROM_EMAIL=noreply@mentorhub.ru
SMTP_FROM_NAME=MentorHub

# Frontend
FRONTEND_URL=https://mentorhub.ru

# Безопасность
MAX_REQUESTS_PER_MINUTE=100
ENABLE_RATE_LIMITING=True
ENABLE_SECURITY_HEADERS=True
```

### 5. Установка зависимостей

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-prod.txt

# Frontend
cd ../frontend
npm install
npm run build
```

### 6. Настройка базы данных

```bash
# Активация виртуального окружения
cd ../backend
source venv/bin/activate

# Запуск миграций
alembic upgrade head

# Создание администратора
python scripts/create_admin.py

# Загрузка начальных данных (опционально)
python scripts/seed_data.py
```

### 7. Настройка Supervisor

Создайте файл `/etc/supervisor/conf.d/mentorhub.conf`:

```ini
[group:mentorhub]
programs=api,cworker,cbeat

[program:api]
command=/home/mentorhub/mentorhub/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
directory=/home/mentorhub/mentorhub/backend
user=mentorhub
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/mentorhub/mentorhub/logs/api.log
environment=PATH="/home/mentorhub/mentorhub/backend/venv/bin"

[program:cworker]
command=/home/mentorhub/mentorhub/backend/venv/bin/celery -A app.tasks.celery_tasks worker --loglevel=info --concurrency=4
directory=/home/mentorhub/mentorhub/backend
user=mentorhub
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/mentorhub/mentorhub/logs/celery-worker.log
environment=PATH="/home/mentorhub/mentorhub/backend/venv/bin"

[program:cbeat]
command=/home/mentorhub/mentorhub/backend/venv/bin/celery -A app.tasks.celery_tasks beat --loglevel=info
directory=/home/mentorhub/mentorhub/backend
user=mentorhub
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/mentorhub/mentorhub/logs/celery-beat.log
environment=PATH="/home/mentorhub/mentorhub/backend/venv/bin"
```

Запустите Supervisor:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start mentorhub:*
```

### 8. Настройка Nginx

Создайте файл `/etc/nginx/sites-available/mentorhub`:

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name mentorhub.ru www.mentorhub.ru;
    
    # Редирект на HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name mentorhub.ru www.mentorhub.ru;
    
    # SSL certificates (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/mentorhub.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mentorhub.ru/privkey.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    
    # Frontend static files
    location / {
        root /home/mentorhub/mentorhub/frontend/out;
        try_files $uri $uri/ /index.html;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
    
    # WebSocket
    location /ws/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
    
    # Media files
    location /media/ {
        alias /home/mentorhub/mentorhub/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Static files
    location /static/ {
        alias /home/mentorhub/mentorhub/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://backend;
        access_log off;
    }
}
```

Активируйте сайт:

```bash
sudo ln -s /etc/nginx/sites-available/mentorhub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 9. SSL сертификаты (Let's Encrypt)

```bash
# Установка certbot
sudo apt install certbot python3-certbot-nginx

# Получение сертификатов
sudo certbot --nginx -d mentorhub.ru -d www.mentorhub.ru

# Автоматическое обновление
sudo crontab -e
# Добавить: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 10. Мониторинг и логирование

#### Logrotate настройка

Создайте `/etc/logrotate.d/mentorhub`:

```
/home/mentorhub/mentorhub/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 mentorhub mentorhub
    postrotate
        supervisorctl restart mentorhub:* > /dev/null 2>&1 || true
    endscript
}
```

#### Health checks скрипт

Создайте `/home/mentorhub/mentorhub/scripts/health-check.sh`:

```bash
#!/bin/bash

API_HEALTH=$(curl -sf http://localhost:8000/health/live)
if [ $? -ne 0 ]; then
    echo "$(date): API health check failed" >> /home/mentorhub/mentorhub/logs/health.log
    supervisorctl restart mentorhub:api
fi

# Проверка Celery workers
CELERY_STATUS=$(supervisorctl status mentorhub:cworker | grep RUNNING)
if [ -z "$CELERY_STATUS" ]; then
    echo "$(date): Celery worker is not running" >> /home/mentorhub/mentorhub/logs/health.log
    supervisorctl restart mentorhub:cworker
fi
```

Сделайте исполняемым и добавьте в cron:

```bash
chmod +x /home/mentorhub/mentorhub/scripts/health-check.sh

# Добавить в crontab
crontab -e
# */5 * * * * /home/mentorhub/mentorhub/scripts/health-check.sh
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions workflow (`.github/workflows/deploy.yml`):

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to production
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.PRIVATE_KEY }}
        script: |
          cd /home/mentorhub/mentorhub
          git pull origin main
          
          # Backend update
          cd backend
          source venv/bin/activate
          pip install -r requirements-prod.txt
          alembic upgrade head
          
          # Frontend update
          cd ../frontend
          npm install
          npm run build
          
          # Restart services
          sudo supervisorctl restart mentorhub:*
```

---

## 📊 Мониторинг

### Prometheus + Grafana

1. Установите Prometheus и Grafana
2. Настройте сбор метрик с `/metrics` endpoint
3. Импортируйте dashboard из `monitoring/grafana/dashboard.json`

### Логирование

```bash
# Просмотр логов
tail -f /home/mentorhub/mentorhub/logs/api.log
tail -f /home/mentorhub/mentorhub/logs/celery-worker.log

# Анализ логов
journalctl -u supervisor -f
```

---

## 🔒 Безопасность

### Firewall (UFW):

```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw deny 8000  # Закрываем порт API извне
```

### Fail2ban:

```bash
sudo apt install fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Добавьте в jail.local:
[nginx-http-auth]
enabled = true

[nginx-botsearch]
enabled = true
```

---

## 🆘 Troubleshooting

### Частые проблемы:

1. **502 Bad Gateway:**
   ```bash
   sudo supervisorctl status  # Проверить статус сервисов
   sudo journalctl -u supervisor  # Логи supervisor
   ```

2. **Nginx не запускается:**
   ```bash
   sudo nginx -t  # Проверка конфигурации
   sudo systemctl status nginx  # Статус сервиса
   ```

3. **База данных недоступна:**
   ```bash
   sudo systemctl status postgresql
   sudo -u postgres psql -c "SELECT 1;"  # Тест подключения
   ```

4. **Celery задачи не выполняются:**
   ```bash
   sudo supervisorctl tail mentorhub:cworker  # Логи Celery
   redis-cli ping  # Проверка Redis
   ```

---

## 📈 Scaling

### Horizontal scaling:
- Используйте load balancer (Nginx upstream)
- Горизонтальное масштабирование Celery workers
- Read replicas для PostgreSQL

### Vertical scaling:
- Увеличьте ресурсы сервера
- Настройте больше worker processes
- Оптимизируйте конфигурацию БД

---

Готово! Ваш MentorHub теперь запущен в продакшене 🚀