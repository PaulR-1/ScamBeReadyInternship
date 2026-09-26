"""HTML pages."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.core import hardware, paths
from app.core.config import DEVICE_CHOICES, LANGUAGE_CHOICES, MODEL_CHOICES
from app.db import store
from app.routes.api import segment_to_dict, transcript_to_dict
from app.services import media

router = APIRouter()
templates = Jinja2Templates(directory=str(paths.web_dir() / "templates"))


@router.get("/", response_class=HTMLResponse)
def library(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "library.html",
        {
            "transcripts": [transcript_to_dict(row) for row in store.list_transcripts()],
            "ffmpeg_available": media.ffmpeg_available(),
        },
    )


@router.get("/transcripts/{transcript_id}", response_class=HTMLResponse)
def transcript_detail(request: Request, transcript_id: int) -> HTMLResponse:
    row = store.get_transcript(transcript_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Transcript not found.")
    return templates.TemplateResponse(
        request,
        "transcript.html",
        {
            "transcript": transcript_to_dict(row),
            "segments": [segment_to_dict(s) for s in store.get_segments(transcript_id)],
            "ffmpeg_available": media.ffmpeg_available(),
        },
    )


@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request) -> HTMLResponse:
    info = hardware.detect()
    settings = store.get_settings()
    plan = hardware.plan_compute(settings["model"], info, settings.get("device", "auto"))
    return templates.TemplateResponse(
        request,
        "settings.html",
        {
            "settings": settings,
            "hardware": info,
            "plan": plan,
            "model_choices": MODEL_CHOICES,
            "language_choices": LANGUAGE_CHOICES,
            "device_choices": DEVICE_CHOICES,
            "ffmpeg_available": media.ffmpeg_available(),
        },
    )
