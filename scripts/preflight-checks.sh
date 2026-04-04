#!/bin/bash
# =====================================================
# MentorHub - Pre-flight Checks Script
# Комплексная проверка перед запуском сервисов
# =====================================================

set -euo pipefail

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

# Счетчики
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNINGS=0

# =====================================================
# ФУНКЦИИ
# =====================================================

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    CHECKS_WARNINGS=$((CHECKS_WARNINGS + 1))
}

section_header() {
    echo ""
    echo -e "${CYAN}[$1]${NC}"
    echo "─────────────────────────────────────────────"
}

# =====================================================
# ПРОВЕРКИ
# =====================================================

check_system_dependencies() {
    section_header "System Dependencies"
    
    # Docker
    if command -v docker &> /dev/null; then
        local docker_version=$(docker --version | grep -oP '\d+\.\d+\.\d+' | head -1)
        local major_version=$(echo $docker_version | cut -d. -f1)
        
        if [ "$major_version" -ge 20 ]; then
            check_pass "Docker установлен: $docker_version"
        else
            check_fail "Docker версия слишком старая: $docker_version (требуется 20+)"
        fi
    else
        check_fail "Docker не установлен"
    fi
    
    # Docker Compose
    if docker compose version &> /dev/null; then
        local compose_version=$(docker compose version 2>&1 | grep -oP '\d+\.\d+\.\d+' | head -1)
        check_pass "Docker Compose (plugin) установлен: $compose_version"
    elif command -v docker-compose &> /dev/null; then
        local compose_version=$(docker-compose --version | grep -oP '\d+\.\d+\.\d+')
        check_pass "Docker Compose (standalone) установлен: $compose_version"
    else
        check_fail "Docker Compose не установлен"
    fi
    
    # Git (опционально)
    if command -v git &> /dev/null; then
        local git_version=$(git --version | grep -oP '\d+\.\d+\.\d+')
        check_pass "Git установлен: $git_version"
    else
        check_warn "Git не установлен (не потребуется для деплоя)"
    fi
    
    # Python3 (для скриптов)
    if command -v python3 &> /dev/null; then
        local python_version=$(python3 --version | awk '{print $2}')
        check_pass "Python3 установлен: $python_version"
    else
        check_warn "Python3 не установлен (некоторые скрипты не будут работать)"
    fi
}

check_environment_file() {
    section_header "Environment Configuration"
    
    local env_file="${1:-.env}"
    
    if [ ! -f "$env_file" ]; then
        check_fail "Файл $env_file не найден"
        echo ""
        echo -e "  ${YELLOW}Рекомендуется запустить:${NC}"
        echo -e "  ${CYAN}make setup${NC} или ${CYAN}bash scripts/auto-ports.sh${NC}"
        echo ""
        return
    fi
    
    check_pass "Файл $env_file найден"
    
    # Проверка прав доступа
    local perms=$(stat -c %a "$env_file" 2>/dev/null || stat -f %A "$env_file" 2>/dev/null || echo "unknown")
    if [ "$perms" != "unknown" ]; then
        if [ "$perms" = "600" ] || [ "$perms" = "400" ]; then
            check_pass "Права на .env файл корректны: $perms"
        else
            check_warn "Права на .env файл: $perms (рекомендуется 600 или 400)"
            echo -e "  ${YELLOW}Исправить:${NC} chmod 600 $env_file"
        fi
    fi
    
    # Валидация содержимого
    if command -v python3 &> /dev/null && [ -f "scripts/generate_env.py" ]; then
        if python3 scripts/generate_env.py --validate "$env_file" > /dev/null 2>&1; then
            check_pass "Валидация .env файла пройдена"
        else
            check_warn "Валидация .env файла выявила проблемы"
            echo -e "  ${YELLOW}Проверить:${NC} python3 scripts/generate_env.py --validate $env_file"
        fi
    elif [ -f "scripts/validate_env.sh" ]; then
        if bash scripts/validate_env.sh "$env_file" > /dev/null 2>&1; then
            check_pass "Валидация .env файла пройдена"
        else
            check_warn "Валидация .env файла выявила проблемы"
        fi
    fi
}

check_ports_availability() {
    section_header "Ports Availability"
    
    local env_file="${1:-.env}"
    
    # Загружаем порты из .env
    if [ -f "$env_file" ]; then
        export $(grep -v '^#' "$env_file" | xargs 2>/dev/null || true)
    fi
    
    # Список портов для проверки
    local ports_to_check=(
        "${BACKEND_PORT:-8000}:Backend API"
        "${FRONTEND_PORT:-3000}:Frontend"
        "${DB_PORT:-5432}:PostgreSQL"
        "${REDIS_PORT:-6379}:Redis"
        "${PROMETHEUS_PORT:-9090}:Prometheus"
        "${GRAFANA_PORT:-3001}:Grafana"
    )
    
    # Nginx порты
    if [ "$(id -u)" -eq 0 ] 2>/dev/null; then
        ports_to_check+=("${NGINX_HTTP_PORT:-80}:Nginx HTTP")
        ports_to_check+=("${NGINX_HTTPS_PORT:-443}:Nginx HTTPS")
    else
        ports_to_check+=("${NGINX_HTTP_PORT:-8080}:Nginx HTTP")
        ports_to_check+=("${NGINX_HTTPS_PORT:-8443}:Nginx HTTPS")
    fi
    
    local ports_busy=0
    
    for port_info in "${ports_to_check[@]}"; do
        local port=$(echo "$port_info" | cut -d: -f1)
        local service=$(echo "$port_info" | cut -d: -f2)
        
        # Проверка порта
        if command -v ss &> /dev/null; then
            if ss -tln | grep -q ":${port} " 2>/dev/null; then
                check_warn "Порт $port ($service) занят"
                ports_busy=$((ports_busy + 1))
            else
                check_pass "Порт $port ($service) свободен"
            fi
        elif command -v netstat &> /dev/null; then
            if netstat -tln | grep -q ":${port} " 2>/dev/null; then
                check_warn "Порт $port ($service) занят"
                ports_busy=$((ports_busy + 1))
            else
                check_pass "Порт $port ($service) свободен"
            fi
        fi
    done
    
    if [ $ports_busy -gt 0 ]; then
        echo ""
        echo -e "  ${YELLOW}Занято портов: $ports_busy${NC}"
        echo -e "  ${YELLOW}Решение:${NC} ${CYAN}make ports-auto${NC} для автоподбора"
    fi
}

check_system_resources() {
    section_header "System Resources"
    
    # Проверка диска
    if command -v df &> /dev/null; then
        local available_mb=$(df -m "$(pwd)" | awk 'NR==2 {print $4}')
        local available_gb=$(echo "scale=2; $available_mb / 1024" | bc 2>/dev/null || echo "N/A")
        
        if [ "$available_mb" -lt 2000 ]; then
            check_fail "Мало места на диске: ${available_gb}GB (требуется минимум 2GB)"
        elif [ "$available_mb" -lt 5000 ]; then
            check_warn "Свободно места: ${available_gb}GB (рекомендуется 5GB+)"
        else
            check_pass "Достаточно места на диске: ${available_gb}GB"
        fi
    fi
    
    # Проверка RAM
    if command -v free &> /dev/null; then
        local total_mb=$(free -m | awk 'NR==2 {print $2}')
        local total_gb=$(echo "scale=2; $total_mb / 1024" | bc 2>/dev/null || echo "N/A")
        
        if [ "$total_mb" -lt 1024 ]; then
            check_fail "Мало RAM: ${total_gb}GB (требуется минимум 1GB)"
        elif [ "$total_mb" -lt 2048 ]; then
            check_warn "RAM: ${total_gb}GB (рекомендуется 2GB+)"
        else
            check_pass "Достаточно RAM: ${total_gb}GB"
        fi
    elif command -v sysctl &> /dev/null; then
        local total_mb=$(sysctl -n hw.memsize 2>/dev/null | awk '{print $1/1024/1024}' || echo "unknown")
        if [ "$total_mb" != "unknown" ]; then
            local total_gb=$(echo "scale=2; $total_mb / 1024" | bc 2>/dev/null || echo "N/A")
            check_pass "RAM: ${total_gb}GB"
        fi
    fi
    
    # Проверка CPU
    if command -v nproc &> /dev/null; then
        local cores=$(nproc)
        if [ "$cores" -lt 2 ]; then
            check_warn "Мало CPU ядер: $cores (рекомендуется 2+)"
        else
            check_pass "CPU ядер: $cores"
        fi
    fi
    
    # Проверка Docker ресурсов
    if command -v docker &> /dev/null; then
        local docker_info=$(docker info 2>/dev/null || true)
        
        if [ -n "$docker_info" ]; then
            local containers_running=$(echo "$docker_info" | grep "Containers Running" | awk '{print $NF}' || echo "0")
            check_pass "Docker контейнеров запущено: $containers_running"
            
            # Проверка Docker root
            if docker info 2>/dev/null | grep -q "rootless"; then
                check_pass "Docker работает в rootless режиме"
            fi
        fi
    fi
}

check_docker_images() {
    section_header "Docker Images"
    
    local compose_file="${1:-docker-compose.yml}"
    
    if [ ! -f "$compose_file" ]; then
        check_warn "Compose файл не найден: $compose_file"
        return
    fi
    
    check_pass "Compose файл найден: $compose_file"
    
    # Получаем список требуемых образов
    if docker compose -f "$compose_file" config &> /dev/null; then
        local images=$(docker compose -f "$compose_file" config | grep "image:" | awk '{print $2}' || true)
        local build_services=$(docker compose -f "$compose_file" config --services 2>/dev/null | grep -v "^$" || true)
        
        if [ -n "$images" ]; then
            local missing_images=0
            
            for image in $images; do
                if docker image inspect "$image" > /dev/null 2>&1; then
                    check_pass "Образ найден: $image"
                else
                    check_warn "Образ не найден (будет скачан): $image"
                    missing_images=$((missing_images + 1))
                fi
            done
            
            if [ $missing_images -gt 0 ]; then
                echo ""
                echo -e "  ${BLUE}Будет скачано образов: $missing_images${NC}"
            fi
        fi
        
        if [ -n "$build_services" ]; then
            check_pass "Сервисы требующие сборки: $(echo $build_services | tr '\n' ', ')"
        fi
    else
        check_fail "Не удалось прочитать compose файл"
    fi
}

check_volumes_and_permissions() {
    section_header "Volumes & Permissions"
    
    # Проверка директорий
    local dirs_to_check=("backend" "frontend" "scripts" "logs" "backups")
    
    for dir in "${dirs_to_check[@]}"; do
        if [ -d "$dir" ]; then
            if [ -w "$dir" ]; then
                check_pass "Директория $dir доступна для записи"
            else
                check_fail "Директория $dir не доступна для записи"
            fi
        else
            check_warn "Директория $dir не найдена"
        fi
    done
    
    # Проверка Docker volumes
    if command -v docker &> /dev/null; then
        local volumes=$(docker volume ls -q | grep mentorhub || true)
        
        if [ -n "$volumes" ]; then
            check_pass "Docker volumes найдены: $(echo $volumes | wc -w)"
        else
            check_warn "Docker volumes не найдены (будут созданы при запуске)"
        fi
    fi
}

check_network_connectivity() {
    section_header "Network Connectivity"
    
    # Проверка DNS
    if command -v nslookup &> /dev/null || command -v host &> /dev/null; then
        if nslookup registry.hub.docker.com > /dev/null 2>&1 || host registry.hub.docker.com > /dev/null 2>&1; then
            check_pass "DNS разрешение работает"
        else
            check_fail "DNS разрешение не работает"
        fi
    fi
    
    # Проверка доступа к Docker Hub
    if command -v curl &> /dev/null; then
        if curl -s --connect-timeout 5 https://registry.hub.docker.com > /dev/null 2>&1; then
            check_pass "Доступ к Docker Hub есть"
        else
            check_warn "Нет доступа к Docker Hub (образы могут не скачиваться)"
        fi
    fi
    
    # Проверка интернета
    if ping -c 1 -W 3 8.8.8.8 > /dev/null 2>&1; then
        check_pass "Интернет соединение работает"
    else
        check_warn "Нет интернет соединения"
    fi
}

check_configuration_consistency() {
    section_header "Configuration Consistency"
    
    local env_file="${1:-.env}"
    local compose_file="${2:-docker-compose.yml}"
    
    if [ ! -f "$env_file" ] || [ ! -f "$compose_file" ]; then
        check_warn "Не все файлы конфигурации найдены"
        return
    fi
    
    # Загружаем переменные
    export $(grep -v '^#' "$env_file" | xargs 2>/dev/null || true)
    
    # Проверка DATABASE_URL
    if [ -n "${DATABASE_URL:-}" ]; then
        local db_host=$(echo "$DATABASE_URL" | sed -E 's|.*@([^:/]+).*|\1|')
        
        if [[ "$db_host" == "localhost" ]] || [[ "$db_host" == "127.0.0.1" ]]; then
            if [[ "$compose_file" == *"docker-compose"* ]] && [[ "$compose_file" != *"dev"* ]]; then
                check_warn "DATABASE_URL указывает на localhost, но используется Docker Compose"
                echo -e "  ${YELLOW}В Docker рекомендуется использовать имя сервиса вместо localhost${NC}"
            fi
        else
            check_pass "DATABASE_URL настроен корректно ($db_host)"
        fi
    fi
    
    # Проверка CORS
    if [ -n "${CORS_ORIGINS:-}" ]; then
        if [[ "$ENVIRONMENT" == "production" ]] && [[ "$CORS_ORIGINS" == *"localhost"* ]]; then
            check_warn "Production режим, но CORS содержит localhost"
        else
            check_pass "CORS настроен"
        fi
    fi
}

# =====================================================
# ИТОГ
# =====================================================

show_summary() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}📊 Резюме проверок${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${GREEN}Пройдено:${NC}       $CHECKS_PASSED"
    echo -e "  ${RED}Не пройдено:${NC}    $CHECKS_FAILED"
    echo -e "  ${YELLOW}Предупреждения:${NC} $CHECKS_WARNINGS"
    echo ""
    
    if [ $CHECKS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✅ Все критические проверки пройдены!${NC}"
        if [ $CHECKS_WARNINGS -gt 0 ]; then
            echo -e "${YELLOW}⚠️  Есть предупреждения (можно запустить, но рекомендуется устранить)${NC}"
        fi
        return 0
    else
        echo -e "${RED}❌ Есть критические проблемы!${NC}"
        echo -e "${RED}Необходимо устранить все ошибки перед запуском!${NC}"
        return 1
    fi
}

# =====================================================
# MAIN
# =====================================================

show_help() {
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   🔍 MentorHub Pre-flight Checks                           ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Использование:${NC}"
    echo "  $0 [OPTIONS]"
    echo ""
    echo -e "${BLUE}Опции:${NC}"
    echo "  --env=FILE         Указать путь к .env файлу (по умолчанию: .env)"
    echo "  --compose=FILE     Указать путь к compose файлу"
    echo "  --quick            Быстрая проверка (только критические проверки)"
    echo "  --help             Показать эту справку"
    echo ""
}

main() {
    local env_file=".env"
    local compose_file="docker-compose.yml"
    local quick_mode=false
    
    # Парсинг аргументов
    for arg in "$@"; do
        case $arg in
            --env=*)
                env_file="${arg#*=}"
                ;;
            --compose=*)
                compose_file="${arg#*=}"
                ;;
            --quick)
                quick_mode=true
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
        esac
    done
    
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║   🔍 MentorHub Pre-flight Checks                           ║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Дата:${NC} $(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${BLUE}Режим:${NC} $([ "$quick_mode" = true ] && echo 'быстрый' || echo 'полный')"
    
    # Основные проверки
    check_system_dependencies
    check_environment_file "$env_file"
    check_ports_availability "$env_file"
    check_system_resources
    
    if [ "$quick_mode" = false ]; then
        check_docker_images "$compose_file"
        check_volumes_and_permissions
        check_network_connectivity
        check_configuration_consistency "$env_file" "$compose_file"
    fi
    
    # Итог
    if show_summary; then
        exit 0
    else
        exit 1
    fi
}

main "$@"
