@echo off
REM ======================================================
REM Iniciar Agent_Solution_BI em REDE LOCAL
REM Para acesso de outros computadores
REM ======================================================

echo ========================================
echo AGENT SOLUTION BI - MODO REDE LOCAL
echo ========================================
echo.
echo Este servidor permite acesso de outros computadores
echo na mesma rede.
echo.

REM Descobrir IP local
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do set IP=%%a

echo Seu IP local: %IP%
echo.
echo ACESSE NO SEU COMPUTADOR (servidor):
echo   http://localhost:8501
echo.
echo COMPARTILHE COM OUTROS USUARIOS:
echo   http://%IP%:8501
echo.
echo IMPORTANTE: Aguarde "Network URL" aparecer abaixo
echo Pressione Ctrl+C para parar
echo ========================================
echo.

REM Rodar Streamlit em modo rede
python -m streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8501

pause
