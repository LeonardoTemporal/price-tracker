@echo off
echo ============================================
echo  PRICE TRACKER v3.0 - Sistema Multi-usuario
echo  Iniciando Backend y Frontend...
echo ============================================
echo.

cd /d %~dp0

:: Verificar que existe .env
if not exist .env (
    echo [ERROR] No se encontro el archivo .env
    echo Copiando desde .env.example...
    copy .env.example .env
    echo.
    echo IMPORTANTE: Edita el archivo .env con tu configuracion
    pause
    exit /b 1
)

:: Inicializar base de datos si no existe
if not exist price_tracker.db (
    echo [INFO] Inicializando base de datos...
    .venv\Scripts\python.exe -m backend.app.database
    echo.
)

:: Iniciar backend
echo [BACKEND] Iniciando servidor FastAPI en puerto 8000...
start "Price Tracker - Backend" cmd /k ".venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload"

:: Esperar 3 segundos
timeout /t 3 /nobreak > nul

:: Verificar si npm esta instalado en frontend
if not exist "frontend\node_modules\" (
    echo [FRONTEND] Instalando dependencias de npm...
    cd frontend
    call npm install
    cd ..
    echo.
)

:: Iniciar frontend
echo [FRONTEND] Iniciando servidor React/Vite en puerto 5173...
start "Price Tracker - Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ============================================
echo  Servidores iniciados exitosamente
echo ============================================
echo.
echo  Frontend: http://localhost:5173
echo  Backend:  http://localhost:8000
echo  API Docs: http://localhost:8000/docs
echo.
echo  1. Abre http://localhost:5173/register para crear tu cuenta
echo  2. O usa http://localhost:5173/login si ya tienes cuenta
echo.
echo  Presiona Ctrl+C en cada ventana para detener los servidores
echo ============================================
pause
