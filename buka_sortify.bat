@echo off
title SORTIFY STUDENT ANALYTICS

cd /d "%~dp0"

echo ==================================
echo      SORTIFY STUDENT ANALYTICS
echo ==================================
echo.
echo Menjalankan server Sortify...

start "SORTIFY SERVER" /D "%~dp0" cmd /k "python main.py"

echo.
echo Menunggu server aktif...
timeout /t 7 /nobreak >nul

echo Membuka Google Chrome...
start "" "http://127.0.0.1:5000"

exit