@echo off
echo ==========================================
echo   AGENT BI - MIGRATION TEST RUNNER
echo ==========================================
echo.
echo 1. Verificando Backend (Porta 8000)...
netstat -ano | findstr :8000 > nul
if %errorlevel% neq 0 (
    echo [ERRO] Backend nao esta rodando!
    echo Por favor, inicie o backend em outro terminal com 'run.bat --backend-only'
    pause
    exit /b
)
echo [OK] Backend detectado.
echo.
echo 2. Iniciando Frontend SolidJS (Porta 3000)...
cd frontend-solid
npm run dev
