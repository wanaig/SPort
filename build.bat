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

set "ISCC="

if defined INNO_SETUP if exist "%INNO_SETUP%" set "ISCC=%INNO_SETUP%"

if not defined ISCC (
    for /f "delims=" %%i in ('where ISCC.exe 2^>nul') do (
        if not defined ISCC set "ISCC=%%i"
    )
)

if not defined ISCC (
    echo [SPort] ISCC.exe not found.
    echo [SPort] Download Inno Setup 6: https://jrsoftware.org/isdl.php
    echo [SPort] Then either:
    echo [SPort]   1. Add ISCC.exe to PATH, or
    echo [SPort]   2. Set INNO_SETUP env var, e.g.:
    echo [SPort]        set INNO_SETUP=D:\develop\Inno Setup 6\ISCC.exe
    echo.
    echo [SPort] PyInstaller build OK: dist\SPort.exe
    echo [SPort] Run this script again after installing Inno Setup 6.
    exit /b 0
)

echo [SPort] Using ISCC: %ISCC%
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
if not "%CI%"=="true" pause
