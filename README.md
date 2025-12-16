# 🎙️ Perfect STT v2.2 - Universal Speech-to-Text

[![Build Windows Installer](https://github.com/YOUR_USERNAME/perfect-stt/actions/workflows/build-installer.yml/badge.svg)](https://github.com/YOUR_USERNAME/perfect-stt/actions/workflows/build-installer.yml)

**Local, Private, No File Size Limits, Zero Dependencies**

A powerful speech-to-text tool that runs entirely on your computer. Works on any hardware - from gaming PCs with NVIDIA GPUs to basic laptops with just a CPU. **Now with standalone EXE support - no Python required for end users!**

![Perfect STT](https://img.shields.io/badge/Version-2.2-blue) ![Python](https://img.shields.io/badge/Python-3.10+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ✨ What's New in v2.1

- **📦 Standalone EXE** - Build a distributable app that works without Python
- **🎬 Portable FFmpeg** - Just drop ffmpeg.exe in the folder, no installation
- **🔧 PyInstaller Ready** - One-click build script for creating installers
- **📋 Professional Packaging** - README, instructions, everything included

### Previous (v2.0)
- 🪶 Light Installer - Small download, models download on first run
- 🧠 Smart Hardware Detection - Auto-switches between GPU (float16) and CPU (INT8)
- 💻 Universal Compatibility - Works on any PC, even without a GPU
- ⚡ INT8 Quantization - Large model runs on standard laptops

---

## 🚀 Two Ways to Use

### Option A: Developer Mode (Run from Source)
For developers or power users who have Python installed.

```bash
# Windows
setup_and_run.bat

# macOS / Linux
./setup_and_run.sh
```

### Option B: Distribution Mode (Standalone EXE)
For sharing with friends who don't have Python.

1. Build the EXE (see [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md))
2. Share the `PerfectSTT_v2.1_Release` folder
3. Friends just double-click `PerfectSTT.exe`

---

## ⚠️ IMPORTANT: Windows Security Warning

When you or your friends run the `.exe` for the first time, **Windows Defender will show a blue warning screen**:

> "Windows protected your PC"

**This is normal!** It happens because the app isn't digitally signed (costs $500/year).

### How to bypass:
1. Click **"More info"**
2. Click **"Run anyway"**

The app is completely safe - it's open source and runs 100% locally.

### Pro Tip for Sharing:
If you're sharing via email or Google Drive, **zip with a password** (e.g., `1234`) to prevent the file from being blocked.

---

## 📦 Distribution Strategies

| Strategy | "Light" Zip | "VIP" Zip |
|----------|-------------|-----------|
| **Size** | ~60-100MB | ~700MB+ |
| **First Run** | Downloads model (5-10 min wait) | Works instantly, even offline |
| **Best For** | Quick sharing, bandwidth-limited | VIP friends, offline use |
| **How** | Zip immediately after build | Run app once to download model, then zip |

### Creating a "VIP" Package:
1. Build the EXE
2. Run `PerfectSTT.exe` once
3. Select the "small" model and transcribe a test file
4. The model downloads to `models/` folder
5. Now zip the entire folder - model included!

---

## 🎯 Features

- **🔒 100% Private** - All processing happens locally
- **📁 No File Size Limits** - Transcribe hours of audio/video
- **🌍 30+ Languages** - Auto-detection or manual selection
- **🔄 Translation** - Translate any language to English
- **📝 Multiple Outputs** - TXT, SRT subtitles, VTT for web
- **💾 Auto-Save** - Files saved automatically to `Outputs/` folder

---

## 📋 Requirements

### For Running from Source (Developer Mode)
- **Python 3.10 or 3.11** - [Download](https://www.python.org/downloads/)
- **8GB RAM minimum** (16GB recommended for large models)

### For Standalone EXE (Distribution Mode)
- **Nothing!** Just unzip and run
- **Optional:** FFmpeg for video support (place in same folder)

### Optional Enhancements
- **NVIDIA GPU** - For maximum speed (RTX 20/30/40 series)
- **Apple Silicon** - M1/M2/M3 uses Metal acceleration

---

## 📊 Model Comparison

| Model | Download | RAM | GPU Speed | CPU Speed | Accuracy |
|-------|----------|-----|-----------|-----------|----------|
| tiny | 75MB | 1GB | ⚡⚡⚡⚡⚡ | ⚡⚡⚡ | ★☆☆☆☆ |
| base | 150MB | 1GB | ⚡⚡⚡⚡ | ⚡⚡ | ★★☆☆☆ |
| small | 500MB | 2GB | ⚡⚡⚡ | ⚡ | ★★★☆☆ |
| medium | 1.5GB | 5GB | ⚡⚡ | 🐢 | ★★★★☆ |
| **large-v3** | 3GB | 10GB | ⚡ | 🐢 | ★★★★★ |

**Recommendations:**
- **GPU users:** Use `large-v3` for best accuracy
- **CPU users:** Use `small` for good balance of speed and accuracy
- **Low RAM:** Use `tiny` or `base`

---

## ⚡ Performance Examples

### NVIDIA RTX 3080
| Audio | Model | Time |
|-------|-------|------|
| 10 min | large-v3 | ~1 min |
| 1 hour | large-v3 | ~6 min |

### Intel i7 (CPU Only, INT8 Mode)
| Audio | Model | Time |
|-------|-------|------|
| 10 min | small | ~5 min |
| 10 min | large-v3 | ~30 min |

---

## 🎬 Supported Formats

**Audio:** MP3, WAV, M4A, FLAC, OGG, AAC, WMA

**Video:** MP4, MKV, MOV, AVI, WebM (requires FFmpeg)

### Adding FFmpeg for Video Support

**For Standalone EXE:**
1. Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
2. Get "ffmpeg-release-essentials.zip"
3. Extract `ffmpeg.exe` and `ffprobe.exe`
4. Place them in the same folder as `PerfectSTT.exe`

**For Source Code:**
- Windows: Add FFmpeg to PATH, or place in app folder
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

---

## 📁 Output Files

All transcriptions are automatically saved:

```
Outputs/
├── meeting_20241211_143052.txt    # Plain text
├── meeting_20241211_143052.srt    # Subtitles (video editors)
└── meeting_20241211_143052.vtt    # Web subtitles
```

---

## 🏗️ Building Standalone EXE

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for detailed steps.

**Quick Start:**
```bash
# Install dependencies
pip install -r requirements.txt
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Build (Windows)
package_for_release.bat

# Build (Linux/Mac)
./package_for_release.sh
```

---

## 🔧 Troubleshooting

### "Windows protected your PC" (Blue Screen)
- Click "More info" → "Run anyway"
- This is normal for unsigned apps

### "Python not found"
- Install from [python.org](https://www.python.org/downloads/)
- **Windows:** Check "Add Python to PATH" during install

### "FFmpeg not found"
- Audio files still work without FFmpeg
- For video: Place `ffmpeg.exe` in the app folder

### "Out of memory"
- Use a smaller model (small instead of large-v3)
- Close other applications

### Slow on CPU
- Use `tiny` or `small` model
- CPU mode uses INT8 quantization for best compatibility

### EXE doesn't start
- Run from Command Prompt to see error messages
- Make sure you extracted the entire folder (not just the .exe)

---

## 📄 License

MIT License - Free for personal and commercial use.

---

## 🙏 Credits

- [faster-whisper](https://github.com/SYSTRAN/faster-whisper) - Fast Whisper implementation
- [OpenAI Whisper](https://github.com/openai/whisper) - Original model
- [Gradio](https://gradio.app/) - Web UI framework
- [CTranslate2](https://github.com/OpenNMT/CTranslate2) - Optimized inference

---

**Made with ❤️ for privacy-conscious transcription**

*Your audio never leaves your computer. Ever.*
