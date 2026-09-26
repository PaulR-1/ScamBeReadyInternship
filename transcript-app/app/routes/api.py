"""JSON API, media streaming, and exports."""

from __future__ import annotations

import mimetypes
import sqlite3
from pathlib import Path
from typing import Any, Iterator

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from app.core import hardware
from app.core.config import DEFAULT_SETTINGS, get_config
from app.db import store
from app.services import exporters, filepicker, media
from app.services.transcriber import build_prompt
from app.services.worker import get_worker

router = APIRouter(prefix="/api")

_STREAM_CHUNK = 1024 * 512


class CreateTranscriptRequest(BaseModel):
    path: str = Field(min_length=1)
    title: str | None = None


class SegmentUpdateRequest(BaseModel):
    text: str


def transcript_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    data = dict(row)
    data["progress"] = round(float(data.get("progress") or 0.0), 4)
    data["source_exists"] = Path(data["source_path"]).is_file()
    data["source_name"] = Path(data["source_path"]).name
    data["is_active"] = data["status"] in store.ACTIVE_STATUSES
    return data


def segment_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "idx": row["idx"],
        "start": row["start"],
        "end": row["end"],
        "text": row["text"],
        "original_text": row["original_text"],
        "edited": bool(row["edited"]),
        "start_label": exporters.clock_timestamp(row["start"]),
        "end_label": exporters.clock_timestamp(row["end"]),
    }


def _require(transcript_id: int) -> sqlite3.Row:
    row = store.get_transcript(transcript_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Transcript not found.")
    return row


@router.get("/system")
def system_info() -> dict[str, Any]:
    settings = store.get_settings()
    info = hardware.detect()
    plan = hardware.plan_compute(settings["model"], info, settings.get("device", "auto"))
    return {
        "hardware": info.as_dict(),
        "plan": {"device": plan.device, "compute_type": plan.compute_type, "reason": plan.reason},
        "ffmpeg_available": media.ffmpeg_available(),
        "max_duration_minutes": round(get_config().max_duration_seconds / 60),
        "worker_busy": get_worker().is_busy(),
    }


@router.post("/browse")
def browse() -> dict[str, Any]:
    selected = filepicker.pick_file()
    if not selected:
        return {"path": None, "message": "No file chosen."}
    return {"path": selected}


@router.get("/transcripts")
def list_transcripts() -> dict[str, Any]:
    return {"transcripts": [transcript_to_dict(row) for row in store.list_transcripts()]}


@router.post("/transcripts", status_code=201)
def create_transcript(payload: CreateTranscriptRequest) -> dict[str, Any]:
    try:
        source = media.resolve_source(payload.path)
        info = media.probe(source)
    except media.MediaError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    settings = store.get_settings()
    prompt = build_prompt(
        settings.get("initial_prompt", DEFAULT_SETTINGS["initial_prompt"]),
        settings.get("glossary", ""),
    )
    transcript_id = store.create_transcript(
        title=(payload.title or source.stem).strip()[:200] or source.stem,
        source_path=str(source),
        source_size=info.size_bytes,
        duration=info.duration,
        model=settings.get("model", DEFAULT_SETTINGS["model"]),
        language=settings.get("language", DEFAULT_SETTINGS["language"]),
        initial_prompt=prompt,
    )
    get_worker().notify()
    return transcript_to_dict(_require(transcript_id))


@router.get("/transcripts/{transcript_id}")
def get_transcript(transcript_id: int, include_segments: bool = True) -> dict[str, Any]:
    row = _require(transcript_id)
    payload = {"transcript": transcript_to_dict(row)}
    if include_segments:
        payload["segments"] = [segment_to_dict(s) for s in store.get_segments(transcript_id)]
    return payload


@router.delete("/transcripts/{transcript_id}")
def delete_transcript(transcript_id: int) -> dict[str, Any]:
    row = _require(transcript_id)
    if row["status"] in store.ACTIVE_STATUSES:
        raise HTTPException(status_code=409, detail="Cancel this transcription before deleting it.")
    store.delete_transcript(transcript_id)
    return {"deleted": transcript_id}


@router.post("/transcripts/{transcript_id}/cancel")
def cancel_transcript(transcript_id: int) -> dict[str, Any]:
    row = _require(transcript_id)
    if row["status"] not in store.ACTIVE_STATUSES:
        raise HTTPException(status_code=409, detail="That transcription is not running.")
    store.request_cancel(transcript_id)
    return transcript_to_dict(_require(transcript_id))


@router.post("/transcripts/{transcript_id}/retry")
def retry_transcript(transcript_id: int) -> dict[str, Any]:
    row = _require(transcript_id)
    if row["status"] in store.ACTIVE_STATUSES:
        raise HTTPException(status_code=409, detail="That transcription is already queued.")
    if not Path(row["source_path"]).is_file():
        raise HTTPException(
            status_code=400, detail=f"The source file is missing: {row['source_path']}"
        )
    settings = store.get_settings()
    store.requeue(
        transcript_id,
        model=settings.get("model"),
        language=settings.get("language"),
        initial_prompt=build_prompt(
            settings.get("initial_prompt", DEFAULT_SETTINGS["initial_prompt"]),
            settings.get("glossary", ""),
        ),
    )
    get_worker().notify()
    return transcript_to_dict(_require(transcript_id))


@router.patch("/segments/{segment_id}")
def update_segment(segment_id: int, payload: SegmentUpdateRequest) -> dict[str, Any]:
    if store.get_segment(segment_id) is None:
        raise HTTPException(status_code=404, detail="Segment not found.")
    row = store.update_segment_text(segment_id, payload.text.strip())
    assert row is not None
    return segment_to_dict(row)


@router.post("/segments/{segment_id}/revert")
def revert_segment(segment_id: int) -> dict[str, Any]:
    if store.get_segment(segment_id) is None:
        raise HTTPException(status_code=404, detail="Segment not found.")
    row = store.revert_segment(segment_id)
    assert row is not None
    return segment_to_dict(row)


@router.get("/transcripts/{transcript_id}/export")
def export_transcript(transcript_id: int, fmt: str = "txt", timestamps: bool = True) -> Response:
    row = _require(transcript_id)
    fmt = fmt.lower()
    if fmt not in exporters.FORMATS:
        raise HTTPException(status_code=400, detail="Choose txt, srt, or vtt.")
    segments = [dict(s) for s in store.get_segments(transcript_id)]
    if not segments:
        raise HTTPException(status_code=409, detail="This transcript has no text yet.")
    body = exporters.render(fmt, segments, include_timestamps=timestamps)
    filename = exporters.safe_filename(row["title"], fmt)
    return Response(
        content=body.encode("utf-8"),
        media_type=f"{exporters.FORMATS[fmt]}; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _parse_range(header: str | None, size: int) -> tuple[int, int] | None:
    if not header or not header.startswith("bytes="):
        return None
    first, _, last = header.removeprefix("bytes=").partition("-")
    try:
        if first:
            start = int(first)
            end = int(last) if last else size - 1
        else:
            start = size - int(last)
            end = size - 1
    except ValueError:
        return None
    start = max(0, start)
    end = min(end, size - 1)
    if start > end:
        return None
    return start, end


def _stream(path: Path, start: int, end: int) -> Iterator[bytes]:
    remaining = end - start + 1
    with path.open("rb") as handle:
        handle.seek(start)
        while remaining > 0:
            chunk = handle.read(min(_STREAM_CHUNK, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk


@router.get("/transcripts/{transcript_id}/media")
def stream_media(transcript_id: int, request: Request) -> Response:
    row = _require(transcript_id)
    path = Path(row["source_path"])
    if not path.is_file():
        raise HTTPException(status_code=404, detail="The source file is no longer on disk.")

    size = path.stat().st_size
    content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    rng = _parse_range(request.headers.get("range"), size)
    if rng is None:
        return StreamingResponse(
            _stream(path, 0, size - 1),
            media_type=content_type,
            headers={"Content-Length": str(size), "Accept-Ranges": "bytes"},
        )
    start, end = rng
    return StreamingResponse(
        _stream(path, start, end),
        status_code=206,
        media_type=content_type,
        headers={
            "Content-Range": f"bytes {start}-{end}/{size}",
            "Content-Length": str(end - start + 1),
            "Accept-Ranges": "bytes",
        },
    )


@router.get("/settings")
def read_settings() -> dict[str, str]:
    return store.get_settings()


@router.put("/settings")
def write_settings(values: dict[str, str]) -> JSONResponse:
    allowed = {key: str(value) for key, value in values.items() if key in DEFAULT_SETTINGS}
    if not allowed:
        raise HTTPException(status_code=400, detail="No recognised settings were provided.")
    store.save_settings(allowed)
    return JSONResponse(store.get_settings())
