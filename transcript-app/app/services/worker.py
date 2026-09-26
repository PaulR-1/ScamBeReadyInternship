"""Single background worker that drains the SQLite-backed transcription queue."""

from __future__ import annotations

import logging
import threading
import time
from pathlib import Path
from typing import Callable

from app.core import hardware
from app.core.config import DEFAULT_SETTINGS
from app.db import store
from app.services import media, transcriber
from app.services.transcriber import TranscriptionError, TranscriptionOptions

logger = logging.getLogger(__name__)

# Persisting in batches keeps long files responsive without hammering SQLite per segment.
_FLUSH_EVERY_SEGMENTS = 10
_FLUSH_EVERY_SECONDS = 3.0
_IDLE_POLL_SECONDS = 2.0


class Cancelled(Exception):
    pass


class TranscriptionWorker:
    def __init__(self, transcribe_fn: Callable = transcriber.transcribe) -> None:
        self._transcribe = transcribe_fn
        self._thread: threading.Thread | None = None
        self._wake = threading.Event()
        self._stopping = threading.Event()
        self.current_id: int | None = None

    # --- lifecycle ---

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stopping.clear()
        self._thread = threading.Thread(target=self._loop, name="transcription-worker", daemon=True)
        self._thread.start()

    def stop(self, timeout: float = 5.0) -> None:
        self._stopping.set()
        self._wake.set()
        if self._thread:
            self._thread.join(timeout=timeout)
        transcriber.unload()

    def notify(self) -> None:
        self._wake.set()

    def is_busy(self) -> bool:
        return self.current_id is not None

    # --- main loop ---

    def _loop(self) -> None:
        store.configure()
        while not self._stopping.is_set():
            try:
                row = store.claim_next_queued()
            except Exception:
                logger.exception("Could not read the job queue")
                row = None

            if row is None:
                self._wake.wait(_IDLE_POLL_SECONDS)
                self._wake.clear()
                continue

            transcript_id = int(row["id"])
            self.current_id = transcript_id
            try:
                self._process(row)
            except Exception:
                logger.exception("Unhandled failure while transcribing %s", transcript_id)
                store.finish_transcript(
                    transcript_id, "failed", "Something went wrong. See app.log for details."
                )
            finally:
                self.current_id = None

    # --- one job ---

    def _process(self, row) -> None:
        transcript_id = int(row["id"])
        audio_path: Path | None = None
        try:
            self._check_cancelled(transcript_id)
            source = self._resolve_source(row["source_path"])
            info = media.probe(source)
            store.set_duration(transcript_id, info.duration)

            options = self._build_options(row)
            store.set_engine_info(transcript_id, options.device, options.compute_type)

            self._check_cancelled(transcript_id)
            audio_path = media.extract_audio(source)

            self._check_cancelled(transcript_id)
            store.clear_segments(transcript_id)
            self._run_engine(transcript_id, audio_path, options, info.duration)

            store.finish_transcript(transcript_id, "completed")
            logger.info("Transcript %s completed", transcript_id)
        except Cancelled:
            store.finish_transcript(transcript_id, "canceled", "Canceled.")
            logger.info("Transcript %s canceled", transcript_id)
        except (media.MediaError, TranscriptionError) as exc:
            store.finish_transcript(transcript_id, "failed", str(exc))
            logger.warning("Transcript %s failed: %s", transcript_id, exc)
        finally:
            media.cleanup(audio_path)

    def _run_engine(
        self,
        transcript_id: int,
        audio_path: Path,
        options: TranscriptionOptions,
        duration: float,
    ) -> None:
        """Run the engine, falling back to CPU if the GPU fails before producing any text."""
        try:
            self._attempt(transcript_id, audio_path, options, duration)
            return
        except TranscriptionError as exc:
            fallback = self._cpu_fallback(options)
            if fallback is None or store.get_segments(transcript_id):
                raise
            logger.warning("GPU attempt failed (%s); retrying transcript %s on CPU", exc, transcript_id)

        store.clear_segments(transcript_id)
        store.set_engine_info(transcript_id, fallback.device, fallback.compute_type)
        self._attempt(transcript_id, audio_path, fallback, duration)

    def _attempt(
        self,
        transcript_id: int,
        audio_path: Path,
        options: TranscriptionOptions,
        duration: float,
    ) -> None:
        meta, segments = self._transcribe(audio_path, options)

        store.set_detected_language(
            transcript_id, meta.get("language"), meta.get("language_probability")
        )
        total = float(meta.get("duration") or duration or 0.0)

        pending: list[dict] = []
        last_flush = time.monotonic()
        for segment in segments:
            pending.append(
                {
                    "idx": segment.idx,
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                    "no_speech_prob": segment.no_speech_prob,
                    "avg_logprob": segment.avg_logprob,
                }
            )
            due = (
                len(pending) >= _FLUSH_EVERY_SEGMENTS
                or time.monotonic() - last_flush >= _FLUSH_EVERY_SECONDS
            )
            if due:
                store.add_segments(transcript_id, pending)
                pending.clear()
                last_flush = time.monotonic()
                if total > 0:
                    store.set_progress(transcript_id, segment.end / total)
                self._check_cancelled(transcript_id)
                if self._stopping.is_set():
                    raise Cancelled()

        if pending:
            store.add_segments(transcript_id, pending)
        self._check_cancelled(transcript_id)

    # --- helpers ---

    @staticmethod
    def _resolve_source(raw_path: str) -> Path:
        path = Path(raw_path)
        if not path.is_file():
            raise media.MediaError(
                f"The source file is no longer at {raw_path}. Move it back or re-import it."
            )
        return path

    @staticmethod
    def _build_options(row) -> TranscriptionOptions:
        settings = store.get_settings()
        info = hardware.detect()
        model = row["model"] or settings.get("model", DEFAULT_SETTINGS["model"])
        preference = settings.get("device", "auto")
        plan = hardware.plan_compute(model, info, preference)
        return TranscriptionOptions(
            model=model,
            device=plan.device,
            compute_type=plan.compute_type,
            language=row["language"] or settings.get("language", "tl"),
            initial_prompt=row["initial_prompt"],
            beam_size=int(settings.get("beam_size", "5") or 5),
            vad_filter=settings.get("vad_filter", "1") == "1",
            word_timestamps=settings.get("word_timestamps", "0") == "1",
            cpu_threads=max(2, info.cpu_threads),
        )

    @staticmethod
    def _cpu_fallback(options: TranscriptionOptions) -> TranscriptionOptions | None:
        if options.device == "cpu":
            return None
        transcriber.unload()
        return TranscriptionOptions(
            model=options.model,
            device="cpu",
            compute_type="int8",
            language=options.language,
            initial_prompt=options.initial_prompt,
            beam_size=options.beam_size,
            vad_filter=options.vad_filter,
            word_timestamps=options.word_timestamps,
            cpu_threads=options.cpu_threads,
        )

    def _check_cancelled(self, transcript_id: int) -> None:
        if store.is_cancel_requested(transcript_id):
            raise Cancelled()


_worker: TranscriptionWorker | None = None


def get_worker() -> TranscriptionWorker:
    global _worker
    if _worker is None:
        _worker = TranscriptionWorker()
    return _worker


def set_worker(worker: TranscriptionWorker | None) -> None:
    global _worker
    _worker = worker
