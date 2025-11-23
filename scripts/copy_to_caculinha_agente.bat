@echo off
rem ------------------------------------------------------------
rem Copy the entire Agent_Solution_BI project to C:\Users\André\Documents\Caculinha_Agente
rem ------------------------------------------------------------
set "SOURCE=%~dp0"
set "DEST=%USERPROFILE%\Documents\Caculinha_Agente"

echo Copiando projeto de "%SOURCE%" para "%DEST%" ...

rem Create destination folder if it does not exist
if not exist "%DEST%" (
    mkdir "%DEST%"
)

rem Use robocopy to mirror the directory, excluding this script itself
robocopy "%SOURCE%" "%DEST%" /MIR /XF copy_to_caculinha_agente.bat

if %errorlevel% leq 3 (
    echo Copia concluida com sucesso.
) else (
    echo Houve erros durante a copia. Codigo de erro: %errorlevel%
)

pause
