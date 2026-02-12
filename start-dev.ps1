# Mental Wellness - Development Startup Script
Write-Host "`n=== Starting Mental Wellness App ===" -ForegroundColor Cyan
Write-Host ""

# Backend
Write-Host "Starting Backend API..." -ForegroundColor Yellow
Set-Location $PSScriptRoot\backend
if (-not (Test-Path .venv)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Gray
    python -m venv .venv
}
.venv\Scripts\activate
pip install -q -r requirements.txt 2>&1 | Out-Null
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; .venv\Scripts\activate; Write-Host 'Backend API running on http://localhost:8000' -ForegroundColor Green; Write-Host 'API Docs: http://localhost:8000/docs' -ForegroundColor Cyan; uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal

Start-Sleep -Seconds 2

# Frontend
Write-Host "Starting Frontend..." -ForegroundColor Yellow
Set-Location $PSScriptRoot\web
if (-not (Test-Path node_modules)) {
    Write-Host "Installing npm packages..." -ForegroundColor Gray
    npm install
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\web'; Write-Host 'Frontend running on http://localhost:3000' -ForegroundColor Green; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "✓ Servers starting in separate windows" -ForegroundColor Green
Write-Host ""
Write-Host "Backend API:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs:     http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Frontend:     http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit (servers will keep running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
