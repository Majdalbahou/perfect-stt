@echo off
REM ============================================================================
REM Perfect STT v2.2 - Complete Installer Builder
REM ============================================================================
REM This script creates a professional Windows installer (.exe) that:
REM - Installs to Program Files
REM - Creates Desktop shortcut
REM - Creates Start Menu entry
REM - Includes uninstaller
REM
REM Prerequisites:
REM 1. Python 3.10+ with pip
REM 2. Inno Setup 6 (https://jrsoftware.org/isdl.php)
REM
REM Output: Output\PerfectSTT_Setup_v2.2.0.exe
REM ============================================================================

setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   Perfect STT v2.2 - Professional Installer Builder
echo ============================================================
echo.

REM ============================================================================
REM STEP 0: Check prerequisites
REM ============================================================================

echo [Step 0/4] Checking prerequisites...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.10+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
echo   [OK] Python found

REM Check for FFmpeg binaries
if not exist "ffmpeg\ffmpeg.exe" (
    echo ERROR: FFmpeg binaries not found!
    echo Please ensure ffmpeg\ffmpeg.exe and ffmpeg\ffprobe.exe exist.
    pause
    exit /b 1
)
echo   [OK] FFmpeg binaries found

REM Check for Inno Setup
set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
)
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
)

if "!ISCC!"=="" (
    echo.
    echo WARNING: Inno Setup 6 not found!
    echo.
    echo To create the installer, please:
    echo   1. Download Inno Setup from: https://jrsoftware.org/isdl.php
    echo   2. Install it (default location)
    echo   3. Run this script again
    echo.
    echo Alternatively, after PyInstaller build completes:
    echo   1. Open Inno Setup Compiler
    echo   2. Open installer.iss
    echo   3. Click Build ^> Compile
    echo.
    set BUILD_INSTALLER=0
) else (
    echo   [OK] Inno Setup found: !ISCC!
    set BUILD_INSTALLER=1
)

echo.

REM ============================================================================
REM STEP 1: Install Python dependencies
REM ============================================================================

echo [Step 1/4] Installing Python dependencies...
echo.

REM Check if PyInstaller is installed
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Install other dependencies
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

REM Check if torch is installed, if not install CPU version
python -c "import torch" >nul 2>&1
if errorlevel 1 (
    echo Installing PyTorch (CPU version)...
    pip install torch --index-url https://download.pytorch.org/whl/cpu
)

echo   [OK] Dependencies installed
echo.

REM ============================================================================
REM STEP 2: Build with PyInstaller
REM ============================================================================

echo [Step 2/4] Building application with PyInstaller...
echo This may take 5-15 minutes...
echo.

REM Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM Build using the folder spec (for Inno Setup)
pyinstaller build_for_installer.spec --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

REM Verify output
if not exist "dist\PerfectSTT\PerfectSTT.exe" (
    echo ERROR: PerfectSTT.exe was not created!
    pause
    exit /b 1
)

echo   [OK] PyInstaller build complete
echo.

REM ============================================================================
REM STEP 3: Create installer with Inno Setup
REM ============================================================================

if "!BUILD_INSTALLER!"=="1" (
    echo [Step 3/4] Creating installer with Inno Setup...
    echo.
    
    REM Create Output directory
    if not exist "Output" mkdir "Output"
    
    REM Run Inno Setup compiler
    "!ISCC!" installer.iss
    
    if errorlevel 1 (
        echo.
        echo ERROR: Inno Setup compilation failed!
        echo Try opening installer.iss in Inno Setup Compiler manually.
        pause
        exit /b 1
    )
    
    echo   [OK] Installer created
    echo.
) else (
    echo [Step 3/4] Skipping installer creation (Inno Setup not found)
    echo.
)

REM ============================================================================
REM STEP 4: Summary
REM ============================================================================

echo [Step 4/4] Build complete!
echo.
echo ============================================================
echo   BUILD SUCCESSFUL!
echo ============================================================
echo.

if "!BUILD_INSTALLER!"=="1" (
    echo   INSTALLER CREATED:
    echo   Output\PerfectSTT_Setup_v2.2.0.exe
    echo.
    echo   This installer will:
    echo   - Install to Program Files
    echo   - Create Desktop shortcut
    echo   - Create Start Menu entry
    echo   - Include uninstaller
    echo.
    echo   DISTRIBUTION:
    echo   Just send the Setup .exe file to your friends!
    echo   They double-click, click Next a few times, and it's installed.
    echo.
) else (
    echo   PYINSTALLER BUILD CREATED:
    echo   dist\PerfectSTT\PerfectSTT.exe
    echo.
    echo   To create the installer:
    echo   1. Install Inno Setup from https://jrsoftware.org/isdl.php
    echo   2. Run this script again, OR
    echo   3. Open installer.iss in Inno Setup and click Build ^> Compile
    echo.
)

echo   ANTIVIRUS NOTE:
echo   Windows Defender may flag the installer as unknown.
echo   Tell users to click "More info" then "Run anyway".
echo.
echo ============================================================
echo.
pause
