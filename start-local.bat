@echo off
echo Starting IPO-AI Local Development Environment...
echo.

echo Launching Backend FastAPI Server (http://localhost:8000)...
start "IPO-AI Backend" cmd /k "python -m uvicorn backend.src.main:app --reload --port 8000"

timeout /t 3 /nobreak >nul

echo Launching Frontend Next.js Server (http://localhost:3000)...
start "IPO-AI Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ===================================================
echo IPO-AI local servers launched successfully!
echo Frontend: http://localhost:3000
echo Backend:  http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo ===================================================
