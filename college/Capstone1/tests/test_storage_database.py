"""Storage plumbing tests (Phase C): sqlite Database + DATABASE_URL resolution."""

from __future__ import annotations

from pathlib import Path

from apps.api.storage.database import Database, is_valid_id, resolve_database_path


def test_resolve_database_path_defaults_under_storage_root(tmp_path: Path) -> None:
    assert resolve_database_path("", tmp_path) == tmp_path / "app.db"


def test_resolve_database_path_parses_sqlite_url(tmp_path: Path) -> None:
    path = tmp_path / "custom" / "db.sqlite"
    assert resolve_database_path(f"sqlite:///{path}", tmp_path) == path


def test_resolve_database_path_rejects_unsupported_urls() -> None:
    try:
        resolve_database_path("postgresql://host:5432/db", Path("/tmp"))
    except ValueError:
        return
    raise AssertionError("expected postgresql URL to be rejected pre-ADR")


def test_database_init_is_idempotent(tmp_path: Path) -> None:
    path = tmp_path / "app.db"
    Database(path)
    second = Database(path)
    second.close()


def test_database_roundtrip_and_schema_isolation(tmp_path: Path) -> None:
    path = tmp_path / "app.db"
    db = Database(path)
    insert = "INSERT INTO sessions (id, status, created_at) VALUES (?, ?, ?)"
    db.execute(insert, ("s1", "ACTIVE", "now"))
    row = db.query_one("SELECT id, status FROM sessions WHERE id = ?", ("s1",))
    assert row is not None and row["status"] == "ACTIVE"
    assert db.query_one("SELECT id FROM sessions WHERE id = ?", ("nope",)) is None
    db.close()


def test_is_valid_id_whitelist() -> None:
    assert is_valid_id("a1B_-c")
    assert not is_valid_id("../escape")
    assert not is_valid_id("a/b")
    assert not is_valid_id("")
