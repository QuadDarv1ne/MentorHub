@echo off
REM =====================================================
REM MentorHub Production Startup Script
REM Platform: Windows CMD
REM Запускает: Docker Compose (все сервисы)
REM =====================================================

setlocal EnableDelayedExpansion

REM Цвета для Windows 10+
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do (
    set "DEL=%%a"
    set "COLOR_GREEN=%%b[32m"
    set "COLOR_RED=%%b[31m"
    set "COLOR_YELLOW=%%b[33m"
    set "COLOR_CYAN=%%b[36m"
    set "COLOR_RESET=%%b[0m"
)

echo ╔════════════════════════════════════════════════════════════╗
echo ║        🚀 MentorHub - Production Mode                      ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM =====================================================
REM ПРОВЕРКА ОКРУЖЕНИЯ
REM =====================================================

REM Проверка Docker
where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo !COLOR_RED!❌ Docker не найден. Установите Docker Desktop!COLOR_RESET!
    exit /b 1
)
for /f "tokens=1-3" %%i in ('docker --version') do set DOCKER_VERSION=%%i %%j %%k
echo !COLOR_GREEN!✓!COLOR_RESET! Docker: %DOCKER_VERSION%

REM Проверка Docker Compose
where docker-compose >nul 2>&1
if %errorlevel% neq 0 (
    where docker >nul 2>&1 && (
        docker compose version >nul 2>&1
        if %errorlevel% neq 0 (
            echo !COLOR_RED!❌ Docker Compose не найден!COLOR_RESET!
            exit /b 1
        )
    ) || (
        echo !COLOR_RED!❌ Docker Compose не найден!COLOR_RESET!
        exit /b 1
    )
)
echo !COLOR_GREEN!✓!COLOR_RESET! Docker Compose найден

echo.

REM =====================================================
REM ЗАГРУЗКА .ENV
REM =====================================================

if not exist .env (
    echo !COLOR_YELLOW!⚠ .env файл не найден. Копирование из .env.example...!COLOR_RESET!
    copy .env.example .env
    echo !COLOR_YELLOW!⚠ Отредактируйте .env файл и запустите скрипт снова!COLOR_RESET!
    exit /b 1
)

echo !COLOR_GREEN!✓!COLOR_RESET! .env файл найден

REM Проверка обязательных переменных
findstr /C:"SECRET_KEY=" .env >nul
if %errorlevel% neq 0 (
    echo !COLOR_RED!❌ SECRET_KEY не установлен в .env!COLOR_RESET!
    exit /b 1
)

findstr /C:"DB_PASSWORD=" .env >nul
if %errorlevel% neq 0 (
    echo !COLOR_RED!❌ DB_PASSWORD не установлен в .env!COLOR_RESET!
    exit /b 1
)

echo !COLOR_GREEN!✓!COLOR_RESET! Все обязательные переменные установлены

REM =====================================================
REM ЗАПУСК DOCKER COMPOSE
REM =====================================================

echo.
echo !COLOR_CYAN!🐳 Запуск Docker Compose сервисов...!COLOR_RESET!
echo.

REM Остановка старых контейнеров
echo !COLOR_YELLOW!⏳ Остановка существующих сервисов...!COLOR_RESET!
docker-compose -f docker-compose.prod.yml down >nul 2>&1

REM Запуск сервисов
echo !COLOR_CYAN!🚀 Запуск сервисов в production режиме...!COLOR_RESET!
docker-compose -f docker-compose.prod.yml up -d --build

REM =====================================================
REM ПРОВЕРКА СТАТУСА
REM =====================================================

echo.
echo !COLOR_CYAN!📊 Проверка статуса сервисов...!COLOR_RESET!
echo.

timeout /t 5 /nobreak >nul

docker-compose -f docker-compose.prod.yml ps

REM =====================================================
REM ИНФОРМАЦИЯ
REM =====================================================

echo.
echo ════════════════════════════════════════════════════════════
echo !COLOR_GREEN!✓ MentorHub запущен в production режиме!COLOR_RESET!
echo.
echo !COLOR_CYAN!📍 URLs:!COLOR_RESET!
echo    Frontend:       !COLOR_CYAN!http://localhost!COLOR_RESET!
echo    Backend API:    !COLOR_CYAN!http://localhost/api/v1!COLOR_RESET!
echo    API Docs:       !COLOR_CYAN!http://localhost/docs!COLOR_RESET!
echo    Grafana:        !COLOR_CYAN!http://localhost:3001!COLOR_RESET!
echo    Prometheus:     !COLOR_CYAN!http://localhost:9090!COLOR_RESET!
echo.
echo !COLOR_YELLOW!🛑 Остановка:!COLOR_RESET!
echo    !COLOR_CYAN!docker-compose -f docker-compose.prod.yml down!COLOR_RESET!
echo.
echo !COLOR_YELLOW!📋 Логи:!COLOR_RESET!
echo    !COLOR_CYAN!docker-compose -f docker-compose.prod.yml logs -f!COLOR_RESET!
echo.
echo ════════════════════════════════════════════════════════════
echo.

endlocal
exit /b 0
