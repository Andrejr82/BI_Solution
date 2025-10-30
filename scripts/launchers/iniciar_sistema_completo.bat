@echo off
chcp 65001 >nul
title Agent Solution BI - Sistema Completo
cls

echo ====================================================================
echo 🚀 INICIANDO SISTEMA COMPLETO - Agent Solution BI
echo ====================================================================
echo.
echo Este script vai iniciar:
echo   1. API FastAPI (porta 5000)
echo   2. React Frontend (porta 8080)
echo.
echo Aguarde aproximadamente 40 segundos...
echo.

echo ====================================================================
echo [1/2] Iniciando API FastAPI...
echo ====================================================================
start "API FastAPI" cmd /k "python api_server.py"

echo.
echo ⏳ Aguardando API carregar (30 segundos)...
timeout /t 30 /nobreak >nul
echo ✓ API deve estar pronta!
echo.

echo ====================================================================
echo [2/2] Iniciando React Frontend...
echo ====================================================================
cd frontend

if not exist "node_modules" (
    echo.
    echo 📦 Instalando dependências do React (primeira vez, ~2 minutos)...
    echo.
    call npm install
)

echo.
echo 🎨 Iniciando React Dev Server...
start "React Frontend" cmd /k "npm run dev"

echo.
echo ====================================================================
echo ✅ SISTEMA INICIADO COM SUCESSO!
echo ====================================================================
echo.
echo Interfaces disponíveis:
echo   • React Frontend: http://localhost:8080
echo   • API FastAPI:    http://localhost:5000/docs
echo.
echo O React vai abrir automaticamente no navegador em 5 segundos...
echo.
echo Para ENCERRAR tudo:
echo   - Feche as janelas de terminal que abriram
echo   - Ou pressione Ctrl+C em cada uma
echo.
echo ====================================================================
echo.
pause
