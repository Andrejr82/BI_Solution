@echo off
REM ========================================
REM   Agent_BI - Inicializador Local
REM   Inicia Backend (FastAPI) e Frontend (Streamlit)
REM ========================================

echo.
echo ========================================
echo   AGENT_BI - AGENTE DE NEGOCIOS
echo   Inicializando aplicacao...
echo ========================================
echo.

REM Verificar se está na pasta correta
if not exist "streamlit_app.py" (
    echo [ERRO] Arquivo streamlit_app.py nao encontrado!
    echo Execute este script na raiz do projeto.
    pause
    exit /b 1
)

REM Verificar se ambiente virtual existe
if not exist ".venv\Scripts\activate.bat" (
    echo [ERRO] Ambiente virtual nao encontrado!
    echo Execute: python -m venv .venv
    pause
    exit /b 1
)

REM Ativar ambiente virtual
echo [1/4] Ativando ambiente virtual...
call .venv\Scripts\activate.bat

REM Verificar se backend existe
if not exist "main.py" (
    echo [AVISO] Backend FastAPI nao encontrado. Pulando...
    echo [3/4] Iniciando Frontend Streamlit...
    start "Agent_BI - Frontend" cmd /k "streamlit run streamlit_app.py"
    echo.
    echo ========================================
    echo   APLICACAO INICIADA COM SUCESSO!
    echo   Frontend: http://localhost:8501
    echo ========================================
    echo.
    pause
    exit /b 0
)

REM Iniciar Backend FastAPI em segundo plano
echo [2/4] Iniciando Backend FastAPI...
start "Agent_BI - Backend" cmd /k "uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

REM Aguardar backend estar pronto
echo [3/4] Aguardando Backend inicializar...
timeout /t 3 /nobreak >nul

:CHECK_BACKEND
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    echo    - Backend ainda inicializando...
    timeout /t 2 /nobreak >nul
    goto CHECK_BACKEND
)

echo    - Backend pronto! [OK]

REM Iniciar Frontend Streamlit
echo [4/4] Iniciando Frontend Streamlit...
timeout /t 1 /nobreak >nul
start "Agent_BI - Frontend" cmd /k "streamlit run streamlit_app.py"

echo.
echo ========================================
echo   APLICACAO INICIADA COM SUCESSO!
echo.
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:8501
echo.
echo   Para encerrar, feche todas as janelas
echo   ou pressione Ctrl+C em cada terminal.
echo ========================================
echo.

REM Manter janela principal aberta
echo Pressione qualquer tecla para encerrar tudo...
pause >nul

REM Encerrar processos ao fechar
taskkill /FI "WindowTitle eq Agent_BI - Backend*" /F >nul 2>&1
taskkill /FI "WindowTitle eq Agent_BI - Frontend*" /F >nul 2>&1

exit /b 0
