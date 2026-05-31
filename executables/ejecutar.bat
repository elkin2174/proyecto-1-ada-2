@echo off
REM ============================================================
REM  Lanzador del proyecto "Plan de riego optimo de una finca"
REM  Ejecuta la interfaz interactiva usando el Python instalado.
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo No se encontro Python en el PATH.
    echo Instala Python 3 desde https://www.python.org/downloads/ y vuelve a intentar.
    pause
    exit /b 1
)

python -X utf8 main.py
echo.
pause
