from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from app.core.hardware import HardwareInfo
from app.services import media, worker as worker_module
from app.services.transcriber import Segment, TranscriptionError
from app.services.worker import TranscriptionWorker

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

SPOKEN = [
    Segment(0, 0.0, 2.0, "Kumusta, nag-meeting kami kanina.", 0.01, -0.2),
    Segment(1, 2.0, 4.5, "The client said okay daw sa proposal.", 0.02, -0.3),
]


@pytest.fixture()
def fake_pipeline(monkeypatch, tmp_path):
    """Replace FFmpeg and hardware probing; track the temporary audio file."""
    created: list[Path] = []

    def fake_probe(path: Path):
        return media.MediaInfo(
            path=path,
            size_bytes=1024,
            duration=4.5,
            has_audio=True,
            has_video=False,
            container="m4a",
        )

    def fake_extract(path: Path) -> Path:
        handle, name = tempfile.mkstemp(dir=tmp_path, suffix=".wav")
        Path(name).write_bytes(b"RIFF")
        created.append(Path(name))
        import os

        os.close(handle)
        return Path(name)

    monkeypatch.setattr(media, "probe", fake_probe)
    monkeypatch.setattr(media, "extract_audio", fake_extract)
    monkeypatch.setattr(worker_module.hardware, "detect", lambda: FAKE_HARDWARE)
    return created


def run_job(db, transcript_id, transcribe_fn) -> None:
    worker = TranscriptionWorker(transcribe_fn=transcribe_fn)
    row = db.claim_next_queued()
    assert row["id"] == transcript_id
    worker._process(row)


def test_successful_job_persists_segments_and_cleans_up(db, transcript_id, fake_pipeline):
    def transcribe(audio_path, options):
        assert Path(audio_path).is_file()
        assert options.device == "cpu"
        assert options.language == "tl"
        return {"language": "tl", "language_probability": 0.92, "duration": 4.5}, iter(SPOKEN)

    run_job(db, transcript_id, transcribe)

    row = db.get_transcript(transcript_id)
    assert row["status"] == "completed"
    assert row["progress"] == 1.0
    assert row["detected_language"] == "tl"
    assert row["device"] == "cpu"

    texts = [segment["text"] for segment in db.get_segments(transcript_id)]
    assert texts == [segment.text for segment in SPOKEN]
    assert all(not path.exists() for path in fake_pipeline)


def test_engine_failure_is_reported_and_temp_audio_removed(db, transcript_id, fake_pipeline):
    def transcribe(audio_path, options):
        raise TranscriptionError("The GPU ran out of memory loading large-v3.")

    run_job(db, transcript_id, transcribe)

    row = db.get_transcript(transcript_id)
    assert row["status"] == "failed"
    assert "ran out of memory" in row["error"]
    assert all(not path.exists() for path in fake_pipeline)


def test_gpu_failure_falls_back_to_cpu(db, transcript_id, fake_pipeline, monkeypatch):
    monkeypatch.setattr(
        worker_module.hardware,
        "detect",
        lambda: FAKE_HARDWARE.__class__(
            **{**FAKE_HARDWARE.as_dict(), "cuda_available": True, "vram_total_gb": 4.0}
        ),
    )
    attempts: list[str] = []

    def transcribe(audio_path, options):
        attempts.append(options.device)
        if options.device == "cuda":
            raise TranscriptionError("CUDA failed with out of memory")
        return {"language": "tl", "language_probability": 0.9, "duration": 4.5}, iter(SPOKEN)

    run_job(db, transcript_id, transcribe)

    assert attempts == ["cuda", "cpu"]
    assert db.get_transcript(transcript_id)["status"] == "completed"
    assert db.get_transcript(transcript_id)["device"] == "cpu"


def test_lazy_decoding_failure_also_falls_back_to_cpu(db, transcript_id, fake_pipeline, monkeypatch):
    """CTranslate2 decodes lazily, so a dead GPU only errors while iterating segments."""
    monkeypatch.setattr(
        worker_module.hardware,
        "detect",
        lambda: HardwareInfo(**{**FAKE_HARDWARE.as_dict(), "cuda_available": True, "vram_total_gb": 4.0}),
    )
    attempts: list[str] = []

    def transcribe(audio_path, options):
        attempts.append(options.device)
        meta = {"language": "tl", "language_probability": 0.9, "duration": 4.5}
        if options.device == "cuda":

            def broken():
                raise TranscriptionError("Library cublas64_12.dll is not found")
                yield  # pragma: no cover

            return meta, broken()
        return meta, iter(SPOKEN)

    run_job(db, transcript_id, transcribe)

    assert attempts == ["cuda", "cpu"]
    row = db.get_transcript(transcript_id)
    assert row["status"] == "completed"
    assert row["device"] == "cpu"
    assert len(db.get_segments(transcript_id)) == len(SPOKEN)


def test_partial_gpu_output_is_not_silently_retried(db, transcript_id, fake_pipeline, monkeypatch):
    """Once text exists, a mid-run failure is reported instead of restarting on CPU."""
    monkeypatch.setattr(
        worker_module.hardware,
        "detect",
        lambda: HardwareInfo(**{**FAKE_HARDWARE.as_dict(), "cuda_available": True, "vram_total_gb": 4.0}),
    )

    many = [Segment(i, float(i), float(i) + 1, f"segment {i}", 0.0, -0.1) for i in range(15)]
    attempts: list[str] = []

    def transcribe(audio_path, options):
        attempts.append(options.device)

        def partial():
            yield from many
            raise TranscriptionError("CUDA device lost")

        return {"language": "tl", "language_probability": 0.9, "duration": 20.0}, partial()

    run_job(db, transcript_id, transcribe)

    row = db.get_transcript(transcript_id)
    assert attempts == ["cuda"]
    assert row["status"] == "failed"
    assert "CUDA device lost" in row["error"]
    assert db.get_segments(transcript_id)


def test_cancellation_stops_the_job(db, transcript_id, fake_pipeline):
    def transcribe(audio_path, options):
        db.request_cancel(transcript_id)
        return {"language": "tl", "language_probability": 0.9, "duration": 4.5}, iter(SPOKEN)

    run_job(db, transcript_id, transcribe)

    row = db.get_transcript(transcript_id)
    assert row["status"] == "canceled"


def test_missing_source_file_gives_a_clear_error(db, tmp_path, fake_pipeline):
    transcript_id = db.create_transcript(
        title="gone",
        source_path=str(tmp_path / "moved.m4a"),
        source_size=None,
        duration=None,
        model="large-v3",
        language="tl",
        initial_prompt=None,
    )

    run_job(db, transcript_id, lambda *args: (_ for _ in ()).throw(AssertionError("unreachable")))

    row = db.get_transcript(transcript_id)
    assert row["status"] == "failed"
    assert "no longer at" in row["error"]
