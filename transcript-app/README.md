# Taglish Transcriber

Local-only transcription for voice memos and videos, tuned for **Taglish** (mixed Tagalog and
English). Runs entirely on your machine: no accounts, no uploads, no cloud API.

Your original recordings are never copied or moved. The app stores only the transcript.

## Requirements

- Windows with Python 3.11 or newer (tested on 3.13, 64-bit)
- FFmpeg
- Optional: an NVIDIA GPU. Without one, everything still works on CPU, just slower.

## Setup

```powershell
winget install Gyan.FFmpeg     # then close and reopen your terminal

cd transcript-app
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Optional, for NVIDIA GPUs:
pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
```

If PowerShell refuses to run the activation script:
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

## Run

```powershell
python -m app
```

This opens `http://127.0.0.1:8756`. The server listens on loopback only.

The first transcription downloads the Whisper model (about 3 GB for `large-v3`). That happens once;
after it, the app works offline.

## Using it

1. On the Library page, paste the full path to a recording, or click **Browse** to pick one.
2. Click **Transcribe**. Progress updates live, and you can leave the page or cancel at any time.
3. Open the transcript to play the audio, click a timestamp to jump there, and click any line to
   correct it. Edits save when you click away or press Enter, and survive a restart. Corrected lines
   are marked, and the model's original wording is kept so you can revert.
4. Export **TXT**, **TXT without timestamps**, **SRT**, or **VTT**.

## Taglish quality

The **Settings** page controls this. Defaults are chosen for Taglish:

- **Model `large-v3`** — clearly better at Tagalog than the smaller models.
- **Decoding language `tl`** — keeps Tagalog words in Tagalog while English passes through as
  English. Auto-detect can lock onto English and mangle the Tagalog half, which editing cannot
  recover. Switch to `auto` or `en` if your recordings are mostly English.
- **Names and terms** — add people, companies, and acronyms here. This is the single most effective
  way to fix repeatedly misspelled proper nouns.
- **Priming prompt** — a Taglish example sentence that biases the model toward mixed-language output.

`agent-docs/taglish-notes.md` in the repository root explains the tradeoffs and how to evaluate a
change properly.

## Hardware

Settings shows what was detected and what will actually be used. The app picks the best precision
that fits your VRAM. On a 4 GB GPU it runs `large-v3` with 8-bit weights, because full precision
needs roughly 4.7 GB. If the GPU fails before producing any text, the job automatically restarts on
CPU rather than failing.

CPU transcription with `large-v3` is roughly real-time or slower, so a 3-hour recording can take
hours. Leave it running; progress is saved continuously and a restart will not lose completed work.

## Configuration

Copy `.env.example` to `.env` to change the port, storage locations, FFmpeg paths, or the maximum
accepted recording length (default 200 minutes).

Data lives in `%LOCALAPPDATA%\TaglishTranscriber\`: the SQLite database, the model cache, and
`app.log`. Delete that folder to reset the app; your recordings are untouched.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Tests use a fake transcription engine and never download a model or touch the network.

## Limits

- One transcription at a time, by design, so a long job cannot exhaust VRAM.
- No speaker labels, translation, or search yet.
- If you move or rename a source file, its transcript survives but playback and re-running do not.
