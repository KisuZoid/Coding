"""SQLite persistence plumbing (Phase C).

Standard-library sqlite3 only. The storage interfaces allow swapping for
PostgreSQL/Supabase later without domain changes. A single Database object owns
its connection, guards it with a lock (FastAPI runs handlers/hardware work on a
threadpool), and initialises the schema idempotently.
"""

from __future__ import annotations

import re
import sqlite3
import threading
from pathlib import Path
from typing import cast

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id          TEXT PRIMARY KEY,
    status      TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    expires_at  TEXT
);

CREATE TABLE IF NOT EXISTS image_assets (
    id            TEXT PRIMARY KEY,
    session_id    TEXT NOT NULL,
    kind          TEXT NOT NULL,
    relative_path TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_image_assets_session ON image_assets(session_id);

-- Consented training side lives in separate tables so cleanup can never reach it.
CREATE TABLE IF NOT EXISTS consent_records (
    id              TEXT PRIMARY KEY,
    session_id      TEXT NOT NULL,
    decision        TEXT NOT NULL,
    dataset_version TEXT,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS training_samples (
    id                TEXT PRIMARY KEY,
    session_id        TEXT NOT NULL,
    consent_id        TEXT NOT NULL,
    dataset_version   TEXT NOT NULL,
    annotation_status TEXT NOT NULL,
    provenance        TEXT NOT NULL,
    image_asset_id    TEXT NOT NULL,
    labels_json       TEXT NOT NULL,
    created_at        TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_training_samples_created
    ON training_samples(created_at DESC);

-- Ephemeral workflow state per session (added Phase K; wiped by cleanup).
CREATE TABLE IF NOT EXISTS session_states (
    id         TEXT PRIMARY KEY,
    state_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def is_valid_id(value: str) -> bool:
    """Whitelist session/asset ids used to build filesystem paths."""
    return _ID_PATTERN.fullmatch(value) is not None


def resolve_database_path(database_url: str, storage_root: Path) -> Path:
    """Map DATABASE_URL to a sqlite file; default lives under storage_root."""
    if database_url.startswith("sqlite:///"):
        return Path(database_url.removeprefix("sqlite:///")).expanduser()
    if database_url:
        raise ValueError("only sqlite:/// URLs are supported until a Postgres ADR")
    return storage_root / "app.db"


class Database:
    """Owns one sqlite3 connection plus a scope-level lock."""

    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            self._conn.executescript(_SCHEMA)
            self._conn.commit()

    def execute(self, sql: str, params: tuple[object, ...] = ()) -> None:
        with self._lock:
            self._conn.execute(sql, params)
            self._conn.commit()

    def query_one(self, sql: str, params: tuple[object, ...] = ()) -> sqlite3.Row | None:
        with self._lock:
            cursor = self._conn.execute(sql, params)
            row = cursor.fetchone()
            if row is None:
                return None
            return cast(sqlite3.Row, row)

    def query_all(self, sql: str, params: tuple[object, ...] = ()) -> list[sqlite3.Row]:
        with self._lock:
            cursor = self._conn.execute(sql, params)
            return list(cursor.fetchall())

    def close(self) -> None:
        with self._lock:
            self._conn.close()
