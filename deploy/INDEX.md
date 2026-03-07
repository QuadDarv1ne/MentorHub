# Deploy Directory

Эта директория содержит конфигурационные файлы для автоматического деплоя MentorHub на различные платформы.

## 📁 Структура

```
deploy/
├── README.md                 # Общая документация по деплою
├── .env.template             # Шаблон переменных окружения
├── INDEX.md                  # Этот файл
├── heroku/                   # Деплой на Heroku
│   ├── app.json              # Конфигурация приложения
│   ├── Procfile              # Процессы Heroku
│   ├── runtime.txt           # Версия Python
│   ├── requirements-heroku.txt
│   └── README.md
├── railway/                  # Деплой на Railway
│   ├── railway.toml          # Конфигурация Railway
│   ├── railway.schema.json   # Схема Railway
│   └── README.md
├── render/                   # Деплой на Render
│   ├── render.yaml           # Infrastructure as Code
│   └── README.md
├── vercel/                   # Деплой frontend на Vercel
│   ├── vercel.json           # Конфигурация Vercel
│   └── README.md
├── netlify/                  # Деплой frontend на Netlify
│   ├── netlify.toml          # Конфигурация Netlify
│   ├── netlify.json          # JSON конфигурация
│   └── README.md
├── cloudflare/               # Деплой frontend на Cloudflare Pages
│   ├── wrangler.toml         # Конфигурация Wrangler
│   ├── wrangler.json         # JSON конфигурация
│   └── README.md
├── aws/                      # Деплой на AWS ECS/Fargate
│   ├── main.tf               # Terraform конфигурация
│   ├── terraform.tfvars      # Переменные Terraform
│   ├── .gitignore
│   └── README.md
└── gcp/                      # Деплой на Google Cloud Run
    ├── cloud-run.yaml        # Kubernetes манифесты
    └── README.md
```

## 🚀 Быстрый старт

### Использование скрипта деплоя

```bash
# Linux/macOS
chmod +x ../scripts/deploy.sh
../scripts/deploy.sh <platform>

# Windows PowerShell
..\scripts\deploy.ps1 -Platform <platform>
```

### Доступные платформы

- `heroku` - Heroku
- `railway` - Railway
- `render` - Render
- `aws` - AWS ECS/Fargate
- `gcp` - Google Cloud Run
- `vercel` - Vercel (frontend)
- `netlify` - Netlify (frontend)
- `cloudflare` - Cloudflare Pages (frontend)
- `docker` - Сборка Docker образа
- `all` - Деплой на все платформы

### Примеры

```bash
# Деплой на Heroku
../scripts/deploy.sh heroku

# Деплой на AWS в staging окружение
../scripts/deploy.sh aws --env staging

# Сборка Docker образа с тегом
../scripts/deploy.sh docker --tag v1.0.0

# Деплой на все платформы
../scripts/deploy.sh all --verbose
```

## 📊 Сравнение платформ

| Платформа | Сложность | Стоимость/мес | Время деплоя |
|-----------|-----------|---------------|--------------|
| Heroku | ⭐ | $64 | 5 мин |
| Railway | ⭐ | $21 | 3 мин |
| Render | ⭐ | $42 | 5 мин |
| Vercel | ⭐ | $0-20 | 2 мин |
| Netlify | ⭐ | $0-19 | 2 мин |
| Cloudflare | ⭐ | $0-5 | 2 мин |
| AWS | ⭐⭐⭐ | $153 | 30 мин |
| GCP | ⭐⭐ | $163 | 15 мин |

## 🔗 Документация

- [Общее руководство по деплою](README.md)
- [Heroku](heroku/README.md)
- [Railway](railway/README.md)
- [Render](render/README.md)
- [Vercel](vercel/README.md)
- [Netlify](netlify/README.md)
- [Cloudflare](cloudflare/README.md)
- [AWS](aws/README.md)
- [Google Cloud](gcp/README.md)

## 🔧 CI/CD

Автоматический деплой настроен через GitHub Actions:

- `.github/workflows/ci-cd.yml` - Основной pipeline
- `.github/workflows/deploy-multi-platform.yml` - Мульти-платформенный деплой

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи платформы
2. Убедитесь, что все переменные окружения установлены
3. Откройте [Issue](https://github.com/QuadDarv1ne/MentorHub/issues)

---

**MentorHub Team © 2025**
