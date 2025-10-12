@echo off
REM Script de Atualização Agendada do Parquet
REM Executa diariamente às 03:00h

cd /d "C:\Users\André\Documents\Agent_Solution_BI"

REM Ativar ambiente virtual se existir
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

REM Executar script Python
python scripts\update_parquet_from_sql.py

REM Log do agendamento
echo [%date% %time%] Atualização do Parquet executada >> logs\scheduled_updates.log
