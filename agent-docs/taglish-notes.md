# Taglish transcription notes

Taglish mixes Tagalog and English inside a single sentence. Whisper has no "Taglish" language, so the
behaviour depends heavily on which language token it decodes with.

## What each language setting does

| Setting | Behaviour | Failure mode |
| --- | --- | --- |
| `tl` (default) | Decodes in Tagalog. Keeps Tagalog words in Tagalog and usually passes English words through as English. | Occasionally renders clear English phrases with Filipino spelling. |
| `en` | Decodes in English. Clean English, but Tagalog gets mangled or silently dropped. | Loses the Tagalog half of the recording. |
| `auto` | Detects per window when `multilingual=True`. | Can flip language mid-recording and produce inconsistent orthography; on English-heavy openings it locks onto English and then mangles Tagalog. |

**Default is `tl`** because losing Tagalog is worse than occasional Filipino spelling of English
words, and the failure is easier to fix by hand. This is a tunable setting, not a hard rule — if
evaluation on real samples shows `auto` wins, change the default and record it in `decisions.md`.

## Decoding options that matter

- `condition_on_previous_text=False` — the biggest win. With it enabled, Whisper loops and
  hallucinates on silence, and a bad Taglish segment poisons everything after it.
- `vad_filter=True` — trims silence so long memos do not generate filler text. Keep
  `min_silence_duration_ms` reasonably high (500 ms) so natural Tagalog pauses do not split words.
- `temperature` fallback ladder (`0.0 → 1.0`) with `compression_ratio_threshold=2.4` — catches the
  repetition loops that code-switching triggers.
- `initial_prompt` — the strongest lever available. A short Taglish sentence plus the user's proper
  nouns biases the decoder toward mixed-language output. The default prompt lives in
  `app/services/transcriber.py`; the user's glossary is appended to it from settings.

## Evaluating a change

Do not tune by vibes. Take a 2–3 minute clip, hand-correct a reference transcript once, then count:

1. Tagalog words wrongly rendered as English (or dropped).
2. English words wrongly rendered with Filipino spelling.
3. Proper nouns missed.
4. Hallucinated or repeated spans.

Change one option at a time and keep the numbers in `status.md`.

## Known limits

- Whisper's Tagalog training data is comparatively small, so expect proper nouns, Filipino slang, and
  regional accents to need manual correction. The editor exists for exactly this reason.
- `large-v3` is noticeably better at Taglish than `medium`. On this 4 GB GPU the tradeoff is quantised
  weights rather than a smaller model — quantisation costs less accuracy than dropping model size.
