#!/bin/bash
# ============================================================================
# Perfect STT - Release Packaging Script (Linux/Mac)
# ============================================================================
# This script builds the standalone executable and prepares it for distribution.
# 
# Prerequisites:
#   1. Python 3.10+ with pip
#   2. All dependencies installed (pip install -r requirements.txt)
#   3. PyInstaller installed (pip install pyinstaller)
#
# Usage:
#   chmod +x package_for_release.sh
#   ./package_for_release.sh
# ============================================================================

set -e

echo ""
echo "============================================================"
echo "  Perfect STT - Release Packaging Script"
echo "============================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed!"
    echo "Please install Python 3.10+ from https://python.org"
    exit 1
fi

# Check if PyInstaller is available
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip3 install pyinstaller
fi

echo ""
echo "[Step 1/4] Cleaning previous builds..."
echo ""
rm -rf dist build

echo ""
echo "[Step 2/4] Building executable with PyInstaller..."
echo "This may take several minutes..."
echo ""
pyinstaller build.spec --noconfirm

echo ""
echo "[Step 3/4] Creating release folder..."
echo ""

# Create release folder
RELEASE_FOLDER="PerfectSTT_v2.1_Release"
rm -rf "$RELEASE_FOLDER"
mkdir -p "$RELEASE_FOLDER"

# Copy the built application
cp -r dist/PerfectSTT/* "$RELEASE_FOLDER/"

# Create empty folders for models and outputs
mkdir -p "$RELEASE_FOLDER/models"
mkdir -p "$RELEASE_FOLDER/Outputs"

# Create README for the release
cat > "$RELEASE_FOLDER/README.txt" << 'EOF'
============================================================
  Perfect STT v2.1 - Local Speech-to-Text Tool
============================================================

QUICK START:
  1. Run "./PerfectSTT" to launch (or double-click on some systems)
  2. Upload an audio/video file
  3. Click "Transcribe"
  4. Find your transcripts in the "Outputs" folder

FIRST RUN:
  - The app will download the AI model on first use (~500MB)
  - This only happens once - models are saved in the "models" folder

VIDEO SUPPORT:
  To enable video file support (MP4, MKV, etc.):
  
  Linux:
    sudo apt install ffmpeg
  
  Mac:
    brew install ffmpeg
  
  Or place ffmpeg and ffprobe binaries in this folder.

SUPPORTED FORMATS:
  Audio: MP3, WAV, M4A, OGG, FLAC, AAC, WMA
  Video: MP4, MKV, MOV, AVI, WebM, WMV, FLV (requires FFmpeg)

HARDWARE:
  - GPU (NVIDIA): Automatically uses GPU for fast processing
  - CPU: Uses optimized INT8 mode for compatibility

TROUBLESHOOTING:
  - If the app doesn't start, run from terminal to see errors
  - Make sure you have enough disk space for models (~3GB for large)
  - For video files, ensure FFmpeg is installed

============================================================
EOF

# Make executable
chmod +x "$RELEASE_FOLDER/PerfectSTT"

echo ""
echo "[Step 4/4] Done!"
echo ""
echo "============================================================"
echo "  BUILD COMPLETE!"
echo "============================================================"
echo ""
echo "Your release folder is ready: $RELEASE_FOLDER"
echo ""
echo "To distribute:"
echo "  1. Test: ./$RELEASE_FOLDER/PerfectSTT"
echo "  2. Create archive: tar -czvf PerfectSTT_v2.1.tar.gz $RELEASE_FOLDER"
echo "  3. Share the archive with friends!"
echo ""
echo "============================================================"
