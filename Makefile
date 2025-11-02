.PHONY: help install install-backend install-frontend dev dev-backend dev-frontend build test clean docker-up docker-down docker-build migrate migrate-up migrate-down lint format type-check setup

help: ## Показать эту справку
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# ==================== INSTALLATION ====================

install: install-backend install-frontend ## Установить все зависимости

install-backend: ## Установить зависимости backend
	cd backend && python -m venv venv || true
	cd backend && source venv/bin/activate || .\venv\Scripts\activate || true
	cd backend && pip install --upgrade pip
	cd backend && pip install -r requirements.txt

install-frontend: ## Установить зависимости frontend
	cd frontend && npm install

# ==================== DEVELOPMENT ====================

dev: ## Запустить backend и frontend в режиме разработки
	@echo "Запуск в режиме разработки..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "API Docs: http://localhost:8000/docs"
	docker-compose up

dev-backend: ## Запустить только backend
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Запустить только frontend
	cd frontend && npm run dev

# ==================== BUILDING ====================

build: build-backend build-frontend ## Собрать проект

build-backend: ## Собрать backend
	cd backend && pip install -r requirements.txt

build-frontend: ## Собрать frontend
	cd frontend && npm run build

# ==================== TESTING ====================

test: test-backend test-frontend ## Запустить все тесты

test-backend: ## Запустить тесты backend
	cd backend && pytest tests/ -v --cov=app --cov-report=html

test-frontend: ## Запустить тесты frontend
	cd frontend && npm run test

test-watch: ## Запустить тесты в watch режиме
	cd backend && pytest tests/ -v --watch || cd frontend && npm run test:watch

# ==================== CODE QUALITY ====================

lint: lint-backend lint-frontend ## Проверить код линтерами

lint-backend: ## Проверить код backend
	cd backend && flake8 app/ --max-line-length=120 --exclude=__pycache__,migrations
	cd backend && black --check app/ || true
	cd backend && isort --check-only app/ || true

lint-frontend: ## Проверить код frontend
	cd frontend && npm run lint

format: format-backend format-frontend ## Форматировать код

format-backend: ## Форматировать код backend
	cd backend && black app/
	cd backend && isort app/

format-frontend: ## Форматировать код frontend
	cd frontend && npm run format

type-check: type-check-backend type-check-frontend ## Проверить типы

type-check-backend: ## Проверить типы backend
	cd backend && mypy app/ --ignore-missing-imports || true

type-check-frontend: ## Проверить типы frontend
	cd frontend && npm run type-check

# ==================== DATABASE ====================

migrate: ## Создать новую миграцию
	cd backend && alembic revision --autogenerate -m "$(msg)"

migrate-up: ## Применить миграции
	cd backend && alembic upgrade head

migrate-down: ## Откатить последнюю миграцию
	cd backend && alembic downgrade -1

migrate-history: ## Показать историю миграций
	cd backend && alembic history

# ==================== DOCKER ====================

docker-up: ## Запустить Docker контейнеры
	docker-compose up -d

docker-down: ## Остановить Docker контейнеры
	docker-compose down

docker-build: ## Собрать Docker образы
	docker-compose build

docker-logs: ## Показать логи Docker
	docker-compose logs -f

docker-clean: ## Очистить Docker (остановить и удалить volumes)
	docker-compose down -v

# ==================== SETUP ====================

setup: ## Первоначальная настройка проекта
	@echo "Настройка проекта MentorHub..."
	@echo "Создание .env файлов..."
	@test -f backend/.env || cp backend/.env.example backend/.env
	@test -f frontend/.env.local || cp frontend/.env.example frontend/.env.local
	@echo "Установка зависимостей..."
	@$(MAKE) install
	@echo "✅ Настройка завершена!"
	@echo "📝 Не забудьте отредактировать .env файлы"

setup-db: ## Настроить базу данных
	@echo "Настройка базы данных..."
	docker-compose up -d postgres redis
	@echo "Ожидание запуска PostgreSQL..."
	@sleep 5
	cd backend && alembic upgrade head
	@echo "✅ База данных настроена!"

# ==================== CLEANUP ====================

clean: ## Очистить временные файлы
	find . -type d -name __pycache__ -exec rm -r {} + || true
	find . -type f -name "*.pyc" -delete || true
	find . -type d -name "*.egg-info" -exec rm -r {} + || true
	find . -type d -name ".pytest_cache" -exec rm -r {} + || true
	find . -type d -name ".mypy_cache" -exec rm -r {} + || true
	rm -rf backend/htmlcov/ || true
	rm -rf frontend/.next/ || true
	rm -rf frontend/coverage/ || true

clean-all: clean docker-clean ## Полная очистка (включая Docker)
	rm -rf backend/venv/ || true
	rm -rf frontend/node_modules/ || true

# ==================== UTILITIES ====================

shell-backend: ## Открыть Python shell для backend
	cd backend && source venv/bin/activate && python

shell-db: ## Открыть PostgreSQL shell
	docker-compose exec postgres psql -U mentorhub_user -d mentorhub

logs-backend: ## Показать логи backend
	docker-compose logs -f backend

logs-frontend: ## Показать логи frontend
	docker-compose logs -f frontend

restart: docker-down docker-up ## Перезапустить Docker контейнеры

status: ## Показать статус сервисов
	docker-compose ps

