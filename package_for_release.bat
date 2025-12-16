@echo off
REM ============================================================================
REM Perfect STT - Release Packaging Script
REM ============================================================================
REM This script builds the standalone executable and prepares it for distribution.
REM 
REM Prerequisites:
REM   1. Python 3.10+ with pip
REM   2. All dependencies installed (pip install -r requirements.txt)
REM   3. PyInstaller installed (pip install pyinstaller)
REM
REM Usage:
REM   Simply double-click this file or run from command prompt.
REM ============================================================================

echo.
echo ============================================================
echo   Perfect STT - Release Packaging Script
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

REM Check if PyInstaller is available
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller!
        pause
        exit /b 1
    )
)

echo.
echo [Step 1/4] Cleaning previous builds...
echo.
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo.
echo [Step 2/4] Building executable with PyInstaller...
echo This may take several minutes...
echo.
pyinstaller build.spec --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller build failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo [Step 3/4] Creating release folder...
echo.

REM Create release folder
set RELEASE_FOLDER=PerfectSTT_v2.1_Release
if exist "%RELEASE_FOLDER%" rmdir /s /q "%RELEASE_FOLDER%"
mkdir "%RELEASE_FOLDER%"

REM Copy the built application
xcopy /s /e /i "dist\PerfectSTT" "%RELEASE_FOLDER%"

REM Create empty folders for models and outputs
mkdir "%RELEASE_FOLDER%\models"
mkdir "%RELEASE_FOLDER%\Outputs"

REM Create README for the release
echo Creating README...
(
echo ============================================================
echo   Perfect STT v2.1 - Local Speech-to-Text Tool
echo ============================================================
echo.
echo QUICK START:
echo   1. Double-click "PerfectSTT.exe" to launch
echo   2. Upload an audio/video file
echo   3. Click "Transcribe"
echo   4. Find your transcripts in the "Outputs" folder
echo.
echo FIRST RUN:
echo   - The app will download the AI model on first use ^(~500MB^)
echo   - This only happens once - models are saved in the "models" folder
echo.
echo VIDEO SUPPORT:
echo   To enable video file support ^(MP4, MKV, etc.^):
echo   1. Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/
echo   2. Get the "ffmpeg-release-essentials.zip" build
echo   3. Extract and copy ONLY these 2 files to this folder:
echo      - ffmpeg.exe
echo      - ffprobe.exe
echo   4. Restart the app
echo.
echo SUPPORTED FORMATS:
echo   Audio: MP3, WAV, M4A, OGG, FLAC, AAC, WMA
echo   Video: MP4, MKV, MOV, AVI, WebM, WMV, FLV ^(requires FFmpeg^)
echo.
echo HARDWARE:
echo   - GPU ^(NVIDIA^): Automatically uses GPU for fast processing
echo   - CPU: Uses optimized INT8 mode for compatibility
echo.
echo TROUBLESHOOTING:
echo   - If the app doesn't start, try running from Command Prompt
echo     to see error messages
echo   - Make sure you have enough disk space for models ^(~3GB for large^)
echo   - For video files, ensure FFmpeg is in this folder
echo.
echo ============================================================
) > "%RELEASE_FOLDER%\README.txt"

echo.
echo [Step 4/4] Done!
echo.
echo ============================================================
echo   BUILD COMPLETE!
echo ============================================================
echo.
echo Your release folder is ready: %RELEASE_FOLDER%
echo.
echo BEFORE DISTRIBUTING:
echo.
echo   1. ^(Optional^) Add FFmpeg for video support:
echo      - Download from: https://www.gyan.dev/ffmpeg/builds/
echo      - Get "ffmpeg-release-essentials.zip"
echo      - Extract ffmpeg.exe and ffprobe.exe
echo      - Place them in the %RELEASE_FOLDER% folder
echo.
echo   2. Test the application:
echo      - Run %RELEASE_FOLDER%\PerfectSTT.exe
echo      - Try transcribing a test audio file
echo.
echo   3. Create distributable:
echo      - Right-click the %RELEASE_FOLDER% folder
echo      - Select "Compress to ZIP file"
echo      - Share the ZIP with friends!
echo.
echo ============================================================
echo.
pause
