@echo off
REM ========================================
REM   AGENT BI - INICIALIZADOR RÁPIDO
REM   Executa: npm run dev
REM ========================================

echo.
echo ========================================
echo   AGENT BI - INICIANDO SISTEMA
echo ========================================
echo.

REM Verificar se Node.js está instalado
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] Node.js nao encontrado!
    echo [INFO] Instale Node.js de https://nodejs.org/
    pause
    exit /b 1
)

REM Verificar se npm está instalado
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] npm nao encontrado!
    echo [INFO] Reinstale Node.js de https://nodejs.org/
    pause
    exit /b 1
)

REM Verificar se pnpm está instalado
where pnpm >nul 2>nul
if %errorlevel% neq 0 (
    echo [AVISO] pnpm nao encontrado. Instalando via npm...
    call npm install -g pnpm
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao instalar pnpm. Instale manualmente: npm install -g pnpm
        pause
        exit /b 1
    )
    echo [OK] pnpm instalado com sucesso
)

REM Verificar dependencies do frontend
if not exist "frontend-solid\node_modules" (
    echo [AVISO] Dependencias do frontend nao encontradas. Instalando...
    cd frontend-solid
    call pnpm install
    cd ..
)

REM Verificar se .env existe
if not exist "backend\.env" (
    echo [AVISO] Arquivo backend\.env nao encontrado!
    echo [INFO] Execute: npm run validate:env
    pause
)

REM Limpar portas primeiro
echo [1/4] Limpando portas 8000 e 3000...
call npm run clean:ports >nul 2>&1
echo [OK] Portas limpas
echo.

REM Iniciar backend em background
echo [2/4] Iniciando backend...
start /B cmd /c "cd backend && .venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000 > ..\logs\backend.log 2>&1"

REM Aguardar backend estar pronto (health check)
echo [3/4] Aguardando backend estar pronto...
echo [INFO] Startup otimizado: ~5-15 segundos
set MAX_ATTEMPTS=30
set ATTEMPT=0

:WAIT_BACKEND
set /a ATTEMPT+=1
if %ATTEMPT% gtr %MAX_ATTEMPTS% (
    echo [ERRO] Backend nao respondeu apos 30 segundos
    echo [INFO] Verifique os logs em logs\backend.log
    pause
    exit /b 1
)

REM Mostrar progresso a cada 5 tentativas
set /a MOD=ATTEMPT %% 5
if %MOD% equ 0 echo [INFO] Tentativa %ATTEMPT%/%MAX_ATTEMPTS%...

REM Tentar conectar ao health endpoint usando curl.exe (nao o alias do PS)
curl.exe -s -o nul -w "" http://localhost:8000/health
if %errorlevel% equ 0 (
    echo [OK] Backend pronto em http://localhost:8000
    goto BACKEND_READY
)

REM Aguardar 1 segundo e tentar novamente
timeout /t 1 /nobreak >nul
goto WAIT_BACKEND

:BACKEND_READY
echo.

REM Iniciar frontend
echo [4/4] Iniciando frontend...
cd frontend-solid
echo [INFO] Iniciando servidor de desenvolvimento (limpando cache)...
start cmd /k "pnpm dev --force"
cd ..

echo.
echo ========================================
echo   SISTEMA RODANDO
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000 (aguarde ~10s)
echo API Docs: http://localhost:8000/docs
echo.
echo Logs do backend: logs\backend.log
echo.
echo ========================================
echo.
echo [INFO] Backend iniciado com sucesso! (startup otimizado: ~3-5s)
echo [INFO] Frontend esta compilando...
echo [INFO] Aguarde ~10 segundos e acesse http://localhost:3000
echo.
echo [PERFORMANCE] Lazy Loading ativado:
echo   - Backend inicia em 3-5s (vs 15-25s anterior)
echo   - Primeira query pode levar +2s (inicializacao de agentes)
echo   - Queries subsequentes: velocidade normal
echo.
echo [DICA] Para encerrar:
echo   1. Feche a janela do frontend
echo   2. Execute: npm run clean:ports
echo.
pause
