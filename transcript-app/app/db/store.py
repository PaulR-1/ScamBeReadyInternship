"""SQLite persistence. Every query in the app lives here."""

from __future__ import annotations

import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from app.core import paths
from app.core.config import DEFAULT_SETTINGS

_local = threading.local()
_db_path: Path | None = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS transcripts (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    title               TEXT    NOT NULL,
    source_path         TEXT    NOT NULL,
    source_size         INTEGER,
    duration            REAL,
    status              TEXT    NOT NULL DEFAULT 'queued',
    error               TEXT,
    progress            REAL    NOT NULL DEFAULT 0.0,
    model               TEXT    NOT NULL,
    language            TEXT    NOT NULL,
    device              TEXT,
    compute_type        TEXT,
    initial_prompt      TEXT,
    detected_language   TEXT,
    language_probability REAL,
    cancel_requested    INTEGER NOT NULL DEFAULT 0,
    created_at          TEXT    NOT NULL,
    started_at          TEXT,
    finished_at         TEXT
);

CREATE TABLE IF NOT EXISTS segments (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    transcript_id INTEGER NOT NULL REFERENCES transcripts(id) ON DELETE CASCADE,
    idx           INTEGER NOT NULL,
    start         REAL    NOT NULL,
    end           REAL    NOT NULL,
    text          TEXT    NOT NULL,
    original_text TEXT    NOT NULL,
    edited        INTEGER NOT NULL DEFAULT 0,
    no_speech_prob REAL,
    avg_logprob   REAL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_segments_transcript_idx
    ON segments(transcript_id, idx);
CREATE INDEX IF NOT EXISTS idx_transcripts_status ON transcripts(status);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

ACTIVE_STATUSES = ("queued", "running")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def configure(db_path: Path | None = None) -> None:
    """Point the store at a database file. Call before any query."""
    global _db_path
    _db_path = db_path or paths.database_path()
    _local.__dict__.pop("conn", None)


def connection() -> sqlite3.Connection:
    conn = getattr(_local, "conn", None)
    if conn is None:
        if _db_path is None:
            configure()
        assert _db_path is not None
        _db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(_db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=30000")
        _local.conn = conn
    return conn


def init_db() -> None:
    conn = connection()
    with conn:
        conn.executescript(SCHEMA)
        for key, value in DEFAULT_SETTINGS.items():
            conn.execute("INSERT OR IGNORE INTO settings(key, value) VALUES (?, ?)", (key, value))


def close() -> None:
    conn = getattr(_local, "conn", None)
    if conn is not None:
        conn.close()
        _local.__dict__.pop("conn", None)


# --- settings ---------------------------------------------------------------


def get_settings() -> dict[str, str]:
    rows = connection().execute("SELECT key, value FROM settings").fetchall()
    merged = dict(DEFAULT_SETTINGS)
    merged.update({row["key"]: row["value"] for row in rows})
    return merged


def save_settings(values: dict[str, str]) -> None:
    conn = connection()
    with conn:
        conn.executemany(
            "INSERT INTO settings(key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            [(key, str(value)) for key, value in values.items()],
        )


# --- transcripts ------------------------------------------------------------


def create_transcript(
    *,
    title: str,
    source_path: str,
    source_size: int | None,
    duration: float | None,
    model: str,
    language: str,
    initial_prompt: str | None,
) -> int:
    conn = connection()
    with conn:
        cur = conn.execute(
            "INSERT INTO transcripts "
            "(title, source_path, source_size, duration, model, language, initial_prompt, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (title, source_path, source_size, duration, model, language, initial_prompt, _now()),
        )
    return int(cur.lastrowid)


def list_transcripts() -> list[sqlite3.Row]:
    return connection().execute(
        "SELECT t.*, (SELECT COUNT(*) FROM segments s WHERE s.transcript_id = t.id) AS segment_count "
        "FROM transcripts t ORDER BY t.created_at DESC, t.id DESC"
    ).fetchall()


def get_transcript(transcript_id: int) -> sqlite3.Row | None:
    return connection().execute(
        "SELECT * FROM transcripts WHERE id = ?", (transcript_id,)
    ).fetchone()


def delete_transcript(transcript_id: int) -> None:
    conn = connection()
    with conn:
        conn.execute("DELETE FROM segments WHERE transcript_id = ?", (transcript_id,))
        conn.execute("DELETE FROM transcripts WHERE id = ?", (transcript_id,))


def count_active() -> int:
    row = connection().execute(
        f"SELECT COUNT(*) AS n FROM transcripts WHERE status IN {ACTIVE_STATUSES}"
    ).fetchone()
    return int(row["n"])


def claim_next_queued() -> sqlite3.Row | None:
    """Move the oldest queued transcript to running and return it."""
    conn = connection()
    with conn:
        cur = conn.execute(
            "UPDATE transcripts SET status='running', started_at=?, progress=0.0, error=NULL "
            "WHERE id = (SELECT id FROM transcripts WHERE status='queued' ORDER BY id LIMIT 1) "
            "RETURNING id",
            (_now(),),
        )
        row = cur.fetchone()
    return get_transcript(int(row["id"])) if row else None


def mark_running_as_interrupted() -> int:
    """Recover rows orphaned by a crash or a hard shutdown."""
    conn = connection()
    with conn:
        cur = conn.execute(
            "UPDATE transcripts SET status='interrupted', finished_at=?, "
            "error='Stopped before it finished. Retry to run it again.' WHERE status='running'",
            (_now(),),
        )
    return cur.rowcount


def set_engine_info(transcript_id: int, device: str, compute_type: str) -> None:
    conn = connection()
    with conn:
        conn.execute(
            "UPDATE transcripts SET device=?, compute_type=? WHERE id=?",
            (device, compute_type, transcript_id),
        )


def set_duration(transcript_id: int, duration: float) -> None:
    conn = connection()
    with conn:
        conn.execute("UPDATE transcripts SET duration=? WHERE id=?", (duration, transcript_id))


def set_progress(transcript_id: int, progress: float) -> None:
    conn = connection()
    with conn:
        conn.execute(
            "UPDATE transcripts SET progress=? WHERE id=?",
            (max(0.0, min(1.0, progress)), transcript_id),
        )


def set_detected_language(transcript_id: int, language: str | None, probability: float | None) -> None:
    conn = connection()
    with conn:
        conn.execute(
            "UPDATE transcripts SET detected_language=?, language_probability=? WHERE id=?",
            (language, probability, transcript_id),
        )


def finish_transcript(transcript_id: int, status: str, error: str | None = None) -> None:
    conn = connection()
    with conn:
        conn.execute(
            "UPDATE transcripts SET status=?, error=?, finished_at=?, "
            "progress=CASE WHEN ?='completed' THEN 1.0 ELSE progress END WHERE id=?",
            (status, error, _now(), status, transcript_id),
        )


def request_cancel(transcript_id: int) -> None:
    conn = connection()
    with conn:
        conn.execute(
            "UPDATE transcripts SET cancel_requested=1 WHERE id=? AND status IN ('queued','running')",
            (transcript_id,),
        )


def is_cancel_requested(transcript_id: int) -> bool:
    row = connection().execute(
        "SELECT cancel_requested FROM transcripts WHERE id=?", (transcript_id,)
    ).fetchone()
    return bool(row and row["cancel_requested"])


def requeue(
    transcript_id: int,
    *,
    model: str | None = None,
    language: str | None = None,
    initial_prompt: str | None = None,
) -> None:
    """Re-run a job. Model and language are refreshed so retrying applies changed settings."""
    conn = connection()
    with conn:
        conn.execute("DELETE FROM segments WHERE transcript_id=?", (transcript_id,))
        conn.execute(
            "UPDATE transcripts SET status='queued', error=NULL, progress=0.0, "
            "cancel_requested=0, started_at=NULL, finished_at=NULL, device=NULL, "
            "compute_type=NULL, detected_language=NULL, language_probability=NULL, "
            "model=COALESCE(?, model), language=COALESCE(?, language), "
            "initial_prompt=COALESCE(?, initial_prompt) WHERE id=?",
            (model, language, initial_prompt, transcript_id),
        )


# --- segments ---------------------------------------------------------------


def clear_segments(transcript_id: int) -> None:
    conn = connection()
    with conn:
        conn.execute("DELETE FROM segments WHERE transcript_id=?", (transcript_id,))


def add_segments(transcript_id: int, rows: Iterable[dict[str, Any]]) -> None:
    conn = connection()
    with conn:
        conn.executemany(
            "INSERT OR REPLACE INTO segments "
            "(transcript_id, idx, start, end, text, original_text, no_speech_prob, avg_logprob) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    transcript_id,
                    row["idx"],
                    row["start"],
                    row["end"],
                    row["text"],
                    row["text"],
                    row.get("no_speech_prob"),
                    row.get("avg_logprob"),
                )
                for row in rows
            ],
        )


def get_segments(transcript_id: int) -> list[sqlite3.Row]:
    return connection().execute(
        "SELECT * FROM segments WHERE transcript_id=? ORDER BY idx", (transcript_id,)
    ).fetchall()


def get_segment(segment_id: int) -> sqlite3.Row | None:
    return connection().execute("SELECT * FROM segments WHERE id=?", (segment_id,)).fetchone()


def update_segment_text(segment_id: int, text: str) -> sqlite3.Row | None:
    conn = connection()
    with conn:
        conn.execute(
            "UPDATE segments SET text=?, edited=(? <> original_text) WHERE id=?",
            (text, text, segment_id),
        )
    return get_segment(segment_id)


def revert_segment(segment_id: int) -> sqlite3.Row | None:
    conn = connection()
    with conn:
        conn.execute("UPDATE segments SET text=original_text, edited=0 WHERE id=?", (segment_id,))
    return get_segment(segment_id)
