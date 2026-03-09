# =============================================================================
# MentorHub PowerShell Deployment Script
# =============================================================================
# Скрипт для деплоя на различные платформы (Windows PowerShell)
# =============================================================================
# Использование:
#   .\deploy.ps1 <platform> [options]
#
# Платформы:
#   heroku     - Деплой на Heroku
#   railway    - Деплой на Railway
#   render     - Деплой на Render
#   aws        - Деплой на AWS ECS
#   gcp        - Деплой на Google Cloud Run
#   vercel     - Деплой frontend на Vercel
#   docker     - Сборка Docker образа
#   all        - Деплой на все платформы
# =============================================================================

param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('heroku', 'railway', 'render', 'aws', 'gcp', 'vercel', 'netlify', 'cloudflare', 'docker', 'all')]
    [string]$Platform,

    [switch]$Verbose,
    [switch]$Force,
    [string]$Tag = 'latest',
    [ValidateSet('staging', 'production')]
    [string]$Env = 'production',

    [switch]$Help
)

# =============================================================================
# Configuration
# =============================================================================
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# =============================================================================
# Helper Functions
# =============================================================================

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Verbose-Custom {
    param([string]$Message)
    if ($Verbose) {
        Write-Host "[VERBOSE] $Message" -ForegroundColor Cyan
    }
}

function Show-Help {
    @'
MentorHub Deployment Script (PowerShell)

Использование:
    .\deploy.ps1 <platform> [options]

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
    -Verbose  Подробный вывод
    -Force    Принудительный деплой
    -Tag      Тег для Docker образа (по умолчанию: latest)
    -Env      Окружение: staging или production (по умолчанию: production)
    -Help     Показать эту справку

Примеры:
    .\deploy.ps1 -Platform heroku
    .\deploy.ps1 -Platform aws -Env staging
    .\deploy.ps1 -Platform docker -Tag v1.2.3
    .\deploy.ps1 -Platform all -Verbose

'@
}

function Test-Command {
    param([string]$Command)
    if (-not (Get-Command $Command -ErrorAction SilentlyContinue)) {
        Write-Error-Custom "$Command не найден. Пожалуйста, установите $Command"
        exit 1
    }
}

function Check-EnvFile {
    $envFile = Join-Path $ProjectRoot ".env"
    $envExample = Join-Path $ProjectRoot ".env.example"

    if (-not (Test-Path $envFile)) {
        Write-Warning ".env файл не найден. Копируем из .env.example"
        if (Test-Path $envExample) {
            Copy-Item $envExample $envFile
        } else {
            Write-Error-Custom ".env.example не найден. Создайте .env файл"
            exit 1
        }
    }
}

# =============================================================================
# Deployment Functions
# =============================================================================

function Deploy-Heroku {
    Write-Info "Деплой на Heroku..."

    Test-Command "docker"

    $herokuApp = $env:HEROKU_APP_NAME
    if (-not $herokuApp) {
        Write-Error-Custom "HEROKU_APP_NAME не установлен в环境变量"
        exit 1
    }

    # Логин
    Write-Info "Аутентификация в Heroku..."
    heroku container:login

    # Сборка
    Write-Info "Сборка Docker образа..."
    docker build -t "registry.heroku.com/$herokuApp/web" `
        -f (Join-Path $ProjectRoot "Dockerfile.production") `
        $ProjectRoot

    # Пуш
    Write-Info "Пуш образа в Heroku..."
    docker push "registry.heroku.com/$herokuApp/web"

    # Релиз
    Write-Info "Релиз на Heroku..."
    heroku container:release web -a $herokuApp

    Write-Success "Деплой на Heroku завершен!"
}

function Deploy-Railway {
    Write-Info "Деплой на Railway..."

    Test-Command "railway"

    Set-Location $ProjectRoot

    Write-Info "Запуск деплоя..."
    railway up --environment $Env

    Write-Success "Деплой на Railway завершен!"
}

function Deploy-Render {
    Write-Info "Деплой на Render..."

    $renderApiKey = $env:RENDER_API_KEY
    $renderServiceId = $env:RENDER_SERVICE_ID

    if ($renderApiKey -and $renderServiceId) {
        Write-Info "Триггер деплоя через API..."
        $body = @{ serviceId = $renderServiceId } | ConvertTo-Json
        Invoke-RestMethod -Method Post `
            -Uri "https://api.render.com/v1/services/$renderServiceId/deploys" `
            -Headers @{ Authorization = "Bearer $renderApiKey"; "Content-Type" = "application/json" } `
            -Body $body
    } else {
        Write-Warning "RENDER_API_KEY не установлен. Деплой будет выполнен автоматически из GitHub."
    }

    Write-Success "Деплой на Render инициирован!"
}

function Deploy-AWS {
    Write-Info "Деплой на AWS ECS..."

    Test-Command "aws"
    Test-Command "docker"

    $awsRegion = $env:AWS_REGION
    $awsAccountId = $env:AWS_ACCOUNT_ID
    $ecrRepo = $env:ECR_REPOSITORY
    $ecsCluster = $env:ECS_CLUSTER
    $ecsService = $env:ECS_SERVICE

    # Логин в ECR
    Write-Info "Аутентификация в ECR..."
    $ecrPassword = aws ecr get-login-password --region $awsRegion
    docker login --username AWS --password-stdin "$awsAccountId.dkr.ecr.$awsRegion.amazonaws.com"

    # Сборка
    Write-Info "Сборка Docker образа..."
    docker build -t "$awsAccountId.dkr.ecr.$awsRegion.amazonaws.com/$ecrRepo`:$Tag" `
        -f (Join-Path $ProjectRoot "Dockerfile.production") `
        $ProjectRoot

    # Пуш
    Write-Info "Пуш образа в ECR..."
    docker push "$awsAccountId.dkr.ecr.$awsRegion.amazonaws.com/$ecrRepo`:$Tag"

    # Обновление сервиса
    Write-Info "Обновление ECS сервиса..."
    aws ecs update-service `
        --cluster $ecsCluster `
        --service $ecsService `
        --force-new-deployment `
        --region $awsRegion

    Write-Success "Деплой на AWS завершен!"
}

function Deploy-GCP {
    Write-Info "Деплой на Google Cloud Run..."

    Test-Command "gcloud"

    $gcpProjectId = $env:GCP_PROJECT_ID
    $gcpServiceName = $env:GCP_SERVICE_NAME
    $gcpRegion = $env:GCP_REGION

    # Сборка и пуш
    Write-Info "Сборка и пуш в Artifact Registry..."
    gcloud builds submit `
        --tag "gcr.io/$gcpProjectId/mentorhub:$Tag" `
        --file=(Join-Path $ProjectRoot "Dockerfile.production") `
        $ProjectRoot

    # Деплой
    Write-Info "Деплой на Cloud Run..."
    gcloud run deploy $gcpServiceName `
        --image "gcr.io/$gcpProjectId/mentorhub:$Tag" `
        --platform managed `
        --region $gcpRegion `
        --allow-unauthenticated `
        --set-env-vars="ENVIRONMENT=$Env"

    Write-Success "Деплой на GCP завершен!"
}

function Deploy-Vercel {
    Write-Info "Деплой frontend на Vercel..."

    Test-Command "vercel"

    $frontendDir = Join-Path $ProjectRoot "frontend"
    Set-Location $frontendDir

    if ($Env -eq "production") {
        vercel --prod
    } else {
        vercel
    }

    Write-Success "Деплой на Vercel завершен!"
}

function Deploy-Netlify {
    Write-Info "Деплой frontend на Netlify..."

    Test-Command "netlify"

    $frontendDir = Join-Path $ProjectRoot "frontend"
    Set-Location $frontendDir

    if ($Env -eq "production") {
        netlify deploy --prod --dir=.next
    } else {
        netlify deploy --dir=.next
    }

    Write-Success "Деплой на Netlify завершен!"
}

function Deploy-Cloudflare {
    Write-Info "Деплой frontend на Cloudflare Pages..."

    Test-Command "wrangler"

    $frontendDir = Join-Path $ProjectRoot "frontend"
    Set-Location $frontendDir

    # Сборка
    Write-Info "Сборка Next.js..."
    npm run build

    # Деплой
    if ($Env -eq "production") {
        wrangler pages deploy .next --project-name=mentorhub --branch=main
    } else {
        wrangler pages deploy .next --project-name=mentorhub
    }

    Write-Success "Деплой на Cloudflare завершен!"
}

function Build-Docker {
    Write-Info "Сборка Docker образа..."

    Test-Command "docker"

    Set-Location $ProjectRoot

    # Сборка
    docker build -t "mentorhub:$Tag" -f (Join-Path $ProjectRoot "Dockerfile.production") $ProjectRoot

    Write-Success "Docker образ собран: mentorhub:$Tag"

    # Тестирование
    if (-not $Force) {
        Write-Info "Запуск тестового контейнера..."
        $containerId = docker run --rm -d --name mentorhub-test -p 8000:8000 "mentorhub:$Tag"
        Start-Sleep -Seconds 5

        # Проверка health endpoint
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-Success "Health check пройден!"
            }
        } catch {
            Write-Warning "Health check не пройден. Проверьте логи."
        }

        # Остановка контейнера
        docker stop mentorhub-test
    }
}

function Deploy-All {
    Write-Info "Деплой на все платформы..."

    Deploy-Heroku
    Deploy-Railway
    Deploy-Render
    Deploy-AWS
    Deploy-GCP
    Deploy-Vercel
    Deploy-Netlify
    Deploy-Cloudflare

    Write-Success "Деплой на все платформы завершен!"
}

# =============================================================================
# Main
# =============================================================================

if ($Help) {
    Show-Help
    exit 0
}

if (-not $Platform) {
    Write-Error-Custom "Платформа не указана"
    Show-Help
    exit 1
}

Write-Info "Начало деплоя на $Platform (окружение: $Env, тег: $Tag)"

Check-EnvFile

switch ($Platform) {
    'heroku' { Deploy-Heroku }
    'railway' { Deploy-Railway }
    'render' { Deploy-Render }
    'aws' { Deploy-AWS }
    'gcp' { Deploy-GCP }
    'vercel' { Deploy-Vercel }
    'netlify' { Deploy-Netlify }
    'cloudflare' { Deploy-Cloudflare }
    'docker' { Build-Docker }
    'all' { Deploy-All }
    default {
        Write-Error-Custom "Неизвестная платформа: $Platform"
        exit 1
    }
}

Write-Success "Деплой завершен успешно!"
