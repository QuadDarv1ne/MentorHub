#!/usr/bin/env pwsh
# Quick Start Script for MentorHub Backend

Write-Host "🚀 Starting MentorHub Backend..." -ForegroundColor Green
Write-Host ""

# Check Python
Write-Host "📌 Checking Python version..." -ForegroundColor Cyan
python --version

# Navigate to backend
Set-Location backend

# Check if dependencies installed
Write-Host ""
Write-Host "📦 Checking dependencies..." -ForegroundColor Cyan
if (-not (Test-Path "venv")) {
    Write-Host "⚠️  Virtual environment not found. Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements-dev.txt
} else {
    Write-Host "✅ Dependencies already installed" -ForegroundColor Green
}

# Initialize database
Write-Host ""
Write-Host "🗄️  Initializing database..." -ForegroundColor Cyan
if (-not (Test-Path "mentorhub.db")) {
    python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine); print('✅ Database created')"
} else {
    Write-Host "✅ Database already exists" -ForegroundColor Green
}

# Start server
Write-Host ""
Write-Host "🌐 Starting FastAPI server..." -ForegroundColor Green
Write-Host "📍 API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "📖 ReDoc: http://localhost:8000/redoc" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
