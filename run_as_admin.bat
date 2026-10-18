@echo off
:: Batch script to run Where Winds Meet Auto Redeemer as Administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Menjalankan sebagai Administrator...
    python "%~dp0app.py"
) else (
    echo Meminta Hak Administrator...
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d \"%~dp0\" && python app.py' -Verb RunAs"
)
