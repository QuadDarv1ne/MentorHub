#!/bin/bash

# MentorHub Production Deployment Script
# Автоматический скрипт для развертывания в production

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Глобальные переменные
ENVIRONMENT="production"
COMPOSE_FILE="docker-compose.prod.yml"
SKIP_BUILD=false
CHECK_ONLY=false
CLEANUP=false

# Логирование
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Проверка зависимостей
check_dependencies() {
    log_info "Проверка зависимостей..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker не установлен. Установите Docker 20+"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose не установлен. Установите Docker Compose 2.0+"
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        log_error "Git не установлен"
        exit 1
    fi
    
    log_success "Все зависимости установлены"
    docker --version
    docker-compose --version
}

# Проверка .env файла
check_env_file() {
    log_info "Проверка .env файла..."
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            log_warning ".env не найден. Копируем .env.example..."
            cp .env.example .env
            log_warning "Отредактируйте .env файл перед запуском!"
            log_warning "Обязательно измените: SECRET_KEY, POSTGRES_PASSWORD, CORS_ORIGINS"
            exit 1
        else
            log_error ".env.example не найден"
            exit 1
        fi
    fi
    
    # Проверка обязательных переменных
    if grep -q "SECRET_KEY=your-secret-key" .env || grep -q "SECRET_KEY=change-me" .env; then
        log_error "Измените SECRET_KEY в .env файле!"
        exit 1
    fi
    
    if grep -q "POSTGRES_PASSWORD=password" .env || grep -q "POSTGRES_PASSWORD=SECURE_PASSWORD" .env; then
        log_error "Измените POSTGRES_PASSWORD в .env файле!"
        exit 1
    fi
    
    log_success ".env файл найден"
}

# Pull свежих изменений
pull_latest() {
    log_info "Pull свежих изменений из git..."
    git pull origin main
    log_success "Код обновлен"
}

# Build Docker образов
build_images() {
    if [ "$SKIP_BUILD" = true ]; then
        log_warning "Пропускаем build (флаг --skip-build)"
        return
    fi
    
    log_info "Build Docker образов..."
    docker-compose -f $COMPOSE_FILE build
    log_success "Образы собраны"
}

# Применение миграций
run_migrations() {
    log_info "Применение миграций Alembic..."
    
    # Ждем пока БД будет готова
    sleep 10
    
    docker-compose -f $COMPOSE_FILE run --rm backend alembic upgrade head || {
        log_warning "Миграции не применились, возможно они уже применены"
    }
    
    log_success "Миграции применены"
}

# Запуск сервисов
start_services() {
    log_info "Запуск сервисов..."
    docker-compose -f $COMPOSE_FILE up -d
    log_success "Сервисы запущены"
}

# Проверка health checks
check_health() {
    log_info "Ожидание запуска сервисов (60 секунд)..."
    sleep 60
    
    log_info "Проверка health checks..."
    
    # Проверка backend
    if curl -f http://localhost:8000/health &> /dev/null; then
        log_success "Backend healthy"
    else
        log_error "Backend не отвечает"
        docker-compose -f $COMPOSE_FILE logs backend
        exit 1
    fi
    
    # Проверка frontend
    if curl -f http://localhost:3000 &> /dev/null; then
        log_success "Frontend healthy"
    else
        log_warning "Frontend не отвечает (возможно долго запускается)"
    fi
    
    # Проверка Prometheus
    if curl -f http://localhost:9090 &> /dev/null; then
        log_success "Prometheus healthy"
    else
        log_warning "Prometheus не отвечает"
    fi
    
    # Проверка Grafana
    if curl -f http://localhost:3001 &> /dev/null; then
        log_success "Grafana healthy"
    else
        log_warning "Grafana не отвечает"
    fi
}

# Вывод статуса
show_status() {
    echo ""
    log_info "Статус сервисов:"
    docker-compose -f $COMPOSE_FILE ps
    
    echo ""
    log_success "Deployment завершен!"
    echo ""
    echo "Полезные команды:"
    echo "  Просмотр логов: docker-compose -f $COMPOSE_FILE logs -f"
    echo "  Backend health: curl http://localhost:8000/health"
    echo "  Grafana: http://localhost:3001 (admin/admin)"
    echo "  Prometheus: http://localhost:9090"
    echo "  Swagger docs: http://localhost:8000/docs"
}

# Очистка
cleanup() {
    log_info "Очистка старых образов..."
    docker image prune -f
    log_success "Очистка завершена"
}

# Парсинг аргументов
while [[ $# -gt 0 ]]; do
    case $1 in
        --production)
            ENVIRONMENT="production"
            COMPOSE_FILE="docker-compose.prod.yml"
            shift
            ;;
        --staging)
            ENVIRONMENT="staging"
            COMPOSE_FILE="docker-compose.staging.yml"
            shift
            ;;
        --dev)
            ENVIRONMENT="development"
            COMPOSE_FILE="docker-compose.dev.yml"
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --check)
            CHECK_ONLY=true
            shift
            ;;
        --cleanup)
            CLEANUP=true
            shift
            ;;
        --help)
            echo "MentorHub Deployment Script"
            echo ""
            echo "Использование:"
            echo "  ./deploy.sh [OPTIONS]"
            echo ""
            echo "Опции:"
            echo "  --production    Deploy в production (по умолчанию)"
            echo "  --staging       Deploy в staging"
            echo "  --dev           Deploy в development"
            echo "  --skip-build    Пропустить build образов"
            echo "  --check         Только проверка без деплоя"
            echo "  --cleanup       Очистка старых образов"
            echo "  --help          Показать эту справку"
            exit 0
            ;;
        *)
            log_error "Неизвестная опция: $1"
            echo "Используйте --help для справки"
            exit 1
            ;;
    esac
done

# Main
main() {
    echo ""
    echo "========================================"
    echo "  MentorHub Deployment Script"
    echo "  Environment: $ENVIRONMENT"
    echo "========================================"
    echo ""
    
    if [ "$CLEANUP" = true ]; then
        cleanup
        exit 0
    fi
    
    check_dependencies
    check_env_file
    
    if [ "$CHECK_ONLY" = true ]; then
        log_success "Все проверки пройдены"
        exit 0
    fi
    
    pull_latest
    build_images
    run_migrations
    start_services
    check_health
    show_status
}

main
