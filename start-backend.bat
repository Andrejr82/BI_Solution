@echo off
REM ========================================
REM   AGENT BI - BACKEND APENAS
REM   Executa: npm run dev:backend
REM ========================================

echo.
echo ========================================
echo   AGENT BI - INICIANDO BACKEND
echo ========================================
echo.

REM Verificar se .env existe
if not exist "backend\.env" (
    echo [AVISO] Arquivo backend\.env nao encontrado!
    pause
)

echo [INFO] Iniciando backend em http://localhost:8000
echo.

npm run dev:backend

if %errorlevel% neq 0 (
    echo.
    echo [ERRO] Falha ao iniciar backend
    pause
    exit /b 1
)
