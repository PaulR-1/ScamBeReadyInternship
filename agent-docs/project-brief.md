# Project brief — Local Taglish Transcriber

## Goal

Transcribe the owner's personal voice memos and videos on their own laptop, with accurate handling of
**Taglish** (sentence-level and word-level code-switching between Tagalog and English).

## Scope (v1)

- Import local audio/video by file path; the app never copies or uploads the original media.
- Transcribe with Whisper (`faster-whisper`), producing timestamped segments.
- Edit segment text in the browser and persist the edits.
- Export TXT, SRT, and VTT.
- Run entirely on `127.0.0.1` with no cloud services.

## Non-goals (v1)

- Speaker diarization, translation, cross-transcript search, and batch queueing beyond a simple
  one-at-a-time worker. These were considered and deferred; see `decisions.md`.
- Multi-user access, authentication, hosting, or any remote deployment.
- Real-time/live microphone transcription.

## Definition of done

1. A 1–3 hour Taglish recording transcribes end to end without freezing the UI or exhausting memory.
2. Tagalog words stay in Tagalog and English words stay in English in the same segment.
3. Edits survive an app restart.
4. Exports have correct, monotonic timecodes.
5. No original media is copied and all temporary audio is deleted.
