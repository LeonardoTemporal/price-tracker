@echo off
echo ============================================
echo   PRICE TRACKER v2.0 - BACKEND API
echo ============================================
echo.
echo Iniciando servidor FastAPI...
echo API disponible en: http://localhost:8000
echo Documentacion: http://localhost:8000/docs
echo.
echo Presiona Ctrl+C para detener
echo.

cd /d %~dp0
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

pause
