"""Whisper model lifecycle and the Taglish-tuned decoding call."""

from __future__ import annotations

import inspect
import logging
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from app.core import cuda, paths

logger = logging.getLogger(__name__)

_model_lock = threading.Lock()
_cached_key: tuple[str, str, str] | None = None
_cached_model: Any = None


class TranscriptionError(Exception):
    """Raised with a message that is safe and useful to show the user."""


@dataclass(frozen=True)
class TranscriptionOptions:
    model: str = "large-v3"
    device: str = "cpu"
    compute_type: str = "int8"
    language: str = "tl"
    initial_prompt: str | None = None
    beam_size: int = 5
    vad_filter: bool = True
    word_timestamps: bool = False
    cpu_threads: int = 4


@dataclass(frozen=True)
class Segment:
    idx: int
    start: float
    end: float
    text: str
    no_speech_prob: float | None
    avg_logprob: float | None


def build_prompt(base_prompt: str, glossary: str) -> str | None:
    """Combine the Taglish priming sentence with the user's proper nouns."""
    parts = [base_prompt.strip()]
    terms = [term.strip() for term in glossary.replace("\n", ",").split(",") if term.strip()]
    if terms:
        parts.append("Mga pangalan at termino: " + ", ".join(terms) + ".")
    combined = " ".join(part for part in parts if part)
    # Whisper only conditions on the last 224 tokens; a longer prompt silently loses its head.
    return combined[:900] or None


def load_model(options: TranscriptionOptions):
    global _cached_key, _cached_model
    key = (options.model, options.device, options.compute_type)
    with _model_lock:
        if _cached_key == key and _cached_model is not None:
            return _cached_model
        unload_locked()
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise TranscriptionError(
                "faster-whisper is not installed. Run: pip install -r requirements.txt"
            ) from exc

        if options.device == "cuda":
            cuda.prepare()
        paths.models_dir().mkdir(parents=True, exist_ok=True)
        logger.info("Loading %s on %s (%s)", options.model, options.device, options.compute_type)
        try:
            _cached_model = WhisperModel(
                options.model,
                device=options.device,
                compute_type=options.compute_type,
                download_root=str(paths.models_dir()),
                cpu_threads=options.cpu_threads if options.device == "cpu" else 0,
            )
        except Exception as exc:
            raise TranscriptionError(explain_failure(options, exc)) from exc
        _cached_key = key
        return _cached_model


def explain_failure(options: TranscriptionOptions, exc: Exception) -> str:
    """Turn an engine exception into something the user can act on."""
    text = str(exc)
    lowered = text.lower()
    if "out of memory" in lowered:
        return (
            f"The GPU ran out of memory running {options.model}. Choose a smaller model in "
            "Settings, or set the device to CPU."
        )
    if "cudnn" in lowered or "cublas" in lowered or "libcuda" in lowered or "cuda" in lowered:
        return (
            "The CUDA runtime libraries are missing or unusable. Run: "
            "pip install nvidia-cublas-cu12 nvidia-cudnn-cu12, or set the device to CPU. "
            f"({text[:150]})"
        )
    if "connection" in lowered or "resolve" in lowered or "offline" in lowered:
        return (
            f"The {options.model} weights are not downloaded yet and the download failed. "
            "Connect to the internet once to fetch them."
        )
    return f"The {options.model} model failed: {text[:300]}"


def unload_locked() -> None:
    global _cached_key, _cached_model
    _cached_model = None
    _cached_key = None


def unload() -> None:
    with _model_lock:
        unload_locked()


def transcribe(audio_path: Path, options: TranscriptionOptions) -> tuple[dict, Iterator[Segment]]:
    """Return detection metadata and a lazy iterator of segments.

    The iterator is lazy on purpose: segments are persisted as they arrive so a three-hour file
    shows progress and survives a crash without buffering the whole transcript in memory.
    """
    model = load_model(options)

    kwargs: dict[str, Any] = {
        "task": "transcribe",
        "beam_size": options.beam_size,
        "word_timestamps": options.word_timestamps,
        # Without this, a single bad Taglish segment poisons everything that follows and
        # Whisper loops on silence.
        "condition_on_previous_text": False,
        "temperature": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        "compression_ratio_threshold": 2.4,
        "log_prob_threshold": -1.0,
        "no_speech_threshold": 0.6,
        "initial_prompt": options.initial_prompt,
        "vad_filter": options.vad_filter,
        "vad_parameters": {"min_silence_duration_ms": 500, "speech_pad_ms": 200},
    }

    if options.language == "auto":
        kwargs["language"] = None
        if "multilingual" in inspect.signature(model.transcribe).parameters:
            kwargs["multilingual"] = True
    else:
        kwargs["language"] = options.language

    try:
        raw_segments, info = model.transcribe(str(audio_path), **kwargs)
    except Exception as exc:
        raise TranscriptionError(explain_failure(options, exc)) from exc

    meta = {
        "language": getattr(info, "language", None),
        "language_probability": getattr(info, "language_probability", None),
        "duration": getattr(info, "duration", None),
    }
    return meta, _iter_segments(raw_segments, options)


def _iter_segments(raw_segments, options: TranscriptionOptions) -> Iterator[Segment]:
    idx = 0
    try:
        for seg in raw_segments:
            text = (seg.text or "").strip()
            if not text:
                continue
            yield Segment(
                idx=idx,
                start=float(seg.start),
                end=float(seg.end),
                text=text,
                no_speech_prob=getattr(seg, "no_speech_prob", None),
                avg_logprob=getattr(seg, "avg_logprob", None),
            )
            idx += 1
    except Exception as exc:
        # CTranslate2 decodes lazily, so device-level failures surface here rather than at load.
        raise TranscriptionError(explain_failure(options, exc)) from exc
