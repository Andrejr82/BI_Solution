@echo off
echo Limpando caches do Python (__pycache__)...
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        echo Removendo %%d
        rmdir /s /q "%%d"
    )
)
echo.
echo Limpando cache do Streamlit...
streamlit cache clear
echo.
echo Limpeza concluida!
pause
