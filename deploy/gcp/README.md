# Google Cloud Run Deployment Guide

## 📋 Требования

- Google Cloud аккаунт
- Установленный gcloud CLI
- Установленный kubectl (опционально)
- Docker

## 🚀 Быстрый старт

### 1. Установка gcloud CLI

```bash
# Windows
choco install google-cloud-cli

# macOS
brew install --cask google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash
```

### 2. Аутентификация

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 3. Создание проекта

```bash
gcloud projects create mentorhub-production --name="MentorHub Production"
gcloud config set project mentorhub-production
```

### 4. Включение необходимых API

```bash
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable sqladmin.googleapis.com
gcloud services enable redis.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable monitoring.googleapis.com
```

### 5. Создание Service Account

```bash
gcloud iam service-accounts create mentorhub-sa \
  --display-name="MentorHub Service Account"

gcloud projects add-iam-policy-binding mentorhub-production \
  --member="serviceAccount:mentorhub-sa@mentorhub-production.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

gcloud projects add-iam-policy-binding mentorhub-production \
  --member="serviceAccount:mentorhub-sa@mentorhub-production.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding mentorhub-production \
  --member="serviceAccount:mentorhub-sa@mentorhub-production.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 6. Создание Cloud SQL (PostgreSQL)

```bash
# Создание инстанса
gcloud sql instances create mentorhub-db \
  --database-version=POSTGRES_16 \
  --tier=db-custom-2-4096 \
  --region=europe-west1 \
  --root-password=CHANGE_ME_SECURE_PASSWORD \
  --storage-type=SSD \
  --storage-size=10GB \
  --availability-type=REGIONAL \
  --backup-start-time=03:00 \
  --maintenance-window-day=SUNDAY \
  --maintenance-window-hour=04:00

# Создание базы данных
gcloud sql databases create mentorhub --instance=mentorhub-db

# Создание пользователя
gcloud sql users create mentorhub_user \
  --instance=mentorhub-db \
  --password=CHANGE_ME_SECURE_PASSWORD
```

### 7. Создание Memorystore (Redis)

```bash
gcloud redis instances create mentorhub-redis \
  --region=europe-west1 \
  --tier=standard \
  --memory-size=1 \
  --redis-version=redis-7 \
  --display-name="MentorHub Redis"
```

### 8. Создание секретов

```bash
# DATABASE_URL
echo "postgresql://mentorhub_user:PASSWORD@/mentorhub?host=/cloudsql/PROJECT_ID:europe-west1:mentorhub-db" | \
  gcloud secrets create database-url --data-file=-

# SECRET_KEY
echo "your-secret-key-here" | \
  gcloud secrets create secret-key --data-file=-

# REDIS_URL
echo "redis://REDIS_IP:6379/0" | \
  gcloud secrets create redis-url --data-file=-

# AGORA_APP_ID
echo "your-agora-app-id" | \
  gcloud secrets create agora-app-id --data-file=-

# STRIPE_API_KEY
echo "sk_test_xxx" | \
  gcloud secrets create stripe-api-key --data-file=-
```

### 9. Сборка и деплой

```bash
# Сборка образа через Cloud Build
gcloud builds submit --tag gcr.io/mentorhub-production/mentorhub:latest \
  --file=Dockerfile.production

# Деплой на Cloud Run
gcloud run deploy mentorhub \
  --image gcr.io/mentorhub-production/mentorhub:latest \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --concurrency 80 \
  --timeout 300 \
  --min-instances 1 \
  --max-instances 10 \
  --set-secrets="DATABASE_URL=database-url:latest,SECRET_KEY=secret-key:latest,REDIS_URL=redis-url:latest,AGORA_APP_ID=agora-app-id:latest,STRIPE_API_KEY=stripe-api-key:latest" \
  --set-env-vars="ENVIRONMENT=production,PORT=8000" \
  --health-cmd="curl -f http://localhost:8000/api/v1/health || exit 1" \
  --health-port 8000
```

### 10. Получение URL

```bash
gcloud run services describe mentorhub \
  --platform managed \
  --region europe-west1 \
  --format='value(status.url)'
```

## 📊 Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                    Google Cloud                         │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │            Cloud Run (Managed)                  │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │   MentorHub Service                     │   │   │
│  │  │   - Auto-scaling (1-10 instances)       │   │   │
│  │  │   - Backend + Frontend                  │   │   │
│  │  │   - Health checks                       │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │            Cloud SQL PostgreSQL                 │   │
│  │  - Multi-AZ                                     │   │
│  │  - Automated backups                            │   │
│  │  - Point-in-time recovery                       │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │            Memorystore Redis                    │   │
│  │  - Cache & Sessions                             │   │
│  │  - High availability                            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │            Secret Manager                       │   │
│  │  - DATABASE_URL                                 │   │
│  │  - SECRET_KEY                                   │   │
│  │  - REDIS_URL                                    │   │
│  │  - API Keys                                     │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │            Cloud Monitoring                     │   │
│  │  - Metrics & Logs                               │   │
│  │  - Alerts                                       │   │
│  │  - Dashboard                                    │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 🔧 Управление

### Обновление сервиса

```bash
# Сборка нового образа
gcloud builds submit --tag gcr.io/mentorhub-production/mentorhub:latest

# Деплой новой версии
gcloud run deploy mentorhub \
  --image gcr.io/mentorhub-production/mentorhub:latest \
  --platform managed \
  --region europe-west1
```

### Масштабирование

```bash
# Изменить минимальное количество инстансов
gcloud run services update mentorhub \
  --platform managed \
  --region europe-west1 \
  --min-instances 2 \
  --max-instances 20
```

### Логи

```bash
# Просмотр логов
gcloud run services logs read mentorhub \
  --platform managed \
  --region europe-west1 \
  --limit 50

# Tail логов
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=mentorhub" \
  --limit 50 \
  --format="table(timestamp,textPayload)"
```

### Метрики

```bash
# Статистика сервиса
gcloud run services describe mentorhub \
  --platform managed \
  --region europe-west1
```

## 🗄️ Бэкапы

### Cloud SQL бэкапы

```bash
# Создать бэкап
gcloud sql backups create --instance=mentorhub-db

# Список бэкапов
gcloud sql backups list --instance=mentorhub-db

# Восстановить из бэкапа
gcloud sql instances restore-from-backup mentorhub-db \
  --backup-id=BACKUP_ID
```

## ⚠️ Troubleshooting

### Ошибка: Permission denied

```bash
# Проверить IAM права
gcloud projects get-iam-policy mentorhub-production

# Добавить права
gcloud projects add-iam-policy-binding mentorhub-production \
  --member="serviceAccount:mentorhub-sa@mentorhub-production.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

### Ошибка: Health check failed

- Проверьте, что health endpoint доступен
- Увеличьте timeout
- Проверьте логи

### Ошибка: Database connection

- Проверьте, что Cloud SQL запущен
- Убедитесь, что Service Account имеет права
- Проверьте connection string

## 💰 Стоимость (примерная)

| Ресурс | Конфигурация | Стоимость/месяц |
|--------|-------------|----------------|
| Cloud Run | 2GB RAM, 1 vCPU, 730h | ~$50 |
| Cloud SQL | 2 vCPU, 4GB, 10GB SSD | ~$80 |
| Memorystore | 1GB | ~$15 |
| Cloud Storage | 10GB | ~$0.26 |
| Network Egress | 100GB | ~$12 |
| Secret Manager | 5 secrets | ~$0.30 |
| Monitoring | Standard | ~$5 |

**Итого:** ~$163/месяц

## 🔗 Полезные ссылки

- [Google Cloud Console](https://console.cloud.google.com)
- [Cloud Run Docs](https://cloud.google.com/run/docs)
- [Cloud SQL Docs](https://cloud.google.com/sql/docs)
- [gcloud CLI](https://cloud.google.com/sdk/gcloud)
- [GCP Pricing Calculator](https://cloud.google.com/products/calculator)
