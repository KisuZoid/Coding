"""Cleanup service tests (Phase C): never touches consented training data."""

from __future__ import annotations

import io
from datetime import UTC, datetime, timedelta
from pathlib import Path

from PIL import Image

from apps.api.storage import (
    ConsentDecision,
    Database,
    FsSqliteImageStore,
    SessionCleanup,
    SQLiteConsentStore,
    SQLiteSessionStore,
    SQLiteTrainingSampleStore,
)
from apps.api.storage.records import ImageKind


def _jpeg() -> bytes:
    out = io.BytesIO()
    Image.new("RGB", (32, 32), (10, 10, 200)).save(out, format="JPEG")
    return out.getvalue()


def _world(
    tmp_path: Path,
) -> tuple[SessionCleanup, Database, Path, SQLiteSessionStore]:
    db = Database(tmp_path / "app.db")
    root = tmp_path / "media"
    images = FsSqliteImageStore(db, root)
    sessions = SQLiteSessionStore(db)
    cleanup = SessionCleanup(sessions, images)
    return cleanup, db, root, sessions


def test_cleanup_removes_session_but_keeps_training_data(tmp_path: Path) -> None:
    cleanup, db, root, _sessions = _world(tmp_path)
    images = FsSqliteImageStore(db, root)
    consents = SQLiteConsentStore(db)
    samples = SQLiteTrainingSampleStore(db)

    SQLiteSessionStore(db).create("sess-1", ttl=timedelta(hours=1))
    asset = images.write("sess-1", "asset-1", ImageKind.UPLOAD, _jpeg())
    consent = consents.record("sess-1", ConsentDecision.GRANTED, dataset_version="v1")
    sample = samples.add(
        session_id="sess-1",
        consent=consent,
        image_asset_id=asset.asset_id,
        dataset_version="v1",
        labels={"class_id": "1"},
        provenance="user",
    )

    assert cleanup.cleanup("sess-1") is True
    assert not (root / "sess-1").exists()
    assert images.list_session("sess-1") == []
    closed = SQLiteSessionStore(db).get("sess-1")
    assert closed is not None and closed.status.value == "CLOSED"
    assert samples.count() == 1
    assert samples.get(sample.sample_id) is not None
    assert consents.get("sess-1") is not None
    db.close()


def test_cleanup_returns_false_for_unknown_session(tmp_path: Path) -> None:
    cleanup, db, _root, _sessions = _world(tmp_path)
    assert cleanup.cleanup("ghost") is False
    db.close()


def test_sweep_expired_only_cleans_expired_sessions(tmp_path: Path) -> None:
    cleanup, db, root, _sessions = _world(tmp_path)
    images = FsSqliteImageStore(db, root)
    sessions = SQLiteSessionStore(db)
    sessions.create("old", ttl=timedelta(seconds=1))
    images.write("old", "a1", ImageKind.UPLOAD, _jpeg())
    sessions.create("fresh", ttl=timedelta(hours=2))
    images.write("fresh", "a2", ImageKind.UPLOAD, _jpeg())

    later = datetime.now(UTC) + timedelta(minutes=5)
    cleaned = cleanup.sweep_expired(later)
    assert sorted(cleaned) == ["old"]
    old = sessions.get("old")
    fresh = sessions.get("fresh")
    assert old is not None and old.status.value == "CLOSED"
    assert not (root / "old").exists()
    assert fresh is not None and fresh.status.value == "ACTIVE"
    assert (root / "fresh").exists()
    db.close()
