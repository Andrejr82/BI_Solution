@echo off
cd /d "%~dp0"
echo Iniciando Streamlit...
python -m streamlit run streamlit_app.py
pause
