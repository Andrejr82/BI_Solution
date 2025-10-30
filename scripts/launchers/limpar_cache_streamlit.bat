@echo off
chcp 65001 > nul
cls

echo ╔═══════════════════════════════════════════════════════════╗
echo ║   🧹 LIMPAR CACHE DO STREAMLIT                           ║
echo ║   Lojas Caçula - Business Intelligence                   ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

echo [1/3] Parando processos Streamlit...
taskkill /F /IM streamlit.exe 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *streamlit*" 2>nul
timeout /t 2 /nobreak > nul
echo ✓ Processos parados

echo.
echo [2/3] Limpando cache do Streamlit...

REM Limpar cache do Streamlit (AppData\Local\Temp\.streamlit)
if exist "%LOCALAPPDATA%\Temp\.streamlit" (
    rd /s /q "%LOCALAPPDATA%\Temp\.streamlit"
    echo ✓ Cache Streamlit limpo
)

REM Limpar cache Python __pycache__
echo Limpando __pycache__...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
echo ✓ __pycache__ limpo

REM Limpar arquivos .pyc
echo Limpando arquivos .pyc...
del /s /q *.pyc 2>nul
echo ✓ Arquivos .pyc limpos

echo.
echo [3/3] Iniciando Streamlit com cache limpo...
echo.
echo 🌐 Acesse: http://localhost:8501
echo.
echo 📋 Interface: Corporativa Caçula (verde)
echo    Título: Agente de Business Intelligence
echo    Subtítulo: Sistema Corporativo Caçula
echo.
echo 🔐 Credenciais (Cloud Fallback - FUNCIONANDO):
echo    Usuário: admin
echo    Senha: admin
echo.
echo 🔐 Credenciais alternativas (SQL Server - Modo Local):
echo    Usuário: admin
echo    Senha: admin123
echo.
echo 💡 Pressione Ctrl+C para parar
echo.

REM Iniciar Streamlit
streamlit run streamlit_app.py --server.headless true --server.port 8501

pause
