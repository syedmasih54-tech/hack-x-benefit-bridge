@echo off
echo ========================================================
echo   Starting BenefitBridge Full Stack (Backend + Frontend)
echo ========================================================

echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "BenefitBridge Backend" cmd /k "cd /d "%~dp0..\codes" && .venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

echo [2/2] Starting Vite Frontend on http://127.0.0.1:5173 ...
start "BenefitBridge Frontend" cmd /k "cd /d "%~dp0" && npm run dev"

echo.
echo Both servers started in background windows!
echo - Frontend: http://localhost:5173
echo - Backend:  http://127.0.0.1:8000
echo ========================================================

