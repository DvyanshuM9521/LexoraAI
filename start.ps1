# Lexora AI — Startup Script
# Run this script to start both the backend and frontend servers

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "   LEXORA AI — Contract Intelligence      " -ForegroundColor Cyan
Write-Host "   Transforming Contracts into Intelligence" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Start Backend
Write-Host "[1/2] Starting Backend (FastAPI)..." -ForegroundColor Yellow
$backend = Start-Process -FilePath "powershell" -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location 'C:\MAJOR PROJECT\LexoraAI\backend'; C:\Users\anmol\anaconda3\envs\lexora-ai\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
) -PassThru

Start-Sleep -Seconds 3

# Start Frontend
Write-Host "[2/2] Starting Frontend (Vite + React)..." -ForegroundColor Yellow
$frontend = Start-Process -FilePath "powershell" -ArgumentList @(
    "-NoExit", "-Command",
    "Set-Location 'C:\MAJOR PROJECT\LexoraAI\frontend'; npm run dev"
) -PassThru

Start-Sleep -Seconds 3

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Application Running!" -ForegroundColor Green
Write-Host ""
Write-Host "  Frontend:  http://localhost:5173" -ForegroundColor White
Write-Host "  Backend:   http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  API Docs:  http://127.0.0.1:8000/api/docs" -ForegroundColor White
Write-Host "==========================================" -ForegroundColor Green
