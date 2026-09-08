"""SQLite-backed consent and training-sample stores (Phase C).

The consented training side is kept fully separate from ephemeral session
bookkeeping: separate tables, no FK cascade from session cleanup, and an
explicit consent record gating every sample. Sampling into the CarDD-style
dataset happens in a later phase.
"""

from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import UTC, datetime

from apps.api.storage.database import Database
from apps.api.storage.records import (
    AnnotationStatus,
    ConsentDecision,
    ConsentRecord,
    TrainingSampleRecord,
)


def _iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC).isoformat()


def _now() -> datetime:
    return datetime.now(UTC)


def _consent_from_row(row: sqlite3.Row) -> ConsentRecord:
    return ConsentRecord(
        session_id=row["session_id"],
        decision=ConsentDecision(row["decision"]),
        dataset_version=row["dataset_version"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


def _sample_from_row(row: sqlite3.Row) -> TrainingSampleRecord:
    return TrainingSampleRecord(
        sample_id=row["id"],
        session_id=row["session_id"],
        consent_id=row["consent_id"],
        dataset_version=row["dataset_version"],
        annotation_status=AnnotationStatus(row["annotation_status"]),
        provenance=row["provenance"],
        image_asset_id=row["image_asset_id"],
        labels_json=row["labels_json"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


class SQLiteConsentStore:
    """One consent record per session (upserts on the session's consent id)."""

    def __init__(self, db: Database) -> None:
        self._db = db

    def record(
        self,
        session_id: str,
        decision: ConsentDecision,
        *,
        dataset_version: str | None = None,
    ) -> ConsentRecord:
        record = ConsentRecord(
            session_id=session_id,
            decision=decision,
            dataset_version=dataset_version,
            created_at=_now(),
        )
        self._db.execute(
            "INSERT OR REPLACE INTO consent_records "
            "(id, session_id, decision, dataset_version, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                session_id,
                session_id,
                decision.value,
                dataset_version,
                _iso(record.created_at),
            ),
        )
        return record

    def get(self, session_id: str) -> ConsentRecord | None:
        row = self._db.query_one(
            "SELECT session_id, decision, dataset_version, created_at "
            "FROM consent_records WHERE id = ?",
            (session_id,),
        )
        if row is None:
            return None
        return _consent_from_row(row)


class SQLiteTrainingSampleStore:
    def __init__(self, db: Database) -> None:
        self._db = db

    def add(
        self,
        *,
        session_id: str,
        consent: ConsentRecord,
        image_asset_id: str,
        dataset_version: str,
        labels: dict[str, object],
        provenance: str,
        annotation_status: AnnotationStatus = AnnotationStatus.MODEL_SUGGESTED,
    ) -> TrainingSampleRecord:
        sample_id = uuid.uuid4().hex
        created_at = _now()
        self._db.execute(
            "INSERT INTO training_samples "
            "(id, session_id, consent_id, dataset_version, annotation_status, "
            " provenance, image_asset_id, labels_json, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                sample_id,
                session_id,
                consent.session_id,
                dataset_version,
                annotation_status.value,
                provenance,
                image_asset_id,
                json.dumps(labels, sort_keys=True),
                _iso(created_at),
            ),
        )
        return TrainingSampleRecord(
            sample_id=sample_id,
            session_id=session_id,
            consent_id=consent.session_id,
            dataset_version=dataset_version,
            annotation_status=annotation_status,
            provenance=provenance,
            image_asset_id=image_asset_id,
            labels_json=json.dumps(labels, sort_keys=True),
            created_at=created_at,
        )

    def get(self, sample_id: str) -> TrainingSampleRecord | None:
        row = self._db.query_one(
            "SELECT id, session_id, consent_id, dataset_version, annotation_status, "
            " provenance, image_asset_id, labels_json, created_at "
            "FROM training_samples WHERE id = ?",
            (sample_id,),
        )
        if row is None:
            return None
        return _sample_from_row(row)

    def count(self) -> int:
        row = self._db.query_one("SELECT COUNT(*) AS n FROM training_samples")
        if row is None:
            return 0
        return int(row["n"])

    def list_recent(self, limit: int = 100) -> list[TrainingSampleRecord]:
        rows = self._db.query_all(
            "SELECT id, session_id, consent_id, dataset_version, annotation_status, "
            " provenance, image_asset_id, labels_json, created_at "
            "FROM training_samples ORDER BY created_at DESC LIMIT ?",
            (limit,),
        )
        return [_sample_from_row(row) for row in rows]
