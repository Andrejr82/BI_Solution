@echo off
echo ========================================
echo   AGENT BI - SISTEMA DE PRODUCAO
echo   Inicializacao Otimizada
echo ========================================
echo.

REM Parar processos antigos
echo [1/5] Limpando processos antigos...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2/5] Iniciando Backend (porta 8000)...
cd /d "%~dp0backend"
start "Agent BI - Backend" cmd /k "python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 5 /nobreak >nul

echo [3/5] Verificando Backend...
curl -s http://127.0.0.1:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend online!
) else (
    echo [AVISO] Backend ainda inicializando...
)

echo.
echo [4/5] Iniciando Frontend de Producao (porta 3000)...
cd /d "%~dp0frontend-solid"
start "Agent BI - Frontend" cmd /k "npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo [5/5] Abrindo navegador...
timeout /t 5 /nobreak >nul
start http://localhost:3000

echo.
echo ========================================
echo   SISTEMA INICIADO COM SUCESSO!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Credenciais de teste:
echo   Admin:     admin / Admin@2024
echo   Comprador: comprador / comprador123
echo.
echo Pressione qualquer tecla para fechar...
pause >nul
