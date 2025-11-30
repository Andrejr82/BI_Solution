@echo off
REM ========================================
REM   AGENT BI - SISTEMA COMPLETO
REM   Backend FastAPI + Frontend SolidJS
REM ========================================

echo.
echo ========================================
echo   AGENT BI - INICIANDO SISTEMA
echo ========================================
echo.

REM Limpar processos antigos
echo [1/6] Limpando processos antigos...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul
echo [OK] Processos limpos.
echo.

REM Iniciar Backend
echo [2/6] Iniciando Backend FastAPI (porta 8000)...
cd /d "%~dp0backend"
start "Agent BI - Backend" cmd /k "python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 5 /nobreak >nul
echo [OK] Backend iniciado.
echo.

REM Verificar Backend
echo [3/6] Verificando Backend...
curl -s http://127.0.0.1:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend online e respondendo!
) else (
    echo [AVISO] Backend ainda inicializando...
)
echo.

REM Iniciar Frontend SolidJS
echo [4/6] Iniciando Frontend SolidJS (porta 3000)...
cd /d "%~dp0frontend-solid"
start "Agent BI - Frontend" cmd /k "pnpm dev"
timeout /t 5 /nobreak >nul
echo [OK] Frontend iniciado.
echo.

REM Abrir navegador
echo [5/6] Abrindo navegador...
timeout /t 3 /nobreak >nul
start http://localhost:3000
echo.

REM Resumo
echo [6/6] Sistema iniciado com sucesso!
echo.
echo ========================================
echo   SISTEMA ONLINE
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Credenciais de teste:
echo   Admin:     admin / Admin@2024
echo   Comprador: comprador / comprador123
echo.
echo ========================================
echo.
echo Pressione qualquer tecla para fechar...
pause >nul
