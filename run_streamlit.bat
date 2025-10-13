@echo off
echo ========================================
echo   Agent_BI - Sistema 100%% IA
echo ========================================
echo.
echo Inicializando Streamlit...
echo.

REM Ativar ambiente virtual se existir
if exist .venv\Scripts\activate.bat (
    echo [1/3] Ativando ambiente virtual...
    call .venv\Scripts\activate.bat
) else (
    echo [1/3] Usando Python global...
)

echo [2/3] Verificando dependencias...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo.
    echo ERRO: Streamlit nao encontrado!
    echo Execute: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo [3/3] Iniciando servidor Streamlit...
echo.
echo ========================================
echo   URLs de Acesso:
echo ========================================
echo   Local:    http://localhost:8501
echo   Network:  http://127.0.0.1:8501
echo ========================================
echo.
echo O navegador abrira automaticamente...
echo Pressione Ctrl+C para parar o servidor
echo.

REM Executar Streamlit
streamlit run streamlit_app.py

pause
