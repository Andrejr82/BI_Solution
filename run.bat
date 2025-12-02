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
echo [1/7] Limpando processos antigos...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul
echo [OK] Processos limpos.
echo.

REM Verificar e limpar porta 8000
echo [2/7] Verificando porta 8000...
setlocal enabledelayedexpansion
set "PORT_CLEARED=0"
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo [AVISO] Processo %%a encontrado na porta 8000
    echo [INFO] Encerrando processo %%a...
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo [OK] Processo %%a encerrado com sucesso
        set "PORT_CLEARED=1"
    ) else (
        echo [ERRO] Falha ao encerrar processo %%a
    )
)
if !PORT_CLEARED! equ 1 (
    echo [INFO] Aguardando liberacao da porta...
    timeout /t 2 /nobreak >nul
)
echo [OK] Porta 8000 livre.
echo.


REM Iniciar Backend
echo [3/7] Iniciando Backend FastAPI (porta 8000)...
cd /d "%~dp0backend"
start "Agent BI - Backend" cmd /k "python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 5 /nobreak >nul
echo [OK] Backend iniciado.
echo.

REM Verificar Backend
echo [4/7] Verificando Backend...
curl -s http://127.0.0.1:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend online e respondendo!
) else (
    echo [AVISO] Backend ainda inicializando...
)
echo.

REM Iniciar Frontend SolidJS
echo [5/7] Iniciando Frontend SolidJS (porta 3000)...
cd /d "%~dp0frontend-solid"
start "Agent BI - Frontend" cmd /k "pnpm dev"
timeout /t 5 /nobreak >nul
echo [OK] Frontend iniciado.
echo.

REM Abrir navegador
echo [6/7] Abrindo navegador...
timeout /t 3 /nobreak >nul
start http://localhost:3000
echo.

REM Resumo
echo [7/7] Sistema iniciado com sucesso!
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

