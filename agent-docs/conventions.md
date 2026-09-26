# Conventions

## Code

- Python 3.11+ syntax, type hints on public functions, `pathlib.Path` over string paths.
- Standard library first. Add a dependency only when it removes real complexity, and record it in
  `decisions.md`.
- No frontend build step. Templates are Jinja; scripts are plain ES modules in `app/web/static/`.
- All SQL lives in `app/db/store.py`. Routes and services call functions, never raw SQL.
- Services must not import from `app/routes/`. Dependencies point inward.
- Comments explain constraints the code cannot show. Do not narrate what the next line does.

## Errors

- User-facing failures are stored on the transcript row as a short, actionable message
  ("FFmpeg not found on PATH"), not a raw traceback. Full tracebacks go to the log file.
- Never swallow an exception silently. If recovery is intentional, log why.

## Paths and privacy

- Treat every incoming path as untrusted: resolve it, confirm it exists, confirm it is a file.
- Never write to the directory containing the user's media.
- Never log the full contents of a transcript.

## Git

- Do not commit: `*.wav`, `*.mp3`, `*.mp4`, `*.m4a`, `.env`, `.venv/`, model weights, `*.sqlite3`.
- `transcript-app/.gitignore` covers these; extend it rather than relying on memory.

## Testing

- `pytest` in `transcript-app/tests/`. Tests must not download models or hit the network.
- Transcription is exercised through a fake engine; real-model checks are manual and documented in
  `status.md`.
