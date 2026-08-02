Write-Host "Starting IPO-AI Local Development Environment..." -ForegroundColor Green

Write-Host "Launching Backend FastAPI Server (http://localhost:8000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "python -m uvicorn backend.src.main:app --reload --port 8000"

Start-Sleep -Seconds 3

Write-Host "Launching Frontend Next.js Server (http://localhost:3000)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location frontend; npm run dev"

Write-Host "`n===================================================" -ForegroundColor Green
Write-Host "IPO-AI local servers launched successfully!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Green
