@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo [SPort] Installing dependencies...
python -m pip install -q -r requirements.txt
if errorlevel 1 (
    echo [SPort] Install failed. Try: python -m pip install -r requirements.txt
    pause
    exit /b 1
)

echo [SPort] Starting monitor on http://127.0.0.1:7777
echo.
python app.py
pause
