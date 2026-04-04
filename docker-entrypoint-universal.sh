#!/bin/bash
# =====================================================
# MentorHub - Universal Docker Entrypoint Script
# Универсальный скрипт для всех Docker контейнеров
# Автоматическая настройка, проверки, graceful shutdown
# =====================================================

set -euo pipefail

# Перехват сигналов для graceful shutdown
trap 'graceful_shutdown' SIGTERM SIGINT SIGQUIT

# Глобальные переменные
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTAINER_ROLE="${CONTAINER_ROLE:-backend}"  # backend, frontend, postgres, redis, celery, nginx
MAX_RETRIES=3
RETRY_DELAY=5
STARTUP_TIMEOUT=60

# =====================================================
# GRACEFUL SHUTDOWN
# =====================================================

graceful_shutdown() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] Получен сигнал завершения. Graceful shutdown..."
    
    # Останавливаем дочерние процессы
    if [ ${#CHILD_PIDS[@]} -gt 0 ] 2>/dev/null; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] Остановка дочерних процессов: ${CHILD_PIDS[@]}"
        for pid in "${CHILD_PIDS[@]}"; do
            kill -TERM "$pid" 2>/dev/null || true
        done
        
        # Ждем завершения
        sleep 5
        
        # Принудительное завершение
        for pid in "${CHILD_PIDS[@]}"; do
            if kill -0 "$pid" 2>/dev/null; then
                echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARNING] Принудительное завершение PID: $pid"
                kill -9 "$pid" 2>/dev/null || true
            fi
        done
    fi
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] Завершение работы контейнера"
    exit 0
}

# Массив для отслеживания дочерних процессов
declare -a CHILD_PIDS=()

# =====================================================
# LOGGING
# =====================================================

log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] [$CONTAINER_ROLE] $1"
}

log_success() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] [$CONTAINER_ROLE] $1"
}

log_warning() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARNING] [$CONTAINER_ROLE] $1"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] [$CONTAINER_ROLE] $1"
}

# =====================================================
# RETRY MECHANISM
# =====================================================

retry_with_backoff() {
    local cmd="$1"
    local description="$2"
    local max_retries="${3:-$MAX_RETRIES}"
    local delay="${4:-$RETRY_DELAY}"
    
    log_info "Попытка: $description (макс. $max_retries попыток)"
    
    for attempt in $(seq 1 $max_retries); do
        log_info "Попытка $attempt/$max_retries..."
        
        if eval "$cmd"; then
            log_success "$description успешно выполнено"
            return 0
        fi
        
        if [ $attempt -lt $max_retries ]; then
            log_warning "Не удалось выполнить, повторная попытка через ${delay}с..."
            sleep $delay
            # Экспоненциальный backoff
            delay=$((delay * 2))
        fi
    done
    
    log_error "Не удалось выполнить после $max_retries попыток: $description"
    return 1
}

# =====================================================
# HEALTH CHECKS
# =====================================================

wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local timeout="${4:-$STARTUP_TIMEOUT}"
    
    log_info "Ожидание сервиса $service_name на $host:$port (таймаут: ${timeout}с)"
    
    local elapsed=0
    while [ $elapsed -lt $timeout ]; do
        if nc -z "$host" "$port" 2>/dev/null; then
            log_success "Сервис $service_name доступен"
            return 0
        fi
        
        sleep 1
        elapsed=$((elapsed + 1))
        
        if [ $((elapsed % 10)) -eq 0 ]; then
            log_info "Все еще ожидаем $service_name... (${elapsed}/${timeout}с)"
        fi
    done
    
    log_error "Таймаут ожидания сервиса $service_name"
    return 1
}

wait_for_database() {
    local db_url="${DATABASE_URL:-}"
    
    if [ -z "$db_url" ]; then
        log_warning "DATABASE_URL не установлена, пропускаем проверку БД"
        return 0
    fi
    
    # Извлекаем host и port из DATABASE_URL
    local db_host=$(echo "$db_url" | sed -E 's|.*@([^:/]+).*|\1|')
    local db_port=$(echo "$db_url" | sed -E 's|.*:([0-9]+)/.*|\1|' || echo "5432")
    
    log_info "Проверка PostgreSQL на $db_host:$db_port"
    
    if wait_for_service "$db_host" "$db_port" "PostgreSQL" 60; then
        log_success "PostgreSQL готова"
        return 0
    else
        log_error "PostgreSQL не доступна"
        return 1
    fi
}

wait_for_redis() {
    local redis_url="${REDIS_URL:-redis://redis:6379/0}"
    
    # Извлекаем host и port
    local redis_host=$(echo "$redis_url" | sed -E 's|redis://([^:/]+).*|\1|')
    local redis_port=$(echo "$redis_url" | sed -E 's|.*:([0-9]+).*|\1|' || echo "6379")
    
    log_info "Проверка Redis на $redis_host:$redis_port"
    
    if wait_for_service "$redis_host" "$redis_port" "Redis" 30; then
        log_success "Redis готов"
        return 0
    else
        log_error "Redis не доступен"
        return 1
    fi
}

# =====================================================
# ROLE-SPECIFIC SETUP
# =====================================================

setup_backend() {
    log_info "Инициализация Backend..."
    
    # Ожидание зависимостей
    if [ -n "${DATABASE_URL:-}" ]; then
        retry_with_backoff "wait_for_database" "Проверка PostgreSQL"
    fi
    
    if [ -n "${REDIS_URL:-}" ]; then
        retry_with_backoff "wait_for_redis" "Проверка Redis"
    fi
    
    # Применение миграций (опционально)
    if [ "${AUTO_MIGRATE:-true}" = "true" ]; then
        log_info "Применение миграций Alembic..."
        if command -v alembic &> /dev/null; then
            cd /app/backend 2>/dev/null || cd /app 2>/dev/null || true
            
            if alembic upgrade head 2>&1; then
                log_success "Миграции применены"
            else
                log_warning "Не удалось применить миграции (возможно они уже применены)"
            fi
        else
            log_warning "Alembic не найден, пропускаем миграции"
        fi
    fi
    
    # Запуск backend
    log_info "Запуск Backend сервера..."
    
    local workers="${WORKERS:-4}"
    local host="${HOST:-0.0.0.0}"
    local port="${PORT:-8000}"
    
    if [ "${ENVIRONMENT:-production}" = "development" ]; then
        # Development режим с reload
        uvicorn app.main:app \
            --host "$host" \
            --port "$port" \
            --reload \
            --reload-dir app \
            --log-level info &
    else
        # Production режим с gunicorn
        if command -v gunicorn &> /dev/null; then
            gunicorn app.main:app \
                --workers "$workers" \
                --worker-class uvicorn.workers.UvicornWorker \
                --bind "$host:$port" \
                --timeout 120 \
                --graceful-timeout 30 \
                --keep-alive 5 \
                --max-requests 1000 \
                --max-requests-jitter 100 \
                --access-logfile - \
                --error-logfile - \
                --log-level info &
        else
            uvicorn app.main:app \
                --host "$host" \
                --port "$port" \
                --workers "$workers" \
                --log-level info &
        fi
    fi
    
    CHILD_PIDS+=($!)
    log_success "Backend запущен (PID: $!)"
}

setup_frontend() {
    log_info "Инициализация Frontend..."
    
    # Ожидание backend
    local backend_host="${BACKEND_HOST:-backend}"
    local backend_port="${BACKEND_PORT:-8000}"
    
    wait_for_service "$backend_host" "$backend_port" "Backend" 60 || {
        log_warning "Backend не доступен, продолжаем без него"
    }
    
    # Запуск frontend
    log_info "Запуск Frontend сервера..."
    
    local port="${FRONTEND_PORT:-3000}"
    
    if [ "${ENVIRONMENT:-production}" = "development" ]; then
        # Development режим
        npm run dev -- --port "$port" &
    else
        # Production режим
        if [ -f "server.js" ]; then
            node server.js &
        elif [ -f ".next/standalone/server.js" ]; then
            node .next/standalone/server.js &
        else
            npm start -- --port "$port" &
        fi
    fi
    
    CHILD_PIDS+=($!)
    log_success "Frontend запущен (PID: $!)"
}

setup_celery_worker() {
    log_info "Инициализация Celery Worker..."
    
    # Ожидание зависимостей
    retry_with_backoff "wait_for_database" "Проверка PostgreSQL"
    retry_with_backoff "wait_for_redis" "Проверка Redis"
    
    # Запуск Celery worker
    log_info "Запуск Celery worker..."
    
    local concurrency="${CELERY_CONCURRENCY:-4}"
    local pool="${CELERY_POOL:-threads}"
    
    celery -A app.tasks worker \
        --loglevel=info \
        --concurrency="$concurrency" \
        --pool="$pool" \
        --max-tasks-per-child=1000 \
        --time-limit=300 \
        --soft-time-limit=240 &
    
    CHILD_PIDS+=($!)
    log_success "Celery worker запущен (PID: $!)"
}

setup_celery_beat() {
    log_info "Инициализация Celery Beat..."
    
    # Ожидание Redis
    retry_with_backoff "wait_for_redis" "Проверка Redis"
    
    # Запуск Celery beat
    log_info "Запуск Celery beat..."
    
    celery -A app.tasks beat --loglevel=info &
    
    CHILD_PIDS+=($!)
    log_success "Celery beat запущен (PID: $!)"
}

setup_postgres() {
    log_info "Инициализация PostgreSQL..."
    
    # PostgreSQL запускается через официальный образ
    # Этот блок для кастомной инициализации если нужно
    
    if [ -d "/docker-entrypoint-initdb.d" ]; then
        log_info "Поиск скриптов инициализации в /docker-entrypoint-initdb.d"
        # Скрипты уже выполнены официальным entrypoint
    fi
    
    log_success "PostgreSQL инициализирован"
}

setup_redis() {
    log_info "Инициализация Redis..."
    
    # Redis запускается через официальный образ
    # Этот блок для кастомной конфигурации
    
    log_success "Redis инициализирован"
}

setup_nginx() {
    log_info "Инициализация Nginx..."
    
    # Проверка конфигурации
    if [ -f "/etc/nginx/nginx.conf" ]; then
        log_info "Проверка nginx конфигурации..."
        if nginx -t 2>&1; then
            log_success "Nginx конфигурация корректна"
        else
            log_error "Ошибка в nginx конфигурации"
            return 1
        fi
    else
        log_warning "Nginx конфигурация не найдена"
    fi
    
    # Запуск nginx
    log_info "Запуск Nginx..."
    nginx -g "daemon off;" &
    
    CHILD_PIDS+=($!)
    log_success "Nginx запущен (PID: $!)"
}

# =====================================================
# MAIN
# =====================================================

main() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║        🚀 MentorHub Docker Entrypoint                      ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    log_info "Запуск контейнера"
    log_info "Роль: $CONTAINER_ROLE"
    log_info "Окружение: ${ENVIRONMENT:-not set}"
    echo ""
    
    # Выполняем настройку в зависимости от роли
    case "$CONTAINER_ROLE" in
        backend)
            setup_backend
            ;;
        frontend)
            setup_frontend
            ;;
        celery_worker|celery)
            setup_celery_worker
            ;;
        celery_beat)
            setup_celery_beat
            ;;
        postgres|db)
            setup_postgres
            ;;
        redis)
            setup_redis
            ;;
        nginx|proxy)
            setup_nginx
            ;;
        *)
            log_error "Неизвестная роль: $CONTAINER_ROLE"
            log_info "Допустимые роли: backend, frontend, celery_worker, celery_beat, postgres, redis, nginx"
            exit 1
            ;;
    esac
    
    # Ожидание завершения дочерних процессов
    log_info "Все сервисы запущены. Ожидание сигналов завершения..."
    wait ${CHILD_PIDS[@]} 2>/dev/null || true
}

main "$@"
