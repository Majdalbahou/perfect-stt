#!/usr/bin/env python3
"""
Perfect STT - Universal Speech-to-Text Tool
============================================
A local, private transcription tool that works on any hardware.

Features:
- Smart hardware detection (GPU/CPU auto-switching)
- Automatic model download on first run
- INT8 quantization for CPU-only machines
- No file size limits
- Multiple output formats (TXT, SRT, VTT)
- Portable FFmpeg support (no installation required)

Uses faster-whisper (CTranslate2) for optimal performance.
"""

import os
import sys
import time
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from datetime import datetime

import gradio as gr

# ============================================================================
# PYINSTALLER COMPATIBILITY
# ============================================================================

def get_app_dir() -> Path:
    """
    Get the application directory.
    Works both in development and when packaged with PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys.executable).parent
    else:
        # Running as script
        return Path(__file__).parent


def get_resource_path(relative_path: str) -> Path:
    """
    Get absolute path to resource, works for dev and PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = Path(sys._MEIPASS)
    else:
        # Running as script
        base_path = Path(__file__).parent
    return base_path / relative_path


# ============================================================================
# CONFIGURATION
# ============================================================================

APP_NAME = "Perfect STT"
APP_VERSION = "2.2.0"
APP_DIR = get_app_dir()
MODELS_DIR = APP_DIR / "models"
OUTPUTS_DIR = APP_DIR / "Outputs"

# Model configurations
MODEL_SIZES = {
    "tiny": {"size": "~75MB", "speed": "Fastest", "accuracy": "Basic", "vram": "~1GB"},
    "base": {"size": "~150MB", "speed": "Fast", "accuracy": "Good", "vram": "~1GB"},
    "small": {"size": "~500MB", "speed": "Medium", "accuracy": "Better", "vram": "~2GB"},
    "medium": {"size": "~1.5GB", "speed": "Slow", "accuracy": "Great", "vram": "~5GB"},
    "large-v3": {"size": "~3GB", "speed": "Slowest", "accuracy": "Best", "vram": "~10GB"},
}

# Supported file formats
SUPPORTED_AUDIO = [".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac", ".wma"]
SUPPORTED_VIDEO = [".mp4", ".mkv", ".mov", ".avi", ".webm", ".wmv", ".flv"]
SUPPORTED_FORMATS = SUPPORTED_AUDIO + SUPPORTED_VIDEO

# Global state
_model = None
_model_name = None
_hardware_info = None
_ffmpeg_path = None
_ffprobe_path = None

# ============================================================================
# FFMPEG DETECTION (BUNDLED + PORTABLE + SYSTEM)
# ============================================================================

def find_ffmpeg() -> Tuple[Optional[str], Optional[str]]:
    """
    Find FFmpeg and FFprobe executables.
    
    Priority:
    1. Bundled: Inside PyInstaller package (sys._MEIPASS)
    2. Portable: Same folder as the application
    3. System PATH
    
    Returns:
        Tuple of (ffmpeg_path, ffprobe_path) or (None, None) if not found
    """
    global _ffmpeg_path, _ffprobe_path
    
    # Return cached paths if already found
    if _ffmpeg_path and _ffprobe_path:
        return _ffmpeg_path, _ffprobe_path
    
    # Determine executable extension based on OS
    exe_ext = ".exe" if sys.platform == "win32" else ""
    
    # Priority 1: Check bundled location (inside PyInstaller package)
    if getattr(sys, 'frozen', False):
        bundled_dir = Path(sys._MEIPASS) / "ffmpeg"
        bundled_ffmpeg = bundled_dir / f"ffmpeg{exe_ext}"
        bundled_ffprobe = bundled_dir / f"ffprobe{exe_ext}"
        
        if bundled_ffmpeg.exists() and bundled_ffprobe.exists():
            _ffmpeg_path = str(bundled_ffmpeg)
            _ffprobe_path = str(bundled_ffprobe)
            print(f"✅ Using bundled FFmpeg")
            return _ffmpeg_path, _ffprobe_path
    
    # Priority 2: Check portable location (same folder as app)
    portable_ffmpeg = APP_DIR / f"ffmpeg{exe_ext}"
    portable_ffprobe = APP_DIR / f"ffprobe{exe_ext}"
    
    if portable_ffmpeg.exists() and portable_ffprobe.exists():
        _ffmpeg_path = str(portable_ffmpeg)
        _ffprobe_path = str(portable_ffprobe)
        print(f"✅ Found portable FFmpeg: {_ffmpeg_path}")
        return _ffmpeg_path, _ffprobe_path
    
    # Priority 3: Check system PATH
    try:
        result = subprocess.run(
            [f"ffmpeg{exe_ext}", "-version"],
            capture_output=True,
            timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        if result.returncode == 0:
            _ffmpeg_path = f"ffmpeg{exe_ext}"
            _ffprobe_path = f"ffprobe{exe_ext}"
            print(f"✅ Found FFmpeg in system PATH")
            return _ffmpeg_path, _ffprobe_path
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    
    return None, None


def check_ffmpeg_available() -> bool:
    """Check if FFmpeg is available (portable or system)."""
    ffmpeg, ffprobe = find_ffmpeg()
    return ffmpeg is not None and ffprobe is not None


# ============================================================================
# HARDWARE DETECTION
# ============================================================================

def detect_hardware() -> Dict[str, Any]:
    """
    Detect available hardware and determine optimal settings.
    
    Returns:
        Dict with hardware info and recommended settings
    """
    info = {
        "has_cuda": False,
        "cuda_device": None,
        "cuda_memory": None,
        "device": "cpu",
        "compute_type": "int8",
        "mode_label": "CPU Mode (INT8 Optimized)",
        "recommendation": "Using INT8 quantization for CPU compatibility",
        "recommended_model": "small"
    }
    
    try:
        import torch
        if torch.cuda.is_available():
            info["has_cuda"] = True
            info["cuda_device"] = torch.cuda.get_device_name(0)
            info["cuda_memory"] = f"{torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB"
            info["device"] = "cuda"
            info["compute_type"] = "float16"
            info["mode_label"] = f"GPU Mode ({info['cuda_device']})"
            info["recommendation"] = "Using float16 for maximum GPU performance"
            info["recommended_model"] = "large-v3"
    except ImportError:
        info["recommendation"] = "PyTorch not found - running in CPU mode"
    except Exception as e:
        print(f"CUDA detection error: {e}")
    
    return info


# ============================================================================
# MODEL MANAGEMENT
# ============================================================================

def get_model_path(model_size: str) -> Path:
    """Get the path where a model should be stored."""
    return MODELS_DIR / f"faster-whisper-{model_size}"


def is_model_downloaded(model_size: str) -> bool:
    """Check if a model is already downloaded."""
    model_path = get_model_path(model_size)
    # Check for model.bin or config.json as indicators
    return model_path.exists() and (
        (model_path / "model.bin").exists() or 
        (model_path / "config.json").exists()
    )


def download_model(model_size: str, progress_callback=None) -> str:
    """
    Download a model from HuggingFace Hub if not already present.
    
    Args:
        model_size: Size of the model to download
        progress_callback: Optional callback for progress updates
        
    Returns:
        Path to the downloaded model (or model name for auto-download)
    """
    # Check if already downloaded locally
    model_path = get_model_path(model_size)
    if is_model_downloaded(model_size):
        if progress_callback:
            progress_callback(1.0, f"Model {model_size} already downloaded")
        return str(model_path)
    
    # Create models directory
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    if progress_callback:
        progress_callback(0.1, f"Downloading {model_size} model... (first run only)")
    
    # Let faster-whisper handle the download automatically
    # It will download to the default cache or we can specify local_files_only=False
    return model_size  # Return model name, faster-whisper will download it


def load_model(model_size: str, hardware_info: Dict[str, Any], progress_callback=None):
    """
    Load the faster-whisper model with appropriate settings.
    
    Args:
        model_size: Size of the model to load
        hardware_info: Hardware detection results
        progress_callback: Optional callback for progress updates
    """
    global _model, _model_name
    
    # Skip if already loaded
    if _model is not None and _model_name == model_size:
        if progress_callback:
            progress_callback(1.0, f"Model {model_size} already loaded")
        return _model
    
    from faster_whisper import WhisperModel
    
    if progress_callback:
        progress_callback(0.2, f"Loading {model_size} model...")
    
    # Check for local model first
    model_path = get_model_path(model_size)
    model_source = str(model_path) if is_model_downloaded(model_size) else model_size
    
    # Load with appropriate settings based on hardware
    try:
        _model = WhisperModel(
            model_source,
            device=hardware_info["device"],
            compute_type=hardware_info["compute_type"],
            download_root=str(MODELS_DIR),
        )
        _model_name = model_size
        
        if progress_callback:
            progress_callback(1.0, f"Model {model_size} loaded successfully!")
        
        return _model
        
    except Exception as e:
        # If GPU fails, fallback to CPU
        if hardware_info["device"] == "cuda":
            if progress_callback:
                progress_callback(0.5, f"GPU loading failed, falling back to CPU...")
            
            hardware_info["device"] = "cpu"
            hardware_info["compute_type"] = "int8"
            hardware_info["mode_label"] = "CPU Mode (Fallback)"
            
            _model = WhisperModel(
                model_source,
                device="cpu",
                compute_type="int8",
                download_root=str(MODELS_DIR),
            )
            _model_name = model_size
            
            if progress_callback:
                progress_callback(1.0, f"Model loaded in CPU mode")
            
            return _model
        else:
            raise


# ============================================================================
# AUDIO EXTRACTION
# ============================================================================

def extract_audio(input_path: str, progress_callback=None) -> str:
    """
    Extract audio from video file using ffmpeg.
    
    Args:
        input_path: Path to input video/audio file
        progress_callback: Optional callback for progress updates
        
    Returns:
        Path to extracted audio file
    """
    if progress_callback:
        progress_callback(0.1, "Extracting audio from video...")
    
    # Find FFmpeg
    ffmpeg_path, _ = find_ffmpeg()
    if not ffmpeg_path:
        raise RuntimeError(
            "❌ FFmpeg not found!\n\n"
            "To enable video support, please:\n\n"
            "Option 1 (Portable - Recommended):\n"
            "  1. Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/\n"
            "  2. Get the 'essentials' build\n"
            "  3. Extract ffmpeg.exe and ffprobe.exe\n"
            "  4. Place them in the same folder as this app\n\n"
            "Option 2 (System Install):\n"
            "  1. Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/\n"
            "  2. Extract and add to your System PATH\n"
            "  3. Restart this application"
        )
    
    # Create temp file for audio
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "audio.wav")
    
    # Use ffmpeg to extract audio (16kHz mono for Whisper)
    cmd = [
        ffmpeg_path,
        "-i", input_path,
        "-vn",  # No video
        "-acodec", "pcm_s16le",  # PCM 16-bit
        "-ar", "16000",  # 16kHz sample rate
        "-ac", "1",  # Mono
        "-y",  # Overwrite
        output_path
    ]
    
    try:
        # Use CREATE_NO_WINDOW on Windows to hide console popup
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
            creationflags=creation_flags
        )
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg error: {result.stderr}")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Audio extraction timed out (>10 minutes)")
    
    if progress_callback:
        progress_callback(0.3, "Audio extracted successfully")
    
    return output_path


# ============================================================================
# OUTPUT GENERATION
# ============================================================================

def format_timestamp_srt(seconds: float) -> str:
    """Format seconds to SRT timestamp (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_timestamp_vtt(seconds: float) -> str:
    """Format seconds to VTT timestamp (HH:MM:SS.mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def generate_srt(segments: list) -> str:
    """Generate SRT subtitle format."""
    lines = []
    for i, seg in enumerate(segments, 1):
        start = format_timestamp_srt(seg["start"])
        end = format_timestamp_srt(seg["end"])
        text = seg["text"].strip()
        lines.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(lines)


def generate_vtt(segments: list) -> str:
    """Generate VTT subtitle format."""
    lines = ["WEBVTT\n"]
    for i, seg in enumerate(segments, 1):
        start = format_timestamp_vtt(seg["start"])
        end = format_timestamp_vtt(seg["end"])
        text = seg["text"].strip()
        lines.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(lines)


def save_outputs(
    transcript: str,
    segments: list,
    input_filename: str,
    output_dir: Path = None
) -> Dict[str, str]:
    """
    Save all output formats to files.
    
    Args:
        transcript: Full transcript text
        segments: List of segment dictionaries
        input_filename: Original input filename
        output_dir: Directory to save outputs (defaults to OUTPUTS_DIR)
        
    Returns:
        Dict mapping format names to file paths
    """
    if output_dir is None:
        output_dir = OUTPUTS_DIR
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create base filename with timestamp
    base_name = Path(input_filename).stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_path = output_dir / f"{base_name}_{timestamp}"
    
    outputs = {}
    
    # Save TXT
    txt_path = f"{base_path}.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(transcript)
    outputs["txt"] = txt_path
    
    # Save SRT
    srt_path = f"{base_path}.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(generate_srt(segments))
    outputs["srt"] = srt_path
    
    # Save VTT
    vtt_path = f"{base_path}.vtt"
    with open(vtt_path, "w", encoding="utf-8") as f:
        f.write(generate_vtt(segments))
    outputs["vtt"] = vtt_path
    
    return outputs


# ============================================================================
# TRANSCRIPTION
# ============================================================================

def transcribe(
    file_path: str,
    model_size: str = "small",
    language: str = "auto",
    translate: bool = False,
) -> Tuple[str, str, str, str]:
    """
    Transcribe an audio/video file.
    
    Args:
        file_path: Path to the input file
        model_size: Whisper model size to use
        language: Language code or "auto" for detection
        translate: Whether to translate to English
        
    Returns:
        Tuple of (status, transcript, srt, vtt)
    """
    global _hardware_info
    
    if not file_path:
        return "❌ Please select a file first", "", "", ""
    
    # Validate file format
    file_ext = Path(file_path).suffix.lower()
    if file_ext not in SUPPORTED_FORMATS:
        return f"❌ Unsupported format: {file_ext}\nSupported: {', '.join(SUPPORTED_FORMATS)}", "", "", ""
    
    try:
        start_time = time.time()
        
        # Detect hardware if not already done
        if _hardware_info is None:
            _hardware_info = detect_hardware()
        
        # Status updates
        status_lines = [
            f"🔧 Mode: {_hardware_info['mode_label']}",
            f"📦 Model: {model_size}",
            f"🔄 Processing..."
        ]
        
        # Extract audio if video file
        audio_path = file_path
        if file_ext in SUPPORTED_VIDEO:
            if not check_ffmpeg_available():
                return (
                    "❌ FFmpeg required for video files!\n\n"
                    "Please place ffmpeg.exe and ffprobe.exe in the app folder,\n"
                    "or install FFmpeg and add it to your system PATH.",
                    "", "", ""
                )
            audio_path = extract_audio(file_path)
            status_lines.append("✅ Audio extracted from video")
        
        # Load model
        model = load_model(model_size, _hardware_info)
        status_lines.append(f"✅ Model loaded")
        
        # Transcribe
        lang_param = None if language == "auto" else language
        task = "translate" if translate else "transcribe"
        
        segments_gen, info = model.transcribe(
            audio_path,
            language=lang_param,
            task=task,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=500,
            ),
        )
        
        # Collect segments
        segments = []
        transcript_parts = []
        
        for segment in segments_gen:
            seg_dict = {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
            }
            segments.append(seg_dict)
            transcript_parts.append(segment.text.strip())
        
        # Generate outputs
        transcript = " ".join(transcript_parts)
        srt_content = generate_srt(segments)
        vtt_content = generate_vtt(segments)
        
        # Save to files
        input_filename = Path(file_path).name
        saved_files = save_outputs(transcript, segments, input_filename)
        
        # Calculate duration
        elapsed = time.time() - start_time
        
        # Final status
        detected_lang = info.language if hasattr(info, 'language') else "unknown"
        status_lines = [
            f"✅ Transcription complete!",
            f"",
            f"📊 Statistics:",
            f"  • Duration: {elapsed:.1f} seconds",
            f"  • Language: {detected_lang}",
            f"  • Segments: {len(segments)}",
            f"  • Words: ~{len(transcript.split())}",
            f"",
            f"💾 Files saved to:",
            f"  • {saved_files['txt']}",
            f"  • {saved_files['srt']}",
            f"  • {saved_files['vtt']}",
        ]
        
        return "\n".join(status_lines), transcript, srt_content, vtt_content
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"❌ Error: {str(e)}\n\nDetails:\n{error_details}", "", "", ""


# ============================================================================
# GRADIO UI
# ============================================================================

def create_ui() -> gr.Blocks:
    """Create the Gradio web interface."""
    global _hardware_info
    
    # Detect hardware on startup
    _hardware_info = detect_hardware()
    
    # Check FFmpeg status
    ffmpeg_available = check_ffmpeg_available()
    ffmpeg_status = "✅ FFmpeg found" if ffmpeg_available else "⚠️ FFmpeg not found (video support disabled)"
    
    # Build UI
    with gr.Blocks(
        title=f"{APP_NAME} v{APP_VERSION}",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="slate",
        ),
        css="""
        .gradio-container { max-width: 1200px !important; }
        .status-box { font-family: monospace; }
        """
    ) as app:
        
        # Header
        gr.Markdown(f"""
        # 🎙️ {APP_NAME} v{APP_VERSION}
        
        **Local, Private Speech-to-Text Transcription**
        
        Upload any audio or video file and get accurate transcriptions with timestamps.
        All processing happens locally on your machine - your files never leave your computer.
        
        ---
        
        **System Status:**
        - 🖥️ {_hardware_info['mode_label']}
        - {ffmpeg_status}
        - 📁 Outputs saved to: `{OUTPUTS_DIR.absolute()}`
        """)
        
        with gr.Row():
            # Left column - Input
            with gr.Column(scale=1):
                gr.Markdown("### 📁 Input")
                
                file_input = gr.File(
                    label="Upload Audio/Video File",
                    file_types=SUPPORTED_FORMATS,
                    type="filepath",
                )
                
                gr.Markdown(f"""
                **Supported formats:**
                - Audio: {', '.join(SUPPORTED_AUDIO)}
                - Video: {', '.join(SUPPORTED_VIDEO)} {'✅' if ffmpeg_available else '(requires FFmpeg)'}
                """)
                
                gr.Markdown("### ⚙️ Settings")
                
                # Model selection with info
                model_choices = [
                    (f"{size} ({info['size']}, {info['speed']}, {info['accuracy']})", size)
                    for size, info in MODEL_SIZES.items()
                ]
                
                model_dropdown = gr.Dropdown(
                    choices=model_choices,
                    value=_hardware_info["recommended_model"],
                    label="Model Size",
                    info=f"Recommended: {_hardware_info['recommended_model']} for your hardware"
                )
                
                language_dropdown = gr.Dropdown(
                    choices=[
                        ("Auto-detect", "auto"),
                        ("English", "en"),
                        ("Spanish", "es"),
                        ("French", "fr"),
                        ("German", "de"),
                        ("Italian", "it"),
                        ("Portuguese", "pt"),
                        ("Russian", "ru"),
                        ("Japanese", "ja"),
                        ("Korean", "ko"),
                        ("Chinese", "zh"),
                        ("Arabic", "ar"),
                        ("Hindi", "hi"),
                    ],
                    value="auto",
                    label="Language",
                    info="Auto-detect works well for most files"
                )
                
                translate_checkbox = gr.Checkbox(
                    label="Translate to English",
                    value=False,
                    info="Translate non-English speech to English"
                )
                
                transcribe_btn = gr.Button(
                    "🎯 Transcribe",
                    variant="primary",
                    size="lg",
                )
            
            # Right column - Output
            with gr.Column(scale=2):
                gr.Markdown("### 📄 Output")
                
                status_output = gr.Textbox(
                    label="Status",
                    lines=10,
                    interactive=False,
                    elem_classes=["status-box"],
                    placeholder="Status updates will appear here..."
                )
                
                with gr.Tabs():
                    with gr.Tab("📝 Transcript"):
                        transcript_output = gr.Textbox(
                            label="Plain Text Transcript",
                            lines=12,
                            show_copy_button=True,
                            placeholder="Transcription will appear here..."
                        )
                    
                    with gr.Tab("🎬 SRT Subtitles"):
                        srt_output = gr.Textbox(
                            label="SRT Format (for video editors)",
                            lines=12,
                            show_copy_button=True,
                            placeholder="SRT subtitles will appear here..."
                        )
                    
                    with gr.Tab("🌐 VTT Subtitles"):
                        vtt_output = gr.Textbox(
                            label="VTT Format (for web)",
                            lines=12,
                            show_copy_button=True,
                            placeholder="VTT subtitles will appear here..."
                        )
        
        # Footer
        gr.Markdown(f"""
        ---
        <div style="text-align: center; color: #666; font-size: 0.9em;">
            {APP_NAME} v{APP_VERSION} • Powered by <a href="https://github.com/SYSTRAN/faster-whisper">faster-whisper</a> • 
            Output files auto-saved to <code>./Outputs/</code>
        </div>
        """)
        
        # Connect button
        transcribe_btn.click(
            fn=transcribe,
            inputs=[file_input, model_dropdown, language_dropdown, translate_checkbox],
            outputs=[status_output, transcript_output, srt_output, vtt_output],
        )
    
    return app


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point."""
    print(f"\n{'='*60}")
    print(f"  {APP_NAME} v{APP_VERSION}")
    print(f"  Local, Private Speech-to-Text Transcription")
    print(f"{'='*60}\n")
    
    # Create necessary directories
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Detect and display hardware
    hw = detect_hardware()
    print(f"🔧 Hardware: {hw['mode_label']}")
    print(f"📁 App directory: {APP_DIR.absolute()}")
    print(f"📁 Models directory: {MODELS_DIR.absolute()}")
    print(f"💾 Outputs directory: {OUTPUTS_DIR.absolute()}")
    
    # Check FFmpeg
    ffmpeg_path, ffprobe_path = find_ffmpeg()
    if ffmpeg_path:
        print(f"🎬 FFmpeg: Available")
    else:
        print(f"⚠️  FFmpeg: Not found (video support disabled)")
        print(f"   To enable video support, place ffmpeg.exe and ffprobe.exe")
        print(f"   in the same folder as this application.")
    
    print(f"\n🌐 Starting web interface...\n")
    
    # Create and launch UI
    app = create_ui()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        inbrowser=True,
    )


if __name__ == "__main__":
    main()
