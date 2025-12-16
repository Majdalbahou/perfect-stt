#!/bin/bash

# ============================================
# Perfect STT v2.0 - Universal Installer
# For macOS and Linux
# Light installer - models download on first run
# ============================================

echo ""
echo "============================================"
echo " Perfect STT v2.0 - Universal Installer"
echo " Local, Private Speech-to-Text"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check for Python
echo "[1/5] Checking for Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 not found!${NC}"
    echo ""
    echo "Please install Python 3.10 or 3.11:"
    echo "  macOS: brew install python@3.11"
    echo "  Ubuntu: sudo apt install python3.11 python3.11-venv"
    echo ""
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "  ${GREEN}Found $PYTHON_VERSION${NC}"

# Check for FFmpeg
echo ""
echo "[2/5] Checking for FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}WARNING: FFmpeg not found!${NC}"
    echo ""
    echo "FFmpeg is required for video files."
    echo "  macOS: brew install ffmpeg"
    echo "  Ubuntu: sudo apt install ffmpeg"
    echo ""
    echo "Audio files (MP3, WAV) will still work."
    sleep 3
else
    echo -e "  ${GREEN}FFmpeg found!${NC}"
fi

# Create virtual environment
echo ""
echo "[3/5] Setting up virtual environment..."
if [ ! -d "venv" ]; then
    echo "  Creating new virtual environment..."
    python3 -m venv venv
    echo -e "  ${GREEN}Virtual environment created!${NC}"
else
    echo "  Virtual environment already exists."
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip --quiet 2>/dev/null

# Detect hardware
echo ""
echo "[4/5] Detecting hardware and installing dependencies..."
echo ""

DEVICE_MODE="CPU"

# Check for NVIDIA GPU (Linux)
if command -v nvidia-smi &> /dev/null && nvidia-smi &> /dev/null; then
    echo -e "  ${GREEN}NVIDIA GPU detected!${NC}"
    echo "  Installing CUDA-enabled version..."
    DEVICE_MODE="GPU"
    pip install torch --index-url https://download.pytorch.org/whl/cu121 --quiet 2>/dev/null || \
    pip install torch --index-url https://download.pytorch.org/whl/cu118 --quiet 2>/dev/null || \
    pip install torch --quiet
# Check for Apple Silicon (macOS)
elif [[ "$(uname -s)" == "Darwin" ]] && [[ "$(uname -m)" == "arm64" ]]; then
    echo -e "  ${GREEN}Apple Silicon detected!${NC}"
    echo "  Installing MPS-enabled version..."
    DEVICE_MODE="MPS"
    pip install torch --quiet
# CPU fallback
else
    echo "  No GPU detected."
    echo "  Installing CPU-optimized version..."
    pip install torch --index-url https://download.pytorch.org/whl/cpu --quiet 2>/dev/null || \
    pip install torch --quiet
fi

# Install core dependencies (minimal for light installer)
echo "  Installing faster-whisper..."
pip install faster-whisper --quiet

echo "  Installing Gradio UI..."
pip install gradio --quiet

echo "  Installing HuggingFace Hub..."
pip install huggingface-hub --quiet

echo "  Installing audio processing..."
pip install av --quiet

echo ""
echo -e "  ${GREEN}All dependencies installed!${NC}"

# Create necessary directories
mkdir -p models
mkdir -p Outputs

# Launch the app
echo ""
echo "[5/5] Launching Perfect STT..."
echo ""
echo "============================================"
echo " Mode: $DEVICE_MODE"
echo " URL:  http://localhost:7860"
echo "============================================"
echo ""
echo "NOTE: On first run, the AI model will be"
echo "downloaded automatically (~600MB for large-v3)."
echo ""
echo "Press Ctrl+C to stop the server."
echo ""

python3 app.py
