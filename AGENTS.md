# AGENTS.md

Entry point for any AI agent or new contributor working in this repository.

**Read [`agent-docs/README.md`](agent-docs/README.md) first.** It is the index for all shared
instructions, architecture notes, decisions, and status logs.

## Repository layout

| Path | What it is |
| --- | --- |
| `agent-docs/` | Shared knowledge base for agents and humans. Read before changing code. |
| `transcript-app/` | Local-only Taglish transcription app (FastAPI + faster-whisper). |
| `scraper/`, `config/`, `data/` | Unrelated Be Scam Ready university partner scraper. |

## Ground rules

1. Read `agent-docs/` before planning work, and update `agent-docs/status.md` after finishing it.
2. Do not mix the two projects. `transcript-app/` is self-contained and must not import from `scraper/`.
3. Never commit media files, transcripts, model weights, or `.env` files.
4. `transcript-app/` must stay offline-capable: no runtime network calls except the one-time model download.
