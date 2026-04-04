#!/bin/bash
# =====================================================
# MentorHub - Adaptive Resource Profile Script
# Автоматическая настройка ресурсов на основе доступных
# =====================================================

set -euo pipefail

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

# =====================================================
# ФУНКЦИИ ОПРЕДЕЛЕНИЯ РЕСУРСОВ
# =====================================================

get_total_memory_mb() {
    """Получает общий объем RAM в MB"""
    if command -v free &> /dev/null; then
        free -m | awk 'NR==2 {print $2}'
    elif command -v sysctl &> /dev/null; then
        sysctl -n hw.memsize 2>/dev/null | awk '{print $1/1024/1024}'
    else
        echo "2048"  # По умолчанию 2GB
    fi
}

get_available_memory_mb() {
    """Получает доступный объем RAM в MB"""
    if command -v free &> /dev/null; then
        free -m | awk 'NR==2 {print $7}'
    else
        get_total_memory_mb
    fi
}

get_cpu_cores() {
    """Получает количество CPU ядер"""
    if command -v nproc &> /dev/null; then
        nproc
    elif command -v sysctl &> /dev/null; then
        sysctl -n hw.ncpu 2>/dev/null || echo "2"
    else
        echo "2"  # По умолчанию 2 ядра
    fi
}

get_disk_space_mb() {
    """Получает доступное место на диске в MB"""
    if command -v df &> /dev/null; then
        df -m "$(pwd)" | awk 'NR==2 {print $4}'
    else
        echo "10000"  # По умолчанию 10GB
    fi
}

# =====================================================
# РЕСУРСНЫЕ ПРОФИЛИ
# =====================================================

detect_resource_profile() {
    """Определяет ресурсный профиль системы"""
    local total_mem=$(get_total_memory_mb)
    local available_mem=$(get_available_memory_mb)
    local cpu_cores=$(get_cpu_cores)
    local disk_space=$(get_disk_space_mb)
    
    echo -e "${BLUE}📊 Определение ресурсного профиля...${NC}"
    echo ""
    echo -e "  ${CYAN}Всего RAM:${NC}      ${total_mem}MB"
    echo -e "  ${CYAN}Доступно RAM:${NC}   ${available_mem}MB"
    echo -e "  ${CYAN}CPU ядер:${NC}       $cpu_cores"
    echo -e "  ${CYAN}Диск свободно:${NC}  ${disk_space}MB"
    echo ""
    
    # Определяем профиль
    local profile="minimal"
    
    if [ "$available_mem" -ge 8192 ] && [ "$cpu_cores" -ge 4 ] && [ "$disk_space" -ge 20000 ]; then
        profile="high"
        echo -e "${GREEN}✓ Профиль: HIGH (высокие ресурсы)${NC}"
    elif [ "$available_mem" -ge 4096 ] && [ "$cpu_cores" -ge 2 ] && [ "$disk_space" -ge 10000 ]; then
        profile="medium"
        echo -e "${GREEN}✓ Профиль: MEDIUM (средние ресурсы)${NC}"
    elif [ "$available_mem" -ge 2048 ] && [ "$cpu_cores" -ge 1 ]; then
        profile="low"
        echo -e "${YELLOW}⚠ Профиль: LOW (низкие ресурсы)${NC}"
    else
        profile="minimal"
        echo -e "${RED}⚠ Профиль: MINIMAL (минимальные ресурсы)${NC}"
    fi
    
    echo ""
    echo "$profile"
}

# =====================================================
# ГЕНЕРАЦИЯ КОНФИГУРАЦИИ
# =====================================================

generate_resource_config() {
    """Генерирует конфигурацию на основе профиля"""
    local profile=$1
    
    case "$profile" in
        high)
            # Высокие ресурсы
            cat << EOF
# =====================================================
# HIGH Resource Profile Configuration
# Для систем с 8GB+ RAM и 4+ CPU ядер
# =====================================================

# ==================== BACKEND ====================
WORKERS=8
GUNICORN_WORKERS=8
GUNICORN_TIMEOUT=120
BACKEND_MEMORY_LIMIT=2g
BACKEND_CPU_LIMIT=2

# ==================== CELERY WORKER ====================
CELERY_CONCURRENCY=8
CELERY_POOL=threads
CELERY_MAX_TASKS_PER_CHILD=1000
CELERY_WORKER_MEMORY_LIMIT=1g
CELERY_WORKER_CPU_LIMIT=1

# ==================== CELERY BEAT ====================
CELERY_BEAT_MEMORY_LIMIT=256m
CELERY_BEAT_CPU_LIMIT=0.5

# ==================== FRONTEND ====================
FRONTEND_WORKERS=4
FRONTEND_MEMORY_LIMIT=1g
FRONTEND_CPU_LIMIT=1
NODE_OPTIONS="--max-old-space-size=1024"

# ==================== DATABASE ====================
POSTGRES_SHARED_BUFFERS=512MB
POSTGRES_EFFECTIVE_CACHE_SIZE=2GB
POSTGRES_MAINTENANCE_WORK_MEM=256MB
POSTGRES_WORK_MEM=32MB
POSTGRES_MAX_CONNECTIONS=200
POSTGRES_MEMORY_LIMIT=2g
POSTGRES_CPU_LIMIT=2

# ==================== REDIS ====================
REDIS_MAXMEMORY=1gb
REDIS_MEMORY_LIMIT=1g
REDIS_CPU_LIMIT=0.5

# ==================== NGINX ====================
NGINX_WORKER_PROCESSES=4
NGINX_WORKER_CONNECTIONS=2048
NGINX_MEMORY_LIMIT=512m
NGINX_CPU_LIMIT=1

# ==================== MONITORING ====================
PROMETHEUS_MEMORY_LIMIT=1g
PROMETHEUS_CPU_LIMIT=1
GRAFANA_MEMORY_LIMIT=512m
GRAFANA_CPU_LIMIT=0.5

# ==================== POOL SIZES ====================
DB_POOL_SIZE=40
DB_MAX_OVERFLOW=80
CELERY_POOL_SIZE=20
EOF
            ;;
        
        medium)
            # Средние ресурсы
            cat << EOF
# =====================================================
# MEDIUM Resource Profile Configuration
# Для систем с 4GB+ RAM и 2+ CPU ядер
# =====================================================

# ==================== BACKEND ====================
WORKERS=4
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=120
BACKEND_MEMORY_LIMIT=1g
BACKEND_CPU_LIMIT=1

# ==================== CELERY WORKER ====================
CELERY_CONCURRENCY=4
CELERY_POOL=threads
CELERY_MAX_TASKS_PER_CHILD=1000
CELERY_WORKER_MEMORY_LIMIT=512m
CELERY_WORKER_CPU_LIMIT=0.5

# ==================== CELERY BEAT ====================
CELERY_BEAT_MEMORY_LIMIT=256m
CELERY_BEAT_CPU_LIMIT=0.25

# ==================== FRONTEND ====================
FRONTEND_WORKERS=2
FRONTEND_MEMORY_LIMIT=512m
FRONTEND_CPU_LIMIT=0.5
NODE_OPTIONS="--max-old-space-size=512"

# ==================== DATABASE ====================
POSTGRES_SHARED_BUFFERS=256MB
POSTGRES_EFFECTIVE_CACHE_SIZE=1GB
POSTGRES_MAINTENANCE_WORK_MEM=128MB
POSTGRES_WORK_MEM=16MB
POSTGRES_MAX_CONNECTIONS=100
POSTGRES_MEMORY_LIMIT=1g
POSTGRES_CPU_LIMIT=1

# ==================== REDIS ====================
REDIS_MAXMEMORY=512mb
REDIS_MEMORY_LIMIT=512m
REDIS_CPU_LIMIT=0.25

# ==================== NGINX ====================
NGINX_WORKER_PROCESSES=2
NGINX_WORKER_CONNECTIONS=1024
NGINX_MEMORY_LIMIT=256m
NGINX_CPU_LIMIT=0.5

# ==================== MONITORING ====================
PROMETHEUS_MEMORY_LIMIT=512m
PROMETHEUS_CPU_LIMIT=0.5
GRAFANA_MEMORY_LIMIT=256m
GRAFANA_CPU_LIMIT=0.25

# ==================== POOL SIZES ====================
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
CELERY_POOL_SIZE=10
EOF
            ;;
        
        low)
            # Низкие ресурсы
            cat << EOF
# =====================================================
# LOW Resource Profile Configuration
# Для систем с 2GB+ RAM и 1+ CPU ядер
# =====================================================

# ==================== BACKEND ====================
WORKERS=2
GUNICORN_WORKERS=2
GUNICORN_TIMEOUT=90
BACKEND_MEMORY_LIMIT=512m
BACKEND_CPU_LIMIT=0.5

# ==================== CELERY WORKER ====================
CELERY_CONCURRENCY=2
CELERY_POOL=threads
CELERY_MAX_TASKS_PER_CHILD=500
CELERY_WORKER_MEMORY_LIMIT=256m
CELERY_WORKER_CPU_LIMIT=0.25

# ==================== CELERY BEAT ====================
CELERY_BEAT_MEMORY_LIMIT=128m
CELERY_BEAT_CPU_LIMIT=0.25

# ==================== FRONTEND ====================
FRONTEND_WORKERS=1
FRONTEND_MEMORY_LIMIT=256m
FRONTEND_CPU_LIMIT=0.25
NODE_OPTIONS="--max-old-space-size=256"

# ==================== DATABASE ====================
POSTGRES_SHARED_BUFFERS=128MB
POSTGRES_EFFECTIVE_CACHE_SIZE=512MB
POSTGRES_MAINTENANCE_WORK_MEM=64MB
POSTGRES_WORK_MEM=8MB
POSTGRES_MAX_CONNECTIONS=50
POSTGRES_MEMORY_LIMIT=512m
POSTGRES_CPU_LIMIT=0.5

# ==================== REDIS ====================
REDIS_MAXMEMORY=256mb
REDIS_MEMORY_LIMIT=256m
REDIS_CPU_LIMIT=0.25

# ==================== NGINX ====================
NGINX_WORKER_PROCESSES=1
NGINX_WORKER_CONNECTIONS=512
NGINX_MEMORY_LIMIT=128m
NGINX_CPU_LIMIT=0.25

# ==================== MONITORING ====================
PROMETHEUS_MEMORY_LIMIT=256m
PROMETHEUS_CPU_LIMIT=0.25
GRAFANA_MEMORY_LIMIT=128m
GRAFANA_CPU_LIMIT=0.25

# ==================== POOL SIZES ====================
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
CELERY_POOL_SIZE=5
EOF
            ;;
        
        minimal)
            # Минимальные ресурсы
            cat << EOF
# =====================================================
# MINIMAL Resource Profile Configuration
# Для систем с < 2GB RAM
# =====================================================

# ==================== BACKEND ====================
WORKERS=1
GUNICORN_WORKERS=1
GUNICORN_TIMEOUT=60
BACKEND_MEMORY_LIMIT=256m
BACKEND_CPU_LIMIT=0.25

# ==================== CELERY WORKER ====================
CELERY_CONCURRENCY=1
CELERY_POOL=threads
CELERY_MAX_TASKS_PER_CHILD=200
CELERY_WORKER_MEMORY_LIMIT=128m
CELERY_WORKER_CPU_LIMIT=0.25

# ==================== CELERY BEAT ====================
CELERY_BEAT_MEMORY_LIMIT=64m
CELERY_BEAT_CPU_LIMIT=0.25

# ==================== FRONTEND ====================
FRONTEND_WORKERS=1
FRONTEND_MEMORY_LIMIT=128m
FRONTEND_CPU_LIMIT=0.25
NODE_OPTIONS="--max-old-space-size=128"

# ==================== DATABASE ====================
POSTGRES_SHARED_BUFFERS=64MB
POSTGRES_EFFECTIVE_CACHE_SIZE=256MB
POSTGRES_MAINTENANCE_WORK_MEM=32MB
POSTGRES_WORK_MEM=4MB
POSTGRES_MAX_CONNECTIONS=20
POSTGRES_MEMORY_LIMIT=256m
POSTGRES_CPU_LIMIT=0.25

# ==================== REDIS ====================
REDIS_MAXMEMORY=128mb
REDIS_MEMORY_LIMIT=128m
REDIS_CPU_LIMIT=0.25

# ==================== NGINX ====================
NGINX_WORKER_PROCESSES=1
NGINX_WORKER_CONNECTIONS=256
NGINX_MEMORY_LIMIT=64m
NGINX_CPU_LIMIT=0.25

# ==================== MONITORING ====================
# Отключаем мониторинг для минимальных ресурсов
PROMETHEUS_ENABLED=false
GRAFANA_ENABLED=false

# ==================== POOL SIZES ====================
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
CELERY_POOL_SIZE=2
EOF
            ;;
    esac
}

# =====================================================
# ПРИМЕНЕНИЕ КОНФИГУРАЦИИ
# =====================================================

apply_resource_profile() {
    """Применяет ресурсный профиль к Docker Compose"""
    local profile=$1
    local compose_file="${2:-docker-compose.yml}"
    local output_file="${3:-}"
    
    echo -e "${BLUE}🔧 Применение профиля: $profile${NC}"
    
    # Генерируем конфигурацию
    local config=$(generate_resource_config "$profile")
    
    if [ -n "$output_file" ]; then
        echo "$config" > "$output_file"
        echo -e "${GREEN}✓ Конфигурация сохранена в: $output_file${NC}"
    else
        echo ""
        echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
        echo "$config"
        echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    fi
    
    # Обновляем .env файл
    update_env_with_resources "$profile"
}

update_env_with_resources() {
    """Обновляет .env файл ресурсными настройками"""
    local profile=$1
    local env_file="${2:-.env}"
    
    if [ ! -f "$env_file" ]; then
        echo -e "${YELLOW}⚠ .env файл не найден, создаем настройки ресурсов${NC}"
        return
    fi
    
    echo -e "${BLUE}📝 Обновление .env файла ресурсными настройками...${NC}"
    
    # Генерируем конфигурацию
    local config=$(generate_resource_config "$profile")
    
    # Добавляем ресурсные настройки в конец .env
    {
        echo ""
        echo "# ==================== RESOURCE PROFILE ===================="
        echo "# Auto-generated resource profile: $profile"
        echo "# Generated: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "$config"
    } >> "$env_file"
    
    echo -e "${GREEN}✓ .env файл обновлен ресурсными настройками${NC}"
}

# =====================================================
# DOCKER COMPOSE OVERLAY
# =====================================================

generate_compose_overlay() {
    """Генерирует Docker Compose overlay файл с ресурсными лимитами"""
    local profile=$1
    local output_file="${2:-docker-compose.resources.yml}"
    
    echo -e "${BLUE}📄 Генерация Docker Compose overlay файла...${NC}"
    
    cat > "$output_file" << EOF
version: '3.8'

# Resource limits overlay for profile: $profile
# Generated: $(date '+%Y-%m-%d %H:%M:%S')

services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '\${BACKEND_CPU_LIMIT:-1}'
          memory: \${BACKEND_MEMORY_LIMIT:-1g}
        reservations:
          cpus: '0.25'
          memory: 256M

  celery_worker:
    deploy:
      resources:
        limits:
          cpus: '\${CELERY_WORKER_CPU_LIMIT:-0.5}'
          memory: \${CELERY_WORKER_MEMORY_LIMIT:-512m}
        reservations:
          cpus: '0.25'
          memory: 128M

  celery_beat:
    deploy:
      resources:
        limits:
          cpus: '\${CELERY_BEAT_CPU_LIMIT:-0.25}'
          memory: \${CELERY_BEAT_MEMORY_LIMIT:-256m}
        reservations:
          cpus: '0.1'
          memory: 64M

  frontend:
    deploy:
      resources:
        limits:
          cpus: '\${FRONTEND_CPU_LIMIT:-0.5}'
          memory: \${FRONTEND_MEMORY_LIMIT:-512m}
        reservations:
          cpus: '0.25'
          memory: 128M

  postgres:
    deploy:
      resources:
        limits:
          cpus: '\${POSTGRES_CPU_LIMIT:-1}'
          memory: \${POSTGRES_MEMORY_LIMIT:-1g}
        reservations:
          cpus: '0.5'
          memory: 512M

  redis:
    deploy:
      resources:
        limits:
          cpus: '\${REDIS_CPU_LIMIT:-0.25}'
          memory: \${REDIS_MEMORY_LIMIT:-512m}
        reservations:
          cpus: '0.1'
          memory: 128M

  nginx:
    deploy:
      resources:
        limits:
          cpus: '\${NGINX_CPU_LIMIT:-0.5}'
          memory: \${NGINX_MEMORY_LIMIT:-256m}
        reservations:
          cpus: '0.25'
          memory: 64M

  prometheus:
    deploy:
      resources:
        limits:
          cpus: '\${PROMETHEUS_CPU_LIMIT:-0.5}'
          memory: \${PROMETHEUS_MEMORY_LIMIT:-512m}
        reservations:
          cpus: '0.25'
          memory: 128M

  grafana:
    deploy:
      resources:
        limits:
          cpus: '\${GRAFANA_CPU_LIMIT:-0.25}'
          memory: \${GRAFANA_MEMORY_LIMIT:-256m}
        reservations:
          cpus: '0.1'
          memory: 64M
EOF
    
    echo -e "${GREEN}✓ Overlay файл создан: $output_file${NC}"
    echo -e "${BLUE}  Использовать:${NC} docker-compose -f docker-compose.yml -f $output_file up -d"
}

# =====================================================
# HELP
# =====================================================

show_help() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   🔧 MentorHub Adaptive Resource Profile                   ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Использование:${NC}"
    echo "  $0 [ACTION] [OPTIONS]"
    echo ""
    echo -e "${BLUE}Действия:${NC}"
    echo "  detect             Определить ресурсный профиль системы"
    echo "  generate           Сгенерировать конфигурацию для профиля"
    echo "  apply              Применить профиль к .env и создать overlay"
    echo "  show               Показать доступные профили"
    echo "  help               Показать эту справку"
    echo ""
    echo -e "${BLUE}Опции:${NC}"
    echo "  --profile=PROFILE  Установить профиль (minimal, low, medium, high)"
    echo "  --output=FILE      Выходной файл конфигурации"
    echo "  --compose=FILE     Docker Compose файл для overlay"
    echo ""
    echo -e "${BLUE}Профили:${NC}"
    echo "  minimal   < 2GB RAM, < 1 CPU (минимальные ресурсы)"
    echo "  low       2GB+ RAM, 1+ CPU (низкие ресурсы)"
    echo "  medium    4GB+ RAM, 2+ CPU (средние ресурсы)"
    echo "  high      8GB+ RAM, 4+ CPU (высокие ресурсы)"
    echo ""
}

# =====================================================
# MAIN
# =====================================================

main() {
    local action="${1:-detect}"
    local profile=""
    local output_file=""
    local compose_file="docker-compose.yml"
    
    # Парсинг аргументов
    for arg in "$@"; do
        case $arg in
            --profile=*)
                profile="${arg#*=}"
                ;;
            --output=*)
                output_file="${arg#*=}"
                ;;
            --compose=*)
                compose_file="${arg#*=}"
                ;;
        esac
    done
    
    case "$action" in
        detect)
            detect_resource_profile
            ;;
        
        generate)
            if [ -z "$profile" ]; then
                profile=$(detect_resource_profile | tail -1)
            fi
            generate_resource_config "$profile"
            ;;
        
        apply)
            if [ -z "$profile" ]; then
                profile=$(detect_resource_profile | tail -1)
            fi
            
            apply_resource_profile "$profile" "$compose_file" "$output_file"
            generate_compose_overlay "$profile" "docker-compose.resources.yml"
            
            echo ""
            echo -e "${GREEN}✅ Ресурсный профиль применен!${NC}"
            echo -e "${BLUE}  Запустите:${NC} docker-compose -f docker-compose.yml -f docker-compose.resources.yml up -d"
            ;;
        
        show)
            echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
            echo -e "${CYAN}║   📊 Доступные ресурсные профили                            ║${NC}"
            echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
            echo ""
            echo -e "${RED}minimal:${NC}  < 2GB RAM, < 1 CPU  (минимальные ресурсы)"
            echo -e "${YELLOW}low:${NC}     2GB+ RAM, 1+ CPU   (низкие ресурсы)"
            echo -e "${GREEN}medium:${NC}   4GB+ RAM, 2+ CPU   (средние ресурсы)"
            echo -e "${GREEN}high:${NC}     8GB+ RAM, 4+ CPU   (высокие ресурсы)"
            echo ""
            ;;
        
        help|--help|-h)
            show_help
            ;;
        
        *)
            echo -e "${RED}❌ Неизвестное действие: $action${NC}"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
