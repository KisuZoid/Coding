"""Ephemeral workflow-state persistence (Phase K).

Keeps each session's graph state JSON so GET /inspection/{id} works across
requests and restarts. Ephemeral like the sessions themselves: cleanup deletes
the row; the consented training tables are never touched.
"""

from __future__ import annotations

from datetime import UTC, datetime

from apps.api.storage.database import Database


def _iso() -> str:
    return datetime.now(UTC).isoformat()


class SQLiteStateStore:
    def __init__(self, db: Database) -> None:
        self._db = db

    def save(self, session_id: str, state_json: str) -> None:
        self._db.execute(
            "INSERT OR REPLACE INTO session_states (id, state_json, updated_at) VALUES (?, ?, ?)",
            (session_id, state_json, _iso()),
        )

    def get(self, session_id: str) -> str | None:
        row = self._db.query_one(
            "SELECT state_json FROM session_states WHERE id = ?",
            (session_id,),
        )
        if row is None:
            return None
        return str(row["state_json"])

    def delete(self, session_id: str) -> None:
        self._db.execute("DELETE FROM session_states WHERE id = ?", (session_id,))
