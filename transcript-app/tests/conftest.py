from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import store  # noqa: E402


@pytest.fixture()
def db(tmp_path, monkeypatch):
    monkeypatch.setenv("TT_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("TT_MODELS_DIR", str(tmp_path / "models"))
    store.close()
    # No explicit path: the app's own startup re-resolves it from TT_DATA_DIR, so both must agree.
    store.configure()
    store.init_db()
    yield store
    store.close()


@pytest.fixture()
def transcript_id(db, tmp_path):
    source = tmp_path / "memo.m4a"
    source.write_bytes(b"not real audio")
    return db.create_transcript(
        title="memo",
        source_path=str(source),
        source_size=source.stat().st_size,
        duration=120.0,
        model="large-v3",
        language="tl",
        initial_prompt="Taglish prompt",
    )
