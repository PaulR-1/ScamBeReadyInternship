"""FFmpeg discovery, media validation, and normalisation to 16 kHz mono WAV."""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from app.core.config import AUDIO_EXTENSIONS, MEDIA_EXTENSIONS, VIDEO_EXTENSIONS, get_config

logger = logging.getLogger(__name__)

# Whisper is trained on 16 kHz mono audio; anything else is resampled internally anyway.
TARGET_SAMPLE_RATE = 16000

_WINDOWS_HINTS = (
    r"C:\ffmpeg\bin",
    r"C:\Program Files\ffmpeg\bin",
)


class MediaError(Exception):
    """Raised with a message that is safe and useful to show the user."""


@dataclass(frozen=True)
class MediaInfo:
    path: Path
    size_bytes: int
    duration: float
    has_audio: bool
    has_video: bool
    container: str


def _no_window_kwargs() -> dict:
    if sys.platform == "win32":
        return {"creationflags": subprocess.CREATE_NO_WINDOW}
    return {}


def _find_tool(name: str, override: str | None) -> str:
    if override:
        if Path(override).is_file():
            return override
        raise MediaError(f"{name} was configured as {override} but that file does not exist.")
    found = shutil.which(name)
    if found:
        return found
    for hint in _WINDOWS_HINTS:
        candidate = Path(hint) / f"{name}.exe"
        if candidate.is_file():
            return str(candidate)
    raise MediaError(
        f"{name} was not found. Install FFmpeg (winget install Gyan.FFmpeg), reopen your "
        f"terminal, or set TT_{name.upper()}_PATH in .env."
    )


def ffmpeg_path() -> str:
    return _find_tool("ffmpeg", get_config().ffmpeg_path)


def ffprobe_path() -> str:
    return _find_tool("ffprobe", get_config().ffprobe_path)


def ffmpeg_available() -> bool:
    try:
        ffmpeg_path()
        ffprobe_path()
        return True
    except MediaError:
        return False


def resolve_source(raw_path: str) -> Path:
    """Validate a user-supplied path before anything else touches it."""
    cleaned = (raw_path or "").strip().strip('"').strip("'")
    if not cleaned:
        raise MediaError("Enter the full path to an audio or video file.")
    path = Path(os.path.expandvars(cleaned)).expanduser()
    try:
        path = path.resolve(strict=True)
    except OSError as exc:
        raise MediaError(f"Could not open that path: {exc.strerror or exc}") from exc
    if not path.is_file():
        raise MediaError(f"{path} is not a file.")
    if path.suffix.lower() not in MEDIA_EXTENSIONS:
        supported = ", ".join(sorted(ext.lstrip(".") for ext in MEDIA_EXTENSIONS))
        raise MediaError(f"{path.suffix or 'That file'} is not a supported format. Supported: {supported}.")
    return path


def probe(path: Path) -> MediaInfo:
    cmd = [
        ffprobe_path(),
        "-v", "error",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        str(path),
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120, check=True, **_no_window_kwargs()
        )
    except subprocess.CalledProcessError as exc:
        raise MediaError(f"FFmpeg could not read that file: {(exc.stderr or '').strip()[:300]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise MediaError("Reading the media file timed out.") from exc

    data = json.loads(result.stdout or "{}")
    streams = data.get("streams", [])
    fmt = data.get("format", {})

    has_audio = any(s.get("codec_type") == "audio" for s in streams)
    has_video = any(s.get("codec_type") == "video" for s in streams)
    if not has_audio:
        raise MediaError("That file has no audio track.")

    duration = 0.0
    for candidate in [fmt.get("duration")] + [s.get("duration") for s in streams]:
        try:
            duration = max(duration, float(candidate))
        except (TypeError, ValueError):
            continue

    max_seconds = get_config().max_duration_seconds
    if duration > max_seconds:
        raise MediaError(
            f"That recording is {duration / 3600:.1f} hours long, above the "
            f"{max_seconds / 3600:.1f} hour limit. Raise TT_MAX_DURATION_MINUTES to allow it."
        )

    return MediaInfo(
        path=path,
        size_bytes=path.stat().st_size,
        duration=duration,
        has_audio=has_audio,
        has_video=has_video,
        container=fmt.get("format_name", path.suffix.lstrip(".")),
    )


def extract_audio(path: Path) -> Path:
    """Decode any supported media to a temporary 16 kHz mono WAV. Caller must delete it."""
    handle, temp_name = tempfile.mkstemp(prefix="taglish_", suffix=".wav")
    os.close(handle)
    target = Path(temp_name)
    cmd = [
        ffmpeg_path(),
        "-nostdin",
        "-y",
        "-i", str(path),
        "-vn",
        "-map", "0:a:0",
        "-ac", "1",
        "-ar", str(TARGET_SAMPLE_RATE),
        "-c:a", "pcm_s16le",
        str(target),
    ]
    try:
        subprocess.run(
            cmd, capture_output=True, text=True, check=True, **_no_window_kwargs()
        )
    except subprocess.CalledProcessError as exc:
        cleanup(target)
        raise MediaError(
            f"FFmpeg failed to extract audio: {(exc.stderr or '').strip()[-300:]}"
        ) from exc
    except BaseException:
        cleanup(target)
        raise
    if not target.is_file() or target.stat().st_size == 0:
        cleanup(target)
        raise MediaError("FFmpeg produced an empty audio file.")
    return target


def cleanup(path: Path | None) -> None:
    if path is None:
        return
    try:
        path.unlink(missing_ok=True)
    except OSError as exc:
        logger.warning("Could not delete temporary audio %s: %s", path, exc)


def guess_media_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in VIDEO_EXTENSIONS:
        return "video"
    if suffix in AUDIO_EXTENSIONS:
        return "audio"
    return "audio"
