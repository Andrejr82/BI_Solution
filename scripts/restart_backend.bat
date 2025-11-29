@echo off
echo ========================================
echo Reiniciando Backend FastAPI
echo ========================================

cd backend

echo.
echo Matando processos Python na porta 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Matando PID %%a
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul

echo.
echo Iniciando backend...
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

pause
