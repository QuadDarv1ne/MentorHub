# AWS ECS/Fargate Deployment Guide

## 📋 Требования

- AWS аккаунт
- Установленный AWS CLI
- Установленный Terraform
- Docker

## 🚀 Быстрый старт

### 1. Установка инструментов

```bash
# AWS CLI
# Windows: https://aws.amazon.com/cli/
# macOS: brew install awscli
# Linux: curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"

# Terraform
# Windows: choco install terraform
# macOS: brew install terraform
# Linux: sudo apt-get install terraform

# Docker
# https://docs.docker.com/get-docker/
```

### 2. Аутентификация в AWS

```bash
aws configure
# AWS Access Key ID: [your-key]
# AWS Secret Access Key: [your-secret]
# Default region name: eu-central-1
# Default output format: json
```

### 3. Создание ECR репозитория

```bash
aws ecr create-repository --repository-name mentorhub --region eu-central-1
```

### 4. Сборка и пуш Docker образа

```bash
# Логин в ECR
aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.eu-central-1.amazonaws.com

# Сборка образа
docker build -t mentorhub -f Dockerfile.production .

# Тегирование
docker tag mentorhub:latest your-account.dkr.ecr.eu-central-1.amazonaws.com/mentorhub:latest

# Пуш
docker push your-account.dkr.ecr.eu-central-1.amazonaws.com/mentorhub:latest
```

### 5. Настройка Terraform

```bash
cd deploy/aws

# Скопируйте пример переменных
cp terraform.tfvars.example terraform.tfvars

# Отредактируйте переменные
# - docker_image: ваш ECR URL
# - db_password: надежный пароль
# - secret_key: надежный секретный ключ
```

### 6. Деплой инфраструктуры

```bash
# Инициализация Terraform
terraform init

# Проверка плана
terraform plan

# Применение
terraform apply

# Введите "yes" когда спросит подтверждение
```

### 7. Получение URL приложения

```bash
terraform output alb_dns_name
# http://mentorhub-production-alb-123456789.eu-central-1.elb.amazonaws.com
```

## 📊 Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                         AWS                                 │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    VPC                              │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │            Public Subnets                   │   │   │
│  │  │  ┌──────────────────────────────────────┐  │   │   │
│  │  │  │     Application Load Balancer        │  │   │   │
│  │  │  │         (Port 80/443)                │  │   │   │
│  │  │  └──────────────────────────────────────┘  │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  │                                                     │   │
│  │  ┌─────────────────────────────────────────────┐   │   │
│  │  │           Private Subnets                   │   │   │
│  │  │  ┌──────────────────────────────────────┐  │   │   │
│  │  │  │      ECS Fargate Tasks (x2)          │  │   │   │
│  │  │  │      - Backend API                   │  │   │   │
│  │  │  │      - Frontend (Next.js)            │  │   │   │
│  │  │  └──────────────────────────────────────┘  │   │   │
│  │  │  ┌──────────────────────────────────────┐  │   │   │
│  │  │  │      Amazon RDS PostgreSQL           │  │   │   │
│  │  │  │      (Multi-AZ)                      │  │   │   │
│  │  │  └──────────────────────────────────────┘  │   │   │
│  │  │  ┌──────────────────────────────────────┐  │   │   │
│  │  │  │     ElastiCache Redis                │  │   │   │
│  │  │  └──────────────────────────────────────┘  │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Secrets Manager                        │   │
│  │  - DATABASE_URL                                     │   │
│  │  - REDIS_URL                                        │   │
│  │  - SECRET_KEY                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              CloudWatch Logs                        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Управление

### Обновление приложения

```bash
# Сборка нового образа
docker build -t mentorhub -f Dockerfile.production .
docker tag mentorhub:latest your-account.dkr.ecr.eu-central-1.amazonaws.com/mentorhub:latest
docker push your-account.dkr.ecr.eu-central-1.amazonaws.com/mentorhub:latest

# Обновление сервиса
aws ecs update-service \
  --cluster mentorhub-production-cluster \
  --service mentorhub-production-service \
  --force-new-deployment \
  --region eu-central-1
```

### Масштабирование

```bash
# Увеличить количество задач
aws ecs update-service \
  --cluster mentorhub-production-cluster \
  --service mentorhub-production-service \
  --desired-count 4 \
  --region eu-central-1

# Или через Terraform
terraform apply -var="desired_count=4"
```

### Логи

```bash
# CloudWatch Logs
aws logs tail /ecs/mentorhub --follow --region eu-central-1
```

### Подключение к БД

```bash
# Получить endpoint
terraform output rds_endpoint

# Подключиться
psql -h <rds-endpoint> -U mentorhub_admin -d mentorhub
```

## 🗄️ Бэкапы

### Автоматические бэкапы RDS

```bash
# Создать snapshot
aws rds create-db-snapshot \
  --db-instance-identifier mentorhub-production-db \
  --db-snapshot-identifier mentorhub-snapshot-$(date +%Y%m%d) \
  --region eu-central-1

# Список snapshot'ов
aws rds describe-db-snapshots \
  --db-instance-identifier mentorhub-production-db \
  --region eu-central-1
```

## ⚠️ Troubleshooting

### Ошибка: Task failed to start

```bash
# Проверить логи задач
aws ecs describe-tasks \
  --cluster mentorhub-production-cluster \
  --tasks <task-arn> \
  --region eu-central-1
```

### Ошибка: Health check failed

- Проверьте, что приложение слушает правильный порт
- Убедитесь, что health endpoint доступен
- Проверьте security groups

### Ошибка: Database connection

- Проверьте, что RDS запущен
- Убедитесь, что security group разрешает подключение
- Проверьте DATABASE_URL в Secrets Manager

## 💰 Стоимость (примерная)

| Ресурс | Конфигурация | Стоимость/месяц |
|--------|-------------|----------------|
| ECS Fargate | 2 x 1 vCPU, 2GB | ~$60 |
| RDS PostgreSQL | db.t3.medium | ~$50 |
| ElastiCache Redis | cache.t3.micro | ~$12 |
| ALB | Application LB | ~$17 |
| S3 | 10GB | ~$0.23 |
| CloudWatch | Logs | ~$5 |
| Data Transfer | 100GB | ~$9 |

**Итого:** ~$153/месяц

## 🔗 Полезные ссылки

- [AWS Console](https://console.aws.amazon.com)
- [ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws)
- [AWS Pricing Calculator](https://calculator.aws/)
