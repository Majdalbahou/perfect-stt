@echo off
setlocal enabledelayedexpansion

:: ============================================
:: Perfect STT v2.0 - Universal Installer
:: ============================================
:: Light installer - models download on first run
:: Works on any PC (GPU or CPU)
:: ============================================

title Perfect STT v2.0 - Setup
color 0A

echo.
echo  ============================================
echo   Perfect STT v2.0 - Universal Installer
echo   Local, Private Speech-to-Text
echo  ============================================
echo.

:: Check for Python
echo [1/5] Checking for Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERROR: Python not found!
    echo.
    echo  Please install Python 3.10 or 3.11:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo  Found Python %PYTHON_VERSION%

:: Check for FFmpeg
echo.
echo [2/5] Checking for FFmpeg...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  WARNING: FFmpeg not found!
    echo.
    echo  FFmpeg is required for video files.
    echo  Download: https://www.gyan.dev/ffmpeg/builds/
    echo  Get "ffmpeg-release-essentials.zip"
    echo  Extract to C:\ffmpeg and add C:\ffmpeg\bin to PATH
    echo.
    echo  Audio files (MP3, WAV) will still work without FFmpeg.
    echo.
    timeout /t 5
) else (
    echo  FFmpeg found!
)

:: Create virtual environment if it doesn't exist
echo.
echo [3/5] Setting up virtual environment...
if not exist "venv" (
    echo  Creating new virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo  ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo  Virtual environment created!
) else (
    echo  Virtual environment already exists.
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Upgrade pip quietly
python -m pip install --upgrade pip --quiet 2>nul

:: Detect GPU and install appropriate PyTorch
echo.
echo [4/5] Detecting hardware and installing dependencies...
echo.

:: Check for NVIDIA GPU
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo  No NVIDIA GPU detected.
    echo  Installing CPU-optimized version...
    echo  (The app will use INT8 mode for good performance)
    echo.
    set TORCH_URL=https://download.pytorch.org/whl/cpu
    set DEVICE_MODE=CPU
) else (
    echo  NVIDIA GPU detected!
    echo  Installing CUDA-enabled version for maximum speed...
    echo.
    set TORCH_URL=https://download.pytorch.org/whl/cu121
    set DEVICE_MODE=GPU
)

:: Install PyTorch
echo  Installing PyTorch (%DEVICE_MODE% mode)...
pip install torch --index-url %TORCH_URL% --quiet 2>nul
if errorlevel 1 (
    echo  Trying alternative PyTorch version...
    pip install torch --index-url https://download.pytorch.org/whl/cu118 --quiet 2>nul
    if errorlevel 1 (
        pip install torch --index-url https://download.pytorch.org/whl/cpu --quiet
        set DEVICE_MODE=CPU
    )
)

:: Install core dependencies (minimal set for light installer)
echo  Installing faster-whisper...
pip install faster-whisper --quiet

echo  Installing Gradio UI...
pip install gradio --quiet

echo  Installing HuggingFace Hub...
pip install huggingface-hub --quiet

echo  Installing audio processing...
pip install av --quiet

if errorlevel 1 (
    echo.
    echo  ERROR: Failed to install dependencies!
    echo  Check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo  All dependencies installed!

:: Create necessary directories
if not exist "models" mkdir models
if not exist "Outputs" mkdir Outputs

:: Launch the app
echo.
echo [5/5] Launching Perfect STT...
echo.
echo  ============================================
echo   Mode: %DEVICE_MODE%
echo   URL:  http://localhost:7860
echo  ============================================
echo.
echo  NOTE: On first run, the AI model will be
echo  downloaded automatically (~600MB for large-v3).
echo.
echo  Press Ctrl+C to stop the server.
echo.

python app.py

:: Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo  The app encountered an error.
    echo  Press any key to exit...
    pause >nul
)

endlocal
