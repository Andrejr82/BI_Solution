@echo off
REM ========================================
REM   AGENT BI - SISTEMA SIMPLIFICADO
REM   Usa concurrently para um único terminal
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
    echo [INFO] Por favor, instale Node.js de https://nodejs.org/
    pause
    exit /b 1
)

REM Verificar se Python está instalado
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo [INFO] Por favor, instale Python de https://python.org/
    pause
    exit /b 1
)

REM Limpar processos antigos
echo [1/5] Limpando processos antigos...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul
echo [OK] Processos limpos.
echo.

REM Limpar cache Python
echo [2/5] Limpando cache Python...
cd /d "%~dp0backend"
for /d /r %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
del /s /q *.pyc 2>nul >nul
cd /d "%~dp0"
echo [OK] Cache limpo.
echo.

REM Instalar/Verificar dependências
echo [3/5] Verificando dependencias...

REM Verificar concurrently
if not exist node_modules\concurrently (
    echo [INFO] Instalando concurrently...
    call npm install --silent
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao instalar concurrently
        pause
        exit /b 1
    )
)

REM Verificar frontend dependencies
if not exist frontend-solid\node_modules (
    echo [INFO] Instalando dependencias do Frontend...
    cd frontend-solid
    call npm install
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao instalar dependencias do frontend
        cd ..
        pause
        exit /b 1
    )
    cd ..
) else (
    echo [OK] Dependencias do frontend ja instaladas
)

echo [OK] Dependencias verificadas.
echo.

REM Verificar backend setup
echo [4/6] Verificando backend Python...
cd /d "%~dp0backend"
if not exist ".venv\Scripts\python.exe" (
    echo [INFO] Backend virtual environment nao encontrado
    echo [INFO] Sera criado automaticamente na primeira execucao
) else (
    echo [OK] Backend virtual environment encontrado
)
cd /d "%~dp0"
echo.

REM Limpar portas
echo [5/6] Limpando portas 8000 e 3000...
node scripts/clean-port.js
echo [OK] Portas limpas.
echo.

REM Iniciar sistema com concurrently
echo [6/6] Iniciando sistema...
echo.
echo ========================================
echo   SISTEMA RODANDO
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Credenciais:
echo   Username: admin
echo   Senha:    Admin@2024
echo.
echo ========================================
echo.
echo [INFO] Backend e Frontend rodando no mesmo terminal
echo [INFO] Logs coloridos por servico:
echo        - BACKEND  (azul)
echo        - FRONTEND (verde)
echo.
echo [DICA] Pressione Ctrl+C para encerrar todos os processos
echo.

REM Iniciar com concurrently
call npm run dev
