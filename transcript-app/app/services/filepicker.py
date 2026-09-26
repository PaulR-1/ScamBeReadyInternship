"""Native file chooser.

Browsers never expose a real filesystem path, and this app deliberately references media in place
instead of uploading it. Since the server and the browser are the same machine, we open the OS
picker ourselves. It runs in a short-lived subprocess because Tk misbehaves off the main thread.
"""

from __future__ import annotations

import logging
import subprocess
import sys

from app.core.config import MEDIA_EXTENSIONS

logger = logging.getLogger(__name__)

_PICKER_SCRIPT = """
import sys, tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)
path = filedialog.askopenfilename(
    title="Choose a voice memo or video",
    filetypes=[("Media files", sys.argv[1]), ("All files", "*.*")],
)
root.destroy()
sys.stdout.write(path or "")
"""


def pick_file(timeout: float = 300.0) -> str | None:
    patterns = " ".join(f"*{ext}" for ext in sorted(MEDIA_EXTENSIONS))
    try:
        result = subprocess.run(
            [sys.executable, "-c", _PICKER_SCRIPT, patterns],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        logger.info("Native file picker unavailable: %s", exc)
        return None
    if result.returncode != 0:
        logger.info("Native file picker exited with %s: %s", result.returncode, result.stderr[:200])
        return None
    return result.stdout.strip() or None
