@echo off
REM ========================================
REM   AGENT BI - FRONTEND APENAS
REM   Executa: npm run dev:frontend
REM ========================================

echo.
echo ========================================
echo   AGENT BI - INICIANDO FRONTEND
echo ========================================
echo.

echo [INFO] Iniciando frontend em http://localhost:3000
echo.

npm run dev:frontend

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha ao iniciar frontend
    pause
    exit /b 1
)
