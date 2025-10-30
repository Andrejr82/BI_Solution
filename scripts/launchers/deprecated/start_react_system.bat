@echo off
echo ========================================
echo    Agent Solution BI - Sistema React
echo ========================================
echo.

REM Limpar cache Python
echo [1/4] Limpando cache Python...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
del /s /q *.pyc 2>nul
echo       Cache limpo!
echo.

REM Iniciar Backend FastAPI
echo [2/4] Iniciando Backend (porta 5000)...
start "Backend API" cmd /k "python api_server.py"
timeout /t 3 >nul
echo       Backend iniciando...
echo.

REM Iniciar Frontend React
echo [3/4] Iniciando Frontend (porta 8080)...
cd frontend
start "Frontend React" cmd /k "npm run dev"
cd ..
timeout /t 2 >nul
echo       Frontend iniciando...
echo.

echo [4/4] Sistema em execucao!
echo.
echo ========================================
echo   Acesse: http://localhost:8080
echo ========================================
echo.
echo Credenciais de teste:
echo   - admin / admin
echo   - user / user123
echo   - cacula / cacula123
echo.
echo Pressione qualquer tecla para fechar esta janela...
pause >nul
