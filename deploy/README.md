# 📚 Руководство по деплою MentorHub

Полное руководство по развертыванию платформы MentorHub на различных платформах.

## 📋 Оглавление

- [Обзор](#обзор)
- [Быстрый старт](#быстрый-старт)
- [Платформы](#платформы)
- [Сравнение платформ](#сравнение-платформ)
- [Автоматизация](#автоматизация)
- [Troubleshooting](#troubleshooting)

---

## 📖 Обзор

MentorHub поддерживает деплой на следующие платформы:

| Платформа | Сложность | Стоимость | Масштабируемость |
|-----------|-----------|-----------|------------------|
| **Heroku** | ⭐ Низкая | $$$ | Средняя |
| **Railway** | ⭐ Низкая | $$ | Средняя |
| **Render** | ⭐ Низкая | $$ | Средняя |
| **Vercel** | ⭐ Низкая | $-$$ | Высокая |
| **Netlify** | ⭐ Низкая | $-$$ | Высокая |
| **Cloudflare** | ⭐ Низкая | $ | Очень высокая |
| **AWS** | ⭐⭐⭐ Высокая | $$-$$$ | Очень высокая |
| **Google Cloud** | ⭐⭐ Средняя | $$-$$$ | Очень высокая |

---

## 🚀 Быстрый старт

### Требования

- Docker
- Git
- Аккаунт на выбранной платформе

### 1. Клонирование репозитория

```bash
git clone https://github.com/QuadDarv1ne/MentorHub.git
cd MentorHub
```

### 2. Настройка окружения

```bash
# Скопируйте пример
cp .env.example .env

# Отредактируйте .env
# SECRET_KEY=your-secret-key
# DATABASE_URL=postgresql://...
# REDIS_URL=redis://...
```

### 3. Быстрый деплой (скрипт)

```bash
# Linux/macOS
chmod +x scripts/deploy.sh
./scripts/deploy.sh <platform>

# Windows PowerShell
.\scripts\deploy.ps1 -Platform <platform>
```

---

## 🌐 Платформы

### Heroku

**Лучше всего подходит для:** Быстрого старта и MVP

```bash
cd deploy/heroku

# 1. Создание приложения
heroku create mentorhub-your-name

# 2. Добавление аддонов
heroku addons:create heroku-postgresql:essential-0
heroku addons:create heroku-redis:mini

# 3. Деплой
git push heroku main
```

📄 [Подробная инструкция →](heroku/README.md)

---

### Railway

**Лучше всего подходит для:** Простого деплоя с GitHub

```bash
# 1. Подключите репозиторий в Railway Dashboard
# 2. Добавьте переменные окружения
# 3. Railway автоматически задеплоит
```

📄 [Подробная инструкция →](railway/README.md)

---

### Render

**Лучше всего подходит для:** Автоматического деплоя из GitHub

```yaml
# render.yaml автоматически настроит:
# - Backend (FastAPI)
# - Frontend (Next.js)
# - PostgreSQL
# - Redis
# - Worker (Celery)
```

📄 [Подробная инструкция →](render/README.md)

---

### Vercel

**Лучше всего подходит для:** Frontend (Next.js)

```bash
cd frontend

# Деплой через CLI
vercel

# Production деплой
vercel --prod
```

📄 [Подробная инструкция →](vercel/README.md)

---

### Netlify

**Лучше всего подходит для:** Frontend (Next.js) с отличной производительностью

```bash
cd frontend

# Деплой через CLI
netlify deploy --prod

# Или через Dashboard
# 1. Подключите репозиторий
# 2. Настройте сборку
# 3. Netlify автоматически задеплоит
```

📄 [Подробная инструкция →](netlify/README.md)

---

### Cloudflare Pages

**Лучше всего подходит для:** Frontend с глобальным CDN

```bash
cd frontend

# Деплой через Wrangler
wrangler pages deploy .next --project-name=mentorhub

# Или через Dashboard
# 1. Подключите репозиторий
# 2. Настройте сборку
# 3. Cloudflare автоматически задеплоит
```

📄 [Подробная инструкция →](cloudflare/README.md)

---

### AWS (ECS/Fargate)

**Лучше всего подходит для:** Production с высокой нагрузкой

```bash
cd deploy/aws

# 1. Настройка Terraform
terraform init
terraform plan

# 2. Деплой инфраструктуры
terraform apply

# 3. Деплой приложения
docker push <ECR_URL>
aws ecs update-service --force-new-deployment
```

📄 [Подробная инструкция →](aws/README.md)

---

### Google Cloud Run

**Лучше всего подходит для:** Serverless production

```bash
# 1. Сборка и пуш
gcloud builds submit --tag gcr.io/PROJECT_ID/mentorhub

# 2. Деплой
gcloud run deploy mentorhub \
  --image gcr.io/PROJECT_ID/mentorhub \
  --platform managed
```

📄 [Подробная инструкция →](gcp/README.md)

---

## 📊 Сравнение платформ

### Стоимость (месяц)

| Платформа | Dev | Production | Enterprise |
|-----------|-----|------------|------------|
| Heroku | $25 | $64 | $200+ |
| Railway | $5 | $21 | $100+ |
| Render | $14 | $42 | $150+ |
| Vercel | $0 | $20 | $100+ |
| Netlify | $0 | $19 | $100+ |
| Cloudflare | $0 | $5 | $200+ |
| AWS | $50 | $153 | $500+ |
| GCP | $50 | $163 | $500+ |

### Время деплоя

| Платформа | Первый деплой | Обновление |
|-----------|---------------|------------|
| Heroku | 5 мин | 2 мин |
| Railway | 3 мин | 1 мин |
| Render | 5 мин | 2 мин |
| Vercel | 2 мин | 30 сек |
| Netlify | 2 мин | 30 сек |
| Cloudflare | 2 мин | 30 сек |
| AWS | 30 мин | 5 мин |
| GCP | 15 мин | 3 мин |

### Масштабируемость

| Платформа | Auto-scaling | Max replicas | Cold start |
|-----------|--------------|--------------|------------|
| Heroku | ✅ | 50 | Нет |
| Railway | ✅ | 20 | Нет |
| Render | ✅ | 20 | Нет |
| Vercel | ✅ | 1000+ | ~100ms |
| Netlify | ✅ | 1000+ | ~100ms |
| Cloudflare | ✅ | 1000+ | ~50ms |
| AWS | ✅ | 1000+ | Нет |
| GCP | ✅ | 1000+ | ~100ms |

---

## 🤖 Автоматизация

### GitHub Actions

Автоматический деплой при пуше в main:

```yaml
# .github/workflows/ci-cd.yml
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # ... деплой
```

### Скрипты деплоя

```bash
# Деплой на все платформы
./scripts/deploy.sh all

# Деплой на конкретную платформу
./scripts/deploy.sh heroku --env production

# Сборка Docker образа
./scripts/deploy.sh docker --tag v1.0.0
```

---

## 🔧 Troubleshooting

### Общие проблемы

#### Ошибка: Build failed

```bash
# Проверьте логи
docker build -t mentorhub -f Dockerfile.production . 2>&1 | tee build.log

# Очистите кэш
docker builder prune -a
```

#### Ошибка: Health check failed

```bash
# Проверьте health endpoint
curl http://localhost:8000/api/v1/health

# Увеличьте timeout в конфигурации
```

#### Ошибка: Database connection

```bash
# Проверьте DATABASE_URL
echo $DATABASE_URL

# Проверьте доступность БД
psql $DATABASE_URL -c "SELECT 1"
```

### Платформо-специфичные проблемы

#### Heroku: H14 (Web process crashed)

```bash
heroku restart
heroku logs --tail
```

#### AWS: Task failed to start

```bash
aws ecs describe-tasks \
  --cluster mentorhub-cluster \
  --tasks <task-arn>
```

#### GCP: Permission denied

```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SERVICE_ACCOUNT" \
  --role="roles/run.invoker"
```

---

## 📞 Поддержка

Если возникли проблемы:

1. Проверьте логи платформы
2. Посмотрите [документацию](#платформы)
3. Откройте [Issue](https://github.com/QuadDarv1ne/MentorHub/issues)

---

## 🔗 Полезные ссылки

- [Основной README](../../README.md)
- [CONTRIBUTING](../../CONTRIBUTING.md)
- [CHANGELOG](../../CHANGELOG.md)
- [GitHub Actions Docs](https://docs.github.com/en/actions)

---

**Made with ❤️ by MentorHub Team**
