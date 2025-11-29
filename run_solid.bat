@echo off
echo ==========================================
echo   AGENT BI - SOLIDJS PRODUCTION (MIGRATED)
echo ==========================================
echo.
echo [1/4] Verificando Backend (Porta 8000)...
netstat -ano | findstr :8000 > nul
if %errorlevel% neq 0 (
    echo [AVISO] Backend nao detectado na porta 8000.
    echo O frontend pode iniciar, mas Login/Chat/Dados nao funcionarao.
    echo Recomendado: Iniciar 'run.bat --backend-only' em outro terminal.
    echo.
    timeout /t 3
) else (
    echo [OK] Backend online.
)

echo.
echo [2/4] Limpando Cache do Frontend...
cd frontend-solid
Remove-Item -Path node_modules/.vite -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path .vite -Recurse -Force -ErrorAction SilentlyContinue
echo [OK] Cache do Vite limpo.
echo.

echo [3/4] Iniciando Frontend SolidJS Oficial...
echo Acessar em: http://localhost:3000 (abrirá automaticamente)
echo.
call npm run dev
pause
