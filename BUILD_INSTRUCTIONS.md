# Perfect STT v2.2 - Build Instructions

## Overview

This guide explains how to create a **professional Windows installer** that non-technical users can simply double-click to install. The final installer:

- ✅ Installs to Program Files
- ✅ Creates Desktop shortcut
- ✅ Creates Start Menu entry  
- ✅ Includes Uninstaller
- ✅ Bundles FFmpeg (video support works immediately)
- ✅ No Python required on user's machine
- ✅ No console window (clean GUI)

---

## Quick Start (One Command)

```batch
BUILD_INSTALLER.bat
```

This single script does everything:
1. Installs Python dependencies
2. Builds the application with PyInstaller
3. Creates the installer with Inno Setup

**Output:** `Output\PerfectSTT_Setup_v2.2.0.exe`

---

## Prerequisites (On Your Build Machine)

### 1. Python 3.10+
- Download from: https://python.org
- **Important:** Check "Add Python to PATH" during installation

### 2. Inno Setup 6 (Free)
- Download from: https://jrsoftware.org/isdl.php
- Install to default location
- This creates the professional installer

---

## Step-by-Step Manual Build

If you prefer to run each step manually:

### Step 1: Install Dependencies
```batch
pip install -r requirements.txt
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install pyinstaller
```

### Step 2: Build with PyInstaller
```batch
pyinstaller build_for_installer.spec --noconfirm
```

This creates: `dist\PerfectSTT\` folder with all files

### Step 3: Create Installer
**Option A:** Run Inno Setup from command line:
```batch
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

**Option B:** Use Inno Setup GUI:
1. Open Inno Setup Compiler
2. File → Open → Select `installer.iss`
3. Build → Compile

**Output:** `Output\PerfectSTT_Setup_v2.2.0.exe`

---

## What Gets Created

### The Installer (~150-200MB)
```
Output\
└── PerfectSTT_Setup_v2.2.0.exe    ← Send this to friends!
```

### When User Installs
```
C:\Program Files\Perfect STT\
├── PerfectSTT.exe                  # Main application
├── ffmpeg\
│   ├── ffmpeg.exe                  # Video processing
│   └── ffprobe.exe
├── models\                         # AI models (downloaded on first use)
├── Outputs\                        # Transcription results
└── [other dependencies]
```

### Shortcuts Created
- Desktop: "Perfect STT" icon
- Start Menu: "Perfect STT" entry
- Uninstaller in Add/Remove Programs

---

## Distribution to Friends

### What to Send
Just send the single file:
```
PerfectSTT_Setup_v2.2.0.exe
```

### User Experience
1. **Double-click** the Setup file
2. **Click Next** a few times
3. **Done!** Desktop shortcut appears
4. **Double-click** the shortcut to run

### First Run
- Browser opens automatically with the app
- First transcription downloads AI model (~500MB)
- Subsequent uses are instant

---

## Antivirus Warning

Windows Defender will likely show a warning because the installer isn't digitally signed (costs $500/year).

### Tell Your Friends:
> "When you run the installer, Windows might show a blue screen saying 'Windows protected your PC'. 
> Click **'More info'** then **'Run anyway'**. It's safe - I built it myself!"

### Pro Tips:
- Zip with password (e.g., "1234") to prevent email/cloud blocking
- Add to antivirus exceptions if needed

---

## Build Options

### Option A: Professional Installer (Recommended)
Uses `BUILD_INSTALLER.bat` → Creates `PerfectSTT_Setup_v2.2.0.exe`

**Pros:**
- Professional installation experience
- Desktop & Start Menu shortcuts
- Proper uninstaller
- Installs to Program Files

**Best for:** Sharing with non-technical users

### Option B: Single EXE (Portable)
Uses `build_standalone.spec` → Creates `dist\PerfectSTT.exe`

**Pros:**
- Single file, no installation needed
- Can run from USB drive
- Portable

**Cons:**
- Slower first startup
- No shortcuts created
- Larger file (~400MB)

**Best for:** Tech-savvy users who want portable app

### Option C: Folder Distribution
Uses `build_for_installer.spec` → Creates `dist\PerfectSTT\` folder

**Pros:**
- Fastest startup
- Easy to inspect/modify

**Cons:**
- Must share entire folder
- No shortcuts

**Best for:** Developers/testing

---

## File Reference

| File | Purpose |
|------|---------|
| `BUILD_INSTALLER.bat` | **One-click build** - runs everything |
| `build_for_installer.spec` | PyInstaller config for folder build |
| `build_standalone.spec` | PyInstaller config for single EXE |
| `installer.iss` | Inno Setup script for installer |
| `app.py` | Main application code |
| `icon.ico` | Application icon |
| `ffmpeg/` | FFmpeg binaries (bundled) |

---

## Troubleshooting

### "Python not found"
- Reinstall Python with "Add to PATH" checked
- Or add manually: System Properties → Environment Variables → Path

### "Inno Setup not found"
- Install from https://jrsoftware.org/isdl.php
- Or compile manually: Open `installer.iss` in Inno Setup GUI

### Build fails with module errors
```batch
pip install --upgrade faster-whisper gradio torch pyinstaller
```

### Installer blocked by antivirus
- Add exception in antivirus settings
- Or zip with password before sharing

### App crashes on user's machine
- Make sure they're running Windows 10 or later
- Check if antivirus is blocking it
- Try running as Administrator

---

## Size Reference

| Component | Size |
|-----------|------|
| Setup installer | ~150-200MB |
| Installed app | ~400MB |
| AI model (small) | ~500MB |
| AI model (large-v3) | ~3GB |

**Total on user's disk:** ~1GB (with small model)

---

## Support

If you encounter issues:
1. Run `BUILD_INSTALLER.bat` and check error messages
2. Try building steps manually to isolate the problem
3. Ensure all prerequisites are installed
4. Check that `ffmpeg/` folder contains both .exe files

Happy transcribing! 🎙️
