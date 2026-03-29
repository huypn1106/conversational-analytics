@echo off
title Stats Center Start Script
color 0b

echo ===================================================
echo     Starting Stats Center (Conversational Analytics)
echo ===================================================
echo.

echo [1/3] Starting Docker containers (StarRocks Database ^& Redis Session Store)...
docker compose up -d redis starrocks
echo.

echo [2/3] Starting FastAPI Backend API...
:: Checks if a Python virtual environment exists and activates it automatically before running Uvicorn
start "Stats Center - Backend" cmd /k "cd backend && (if exist venv\Scripts\activate call venv\Scripts\activate) && python -m uvicorn app.main:app --reload --port 8000"

echo [3/3] Starting Vite+React Frontend...
start "Stats Center - Frontend" cmd /k "cd frontend && npm run dev"
echo.

echo ===================================================
echo      All systems are booting up!
echo ===================================================
echo.
echo IMPORTANT REMINDER: Make sure your local complete Ollama Desktop app is open and running in the background!
echo.
echo The Application will be available at:
echo   - Frontend UI: http://localhost:5173
echo   - Backend Swagger: http://localhost:8000/docs
echo.
echo Press any key to close this launcher...
pause >nul
