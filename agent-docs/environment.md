# Environment

## Target machine (detected 2026-09-21)

| Item | Value |
| --- | --- |
| OS | Windows 10/11, 64-bit |
| Python | 3.13.4, 64-bit, `C:\Users\paulr\AppData\Local\Programs\Python\Python313\python.exe` |
| System RAM | ~40 GB |
| GPU | NVIDIA GeForce RTX 3050 Laptop, **4 GB VRAM** |
| FFmpeg | Not installed at scaffold time — required |

The 4 GB VRAM ceiling is the single most important constraint. `large-v3` weights are roughly
3.1 GB in `int8_float16` and roughly 4.7 GB in `float16`, so **float16 does not fit** alongside the
display driver. See `decisions.md` D-002.

## Setup

```powershell
winget install Gyan.FFmpeg          # then restart the terminal so PATH updates
cd transcript-app
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app                        # serves http://127.0.0.1:8756
```

If PowerShell blocks the activation script:
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

## GPU acceleration

`faster-whisper` uses CTranslate2, which needs the NVIDIA CUDA 12 runtime libraries. Install them into
the virtual environment:

```powershell
pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
```

If CUDA initialisation fails at runtime the app logs the reason and falls back to CPU automatically.
CPU transcription with `large-v3` is roughly real-time or slower, so a 3-hour file can take hours.

## Where data lives

- App data (SQLite database, logs, settings): `%LOCALAPPDATA%\TaglishTranscriber\`
- Model weights cache: `%LOCALAPPDATA%\TaglishTranscriber\models\` (override with `TT_MODELS_DIR`)
- Temporary normalised audio: system temp, deleted on success *and* on failure.

Nothing is written next to the user's original media.
