# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Perfect STT
=====================================

This spec file creates a standalone executable that includes:
- Python interpreter
- All required libraries (faster-whisper, gradio, torch, etc.)
- CTranslate2 binaries

Usage:
    pyinstaller build.spec

The output will be in the 'dist' folder.
"""

import sys
import os
from pathlib import Path

# Get the path to site-packages for finding library binaries
import site
site_packages = site.getsitepackages()[0]

# Try to find CTranslate2 library path
ctranslate2_path = None
try:
    import ctranslate2
    ctranslate2_path = Path(ctranslate2.__file__).parent
except ImportError:
    print("Warning: ctranslate2 not found, binaries may be missing")

# Try to find faster_whisper assets
faster_whisper_path = None
try:
    import faster_whisper
    faster_whisper_path = Path(faster_whisper.__file__).parent
except ImportError:
    print("Warning: faster_whisper not found")

# Collect data files
datas = []

# Add CTranslate2 binaries if found
if ctranslate2_path and ctranslate2_path.exists():
    # Include all .dll, .so files from ctranslate2
    for ext in ['*.dll', '*.so', '*.dylib', '*.pyd']:
        for f in ctranslate2_path.glob(ext):
            datas.append((str(f), 'ctranslate2'))
    # Include subdirectories
    if (ctranslate2_path / 'bin').exists():
        datas.append((str(ctranslate2_path / 'bin'), 'ctranslate2/bin'))

# Add faster_whisper assets if found
if faster_whisper_path and faster_whisper_path.exists():
    assets_path = faster_whisper_path / 'assets'
    if assets_path.exists():
        datas.append((str(assets_path), 'faster_whisper/assets'))

# Hidden imports that PyInstaller might miss
hidden_imports = [
    'ctranslate2',
    'faster_whisper',
    'huggingface_hub',
    'tokenizers',
    'torch',
    'torchaudio',
    'numpy',
    'gradio',
    'gradio.themes',
    'gradio.components',
    'gradio.blocks',
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'starlette',
    'httpx',
    'httpcore',
    'anyio',
    'sniffio',
    'h11',
    'certifi',
    'charset_normalizer',
    'idna',
    'urllib3',
    'requests',
    'PIL',
    'PIL.Image',
    'pydub',
    'av',
    'soundfile',
    'scipy',
    'scipy.signal',
    'scipy.io',
    'scipy.io.wavfile',
]

# Analysis
a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'tkinter',
        'PyQt5',
        'PyQt6',
        'PySide2',
        'PySide6',
        'IPython',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Create PYZ archive
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PerfectSTT',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Keep console for debugging; set to False for release
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,  # Place icon.ico in project folder
)

# Collect all files
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PerfectSTT',
)
