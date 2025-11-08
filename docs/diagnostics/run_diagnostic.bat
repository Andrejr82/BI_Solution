@echo off
cd /d "C:\Users\André\Documents\Agent_Solution_BI"
python diagnostic_detailed.py > diagnostic_output.txt 2>&1
type diagnostic_output.txt
