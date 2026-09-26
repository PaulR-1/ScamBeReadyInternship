"""Makes the pip-installed NVIDIA runtime libraries visible to CTranslate2.

The nvidia-cublas-cu12 / nvidia-cudnn-cu12 wheels drop their DLLs in
`site-packages/nvidia/<lib>/bin`, which Windows does not search. Without this, CTranslate2 reports a
usable CUDA device and then fails mid-decode with "cublas64_12.dll is not found".
"""

from __future__ import annotations

import ctypes
import logging
import os
import site
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

_prepared: list[Path] | None = None

_CUBLAS = "cublas64_12.dll" if sys.platform == "win32" else "libcublas.so.12"
_CUDNN_CANDIDATES = (
    ("cudnn64_9.dll", "cudnn64_8.dll")
    if sys.platform == "win32"
    else ("libcudnn.so.9", "libcudnn.so.8")
)


def _site_dirs() -> list[Path]:
    dirs = [Path(p) for p in site.getsitepackages()]
    try:
        dirs.append(Path(site.getusersitepackages()))
    except AttributeError:
        pass
    dirs.append(Path(sys.prefix) / "Lib" / "site-packages")
    return dirs


def prepare() -> list[Path]:
    """Register the wheel-provided CUDA library directories. Safe to call repeatedly."""
    global _prepared
    if _prepared is not None:
        return _prepared

    added: list[Path] = []
    if sys.platform == "win32":
        seen: set[Path] = set()
        for base in _site_dirs():
            nvidia = base / "nvidia"
            if not nvidia.is_dir():
                continue
            for bin_dir in nvidia.glob("*/bin"):
                resolved = bin_dir.resolve()
                if resolved in seen or not any(resolved.glob("*.dll")):
                    continue
                seen.add(resolved)
                try:
                    os.add_dll_directory(str(resolved))
                    added.append(resolved)
                except OSError as exc:
                    logger.info("Could not register CUDA library directory %s: %s", resolved, exc)
        if added:
            logger.info("Registered %d CUDA library director(ies)", len(added))

    _prepared = added
    return added


def libraries_ready() -> bool:
    """True when cuBLAS and cuDNN can actually be loaded, not just when a GPU exists."""
    prepare()
    try:
        ctypes.CDLL(_CUBLAS)
    except OSError:
        return False
    for name in _CUDNN_CANDIDATES:
        try:
            ctypes.CDLL(name)
            return True
        except OSError:
            continue
    return False
