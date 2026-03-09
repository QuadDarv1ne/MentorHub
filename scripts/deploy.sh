#!/bin/bash
# =============================================================================
# MentorHub Universal Deployment Script
# =============================================================================
# Универсальный скрипт для деплоя на различные платформы
# =============================================================================
# Использование:
#   ./deploy.sh <platform> [options]
#
# Платформы:
#   heroku     - Деплой на Heroku
#   railway    - Деплой на Railway
#   render     - Деплой на Render
#   aws        - Деплой на AWS ECS
#   gcp        - Деплой на Google Cloud Run
#   vercel     - Деплой frontend на Vercel
#   netlify    - Деплой frontend на Netlify
#   cloudflare - Деплой frontend на Cloudflare Pages
#   docker     - Сборка Docker образа
#   all        - Деплой на все платформы
#
# Опции:
#   -h, --help     Показать справку
#   -v, --verbose  Подробный вывод
#   -f, --force    Принудительный деплой
#   -t, --tag      Тег для Docker образа
#   -e, --env      Окружение (staging/production)
# =============================================================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Переменные по умолчанию
PLATFORM=""
VERBOSE=false
FORCE=false
TAG="latest"
ENV="production"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# =============================================================================
# Utility Functions
# =============================================================================

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

log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[VERBOSE]${NC} $1"
    fi
}

show_help() {
    cat << EOF
MentorHub Deployment Script

Использование:
    $0 <platform> [options]

Платформы:
    heroku     Деплой на Heroku
    railway    Деплой на Railway
    render     Деплой на Render
    aws        Деплой на AWS ECS
    gcp        Деплой на Google Cloud Run
    vercel     Деплой frontend на Vercel
    netlify    Деплой frontend на Netlify
    cloudflare Деплой frontend на Cloudflare Pages
    docker     Сборка Docker образа
    all        Деплой на все платформы

Опции:
    -h, --help     Показать эту справку
    -v, --verbose  Подробный вывод
    -f, --force    Принудительный деплой
    -t, --tag      Тег для Docker образа (по умолчанию: latest)
    -e, --env      Окружение: staging или production (по умолчанию: production)

Примеры:
    $0 heroku
    $0 aws --env staging
    $0 docker --tag v1.2.3
    $0 all --verbose

EOF
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 не найден. Пожалуйста, установите $1"
        exit 1
    fi
}

check_env_file() {
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        log_warning ".env файл не найден. Копируем из .env.example"
        if [ -f "$PROJECT_ROOT/.env.example" ]; then
            cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
        else
            log_error ".env.example не найден. Создайте .env файл"
            exit 1
        fi
    fi
}

# =============================================================================
# Platform Functions
# =============================================================================

deploy_heroku() {
    log_info "Деплой на Heroku..."

    check_command "heroku"
    check_command "docker"

    cd "$PROJECT_ROOT/deploy/heroku"

    # Логин в Heroku
    log_info "Аутентификация в Heroku..."
    heroku container:login

    # Сборка и пуш образа
    log_info "Сборка Docker образа..."
    docker build -t registry.heroku.com/"$HEROKU_APP_NAME"/web -f ../../Dockerfile.production "$PROJECT_ROOT"

    log_info "Пуш образа в Heroku..."
    docker push registry.heroku.com/"$HEROKU_APP_NAME"/web

    # Релиз
    log_info "Релиз на Heroku..."
    heroku container:release web -a "$HEROKU_APP_NAME"

    log_success "Деплой на Heroku завершен!"
}

deploy_railway() {
    log_info "Деплой на Railway..."

    check_command "railway"

    cd "$PROJECT_ROOT"

    # Деплой через Railway CLI
    log_info "Запуск деплоя..."
    railway up --environment "$ENV"

    log_success "Деплой на Railway завершен!"
}

deploy_render() {
    log_info "Деплой на Render..."

    # Render автоматически деплоит из GitHub
    # Этот скрипт может триггерить деплой через API

    if [ -n "$RENDER_API_KEY" ]; then
        log_info "Триггер деплоя через API..."
        curl -X POST \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $RENDER_API_KEY" \
            -d '{"serviceId": "'"$RENDER_SERVICE_ID"'"}' \
            "https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys"
    else
        log_warning "RENDER_API_KEY не установлен. Деплой будет выполнен автоматически из GitHub."
    fi

    log_success "Деплой на Render инициирован!"
}

deploy_aws() {
    log_info "Деплой на AWS ECS..."

    check_command "aws"
    check_command "docker"

    cd "$PROJECT_ROOT"

    # Логин в ECR
    log_info "Аутентификация в ECR..."
    aws ecr get-login-password --region "$AWS_REGION" | \
        docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID".dkr.ecr."$AWS_REGION".amazonaws.com

    # Сборка и пуш
    log_info "Сборка Docker образа..."
    docker build -t "$AWS_ACCOUNT_ID".dkr.ecr."$AWS_REGION".amazonaws.com/"$ECR_REPOSITORY":"$TAG" \
        -f Dockerfile.production "$PROJECT_ROOT"

    log_info "Пуш образа в ECR..."
    docker push "$AWS_ACCOUNT_ID".dkr.ecr."$AWS_REGION".amazonaws.com/"$ECR_REPOSITORY":"$TAG"

    # Обновление сервиса
    log_info "Обновление ECS сервиса..."
    aws ecs update-service \
        --cluster "$ECS_CLUSTER" \
        --service "$ECS_SERVICE" \
        --force-new-deployment \
        --region "$AWS_REGION"

    log_success "Деплой на AWS завершен!"
}

deploy_gcp() {
    log_info "Деплой на Google Cloud Run..."

    check_command "gcloud"

    cd "$PROJECT_ROOT"

    # Сборка и пуш
    log_info "Сборка и пуш в Artifact Registry..."
    gcloud builds submit \
        --tag "gcr.io/$GCP_PROJECT_ID/mentorhub:$TAG" \
        --file=Dockerfile.production \
        "$PROJECT_ROOT"

    # Деплой
    log_info "Деплой на Cloud Run..."
    gcloud run deploy "$GCP_SERVICE_NAME" \
        --image "gcr.io/$GCP_PROJECT_ID/mentorhub:$TAG" \
        --platform managed \
        --region "$GCP_REGION" \
        --allow-unauthenticated \
        --set-env-vars="ENVIRONMENT=$ENV"

    log_success "Деплой на GCP завершен!"
}

deploy_vercel() {
    log_info "Деплой frontend на Vercel..."

    check_command "vercel"

    cd "$PROJECT_ROOT/frontend"

    # Деплой
    if [ "$ENV" = "production" ]; then
        vercel --prod
    else
        vercel
    fi

    log_success "Деплой на Vercel завершен!"
}

deploy_netlify() {
    log_info "Деплой frontend на Netlify..."

    check_command "netlify"

    cd "$PROJECT_ROOT/frontend"

    # Деплой
    if [ "$ENV" = "production" ]; then
        netlify deploy --prod --dir=.next
    else
        netlify deploy --dir=.next
    fi

    log_success "Деплой на Netlify завершен!"
}

deploy_cloudflare() {
    log_info "Деплой frontend на Cloudflare Pages..."

    check_command "wrangler"

    cd "$PROJECT_ROOT/frontend"

    # Сборка
    log_info "Сборка Next.js..."
    npm run build

    # Деплой
    if [ "$ENV" = "production" ]; then
        wrangler pages deploy .next --project-name=mentorhub --branch=main
    else
        wrangler pages deploy .next --project-name=mentorhub
    fi

    log_success "Деплой на Cloudflare завершен!"
}

build_docker() {
    log_info "Сборка Docker образа..."

    check_command "docker"

    cd "$PROJECT_ROOT"

    # Сборка
    docker build -t "mentorhub:$TAG" -f Dockerfile.production "$PROJECT_ROOT"

    log_success "Docker образ собран: mentorhub:$TAG"

    # Тестирование
    if [ "$FORCE" = false ]; then
        log_info "Запуск тестового контейнера..."
        docker run --rm -d --name mentorhub-test -p 8000:8000 "mentorhub:$TAG"
        sleep 5

        # Проверка health endpoint
        if curl -f http://localhost:8000/api/v1/health &> /dev/null; then
            log_success "Health check пройден!"
        else
            log_warning "Health check не пройден. Проверьте логи."
        fi

        # Остановка контейнера
        docker stop mentorhub-test
    fi
}

deploy_all() {
    log_info "Деплой на все платформы..."

    deploy_heroku
    deploy_railway
    deploy_render
    deploy_aws
    deploy_gcp
    deploy_vercel
    deploy_netlify
    deploy_cloudflare

    log_success "Деплой на все платформы завершен!"
}

# =============================================================================
# Parse Arguments
# =============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        heroku|railway|render|aws|gcp|vercel|docker|all)
            PLATFORM="$1"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -e|--env)
            ENV="$2"
            shift 2
            ;;
        *)
            log_error "Неизвестный параметр: $1"
            show_help
            exit 1
            ;;
    esac
done

# =============================================================================
# Main
# =============================================================================

if [ -z "$PLATFORM" ]; then
    log_error "Платформа не указана"
    show_help
    exit 1
fi

log_info "Начало деплоя на $PLATFORM (окружение: $ENV, тег: $TAG)"

check_env_file

case $PLATFORM in
    heroku)
        deploy_heroku
        ;;
    railway)
        deploy_railway
        ;;
    render)
        deploy_render
        ;;
    aws)
        deploy_aws
        ;;
    gcp)
        deploy_gcp
        ;;
    vercel)
        deploy_vercel
        ;;
    netlify)
        deploy_netlify
        ;;
    cloudflare)
        deploy_cloudflare
        ;;
    docker)
        build_docker
        ;;
    all)
        deploy_all
        ;;
    *)
        log_error "Неизвестная платформа: $PLATFORM"
        exit 1
        ;;
esac

log_success "Деплой завершен успешно!"
