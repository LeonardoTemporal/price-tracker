@echo off
echo ============================================
echo   PRICE TRACKER v2.0 - FRONTEND REACT
echo ============================================
echo.
echo Instalando dependencias de npm (solo primera vez)...
cd frontend
call npm install
echo.
echo Iniciando servidor de desarrollo...
echo App disponible en: http://localhost:5173
echo.
echo Presiona Ctrl+C para detener
echo.
call npm run dev

pause
