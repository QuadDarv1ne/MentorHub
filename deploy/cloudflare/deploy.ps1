# Cloudflare Pages Deploy Script для MentorHub (PowerShell)
# =====================================================

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🚀 MentorHub - Cloudflare Pages Deploy" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Проверка Wrangler
try {
    $wrangler = Get-Command wrangler -ErrorAction Stop
} catch {
    Write-Host "❌ Wrangler не установлен. Установите:" -ForegroundColor Red
    Write-Host "   npm install -g wrangler" -ForegroundColor Yellow
    exit 1
}

# Проверка авторизации
Write-Host ""
Write-Host "🔐 Проверка авторизации..." -ForegroundColor Yellow
try {
    wrangler whoami | Out-Null
} catch {
    Write-Host "⚠️  Требуется авторизация в Cloudflare" -ForegroundColor Yellow
    wrangler login
}

# Переход в директорию frontend
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendDir = Join-Path $scriptDir "..\..\frontend"
Set-Location $frontendDir

Write-Host ""
Write-Host "📦 Установка зависимостей..." -ForegroundColor Yellow
npm ci --legacy-peer-deps

Write-Host ""
Write-Host "🔨 Сборка frontend..." -ForegroundColor Yellow
$env:NEXT_TELEMETRY_DISABLED = "1"
npm run build

Write-Host ""
Write-Host "🚀 Деплой на Cloudflare Pages..." -ForegroundColor Green

# Деплой
wrangler pages deploy .next `
    --project-name=mentorhub `
    --branch=main `
    --commit-dirty=true

Write-Host ""
Write-Host "✅ Деплой завершён!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Проверить статус:" -ForegroundColor Cyan
Write-Host "   https://dash.cloudflare.com/?to=/:account/pages/view/mentorhub" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Сайт доступен по адресу:" -ForegroundColor Cyan
Write-Host "   https://mentorhub.pages.dev" -ForegroundColor White
Write-Host ""
