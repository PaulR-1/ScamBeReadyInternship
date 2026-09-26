"""Environment-backed configuration and the user-editable settings schema."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from app.core import paths

MODEL_CHOICES = {
    "large-v3": "large-v3 - best Taglish accuracy, slowest",
    "distil-large-v3": "distil-large-v3 - much faster, English-leaning",
    "medium": "medium - lighter, noticeably weaker on Tagalog",
    "small": "small - fast draft quality",
}

LANGUAGE_CHOICES = {
    "tl": "Tagalog (recommended for Taglish)",
    "auto": "Auto-detect per segment",
    "en": "English",
}

DEVICE_CHOICES = {"auto": "Auto-detect", "cuda": "GPU (CUDA)", "cpu": "CPU"}

# Biases the decoder toward mixed-language output instead of collapsing to one language.
DEFAULT_INITIAL_PROMPT = (
    "Ito ay isang Taglish na usapan. Nagha-halo ang Tagalog at English sa iisang pangungusap, "
    "like this, kaya keep the English words in English at ang Tagalog sa Tagalog."
)

DEFAULT_SETTINGS: dict[str, str] = {
    "model": "large-v3",
    "language": "tl",
    "device": "auto",
    "initial_prompt": DEFAULT_INITIAL_PROMPT,
    "glossary": "",
    "beam_size": "5",
    "vad_filter": "1",
    "word_timestamps": "0",
}

AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".wma", ".amr", ".3gp"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".mpg", ".mpeg", ".wmv"}
MEDIA_EXTENSIONS = AUDIO_EXTENSIONS | VIDEO_EXTENSIONS


def load_dotenv(path: Path | None = None) -> None:
    """Populate os.environ from a .env file without overriding real environment variables."""
    env_file = path or paths.PROJECT_ROOT / ".env"
    if not env_file.is_file():
        return
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True)
class AppConfig:
    host: str
    port: int
    max_duration_seconds: float
    ffmpeg_path: str | None
    ffprobe_path: str | None
    device_override: str | None

    @classmethod
    def from_env(cls) -> "AppConfig":
        minutes = float(os.environ.get("TT_MAX_DURATION_MINUTES", "200"))
        device = os.environ.get("TT_DEVICE")
        return cls(
            host=os.environ.get("TT_HOST", "127.0.0.1"),
            port=int(os.environ.get("TT_PORT", "8756")),
            max_duration_seconds=minutes * 60,
            ffmpeg_path=os.environ.get("TT_FFMPEG_PATH"),
            ffprobe_path=os.environ.get("TT_FFPROBE_PATH"),
            device_override=device if device in DEVICE_CHOICES and device != "auto" else None,
        )


def get_config() -> AppConfig:
    return AppConfig.from_env()
