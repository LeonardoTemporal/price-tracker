@echo off
echo ============================================
echo  ACTUALIZADOR AUTOMATICO DE PRECIOS
echo ============================================
echo.
echo Este programa actualizara los precios
echo automaticamente cada 6 horas.
echo.
echo Para detenerlo, presiona Ctrl+C
echo.

cd /d %~dp0
.venv\Scripts\python.exe src\scheduler.py --intervalo 6

pause
