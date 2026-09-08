"""Session lifecycle tests (Phase C): SQLiteSessionStore."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

from apps.api.storage import Database, SQLiteSessionStore
from apps.api.storage.records import SessionStatus


def _store(tmp_path: Path) -> tuple[SQLiteSessionStore, Database]:
    db = Database(tmp_path / "app.db")
    return SQLiteSessionStore(db), db


def test_create_and_get_roundtrip(tmp_path: Path) -> None:
    store, db = _store(tmp_path)
    record = store.create("abc-123")
    assert record.session_id == "abc-123"
    assert record.status == SessionStatus.ACTIVE
    assert record.expires_at is not None and record.expires_at > record.created_at
    got = store.get("abc-123")
    assert got is not None and got.session_id == "abc-123"
    assert store.get("missing") is None
    db.close()


def test_ttl_defaults_and_override(tmp_path: Path) -> None:
    store, db = _store(tmp_path)
    short = store.create("short", ttl=timedelta(seconds=1))
    assert short.expires_at is not None
    assert short.expires_at - short.created_at == timedelta(seconds=1)
    db.close()


def test_close_soft_closes_session(tmp_path: Path) -> None:
    store, db = _store(tmp_path)
    store.create("c1")
    closed = store.close("c1")
    assert closed is not None and closed.status == SessionStatus.CLOSED
    db.close()


def test_list_expired_only_returns_expired(tmp_path: Path) -> None:
    store, db = _store(tmp_path)
    store.create("expired", ttl=timedelta(seconds=1))
    store.create("still-live", ttl=timedelta(hours=1))
    future = datetime.now(UTC) + timedelta(seconds=30)
    expired_ids = {r.session_id for r in store.list_expired(future)}
    assert expired_ids == {"expired"}
    db.close()


def test_invalid_session_id_rejected(tmp_path: Path) -> None:
    store, db = _store(tmp_path)
    try:
        store.create("../escape")
    except ValueError:
        return
    finally:
        db.close()
    raise AssertionError("expected invalid session id to be rejected")
