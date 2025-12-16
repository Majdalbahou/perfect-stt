# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File for Perfect STT v2.2 - Standalone Edition
================================================================

This creates a SINGLE executable file with:
- Python interpreter bundled
- All dependencies included
- FFmpeg binaries bundled inside
- No console window (GUI only)
- Custom icon

Usage:
    pyinstaller build_standalone.spec

Output: dist/PerfectSTT.exe (single file, ~300MB+)
"""

import sys
import os
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

APP_NAME = "PerfectSTT"
APP_VERSION = "2.2.0"
SCRIPT_PATH = "app.py"
ICON_PATH = "icon.ico"

# FFmpeg binaries to bundle (must be in ./ffmpeg/ folder)
FFMPEG_DIR = Path("ffmpeg")

# ============================================================================
# COLLECT DATA FILES
# ============================================================================

datas = []
binaries = []

# Bundle FFmpeg executables
if FFMPEG_DIR.exists():
    ffmpeg_exe = FFMPEG_DIR / "ffmpeg.exe"
    ffprobe_exe = FFMPEG_DIR / "ffprobe.exe"
    
    if ffmpeg_exe.exists():
        # Add as binary with destination folder 'ffmpeg'
        binaries.append((str(ffmpeg_exe), 'ffmpeg'))
        print(f"✅ Bundling: {ffmpeg_exe}")
    
    if ffprobe_exe.exists():
        binaries.append((str(ffprobe_exe), 'ffmpeg'))
        print(f"✅ Bundling: {ffprobe_exe}")
else:
    print("⚠️ Warning: ffmpeg folder not found. Video support will require external FFmpeg.")

# Try to find CTranslate2 library files
try:
    import ctranslate2
    ct2_path = Path(ctranslate2.__file__).parent
    
    # Include DLLs/shared libraries
    for pattern in ['*.dll', '*.so', '*.dylib', '*.pyd']:
        for f in ct2_path.glob(pattern):
            binaries.append((str(f), 'ctranslate2'))
            print(f"✅ Including: {f.name}")
except ImportError:
    print("⚠️ ctranslate2 not installed - will be handled by PyInstaller hooks")

# Try to find faster_whisper assets
try:
    import faster_whisper
    fw_path = Path(faster_whisper.__file__).parent
    assets_path = fw_path / 'assets'
    if assets_path.exists():
        datas.append((str(assets_path), 'faster_whisper/assets'))
        print(f"✅ Including faster_whisper assets")
except ImportError:
    print("⚠️ faster_whisper not installed")

# ============================================================================
# HIDDEN IMPORTS
# ============================================================================

# These modules are dynamically imported and PyInstaller might miss them
hidden_imports = [
    # Core transcription
    'ctranslate2',
    'faster_whisper',
    'faster_whisper.transcribe',
    'faster_whisper.audio',
    'faster_whisper.tokenizer',
    'faster_whisper.vad',
    
    # HuggingFace for model downloads
    'huggingface_hub',
    'huggingface_hub.file_download',
    'huggingface_hub.hf_api',
    
    # Tokenizers
    'tokenizers',
    
    # Audio processing
    'av',
    'av.audio',
    'av.audio.frame',
    'av.audio.resampler',
    
    # Gradio UI
    'gradio',
    'gradio.themes',
    'gradio.themes.soft',
    'gradio.components',
    'gradio.blocks',
    'gradio.routes',
    
    # Web server
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    
    # FastAPI/Starlette
    'fastapi',
    'starlette',
    'starlette.routing',
    'starlette.middleware',
    
    # HTTP clients
    'httpx',
    'httpcore',
    'h11',
    'anyio',
    'sniffio',
    
    # Standard libs that might be missed
    'multiprocessing',
    'concurrent.futures',
    'asyncio',
    'json',
    'typing_extensions',
    
    # NumPy/Scientific
    'numpy',
    'numpy.core',
    
    # Networking
    'certifi',
    'charset_normalizer',
    'idna',
    'urllib3',
    'requests',
    
    # Websockets for Gradio
    'websockets',
    'websockets.legacy',
    'websockets.legacy.server',
]

# ============================================================================
# EXCLUDED MODULES (reduce size)
# ============================================================================

excludes = [
    # GUI frameworks we don't use
    'tkinter',
    'PyQt5',
    'PyQt6', 
    'PySide2',
    'PySide6',
    'wx',
    
    # Development tools
    'IPython',
    'jupyter',
    'notebook',
    'pytest',
    
    # Visualization (not needed)
    'matplotlib',
    'plotly',
    'seaborn',
    
    # Other heavy packages
    'scipy',
    'pandas',
    'PIL',  # We don't need image processing
]

# ============================================================================
# ANALYSIS
# ============================================================================

a = Analysis(
    [SCRIPT_PATH],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# ============================================================================
# CREATE SINGLE EXECUTABLE
# ============================================================================

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,        # Include binaries in EXE
    a.zipfiles,        # Include zipfiles in EXE
    a.datas,           # Include data in EXE
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,          # Compress with UPX if available
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,     # NO CONSOLE WINDOW - GUI only!
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH if os.path.exists(ICON_PATH) else None,
)

# ============================================================================
# NOTE: This creates a SINGLE FILE executable
# ============================================================================
# 
# The output will be: dist/PerfectSTT.exe
#
# This single file contains:
# - Python interpreter
# - All Python packages
# - FFmpeg binaries
# - Application code
#
# File size will be approximately 300-500MB depending on dependencies.
#
# When the user runs the EXE, it extracts to a temp folder and runs from there.
# This is slightly slower to start but much easier to distribute.
#
# ============================================================================
