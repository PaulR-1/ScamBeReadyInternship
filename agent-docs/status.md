# Status

Newest entry first.

---

## 2026-10-02 — Desktop window shell

`python -m app` opens a WebView2 window on the existing pages. `python -m app --server` serves http://127.0.0.1:8756 with no window and no system browser. A taken port fails at bind, so that launch does not start a second lifespan.

Verified from `transcript-app` with `.venv\Scripts\python.exe -m pytest tests` (50 passed, plus the existing Starlette deprecation warning). A real `UvicornSession` on a free loopback port returned the library page with HTTP 200, then shutdown finished and the port could be bound again. `pywebview` 6.2.1 is installed in the project virtualenv. `python -m app` on port 8761 logged application startup. The window title was not confirmed, and WebView2 audio seeking has not been tried.

---

## 2026-10-02 — Globe added to partnership outreach file

Appended Globe Telecom to `data/partnership_outreach.json`. Published inboxes: `gtcorpcomm@globe.com.ph` (Yoly Crisanto / newsroom), `privacy@globe.com.ph` (DPO / OSAEC reports), plus named officers without personal emails (Anton Bonifacio, Derick Adil). Current Digital Thumbprint and #StopSPAM paths are web forms. IR, enterprise support, and procurement recorded as non-partnership. No guessed personal `@globe.com.ph` addresses.

---

## 2026-10-02 — DICT + GCash partnership outreach file

Wrote `data/partnership_outreach.json`. DICT names/emails are the BetterGov industry, consumer-protection, cybersecurity, literacy, and secretary rows plus CERT-PH `cert-ph@dict.gov.ph`. GCash uses official Partner Solutions, Mynt corporate communications, and a 2022 GCash press-release public-sector inbox. No guessed personal GCash emails.

---


## 2026-09-28 — Architecture guide written

Added `transcript-app/docs/Taglish-Transcriber-Architecture.pdf` (source HTML beside it). It explains the local transcriber layer by layer for study. No application behavior changed.

Added `transcript-app/docs/Taglish-Transcriber-Explained-From-Zero.pdf`, the same system written for a reader who does not write code. No application behavior changed.

Added `transcript-app/docs/flowcharts/`: three architecture charts (placeholders, Whisper named, full path with a note per block) and `settings.html`. No application behavior changed.

Added a spoken summary at the top of `settings.html`, and `interview-answers.html` with 30 interview answers. Answer 4 now compares FastAPI and Uvicorn with Flask, Django, and Gunicorn. Answer 31 explains the full stack. No application behavior changed.

---

## 2026-09-26 — Transcript app published

Public repo, transcript app only: https://github.com/PaulR-1/taglish-transcriber
The scraper stays in this repository.

---

## 2026-09-26 — Transcript UI restyled as a cutting mat

Installed `frontend-design` and `redesign-existing-projects`. The library opens with a torn-letter
Taglish title on a green gridded mat; working surfaces stay paper sheets so the editor remains
readable. No network fonts. Behavior is unchanged.

---

## 2026-09-25 — DICT officials file added

Wrote `data/dict.json` from BetterGov’s DICT directory plus public news/hiring pages. Personal emails were recorded only when printed on those pages. Jaemie D. Ruiz-Chua and Atty. Carlo Paolo P. Murcia still have no published personal `@dict.gov.ph` inbox.

---

## 2026-09-21 — v1 built and verified end to end

**State:** working. `transcript-app/` imports, transcribes, edits, and exports.

### Done

- Shared docs (`agent-docs/`, root `AGENTS.md`).
- Full app: SQLite store, FFmpeg media handling, faster-whisper engine, single background worker,
  TXT/SRT/VTT export, library / transcript editor / settings pages.
- 46 tests passing, none of which download a model or touch the network.

### Verified on the target machine

- FFmpeg 9.0.1 installed via winget; detected by the app.
- CUDA works after `pip install nvidia-cublas-cu12 nvidia-cudnn-cu12` plus the DLL directory
  registration in `app/core/cuda.py` (see D-007).
- **`large-v3` runs on the 4 GB RTX 3050 at `int8_float16`.** This was the riskiest assumption in
  the design and it holds.
- End-to-end on a 9-second synthesised Taglish clip, GPU path, ~30 s including model load.

### Taglish result (synthetic clip, `large-v3`, language `tl`)

- Spoken: "Kumusta, this is a test recording. Nag meeting kami kanina, and the client said okay daw
  sa proposal."
- Output: "Kumusta, this is a test recording, nag-meeting kami kanina, and the client said ok da sa
  proposal."

Tagalog stayed Tagalog and English stayed English within one sentence, which is the behaviour the
whole design targets. Only "okay daw" → "ok da" was wrong. Note this was text-to-speech with an
English voice, so it is a smoke test, **not** evidence about real accented Taglish speech.

### Bugs found and fixed during verification

1. CUDA reported available while its DLLs were unloadable (D-007).
2. CPU fallback did not cover lazy decoding failures, so it never triggered in practice (D-008).
3. `[hidden]` was overridden by the button CSS, so Cancel/Retry showed on finished transcripts.
4. The FFmpeg warning banner appeared on pages that did not pass `ffmpeg_available`.

### Open / next

- **Needs real samples.** Run 2–3 genuine Taglish recordings and count errors using the method in
  `taglish-notes.md`. Only then decide whether `tl` stays the default over `auto`.
- Not yet exercised: a multi-hour recording (progress pacing, memory, cancel mid-run) and a video
  file rather than audio.
- Populate the glossary in Settings with the user's real names and acronyms.
- `transcript-app/samples/taglish_test.wav` is a throwaway test clip; `samples/` is gitignored.
