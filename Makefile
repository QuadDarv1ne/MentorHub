# MentorHub - Development Makefile
# Convenient commands for development, testing, and deployment

.PHONY: help install dev test clean docker-up docker-down backup restore security lint format

# Colors
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)MentorHub - Available Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# ==================== SETUP ====================

setup: ## Initial project setup (create .env with auto-detected ports)
	@echo "$(BLUE)Setting up MentorHub...$(NC)"
	@bash scripts/auto-ports.sh

# ==================== INSTALLATION ====================

install: ## Install all dependencies (backend + frontend)
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	cd backend && pip install -r requirements.txt
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN)✓ All dependencies installed$(NC)"

install-backend: ## Install backend dependencies only
	@echo "$(BLUE)Installing backend dependencies...$(NC)"
	cd backend && pip install -r requirements.txt
	@echo "$(GREEN)✓ Backend dependencies installed$(NC)"

install-frontend: ## Install frontend dependencies only
	@echo "$(BLUE)Installing frontend dependencies...$(NC)"
	cd frontend && npm install
	@echo "$(GREEN)✓ Frontend dependencies installed$(NC)"

# ==================== DEVELOPMENT ====================

dev: ## Start development servers (backend + frontend)
	@echo "$(BLUE)Starting development servers...$(NC)"
	@make -j2 dev-backend dev-frontend

dev-backend: ## Start backend development server
	@echo "$(BLUE)Starting backend server...$(NC)"
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend development server
	@echo "$(BLUE)Starting frontend server...$(NC)"
	cd frontend && npm run dev

# ==================== TESTING ====================

test: ## Run all tests (backend + frontend)
	@echo "$(BLUE)Running all tests...$(NC)"
	@make test-backend
	@make test-frontend
	@echo "$(GREEN)✓ All tests completed$(NC)"

test-backend: ## Run backend tests with coverage
	@echo "$(BLUE)Running backend tests...$(NC)"
	cd backend && pytest -v --cov=app --cov-report=term-missing --cov-report=html

test-frontend: ## Run frontend tests
	@echo "$(BLUE)Running frontend tests...$(NC)"
	cd frontend && npm test

test-coverage: ## Generate test coverage report
	@echo "$(BLUE)Generating coverage report...$(NC)"
	cd backend && pytest --cov=app --cov-report=html --cov-report=xml
	@echo "$(GREEN)✓ Coverage report generated in backend/htmlcov/$(NC)"

test-load: ## Run load tests with k6
	@echo "$(BLUE)Running load tests...$(NC)"
	k6 run k6-load-test.js

# ==================== CODE QUALITY ====================

lint: ## Run linters (backend + frontend)
	@echo "$(BLUE)Running linters...$(NC)"
	@make lint-backend
	@make lint-frontend
	@echo "$(GREEN)✓ Linting completed$(NC)"

lint-backend: ## Run backend linters
	@echo "$(BLUE)Running backend linters...$(NC)"
	cd backend && flake8 app --max-line-length=120
	cd backend && mypy app --config-file=pyproject.toml

lint-frontend: ## Run frontend linters
	@echo "$(BLUE)Running frontend linters...$(NC)"
	cd frontend && npm run lint

format: ## Format code (backend + frontend)
	@echo "$(BLUE)Formatting code...$(NC)"
	@make format-backend
	@make format-frontend
	@echo "$(GREEN)✓ Code formatted$(NC)"

format-backend: ## Format backend code with black and isort
	@echo "$(BLUE)Formatting backend code...$(NC)"
	cd backend && black app --line-length=120
	cd backend && isort app --profile=black

format-frontend: ## Format frontend code with prettier
	@echo "$(BLUE)Formatting frontend code...$(NC)"
	cd frontend && npm run format

security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	cd backend && safety check
	cd backend && bandit -r app -ll
	cd frontend && npm audit
	@echo "$(GREEN)✓ Security checks completed$(NC)"

# ==================== DOCKER ====================

docker-build: ## Build Docker images
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build
	@echo "$(GREEN)✓ Docker images built$(NC)"

docker-up: ## Start Docker containers (development)
	@echo "$(BLUE)Starting Docker containers...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)⚠ .env not found. Running setup...$(NC)"; \
		make setup; \
	fi
	docker-compose up -d
	@echo "$(GREEN)✓ Docker containers started$(NC)"
	@make docker-status

docker-down: ## Stop Docker containers
	@echo "$(BLUE)Stopping Docker containers...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Docker containers stopped$(NC)"

docker-prod: ## Start production Docker containers
	@echo "$(BLUE)Starting production containers...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)⚠ .env not found. Running setup...$(NC)"; \
		make setup; \
	fi
	docker-compose -f docker-compose.prod.yml up -d
	@echo "$(GREEN)✓ Production containers started$(NC)"

docker-logs: ## Show Docker logs
	docker-compose logs -f

docker-clean: ## Clean Docker resources
	@echo "$(YELLOW)Cleaning Docker resources...$(NC)"
	docker-compose down -v
	docker system prune -f
	@echo "$(GREEN)✓ Docker resources cleaned$(NC)"

docker-restart: docker-down docker-up ## Restart Docker containers

docker-status: ## Show running containers and ports
	@echo "$(BLUE)Running containers:$(NC)"
	@docker ps --filter "name=mentorhub" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@if [ -f .env ]; then \
		echo "$(BLUE)Configured ports from .env:$(NC)"; \
		@grep -E '^(BACKEND|FRONTEND|DB|REDIS|NGINX|PROMETHEUS|GRAFANA)_PORT=' .env 2>/dev/null | while read line; do \
			echo "  $$line"; \
		done; \
	fi

# ==================== DATABASE ====================

db-migrate: ## Run database migrations
	@echo "$(BLUE)Running database migrations...$(NC)"
	cd backend && alembic upgrade head
	@echo "$(GREEN)✓ Migrations completed$(NC)"

db-rollback: ## Rollback last migration
	@echo "$(YELLOW)Rolling back last migration...$(NC)"
	cd backend && alembic downgrade -1
	@echo "$(GREEN)✓ Rollback completed$(NC)"

db-reset: ## Reset database (drop and recreate)
	@echo "$(RED)WARNING: This will delete all data!$(NC)"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ]
	cd backend && alembic downgrade base
	cd backend && alembic upgrade head
	@echo "$(GREEN)✓ Database reset completed$(NC)"

backup: ## Create database backup
	@echo "$(BLUE)Creating database backup...$(NC)"
	./scripts/backup.sh
	@echo "$(GREEN)✓ Backup completed$(NC)"

restore: ## Restore database from backup
	@echo "$(YELLOW)Restoring database...$(NC)"
	@read -p "Enter backup file path: " backup_file && ./scripts/restore.sh $$backup_file
	@echo "$(GREEN)✓ Restore completed$(NC)"

# ==================== DEPLOYMENT ====================

deploy-staging: ## Deploy to staging environment
	@echo "$(BLUE)Deploying to staging...$(NC)"
	git push origin dev
	@echo "$(GREEN)✓ Deployed to staging$(NC)"

deploy-production: ## Deploy to production environment
	@echo "$(RED)Deploying to production...$(NC)"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ]
	git checkout main
	git merge dev
	git push origin main
	@echo "$(GREEN)✓ Deployed to production$(NC)"

# ==================== CLEANUP ====================

clean: ## Clean temporary files and caches
	@echo "$(BLUE)Cleaning temporary files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	cd frontend && rm -rf .next node_modules/.cache 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup completed$(NC)"

clean-all: clean docker-clean ## Clean everything including Docker
	@echo "$(GREEN)✓ Full cleanup completed$(NC)"

# ==================== MONITORING ====================

logs: ## Show application logs
	@echo "$(BLUE)Showing logs...$(NC)"
	docker-compose logs -f backend

logs-backend: ## Show backend logs
	docker-compose logs -f backend

logs-frontend: ## Show frontend logs
	docker-compose logs -f frontend

logs-db: ## Show database logs
	docker-compose logs -f postgres

logs-redis: ## Show Redis logs
	docker-compose logs -f redis

# ==================== UTILITIES ====================

shell-backend: ## Open backend shell
	cd backend && python -m app.main

shell-db: ## Open database shell
	docker-compose exec postgres psql -U mentorhub_user -d mentorhub

shell-redis: ## Open Redis CLI
	docker-compose exec redis redis-cli

check: ## Run all checks (lint + test + security)
	@echo "$(BLUE)Running all checks...$(NC)"
	@make lint
	@make test
	@make security
	@echo "$(GREEN)✓ All checks passed$(NC)"

# ==================== PORTS ====================

ports-auto: ## Auto-detect free ports and generate .env
	@bash scripts/auto-ports.sh

ports-validate: ## Validate if configured ports are available
	@bash scripts/validate-ports.sh

ports-show: ## Show current port configuration
	@echo "$(BLUE)Current port configuration:$(NC)"
	@if [ -f .env ]; then \
		echo ""; \
		echo "$(CYAN)From .env:$(NC)"; \
		@grep -E '^(BACKEND|FRONTEND|DB|REDIS|NGINX|PROMETHEUS|GRAFANA)_PORT=' .env 2>/dev/null || echo "  $(YELLOW)No port variables found$(NC)"; \
	else \
		echo "  $(YELLOW).env file not found$(NC)"; \
		echo "  $(CYAN)Run 'make ports-auto' to generate$(NC)"; \
	fi
	@echo ""
	@echo "$(CYAN)Currently listening ports:$(NC)"
	@if command -v netstat &> /dev/null; then \
		netstat -tln 2>/dev/null | grep -E '(8000|3000|3001|5432|6379|9090|80|443)' || echo "  No matching ports found"; \
	elif command -v ss &> /dev/null; then \
		ss -tln 2>/dev/null | grep -E '(8000|3000|3001|5432|6379|9090|80|443)' || echo "  No matching ports found"; \
	else \
		echo "  $(YELLOW)netstat/ss not available$(NC)"; \
	fi

ports-change: ## Change ports interactively
	@echo "$(BLUE)Interactive port configuration$(NC)"
	@echo "Enter new ports (press Enter for default):"
	@read -p "Backend port [8000]: " backend_port; \
	read -p "Frontend port [3000]: " frontend_port; \
	read -p "Database port [5432]: " db_port; \
	read -p "Redis port [6379]: " redis_port; \
	echo ""; \
	echo "$(GREEN)✓ Ports updated$(NC)"

.DEFAULT_GOAL := help
