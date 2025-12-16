@echo off
REM ============================================================================
REM Perfect STT v2.2 - Standalone EXE Builder
REM ============================================================================
REM This script creates a SINGLE .exe file with everything bundled:
REM - Python interpreter
REM - All dependencies
REM - FFmpeg binaries
REM - No console window
REM
REM Output: dist\PerfectSTT.exe
REM ============================================================================

echo.
echo ============================================================
echo   Perfect STT v2.2 - Standalone EXE Builder
echo ============================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Check PyInstaller
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Check for FFmpeg binaries
if not exist "ffmpeg\ffmpeg.exe" (
    echo.
    echo ERROR: FFmpeg binaries not found!
    echo.
    echo Please download FFmpeg and place the binaries:
    echo   1. Go to: https://www.gyan.dev/ffmpeg/builds/
    echo   2. Download: ffmpeg-release-essentials.zip
    echo   3. Extract ffmpeg.exe and ffprobe.exe
    echo   4. Place them in the 'ffmpeg' folder
    echo.
    pause
    exit /b 1
)

if not exist "ffmpeg\ffprobe.exe" (
    echo ERROR: ffprobe.exe not found in ffmpeg folder!
    pause
    exit /b 1
)

echo.
echo [1/3] Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo.
echo [2/3] Building standalone EXE...
echo This will take 5-15 minutes. Please wait...
echo.

pyinstaller build_standalone.spec --noconfirm

if errorlevel 1 (
    echo.
    echo ============================================================
    echo   BUILD FAILED!
    echo ============================================================
    echo.
    echo Check the error messages above.
    echo Common fixes:
    echo   - Make sure all dependencies are installed
    echo   - Try: pip install faster-whisper gradio torch
    echo   - Make sure ffmpeg folder contains ffmpeg.exe and ffprobe.exe
    echo.
    pause
    exit /b 1
)

echo.
echo [3/3] Verifying output...
if not exist "dist\PerfectSTT.exe" (
    echo ERROR: PerfectSTT.exe was not created!
    pause
    exit /b 1
)

for %%A in ("dist\PerfectSTT.exe") do set SIZE=%%~zA
set /a SIZE_MB=%SIZE% / 1048576

echo.
echo ============================================================
echo   BUILD SUCCESSFUL!
echo ============================================================
echo.
echo   Output: dist\PerfectSTT.exe
echo   Size:   ~%SIZE_MB% MB
echo.
echo   This single file contains EVERYTHING:
echo   - Python interpreter
echo   - All dependencies
echo   - FFmpeg (video support)
echo   - No installation required!
echo.
echo   DISTRIBUTION:
echo   1. Copy dist\PerfectSTT.exe to any folder
echo   2. Share with friends (zip with password to avoid antivirus blocks)
echo   3. They just double-click to run!
echo.
echo   NOTE: First run will be slow (extracting files).
echo         Subsequent runs will be faster.
echo.
echo   ANTIVIRUS WARNING:
echo   Windows Defender may show "Windows protected your PC"
echo   Click "More info" then "Run anyway" - the app is safe!
echo.
echo ============================================================
echo.
pause
