"""TXT, SRT, and VTT serialisation."""

from __future__ import annotations

import re
from typing import Any, Iterable, Mapping, Sequence

FORMATS = {"txt": "text/plain", "srt": "application/x-subrip", "vtt": "text/vtt"}
_UNSAFE_FILENAME = re.compile(r"[^A-Za-z0-9._ -]+")


def _parts(seconds: float) -> tuple[int, int, int, int]:
    total_ms = max(0, round(float(seconds) * 1000))
    hours, rest = divmod(total_ms, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    secs, millis = divmod(rest, 1000)
    return hours, minutes, secs, millis


def srt_timestamp(seconds: float) -> str:
    h, m, s, ms = _parts(seconds)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def vtt_timestamp(seconds: float) -> str:
    h, m, s, ms = _parts(seconds)
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"


def clock_timestamp(seconds: float) -> str:
    h, m, s, _ = _parts(seconds)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _normalise(segments: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Force non-negative, non-overlapping, monotonic cues so players accept the file."""
    rows: list[dict[str, Any]] = []
    previous_end = 0.0
    for seg in segments:
        text = str(seg["text"]).strip()
        if not text:
            continue
        start = max(0.0, float(seg["start"]))
        end = float(seg["end"])
        start = max(start, previous_end)
        if end <= start:
            end = start + 0.05
        rows.append({"start": start, "end": end, "text": text})
        previous_end = end
    return rows


def to_txt(segments: Sequence[Mapping[str, Any]], include_timestamps: bool = True) -> str:
    rows = _normalise(segments)
    if not include_timestamps:
        return "\n".join(row["text"] for row in rows) + ("\n" if rows else "")
    return "".join(f"[{clock_timestamp(row['start'])}] {row['text']}\n" for row in rows)


def to_srt(segments: Sequence[Mapping[str, Any]]) -> str:
    out: list[str] = []
    for number, row in enumerate(_normalise(segments), start=1):
        out.append(
            f"{number}\n{srt_timestamp(row['start'])} --> {srt_timestamp(row['end'])}\n"
            f"{row['text']}\n\n"
        )
    return "".join(out)


def to_vtt(segments: Sequence[Mapping[str, Any]]) -> str:
    out = ["WEBVTT\n\n"]
    for row in _normalise(segments):
        out.append(
            f"{vtt_timestamp(row['start'])} --> {vtt_timestamp(row['end'])}\n{row['text']}\n\n"
        )
    return "".join(out)


def render(fmt: str, segments: Sequence[Mapping[str, Any]], include_timestamps: bool = True) -> str:
    if fmt == "txt":
        return to_txt(segments, include_timestamps)
    if fmt == "srt":
        return to_srt(segments)
    if fmt == "vtt":
        return to_vtt(segments)
    raise ValueError(f"Unsupported export format: {fmt}")


def safe_filename(title: str, fmt: str) -> str:
    cleaned = _UNSAFE_FILENAME.sub("_", title).strip(" ._") or "transcript"
    return f"{cleaned[:80]}.{fmt}"
