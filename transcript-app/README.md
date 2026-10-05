# Taglish Transcriber

## What it is

Taglish Transcriber is a **local-only** web app for turning voice memos and videos into text. It is aimed at **Taglish**—speech that mixes Tagalog and English in the same recording.

The app runs on your own computer. It does **not** upload your files to a cloud service. You point it at a file path on disk; it keeps the path and saves the transcript in a local database. Your original audio or video is never copied into the app folder.

I built this for my **Software Engineering** class and used **Cursor** to help design and implement it.

## Technical elements

| Layer | Technology |
| --- | --- |
| **Speech model** | [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (OpenAI Whisper `large-v3` by default) |
| **Backend** | Python 3.11+, [FastAPI](https://fastapi.tiangolo.com/), Uvicorn |
| **Frontend** | Jinja HTML templates, vanilla CSS and JavaScript (no separate build step) |
| **Storage** | SQLite (transcripts, segments, settings under `%LOCALAPPDATA%\TaglishTranscriber\`) |
| **Media** | FFmpeg / ffprobe for format checks and audio extraction |
| **Compute** | CPU or NVIDIA GPU (CUDA via CTranslate2); auto-picks precision based on VRAM |
| **Exports** | TXT, SRT, and VTT with editable timestamped segments in the browser |

Other behavior worth noting:

- One transcription job at a time (background worker).
- Optional glossary and Taglish priming prompt in Settings.
- Model weights download once (~3 GB for `large-v3`), then offline use is possible.

## Download and run on your machine

### Requirements

- **Windows** (primary target; paths and setup below are for Windows)
- **Python 3.11 or newer** (64-bit)
- **FFmpeg** on your PATH
- **Git** (to clone the repo)
- **Optional:** NVIDIA GPU and CUDA runtime packages for faster transcription

### 1. Get the code

```powershell
git clone https://github.com/PaulR-1/taglish-transcriber.git
cd taglish-transcriber
```

### 2. Install FFmpeg (if needed)

```powershell
winget install Gyan.FFmpeg
```

Close and reopen your terminal so `ffmpeg` is on your PATH.

### 3. Python environment and dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks the activation script:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

**Optional (NVIDIA GPU):**

```powershell
pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
```

Skip this if you only want CPU transcription (slower but works).

### 4. Start the app

Open the app window:

```powershell
python -m app
```

For a terminal, serve http://127.0.0.1:8756 with no window:

```powershell
python -m app --server
```

The host stays 127.0.0.1.

Copy `.env.example` to `.env` if you want to change the port, max recording length, or FFmpeg paths.

### 5. Use it

1. On **Library**, paste the full path to a recording or click **Browse**.
2. Click **Transcribe** and wait for progress to finish.
3. Open the transcript to play audio, edit lines, and export TXT / SRT / VTT.
4. Adjust model, language, and glossary under **Settings** (applies to the next job; use **Retry** to re-run with new settings).

The first run downloads the Whisper model into your user data folder. After that, transcription can run without internet.

### Tests (optional)

```powershell
pip install -r requirements-dev.txt
pytest
```
