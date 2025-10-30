@echo off
chcp 65001 >nul
cls

echo ====================================================================
echo 🚀 INICIANDO SISTEMA COMPLETO - SEM CACHE
echo ====================================================================
echo.

REM Matar processos antigos
echo [1/5] Encerrando processos antigos...
taskkill /F /IM "node.exe" /T >nul 2>&1
taskkill /F /IM "python.exe" /FI "WINDOWTITLE eq *api_server*" >nul 2>&1
timeout /t 2 /nobreak >nul
echo ✓ Processos antigos encerrados
echo.

REM Limpar cache do frontend
echo [2/5] Limpando cache do React...
cd frontend
if exist dist rmdir /s /q dist
if exist .vite rmdir /s /q .vite
if exist node_modules\.vite rmdir /s /q node_modules\.vite
cd ..
echo ✓ Cache limpo
echo.

REM Iniciar API
echo [3/5] Iniciando API FastAPI...
start "API FastAPI - Agent Solution BI" cmd /k "echo Iniciando API... && python api_server.py"
timeout /t 5 /nobreak >nul
echo ✓ API iniciando em background
echo.

REM Aguardar API carregar
echo [4/5] Aguardando API carregar (30 segundos)...
timeout /t 30 /nobreak
echo ✓ API deve estar pronta
echo.

REM Iniciar React
echo [5/5] Iniciando React Frontend...
cd frontend
start "React Frontend - Agent Solution BI" cmd /k "echo Iniciando React... && npm run dev"
cd ..
echo ✓ React iniciando
echo.

echo ====================================================================
echo ✅ SISTEMA INICIADO!
echo ====================================================================
echo.
echo Aguarde mais 10 segundos e depois:
echo.
echo 1. Abra o navegador em MODO ANONIMO:
echo    - Chrome/Edge: Ctrl + Shift + N
echo    - Firefox: Ctrl + Shift + P
echo.
echo 2. Acesse: http://localhost:8080
echo.
echo 3. Deve aparecer: "Olá! Sou o Caçulinha..."
echo.
echo Para ENCERRAR:
echo    - Feche as 2 janelas de terminal que abriram
echo.
echo ====================================================================
echo.

timeout /t 10 /nobreak
echo.
echo Abrindo navegador em 5 segundos...
timeout /t 5 /nobreak

REM Abrir navegador
start http://localhost:8080

echo.
echo ✅ Navegador aberto!
echo.
echo Se aparecer interface antiga do Lovable:
echo    1. Pressione Ctrl + Shift + R (hard refresh)
echo    2. Ou feche e abra em modo anônimo
echo.
pause
