@echo off
REM ===========================================
REM   AGENT BI - SCRIPT DE INICIALIZAÇÃO
REM   Use este script para iniciar o sistema
REM ===========================================

echo.
echo ╔══════════════════════════════════════════╗
echo ║   AGENT BI - INICIANDO SISTEMA           ║
echo ╚══════════════════════════════════════════╝
echo.

REM Ir para o diretório do projeto
cd /d "%~dp0"

REM Verificar se Node.js está instalado
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] Node.js nao encontrado!
    echo        Instale de: https://nodejs.org/
    pause
    exit /b 1
)

REM Verificar se Python está instalado
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo        Instale de: https://python.org/
    pause
    exit /b 1
)

REM Verificar se venv existe
if not exist "backend\.venv\Scripts\python.exe" (
    echo [INFO] Ambiente virtual nao encontrado.
    echo [INFO] Criando ambiente virtual...
    cd backend
    python -m venv .venv
    echo [INFO] Instalando dependencias...
    .venv\Scripts\python.exe -m pip install --upgrade pip
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    cd ..
    echo [OK] Ambiente configurado!
    echo.
)

REM Matar processos antigos
echo [1/3] Limpando processos antigos...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul
echo       [OK] Processos limpos
echo.

REM Verificar dependências do frontend
if not exist "frontend-solid\node_modules" (
    echo [2/3] Instalando dependencias do Frontend...
    cd frontend-solid
    call npm install
    cd ..
    echo       [OK] Dependencias instaladas
    echo.
) else (
    echo [2/3] Dependencias do frontend OK
    echo.
)

REM Iniciar sistema
echo [3/3] Iniciando sistema...
echo.
echo ══════════════════════════════════════════
echo   SISTEMA INICIADO COM SUCESSO!
echo ══════════════════════════════════════════
echo.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo.
echo   Login: admin
echo   Senha: Admin@2024
echo.
echo ══════════════════════════════════════════
echo.
echo [INFO] Os processos serao iniciados agora
echo [INFO] Nao feche estas janelas!
echo.
pause

REM Iniciar Backend em uma nova janela
start "AGENT BI - BACKEND" cmd /k "cd /d %~dp0backend && .venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000"

REM Aguardar backend inicializar
echo Aguardando backend inicializar...
timeout /t 5 /nobreak >nul

REM Iniciar Frontend em uma nova janela
start "AGENT BI - FRONTEND" cmd /k "cd /d %~dp0frontend-solid && npm run dev"

REM Aguardar frontend inicializar
echo Aguardando frontend inicializar...
timeout /t 5 /nobreak >nul

REM Abrir navegador
echo.
echo Abrindo navegador...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo ══════════════════════════════════════════
echo   SISTEMA RODANDO!
echo ══════════════════════════════════════════
echo.
echo Acesse: http://localhost:3000
echo.
echo Para ENCERRAR o sistema:
echo   - Feche as janelas do Backend e Frontend
echo   - Ou execute: taskkill /F /IM python.exe ^& taskkill /F /IM node.exe
echo.
echo ══════════════════════════════════════════
pause
