"""Storage contracts (Phase C).

Typed seams so the local SQLite/filesystem implementation can later be swapped
for PostgreSQL/S3/Supabase without touching application logic (brief mandate
§20, gap report §7). Implementations live in the sibling modules.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timedelta
from pathlib import Path
from typing import Protocol

from apps.api.storage.records import (
    AnnotationStatus,
    ConsentDecision,
    ConsentRecord,
    ImageAssetRecord,
    ImageKind,
    SessionRecord,
    TrainingSampleRecord,
)


class ImageStore(Protocol):
    """Temporary, per-session image storage (filesystem + asset ledger today)."""

    def write(
        self,
        session_id: str,
        asset_id: str,
        kind: ImageKind,
        data: bytes,
        *,
        strip_exif: bool = True,
    ) -> ImageAssetRecord:
        """Validate, normalise (stripping metadata by default) and persist."""
        ...

    def get(self, asset_id: str) -> ImageAssetRecord | None:
        """Look up an asset by id."""
        ...

    def read(self, asset: ImageAssetRecord) -> bytes:
        """Read the stored bytes for a previously written asset."""
        ...

    def list_session(self, session_id: str) -> list[ImageAssetRecord]:
        """All assets belonging to a session."""
        ...

    def delete_session_files(self, session_id: str) -> None:
        """Remove a session's files and asset rows (ephemeral data only)."""
        ...

    def session_root(self, session_id: str) -> Path:
        """Directory a session's files live in (creates it if needed)."""
        ...


class SessionStore(Protocol):
    def create(self, session_id: str, ttl: timedelta | None = None) -> SessionRecord:
        """Open a new ephemeral session."""
        ...

    def get(self, session_id: str) -> SessionRecord | None: ...

    def list_expired(self, now: datetime) -> list[SessionRecord]:
        """Sessions whose expiry has passed (for the cleanup sweep)."""
        ...

    def close(self, session_id: str) -> SessionRecord | None:
        """Soft-close a session; returns the updated record or None."""
        ...


class ConsentStore(Protocol):
    def record(
        self,
        session_id: str,
        decision: ConsentDecision,
        *,
        dataset_version: str | None = None,
    ) -> ConsentRecord:
        """Record or update the training-consent decision for a session."""
        ...

    def get(self, session_id: str) -> ConsentRecord | None: ...


class TrainingSampleStore(Protocol):
    def add(
        self,
        *,
        session_id: str,
        consent: ConsentRecord,
        image_asset_id: str,
        dataset_version: str,
        labels: Mapping[str, str],
        provenance: str,
        annotation_status: AnnotationStatus = AnnotationStatus.MODEL_SUGGESTED,
    ) -> TrainingSampleRecord:
        """Persist one consented training sample under a dataset version."""
        ...

    def get(self, sample_id: str) -> TrainingSampleRecord | None: ...

    def count(self) -> int: ...

    def list_recent(self, limit: int = 100) -> list[TrainingSampleRecord]: ...
