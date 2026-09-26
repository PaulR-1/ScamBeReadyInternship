"""Resolves the per-user directories the app writes to."""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_DIR_NAME = "TaglishTranscriber"
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = PACKAGE_ROOT.parent


def _default_data_dir() -> Path:
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local"
        return Path(base) / APP_DIR_NAME
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_DIR_NAME
    base = os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share"
    return Path(base) / "taglish-transcriber"


def data_dir() -> Path:
    override = os.environ.get("TT_DATA_DIR")
    return Path(override).expanduser() if override else _default_data_dir()


def models_dir() -> Path:
    override = os.environ.get("TT_MODELS_DIR")
    return Path(override).expanduser() if override else data_dir() / "models"


def database_path() -> Path:
    return data_dir() / "transcripts.sqlite3"


def log_path() -> Path:
    return data_dir() / "app.log"


def web_dir() -> Path:
    return PACKAGE_ROOT / "web"


def ensure_directories() -> None:
    for path in (data_dir(), models_dir()):
        path.mkdir(parents=True, exist_ok=True)
