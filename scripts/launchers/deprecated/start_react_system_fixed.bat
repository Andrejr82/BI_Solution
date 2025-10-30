@echo off
chcp 65001 > nul
cls

echo ╔═══════════════════════════════════════════════════════════╗
echo ║   🚀 AGENT BI - SISTEMA REACT + FASTAPI                  ║
echo ║   Lojas Caçula - Business Intelligence                   ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Verificar se Python está disponível
echo [1/5] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Python não encontrado!
    echo Por favor, instale Python 3.9+ e tente novamente.
    pause
    exit /b 1
)
echo ✓ Python OK

REM Verificar se Node.js está disponível
echo [2/5] Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Node.js não encontrado!
    echo Por favor, instale Node.js 18+ e tente novamente.
    pause
    exit /b 1
)
echo ✓ Node.js OK

REM Verificar se as dependências do frontend estão instaladas
echo [3/5] Verificando dependências do frontend...
if not exist "frontend\node_modules" (
    echo ⚙️  Instalando dependências do frontend...
    cd frontend
    call npm install
    cd ..
    echo ✓ Dependências instaladas
) else (
    echo ✓ Dependências já instaladas
)

REM Matar processos nas portas 5000 e 8080
echo [4/5] Liberando portas...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo ✓ Portas liberadas

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║   🎯 INICIANDO SERVIDORES                                ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

echo [5/5] Iniciando Backend FastAPI (porta 5000)...
echo.
start "Agent BI - Backend FastAPI" cmd /k "echo 🔥 BACKEND FASTAPI - PORTA 5000 && echo. && python -m uvicorn api_server:app --host 0.0.0.0 --port 5000 --reload"

timeout /t 3 /nobreak > nul

echo [5/5] Iniciando Frontend React (porta 8080)...
echo.
cd frontend
start "Agent BI - Frontend React" cmd /k "echo 🎨 FRONTEND REACT - PORTA 8080 && echo. && npm run dev"
cd ..

timeout /t 3 /nobreak > nul

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║   ✅ SISTEMA INICIADO COM SUCESSO!                       ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.
echo 📡 Backend API:  http://localhost:5000
echo 🌐 Frontend:     http://localhost:8080
echo.
echo 📋 Credenciais de teste:
echo    Usuário: admin
echo    Senha: admin123
echo.
echo 💡 Pressione Ctrl+C nas janelas para parar os servidores
echo.
pause
