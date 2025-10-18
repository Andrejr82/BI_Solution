@echo off
echo ============================================================
echo VALIDACAO DE INTEGRIDADE DE DADOS E PERFORMANCE
echo Agent_Solution_BI - BI Agent (Caçulinha BI)
echo ============================================================
echo.

cd /d "%~dp0.."

echo Iniciando validacao...
echo.

python scripts/validacao_integridade_dados.py

echo.
echo ============================================================
echo VALIDACAO CONCLUIDA
echo ============================================================
echo.
echo Verifique o relatorio em ./reports/
echo.

pause
