# MentorHub — Руководство по запуску на всех платформах

**Дата обновления:** 20 марта 2026 г.  
**Версия:** 1.0.0

---

## 📋 Содержание

1. [Windows](#windows)
2. [Linux](#linux)
3. [macOS](#macos)
4. [Android (Termux)](#android-termux)
5. [iOS (iSH)](#ios-ish)
6. [Docker (Production)](#docker-production)
7. [Устранение проблем](#устранение-проблем)

---

## Windows

### Требования

- **Python 3.10+** — [Скачать](https://www.python.org/downloads/)
- **Node.js 18+** — [Скачать](https://nodejs.org/)
- **Git** — [Скачать](https://git-scm.com/)

### Development режим

**Вариант 1: PowerShell скрипт**
```powershell
.\start-dev.ps1
```

**Вариант 2: CMD скрипт**
```cmd
start-dev.bat
```

**Вариант 3: Вручную**
```cmd
REM Backend
cd backend
pip install -e .
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

REM Frontend (в новом окне)
cd frontend
npm install
npm run dev
```

**URL:**
- Backend API: http://127.0.0.1:8000
- API Docs: http://127.0.0.1:8000/docs
- Frontend: http://localhost:3001

### Production режим (Docker)

**Требования:**
- **Docker Desktop** — [Скачать](https://www.docker.com/products/docker-desktop)

**Запуск:**
```cmd
start-production.bat
```

**Или вручную:**
```cmd
docker-compose -f docker-compose.prod.yml up -d --build
```

**URL:**
- Frontend: http://localhost
- Backend API: http://localhost/api/v1
- Grafana: http://localhost:3001
- Prometheus: http://localhost:9090

---

## Linux

### Требования

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip nodejs npm git docker.io docker-compose

# Fedora/RHEL
sudo dnf install python3 python3-pip nodejs npm git docker docker-compose

# Arch Linux
sudo pacman -S python python-pip nodejs npm git docker docker-compose
```

### Development режим

**Вариант 1: Bash скрипт**
```bash
chmod +x start-dev.sh
./start-dev.sh
```

**Вариант 2: Вручную**
```bash
# Backend
cd backend
pip3 install -e .
PORT=8000 uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &

# Frontend
cd frontend
npm install
PORT=3001 npm run dev &
```

**URL:**
- Backend API: http://127.0.0.1:8000
- API Docs: http://127.0.0.1:8000/docs
- Frontend: http://localhost:3001

### Production режим (Docker)

**Запуск:**
```bash
chmod +x start-production.sh
./start-production.sh
```

**Или вручную:**
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

**Остановка:**
```bash
docker compose -f docker-compose.prod.yml down
```

**Просмотр логов:**
```bash
docker compose -f docker-compose.prod.yml logs -f
```

---

## macOS

### Требования

**Установка через Homebrew:**
```bash
# Установка Homebrew (если нет)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Установка зависимостей
brew install python3 node git docker
```

### Development режим

**Вариант 1: Bash скрипт**
```bash
chmod +x start-dev.sh
./start-dev.sh
```

**Вариант 2: Вручную**
```bash
# Backend
cd backend
pip3 install -e .
PORT=8000 uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &

# Frontend
cd frontend
npm install
PORT=3001 npm run dev &
```

**URL:**
- Backend API: http://127.0.0.1:8000
- API Docs: http://127.0.0.1:8000/docs
- Frontend: http://localhost:3001

### Production режим (Docker)

**Требования:**
- **Docker Desktop для Mac** — [Скачать](https://www.docker.com/products/docker-desktop)

**Запуск:**
```bash
./start-production.sh
```

**Или вручную:**
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

---

## Android (Termux)

### Требования

- **Termux** — [F-Droid](https://f-droid.org/packages/com.termux/) или [Google Play](https://play.google.com/store/apps/details?id=com.termux)

### Установка зависимостей

```bash
# Обновление пакетов
pkg update && pkg upgrade

# Установка Python и Node.js
pkg install python nodejs git

# Установка дополнительных утилит (опционально)
pkg install postgresql curl netcat-openbsd
```

### Development режим

**Вариант 1: Скрипт для Termux**
```bash
chmod +x start-android.sh
./start-android.sh
```

**Вариант 2: Вручную**
```bash
# Клонирование репозитория
git clone https://github.com/QuadDarv1ne/MentorHub.git
cd MentorHub

# Backend
cd backend
pip install -e .
PORT=8000 uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Frontend
cd frontend
npm install
PORT=3001 npm run dev &
```

**URL:**
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3001

### Оптимизация для Android

```bash
# Ограничение памяти для Node.js
export NODE_OPTIONS="--max-old-space-size=512"

# Оптимизация Python
export PYTHONMALLOC=malloc
export PYTHONDONTWRITEBYTECODE=1
```

### Остановка

```bash
# Найти PID процессов
ps -A | grep -E 'node|uvicorn|python'

# Остановить процессы
kill <PID>
```

---

## iOS (iSH)

### Требования

- **iSH Shell** — [App Store](https://apps.apple.com/app/ish-shell/id1436902243)

### Установка зависимостей

```bash
# Обновление пакетов
apk update

# Установка Python и Node.js
apk add python3 py3-pip nodejs npm git
```

### Development режим

**Вариант 1: Скрипт для iSH**
```bash
chmod +x start-ios.sh
./start-ios.sh
```

**Вариант 2: Вручную**
```bash
# Клонирование репозитория
git clone https://github.com/QuadDarv1ne/MentorHub.git
cd MentorHub

# Backend
cd backend
pip3 install uvicorn fastapi python-dotenv
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Frontend
cd frontend
npm install
PORT=3001 npm run dev &
```

**URL:**
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3001

### Оптимизация для iOS

```bash
# Ограничение памяти для Node.js
export NODE_OPTIONS="--max-old-space-size=256"

# Отключение байт-кода Python
export PYTHONDONTWRITEBYTECODE=1
```

### Остановка

```bash
# Найти PID процессов
ps | grep -E 'node|python'

# Остановить процессы
kill <PID>
```

### ⚠ Ограничения iSH

- Производительность ограничена эмуляцией x86 на ARM
- Рекомендуется только для тестирования
- Не подходит для production нагрузки

---

## Docker (Production)

### Требования

- **Docker** 20.10+
- **Docker Compose** 2.0+

### Быстрый старт

```bash
# Клонирование репозитория
git clone https://github.com/QuadDarv1ne/MentorHub.git
cd MentorHub

# Копирование .env
cp .env.example .env

# Редактирование .env (обязательно установите SECRET_KEY и DB_PASSWORD)
nano .env

# Запуск всех сервисов
docker compose -f docker-compose.prod.yml up -d --build

# Проверка статуса
docker compose -f docker-compose.prod.yml ps
```

### Сервисы

| Сервис | Порт | Описание |
|--------|------|----------|
| Nginx | 80, 443 | Reverse Proxy |
| Backend | 8000 | FastAPI API |
| Frontend | 3000 | Next.js UI |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache |
| Celery Worker | - | Background Tasks |
| Celery Beat | - | Scheduled Tasks |
| Prometheus | 9090 | Metrics |
| Grafana | 3001 | Dashboards |

### Управление

```bash
# Остановка
docker compose -f docker-compose.prod.yml down

# Перезапуск
docker compose -f docker-compose.prod.yml restart

# Просмотр логов
docker compose -f docker-compose.prod.yml logs -f

# Логи конкретного сервиса
docker compose -f docker-compose.prod.yml logs backend

# Обновление
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d --build
```

### Безопасность

```bash
# Обязательно измените в .env:
SECRET_KEY=<сложный_секретный_ключ>
DB_PASSWORD=<сложный_пароль>
GRAFANA_ADMIN_PASSWORD=<сложный_пароль>
```

---

## Устранение проблем

### Windows

**Проблема:** Python не найден
```cmd
# Проверка установки
python --version

# Если не работает, добавьте Python в PATH
# Панель управления → Система → Дополнительные параметры → Переменные среды
# Добавьте C:\Python310\ и C:\Python310\Scripts\ в PATH
```

**Проблема:** npm не найден
```cmd
# Переустановка Node.js
# Скачайте с https://nodejs.org/ и установите заново
```

**Проблема:** Docker не запускается
```cmd
# Включите виртуализацию в BIOS
# Проверьте Hyper-V: dism.exe /Online /Get-Features | find "Hyper-V"
```

### Linux

**Проблема:** Permission denied при запуске Docker
```bash
# Добавьте пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker
```

**Проблема:** Порт уже занят
```bash
# Проверка占用 порта
sudo lsof -i :8000
sudo lsof -i :3000

# Остановка процесса
sudo kill <PID>
```

**Проблема:** Недостаточно памяти
```bash
# Добавление swap файла
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### macOS

**Проблема:** Docker не запускается
```bash
# Перезапуск Docker Desktop
open -a Docker

# Или через терминал
killall Docker
open -a Docker
```

**Проблема:** Ошибки при установке npm
```bash
# Очистка кэша npm
npm cache clean --force

# Переустановка node_modules
rm -rf node_modules package-lock.json
npm install
```

### Android (Termux)

**Проблема:** Недостаточно памяти
```bash
# Проверка памяти
free -h

# Остановка ненужных процессов
ps -A
kill <PID>
```

**Проблема:** Ошибки компиляции
```bash
# Установка build инструментов
pkg install build-tools clang llvm
```

### iOS (iSH)

**Проблема:** Медленная работа
- iSH эмулирует x86 на ARM, что медленно
- Используйте для тестирования, не production
- Рассмотрите удалённый сервер вместо локального запуска

**Проблема:** Недостаточно памяти
```bash
# Проверка памяти
free -h

# Остановка процессов
ps | grep node
kill <PID>
```

### Общие проблемы

**Проблема:** .env файл не найден
```bash
# Копирование из примера
cp .env.example .env

# Редактирование
nano .env
```

**Проблема:** Миграции базы данных
```bash
# Запуск миграций
cd backend
alembic upgrade head
```

**Проблема:** Ошибки CORS
```bash
# Проверьте CORS_ORIGINS в .env
CORS_ORIGINS=http://localhost:3001,http://127.0.0.1:3001
```

---

## 📞 Поддержка

- **GitHub Issues:** https://github.com/QuadDarv1ne/MentorHub/issues
- **Документация:** https://github.com/QuadDarv1ne/MentorHub/tree/main/docs

---

## 📝 Чек-лист перед запуском

- [ ] Python 3.10+ установлен
- [ ] Node.js 18+ установлен
- [ ] Git установлен
- [ ] .env файл создан и настроен
- [ ] SECRET_KEY установлен
- [ ] DB_PASSWORD установлен
- [ ] Порты 8000, 3000/3001 свободны
- [ ] Достаточно памяти (минимум 2GB RAM)
- [ ] Достаточно места на диске (минимум 5GB)
