@echo off
chcp 65001 > nul
cls

echo ╔═══════════════════════════════════════════════════════════╗
echo ║   🎯 AGENT BI - STREAMLIT (VERSÃO ORIGINAL)             ║
echo ║   Lojas Caçula - Business Intelligence                   ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Verificar se Python está disponível
echo [1/3] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERRO: Python não encontrado!
    echo Por favor, instale Python 3.9+ e tente novamente.
    pause
    exit /b 1
)
echo ✓ Python OK

REM Verificar se Streamlit está instalado
echo [2/3] Verificando Streamlit...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo ⚙️  Streamlit não encontrado. Instalando...
    pip install streamlit
)
echo ✓ Streamlit OK

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║   🚀 INICIANDO STREAMLIT                                 ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

echo [3/3] Iniciando aplicação Streamlit...
echo.
echo 🌐 Acesse: http://localhost:8501
echo.
echo 📋 Credenciais de teste:
echo    Usuário: admin
echo    Senha: admin123
echo.
echo 💡 Pressione Ctrl+C para parar
echo.

REM Iniciar Streamlit
streamlit run streamlit_app.py

pause
