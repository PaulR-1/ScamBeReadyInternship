from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core import hardware
from app.core.hardware import ComputePlan, HardwareInfo
from app.services import media, worker as worker_module

FAKE_HARDWARE = HardwareInfo(
    cuda_available=False,
    cuda_device_count=0,
    gpu_name=None,
    vram_total_gb=None,
    vram_free_gb=None,
    ram_total_gb=40.0,
    cpu_threads=8,
    notes=[],
)


class StubWorker:
    """Stands in for the background thread so tests never load a model."""

    def __init__(self) -> None:
        self.notified = 0

    def start(self) -> None: ...

    def stop(self, timeout: float = 5.0) -> None: ...

    def notify(self) -> None:
        self.notified += 1

    def is_busy(self) -> bool:
        return False


@pytest.fixture()
def client(db, tmp_path, monkeypatch):
    monkeypatch.setattr(worker_module, "_worker", StubWorker())
    monkeypatch.setattr(
        media,
        "probe",
        lambda path: media.MediaInfo(
            path=path,
            size_bytes=path.stat().st_size,
            duration=90.0,
            has_audio=True,
            has_video=False,
            container="m4a",
        ),
    )
    monkeypatch.setattr(media, "ffmpeg_available", lambda: True)
    monkeypatch.setattr(hardware, "detect", lambda: FAKE_HARDWARE)
    monkeypatch.setattr(
        hardware, "plan_compute", lambda *args, **kwargs: ComputePlan("cpu", "int8", "test")
    )

    from app.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture()
def sample(tmp_path) -> Path:
    path = tmp_path / "voice memo.m4a"
    path.write_bytes(b"fake audio bytes")
    return path


def test_import_rejects_a_bad_path(client):
    response = client.post("/api/transcripts", json={"path": "Z:\\nope.m4a"})
    assert response.status_code == 400
    assert response.json()["detail"]


def test_import_creates_a_queued_transcript(client, sample):
    response = client.post("/api/transcripts", json={"path": str(sample)})
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "queued"
    assert body["title"] == "voice memo"
    assert body["source_path"] == str(sample.resolve())
    assert worker_module._worker.notified == 1


def test_edit_persists_and_exports(client, sample, db):
    transcript_id = client.post("/api/transcripts", json={"path": str(sample)}).json()["id"]
    db.add_segments(
        transcript_id,
        [
            {"idx": 0, "start": 0.0, "end": 2.0, "text": "Kumusta, are you okay?"},
            {"idx": 1, "start": 2.0, "end": 4.0, "text": "Oo naman."},
        ],
    )
    db.finish_transcript(transcript_id, "completed")

    segments = client.get(f"/api/transcripts/{transcript_id}").json()["segments"]
    patched = client.patch(
        f"/api/segments/{segments[0]['id']}", json={"text": "Kumusta, are you okay ba?"}
    )
    assert patched.status_code == 200
    assert patched.json()["edited"] is True

    reloaded = client.get(f"/api/transcripts/{transcript_id}").json()["segments"]
    assert reloaded[0]["text"] == "Kumusta, are you okay ba?"

    srt = client.get(f"/api/transcripts/{transcript_id}/export", params={"fmt": "srt"})
    assert srt.status_code == 200
    assert "Kumusta, are you okay ba?" in srt.text
    assert "voice memo.srt" in srt.headers["content-disposition"]

    reverted = client.post(f"/api/segments/{segments[0]['id']}/revert").json()
    assert reverted["text"] == "Kumusta, are you okay?"
    assert reverted["edited"] is False


def test_export_rejects_unknown_format(client, sample, db):
    transcript_id = client.post("/api/transcripts", json={"path": str(sample)}).json()["id"]
    db.add_segments(transcript_id, [{"idx": 0, "start": 0.0, "end": 1.0, "text": "hi"}])
    assert client.get(f"/api/transcripts/{transcript_id}/export", params={"fmt": "docx"}).status_code == 400


def test_export_of_an_empty_transcript_is_refused(client, sample):
    transcript_id = client.post("/api/transcripts", json={"path": str(sample)}).json()["id"]
    assert client.get(f"/api/transcripts/{transcript_id}/export").status_code == 409


def test_queued_transcript_cannot_be_deleted(client, sample):
    transcript_id = client.post("/api/transcripts", json={"path": str(sample)}).json()["id"]
    assert client.delete(f"/api/transcripts/{transcript_id}").status_code == 409

    assert client.post(f"/api/transcripts/{transcript_id}/cancel").status_code == 200


def test_media_streaming_supports_range_requests(client, sample):
    transcript_id = client.post("/api/transcripts", json={"path": str(sample)}).json()["id"]

    full = client.get(f"/api/transcripts/{transcript_id}/media")
    assert full.status_code == 200
    assert full.content == sample.read_bytes()

    partial = client.get(
        f"/api/transcripts/{transcript_id}/media", headers={"Range": "bytes=0-3"}
    )
    assert partial.status_code == 206
    assert partial.content == sample.read_bytes()[:4]
    assert partial.headers["content-range"].endswith(f"/{sample.stat().st_size}")


def test_settings_update_ignores_unknown_keys(client):
    response = client.put("/api/settings", json={"language": "en", "hack": "1"})
    assert response.status_code == 200
    assert response.json()["language"] == "en"
    assert "hack" not in response.json()


def test_library_page_renders(client, sample):
    client.post("/api/transcripts", json={"path": str(sample)})
    assert client.get("/").status_code == 200
    assert client.get("/settings").status_code == 200


def test_missing_transcript_returns_404(client):
    assert client.get("/api/transcripts/999").status_code == 404
