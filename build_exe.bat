@echo off
title Build Where Winds Meet Auto Redeemer EXE
echo ===================================================
echo   Building Where Winds Meet Auto Redeemer to EXE
echo ===================================================
echo.

echo [1/3] Memeriksa & Menginstall PyInstaller...
python -m pip install --upgrade pyinstaller

echo.
echo [2/3] Mengompilasi aplikasi menjadi Standalone EXE...
python -m PyInstaller --noconsole --onefile --uac-admin --clean --name "WhereWindsMeet_AutoRedeemer" --collect-all customtkinter app.py

echo.
echo [3/3] Menyalin file EXE ke root folder...
copy /y "dist\WhereWindsMeet_AutoRedeemer.exe" "WhereWindsMeet_AutoRedeemer.exe"

echo.
echo Selesai! File EXE terbaru tersedia di:
echo 1. WhereWindsMeet_AutoRedeemer.exe (Root)
echo 2. dist\WhereWindsMeet_AutoRedeemer.exe
echo.
pause
