@echo off
echo ========================================
echo   AGENT_BI - Inicializador
echo ========================================
echo.

REM Ativar ambiente virtual
call .venv\Scripts\activate.bat

REM Instalar dependencias
echo Instalando dependencias (pode demorar)...
pip install -r requirements.txt
echo.

REM Iniciar backend em background
echo Iniciando Backend...
start /B python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
timeout /t 5 /nobreak >nul

REM Iniciar frontend
echo.
echo ========================================
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:8501
echo ========================================
echo.
echo Iniciando Frontend...
echo.

python -m streamlit run streamlit_app.py

pause
