@echo off
echo ============================================
echo   PRICE TRACKER v2.0 - FULL STACK
echo ============================================
echo.
echo Este script iniciara:
echo   1. Backend API (FastAPI) en puerto 8000
echo   2. Frontend (React) en puerto 5173
echo.
echo Presiona cualquier tecla para continuar...
pause > nul

echo.
echo Instalando dependencias del frontend...
cd frontend
call npm install
cd ..

echo.
echo ============================================
echo   INICIANDO SERVIDORES...
echo ============================================
echo.
echo Backend API: http://localhost:8000
echo Frontend: http://localhost:5173
echo Docs API: http://localhost:8000/docs
echo.
echo IMPORTANTE: Mantén esta ventana abierta
echo Presiona Ctrl+C para detener ambos servidores
echo.

start "Backend API" cmd /k "cd /d %~dp0 && .venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak > nul

start "Frontend React" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo Servidores iniciados en ventanas separadas
echo.
pause
