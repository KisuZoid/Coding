"""Ephemeral-session cleanup service (Phase C).

Encapsulates the mand-ate §17 invariant: closing or expiring an inspection
session removes its images and asset ledger rows, while consented training
samples (and their consent records) are never touched. Wiring a scheduler or an
API endpoint to this service happens in a later phase.
"""

from __future__ import annotations

from datetime import UTC, datetime

from apps.api.storage.interfaces import ImageStore, SessionStore


class SessionCleanup:
    def __init__(self, sessions: SessionStore, images: ImageStore) -> None:
        self._sessions = sessions
        self._images = images

    def cleanup(self, session_id: str) -> bool:
        """Close one session and delete its files/session rows. Returns False
        if the session never existed."""
        if self._sessions.get(session_id) is None:
            return False
        self._images.delete_session_files(session_id)
        self._sessions.close(session_id)
        return True

    def sweep_expired(self, now: datetime | None = None) -> list[str]:
        """Close and clean all expired sessions; returns their ids."""
        now = now or datetime.now(UTC)
        cleaned: list[str] = []
        for record in self._sessions.list_expired(now):
            self._images.delete_session_files(record.session_id)
            self._sessions.close(record.session_id)
            cleaned.append(record.session_id)
        return cleaned
