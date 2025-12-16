# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Spec File for Perfect STT v2.2 - Installer Edition
===============================================================

This creates a FOLDER distribution (not single file) for use with Inno Setup.
The folder approach is better for installers because:
- Faster startup (no extraction needed)
- Easier to update individual components
- Better compatibility with antivirus software

Usage:
    pyinstaller build_for_installer.spec

Output: dist/PerfectSTT/ (folder with all files)
Then use Inno Setup with installer.iss to create the final installer.
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

# FFmpeg binaries to bundle
FFMPEG_DIR = Path("ffmpeg")

# ============================================================================
# COLLECT DATA FILES AND BINARIES
# ============================================================================

datas = []
binaries = []

# Bundle FFmpeg executables
if FFMPEG_DIR.exists():
    ffmpeg_exe = FFMPEG_DIR / "ffmpeg.exe"
    ffprobe_exe = FFMPEG_DIR / "ffprobe.exe"
    
    if ffmpeg_exe.exists():
        binaries.append((str(ffmpeg_exe), 'ffmpeg'))
        print(f"✅ Bundling: {ffmpeg_exe}")
    
    if ffprobe_exe.exists():
        binaries.append((str(ffprobe_exe), 'ffmpeg'))
        print(f"✅ Bundling: {ffprobe_exe}")
else:
    print("⚠️ Warning: ffmpeg folder not found!")

# Try to find CTranslate2 library files
try:
    import ctranslate2
    ct2_path = Path(ctranslate2.__file__).parent
    for pattern in ['*.dll', '*.so', '*.dylib', '*.pyd']:
        for f in ct2_path.glob(pattern):
            binaries.append((str(f), 'ctranslate2'))
except ImportError:
    pass

# Try to find faster_whisper assets
try:
    import faster_whisper
    fw_path = Path(faster_whisper.__file__).parent
    assets_path = fw_path / 'assets'
    if assets_path.exists():
        datas.append((str(assets_path), 'faster_whisper/assets'))
except ImportError:
    pass

# ============================================================================
# HIDDEN IMPORTS
# ============================================================================

hidden_imports = [
    # Core transcription
    'ctranslate2',
    'faster_whisper',
    'faster_whisper.transcribe',
    'faster_whisper.audio',
    'faster_whisper.tokenizer',
    'faster_whisper.vad',
    
    # HuggingFace
    'huggingface_hub',
    'huggingface_hub.file_download',
    'tokenizers',
    
    # Audio
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
    
    # HTTP
    'httpx',
    'httpcore',
    'h11',
    'anyio',
    'sniffio',
    
    # Standard
    'multiprocessing',
    'concurrent.futures',
    'asyncio',
    'typing_extensions',
    'numpy',
    'certifi',
    'websockets',
    'websockets.legacy',
]

# ============================================================================
# EXCLUDED MODULES
# ============================================================================

excludes = [
    'tkinter',
    'PyQt5',
    'PyQt6', 
    'PySide2',
    'PySide6',
    'wx',
    'IPython',
    'jupyter',
    'notebook',
    'pytest',
    'matplotlib',
    'plotly',
    'seaborn',
    'scipy',
    'pandas',
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
# CREATE FOLDER DISTRIBUTION
# ============================================================================

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # Keep binaries separate (folder mode)
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # NO CONSOLE WINDOW
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH if os.path.exists(ICON_PATH) else None,
)

# Collect all files into a folder
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=APP_NAME,
)
