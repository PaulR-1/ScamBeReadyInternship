# Decisions

Append-only. Supersede entries instead of deleting them.

---

## D-001 — Python-only stack, no frontend build (2026-09-21)

FastAPI + Jinja + vanilla JS. A React/Vite frontend would add Node.js, a build step, and a second
dependency tree to a single-user local tool. The UI is three pages.

**Tradeoff:** the editor stays deliberately simple. If it grows into a real waveform editor, revisit.

---

## D-002 — `large-v3` with `int8_float16` on CUDA, not `float16` (2026-09-21)

The target GPU has 4 GB of VRAM. `float16` `large-v3` needs roughly 4.7 GB and will not load;
`int8_float16` needs roughly 3.1 GB and fits. Quantising `large-v3` loses less Taglish accuracy than
dropping to `medium`, which is the other way to fit in 4 GB.

`app/core/hardware.py` picks the compute type from detected VRAM, so a different machine gets
`float16` automatically. CPU falls back to `int8` with 40 GB of RAM available.

**Tradeoff:** CPU fallback is roughly real-time or slower; a 3-hour file can take hours.

---

## D-003 — Reference media by path instead of uploading (2026-09-21)

The user asked to keep original media in place. Browser uploads of multi-gigabyte video would also be
slow and would duplicate the file. The import form takes a path, with a native file picker launched
as a short-lived subprocess because browsers do not expose full paths.

**Tradeoff:** moving or renaming the source file breaks playback and retry for that transcript.

---

## D-004 — Single worker thread, SQLite-backed queue (2026-09-21)

One job at a time protects the 4 GB VRAM budget. The queue lives in SQLite so a crash or restart does
not lose work; rows left in `running` at startup are marked `interrupted` and can be retried.
Celery/Redis would be infrastructure for a single-user local app.

**Tradeoff:** no parallelism. Batch import is possible later by enqueueing multiple rows.

---

## D-005 — Default decoding language is `tl`, not `auto` (2026-09-21)

See `taglish-notes.md` for the full reasoning. Short version: `auto` can lock onto English and mangle
or drop the Tagalog half of a recording, which is unrecoverable by editing. `tl` keeps both halves
and its failure mode is cosmetic.

**Tradeoff:** occasional Filipino spelling of clearly English phrases. Revisit after evaluating real
samples.

---

## D-007 — Register the NVIDIA wheel DLL directories ourselves (2026-09-21)

`nvidia-cublas-cu12` and `nvidia-cudnn-cu12` install their DLLs under
`site-packages/nvidia/<lib>/bin`, which Windows does not search. CTranslate2 does not add these
itself (PyTorch does, which is why this is rarely reported). Symptom: `get_cuda_device_count()`
returns 1, the model loads, and decoding then dies with
`Library cublas64_12.dll is not found or cannot be loaded`.

[`app/core/cuda.py`](../transcript-app/app/core/cuda.py) calls `os.add_dll_directory` for those
paths and verifies both libraries actually load before the app claims CUDA is usable.

---

## D-008 — Fallback must cover lazy decoding, not just model loading (2026-09-21)

CTranslate2 returns a generator, so GPU failures surface while iterating segments, after
`transcribe()` has already returned successfully. The first implementation wrapped only the call and
missed every real GPU failure. The worker now retries on CPU if the GPU attempt fails **and nothing
has been persisted yet**; once text exists, the error is reported instead, so a mid-run failure
never silently discards work and restarts a three-hour job.

---

## D-009 — Retry applies current settings (2026-09-21)

Retrying reloads model, language, and prompt from Settings rather than replaying the original job.
Retry is almost always used after a failure or a bad result, which is exactly when the user has just
changed something.

**Tradeoff:** retry is not a reproducible re-run. The engine actually used is recorded per
transcript, so results stay traceable.

---

## D-006 — Deferred from v1 (2026-09-21)

Diarization (`pyannote`, needs a gated model download and a licence acceptance), translation,
cross-transcript search, and batch queueing. All were considered; none are needed to answer "what was
said in this memo". The schema does not block adding them later.
