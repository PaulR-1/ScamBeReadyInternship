# Status

Newest entry first.

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
