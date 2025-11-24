#!/usr/bin/env pwsh
# Start both Backend and Frontend servers

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        🚀 MentorHub - Starting Development Servers        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Backend
Write-Host "📡 Starting Backend (FastAPI)..." -ForegroundColor Green
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd backend; uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
Start-Sleep -Seconds 3

# Frontend  
Write-Host "🎨 Starting Frontend (Next.js)..." -ForegroundColor Green
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Yellow
Write-Host "✅ Servers are starting..." -ForegroundColor Green
Write-Host ""
Write-Host "📍 URLs:" -ForegroundColor Cyan
Write-Host "   Backend API:    http://127.0.0.1:8000" -ForegroundColor White
Write-Host "   API Docs:       http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "   Frontend:       http://localhost:3001" -ForegroundColor White
Write-Host ""
Write-Host "🛑 To stop: Close both terminal windows or press Ctrl+C" -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════════" -ForegroundColor Yellow
