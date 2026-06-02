@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo [SPort] Step 1/2: PyInstaller (build single-file .exe)
echo.
pyinstaller build.spec
if errorlevel 1 (
    echo.
    echo [SPort] PyInstaller build FAILED
    exit /b 1
)

echo.
echo [SPort] Step 2/2: Inno Setup (build installer)
echo.

set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
    echo [SPort] Inno Setup 6 not found.
    echo [SPort]   Expected: %%ProgramFiles(x86)%%\Inno Setup 6\ISCC.exe
    echo [SPort]   Download: https://jrsoftware.org/isdl.php
    echo.
    echo [SPort] PyInstaller build OK.
    echo [SPort]   Executable only: dist\SPort.exe
    echo [SPort] Run this script again after installing Inno Setup 6.
    exit /b 0
)

"%ISCC%" installer.iss
if errorlevel 1 (
    echo.
    echo [SPort] Installer build FAILED
    exit /b 1
)

echo.
echo [SPort] Build complete:
echo [SPort]   Executable: dist\SPort.exe
echo [SPort]   Installer:  dist\SPort-Setup-0.2.0.exe
echo.
pause
