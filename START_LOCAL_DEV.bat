@echo off
REM ============================================================
REM DESENVOLVIMENTO LOCAL SEM DOCKER - Agent BI
REM Otimizado com health check para garantir backend pronto
REM ============================================================

echo.
echo ============================================================
echo   AGENT BI - DESENVOLVIMENTO LOCAL (SEM DOCKER)
echo   Otimizado para 8GB RAM + Health Check
echo ============================================================
echo.

cd /d C:\Agente_BI\BI_Solution

echo [LIMPEZA] Encerrando processos antigos...
REM Matar processos Python, Node e Uvicorn genericamente
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM uvicorn.exe >nul 2>&1
REM Matar processo especifico na porta 8000 (backend)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo [OK] Ambiente limpo
echo.

echo [VERIFICACAO] Checando pre-requisitos...
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo Instale Python 3.11+ de: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [OK] Python instalado

REM Verificar Node
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Node.js nao encontrado!
    echo Instale Node.js 18+ de: https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js instalado

REM Verificar .env
if not exist "backend\.env" (
    echo [AVISO] Arquivo .env nao encontrado. Copiando do exemplo...
    copy backend\.env.example backend\.env
    echo [ACAO NECESSARIA] Configure GEMINI_API_KEY em backend\.env
    notepad backend\.env
    pause
)
echo [OK] Arquivo .env configurado

REM Verificar Parquet
if not exist "backend\data\parquet\admmat.parquet" (
    echo [ERRO] Arquivo Parquet nao encontrado!
    echo Localizacao esperada: backend\data\parquet\admmat.parquet
    pause
    exit /b 1
)
echo [OK] Arquivo Parquet encontrado

REM Verificar Supabase Auth
findstr /C:"USE_SUPABASE_AUTH=true" backend\.env >nul
if %errorlevel% equ 0 (
    echo [OK] Supabase Auth ativado
) else (
    echo [AVISO] Supabase Auth pode estar desativado
)

echo.
echo ============================================================
echo   INICIANDO SERVICOS LOCAIS
echo ============================================================
echo.

echo [1/2] Iniciando BACKEND (FastAPI - Porta 8000)...
echo       Aguarde... O backend pode levar 15-30 segundos para inicializar
echo.
start "Agent BI - Backend" cmd /k "cd /d C:\Agente_BI\BI_Solution\backend && python main.py"

REM Aguardar backend estar pronto (health check)
echo [HEALTH CHECK] Aguardando backend ficar disponivel...
echo.

set BACKEND_READY=0
set RETRY_COUNT=0
set MAX_RETRIES=60

:WAIT_BACKEND
set /a RETRY_COUNT+=1

REM Tentar acessar o endpoint de health
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    set BACKEND_READY=1
    goto BACKEND_OK
)

REM Tentar endpoint raiz como fallback
curl -s http://localhost:8000/ >nul 2>&1
if %errorlevel% equ 0 (
    set BACKEND_READY=1
    goto BACKEND_OK
)

if %RETRY_COUNT% geq %MAX_RETRIES% (
    echo.
    echo [ERRO] Backend nao respondeu apos 60 segundos!
    echo Verifique a janela do Backend para erros.
    pause
    exit /b 1
)

REM Mostrar progresso
if %RETRY_COUNT% equ 10 echo [AGUARDANDO] 10 segundos...
if %RETRY_COUNT% equ 20 echo [AGUARDANDO] 20 segundos...
if %RETRY_COUNT% equ 30 echo [AGUARDANDO] 30 segundos... (ChatServiceV3 inicializando)

timeout /t 1 /nobreak >nul
goto WAIT_BACKEND

:BACKEND_OK
    echo [OK] Backend esta PRONTO! (tempo: %RETRY_COUNT% segundos)
    echo.
    echo [2/2] Iniciando FRONTEND (Vite - Porta 3000)...
    echo Publicando frontend...
    start "Agent BI - Frontend" cmd /k "cd /d C:\Agente_BI\BI_Solution\frontend-solid && npm run dev"

echo.
echo ============================================================
echo   SERVICOS INICIADOS COM SUCESSO!
echo ============================================================
echo.
echo Acesse:
echo   - Frontend: http://localhost:3000
echo   - Backend:  http://localhost:8000/docs
echo.
echo Autenticacao:
echo   - Supabase Auth: ATIVO
echo   - Usuarios cadastrados no Supabase com perfis e segmentos
echo.
echo Arquitetura:
echo   - ChatServiceV3 (Metrics-First) - ATIVO
echo   - Truth Contract - ATIVO
echo   - Heuristica-First (80/20) - ATIVO
echo.
echo Memoria estimada: ~1.5GB (vs ~6GB com Docker)
echo.
echo Para parar:
echo   - Feche as janelas do Backend e Frontend
echo   - Ou pressione Ctrl+C em cada janela
echo.
pause
