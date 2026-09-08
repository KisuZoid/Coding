"""Storage package (Phase C): interfaces, SQLite/fs implementations, cleanup."""

from __future__ import annotations

from apps.api.storage.cleanup import SessionCleanup
from apps.api.storage.database import Database, resolve_database_path
from apps.api.storage.image_store import FsSqliteImageStore, ImageValidationError
from apps.api.storage.records import (
    AnnotationStatus,
    ConsentDecision,
    ConsentRecord,
    ImageAssetRecord,
    ImageKind,
    SessionRecord,
    SessionStatus,
    TrainingSampleRecord,
)
from apps.api.storage.session_store import SQLiteSessionStore
from apps.api.storage.state_store import SQLiteStateStore
from apps.api.storage.training_store import SQLiteConsentStore, SQLiteTrainingSampleStore

__all__ = [
    "AnnotationStatus",
    "ConsentDecision",
    "ConsentRecord",
    "Database",
    "FsSqliteImageStore",
    "ImageAssetRecord",
    "ImageKind",
    "ImageValidationError",
    "SQLiteConsentStore",
    "SQLiteSessionStore",
    "SQLiteStateStore",
    "SQLiteTrainingSampleStore",
    "SessionCleanup",
    "SessionRecord",
    "SessionStatus",
    "TrainingSampleRecord",
    "resolve_database_path",
]
