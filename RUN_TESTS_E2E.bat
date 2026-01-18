@echo off
REM Script para executar testes E2E completos
REM Agent Solution BI - Lojas Caçula

echo ========================================
echo Testes E2E - Agent Solution BI
echo ========================================
echo.

echo [1/4] Verificando instalacao do Playwright...
cd /d "%~dp0frontend-solid"
if not exist "node_modules\@playwright" (
    echo Instalando Playwright...
    call npm install -D @playwright/test
    call npx playwright install chromium
)

echo.
echo [2/4] Iniciando servidor de desenvolvimento...
echo.

REM Verificar se servidor já está rodando
powershell -Command "(Test-NetConnection -ComputerName localhost -Port 3000 -InformationLevel Quiet)" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Servidor já está rodando em http://localhost:3000
) else (
    echo ⚠️  Servidor não está rodando!
    echo.
    echo OPCOES:
    echo 1. Abrir novo terminal e executar:
    echo    cd frontend-solid
    echo    npm run dev
    echo.
    echo 2. OU pressionar qualquer tecla para tentar iniciar automaticamente
    echo    (Ctrl+C para cancelar)
    pause
    
    echo Iniciando servidor em background...
    start "Agent BI Dev Server" cmd /k "cd /d %~dp0frontend-solid && npm run dev"
    
    echo Aguardando servidor iniciar (30s)...
    timeout /t 30 /nobreak
)

echo.
echo [3/4] Executando testes E2E...
echo.
call npx playwright test --reporter=html,list

echo.
echo [4/4] Gerando relatorio...
echo.

if exist "test-results\html-report\index.html" (
    echo ✅ Relatorio gerado com sucesso!
    echo.
    echo Abrindo relatorio...
    start test-results\html-report\index.html
) else (
    echo ⚠️  Relatorio nao encontrado
)

echo.
echo ========================================
echo Testes concluidos!
echo ========================================
echo.
echo Screenshots: test-results\screenshots\
echo Relatorio HTML: test-results\html-report\index.html
echo.
pause
