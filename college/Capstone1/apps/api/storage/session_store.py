"""SQLite-backed SessionStore (Phase C).

Ephemeral session lifecycle only: open, read, list expired, soft-close.
Timestamps are stored as UTC ISO-8601 text.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime, timedelta

from apps.api.storage.database import Database, is_valid_id
from apps.api.storage.records import SessionRecord, SessionStatus

_DEFAULT_TTL = timedelta(hours=6)


def _iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC).isoformat()


def _parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _from_row(row: sqlite3.Row) -> SessionRecord:
    expires_at = _parse_iso(row["expires_at"]) if row["expires_at"] else None
    return SessionRecord(
        session_id=row["id"],
        status=SessionStatus(row["status"]),
        created_at=_parse_iso(row["created_at"]),
        expires_at=expires_at,
    )


class SQLiteSessionStore:
    def __init__(self, db: Database) -> None:
        self._db = db

    def create(self, session_id: str, ttl: timedelta | None = None) -> SessionRecord:
        if not is_valid_id(session_id):
            raise ValueError(f"invalid session id: {session_id!r}")
        ttl = ttl or _DEFAULT_TTL
        now = datetime.now(UTC)
        expires_at = now + ttl
        self._db.execute(
            "INSERT INTO sessions (id, status, created_at, expires_at) VALUES (?, ?, ?, ?)",
            (session_id, SessionStatus.ACTIVE.value, _iso(now), _iso(expires_at)),
        )
        return SessionRecord(
            session_id=session_id,
            status=SessionStatus.ACTIVE,
            created_at=now,
            expires_at=expires_at,
        )

    def get(self, session_id: str) -> SessionRecord | None:
        row = self._db.query_one(
            "SELECT id, status, created_at, expires_at FROM sessions WHERE id = ?",
            (session_id,),
        )
        if row is None:
            return None
        return _from_row(row)

    def list_expired(self, now: datetime) -> list[SessionRecord]:
        rows = self._db.query_all(
            "SELECT id, status, created_at, expires_at FROM sessions "
            "WHERE status = ? AND expires_at IS NOT NULL AND expires_at <= ?",
            (SessionStatus.ACTIVE.value, _iso(now)),
        )
        return [_from_row(row) for row in rows]

    def close(self, session_id: str) -> SessionRecord | None:
        self._db.execute(
            "UPDATE sessions SET status = ? WHERE id = ? AND status = ?",
            (SessionStatus.CLOSED.value, session_id, SessionStatus.ACTIVE.value),
        )
        return self.get(session_id)
