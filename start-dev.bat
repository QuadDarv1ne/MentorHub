@echo off
REM =====================================================
REM MentorHub Development Startup Script
REM Platform: Windows CMD
REM Запускает: Backend (FastAPI) + Frontend (Next.js)
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
echo ║        🚀 MentorHub - Development Mode                     ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM =====================================================
REM ПРОВЕРКА ОКРУЖЕНИЯ
REM =====================================================

REM Проверка Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo !COLOR_RED!❌ Python не найден. Установите Python 3.10+!COLOR_RESET!
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo !COLOR_GREEN!✓!COLOR_RESET! Python: %PYTHON_VERSION%

REM Проверка Node.js
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo !COLOR_RED!❌ Node.js не найден. Установите Node.js 18+!COLOR_RESET!
    exit /b 1
)
for /f "tokens=2" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
echo !COLOR_GREEN!✓!COLOR_RESET! Node.js: %NODE_VERSION%

REM Проверка npm
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo !COLOR_RED!❌ npm не найден!COLOR_RESET!
    exit /b 1
)
for /f "tokens=2" %%i in ('npm --version 2^>^&1') do set NPM_VERSION=%%i
echo !COLOR_GREEN!✓!COLOR_RESET! npm: %NPM_VERSION%

echo.

REM =====================================================
REM ЗАГРУЗКА .ENV
REM =====================================================

if exist .env (
    echo !COLOR_GREEN!✓!COLOR_RESET! Загрузка переменных из .env
    for /f "delims=" %%a in (.env) do (
        setlocal enabledelayedexpansion
        for /f "tokens=1,* delims==" %%b in ("%%a") do (
            if not "%%b"=="#" set "%%b=%%c"
        )
        endlocal
    )
)

REM =====================================================
REM ЗАПУСК BACKEND
REM =====================================================

echo.
echo !COLOR_CYAN!📡 Запуск Backend (FastAPI) на порту 8000...!COLOR_RESET!

cd backend

REM Установка зависимостей Python если нужно
if not exist "__pycache__" (
    echo !COLOR_YELLOW!⚠ Установка Python зависимостей...!COLOR_RESET!
    pip install -e . 2>nul
)

REM Запуск backend в отдельном окне
start "MentorHub Backend" cmd /k "cd backend && set PORT=8000 && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo !COLOR_GREEN!✓!COLOR_RESET! Backend запущен в отдельном окне
echo    URL: !COLOR_CYAN!http://127.0.0.1:8000!COLOR_RESET!
echo    API Docs: !COLOR_CYAN!http://127.0.0.1:8000/docs!COLOR_RESET!

cd ..

REM =====================================================
REM ЗАПУСК FRONTEND
REM =====================================================

echo.
echo !COLOR_CYAN!🎨 Запуск Frontend (Next.js) на порту 3001...!COLOR_RESET!

cd frontend

REM Установка зависимостей Node.js если нужно
if not exist "node_modules" (
    echo !COLOR_YELLOW!⚠ Установка Node.js зависимостей...!COLOR_RESET!
    call npm install
)

REM Запуск frontend в отдельном окне
start "MentorHub Frontend" cmd /k "cd frontend && set PORT=3001 && npm run dev"

echo !COLOR_GREEN!✓!COLOR_RESET! Frontend запущен в отдельном окне
echo    URL: !COLOR_CYAN!http://localhost:3001!COLOR_RESET!

cd ..

REM =====================================================
REM ИНФОРМАЦИЯ
REM =====================================================

echo.
echo ════════════════════════════════════════════════════════════
echo !COLOR_GREEN!✓ Серверы запущены!COLOR_RESET!
echo.
echo !COLOR_CYAN!📍 URLs:!COLOR_RESET!
echo    Backend API:    !COLOR_CYAN!http://127.0.0.1:8000!COLOR_RESET!
echo    API Docs:       !COLOR_CYAN!http://127.0.0.1:8000/docs!COLOR_RESET!
echo    Frontend:       !COLOR_CYAN!http://localhost:3001!COLOR_RESET!
echo.
echo !COLOR_YELLOW!🛑 Остановка: Закройте оба окна!COLOR_RESET!
echo ════════════════════════════════════════════════════════════
echo.

endlocal
exit /b 0
