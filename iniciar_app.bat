@echo off
echo ============================================
echo    PRICE TRACKER - Rastreador de Precios
echo ============================================
echo.
echo Iniciando aplicacion web...
echo.
echo La aplicacion se abrira en tu navegador.
echo Para detenerla, presiona Ctrl+C
echo.

cd /d %~dp0
.venv\Scripts\streamlit.exe run app.py --server.headless true

pause
