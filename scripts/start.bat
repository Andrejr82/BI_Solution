@echo off
chcp 65001 >nul
title Agent Solution BI - Launcher

echo ====================================================================
echo 🤖 Agent Solution BI - Launcher
echo ====================================================================
echo.

echo [1/2] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado! Instale Python 3.11+
    pause
    exit /b 1
)
echo ✓ Python OK

echo.
echo [2/2] Iniciando launcher...
echo.

python start_all.py

pause
