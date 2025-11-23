@echo off
REM ======================================================
REM Iniciar Agent_Solution_BI
REM ======================================================

echo ========================================
echo AGENT SOLUTION BI - Iniciando...
echo ========================================
echo.
echo O navegador vai abrir automaticamente em:
echo   http://localhost:8501
echo.
echo Aguarde...
echo ========================================
echo.

REM Abrir navegador após 5 segundos
start /B cmd /c "timeout /t 5 /nobreak >nul && start http://localhost:8501"

REM Rodar Streamlit
python -m streamlit run streamlit_app.py

pause
