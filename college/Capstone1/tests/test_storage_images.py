"""Image store tests (Phase C): validation, EXIF stripping, lifecycle, safety."""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from PIL import Image

from apps.api.storage import Database, FsSqliteImageStore, ImageValidationError
from apps.api.storage.records import ImageKind


def _jpeg_with_exif() -> bytes:
    img = Image.new("RGB", (64, 64), (200, 30, 30))
    exif = img.getexif()
    exif[0x0110] = "CameraModel-X"
    out = io.BytesIO()
    img.save(out, format="JPEG", exif=exif)
    return out.getvalue()


def _store(tmp_path: Path) -> tuple[FsSqliteImageStore, Database, Path]:
    root = tmp_path / "media"
    db = Database(tmp_path / "app.db")
    return FsSqliteImageStore(db, root), db, root


def test_write_read_roundtrip(tmp_path: Path) -> None:
    store, db, _root = _store(tmp_path)
    asset = store.write("sess-1", "asset-1", ImageKind.UPLOAD, _jpeg_with_exif())
    assert asset.path.is_file()
    assert asset.kind == ImageKind.UPLOAD
    assert store.read(asset) == asset.path.read_bytes()
    assert store.get("asset-1") is not None
    assert store.get("missing") is None
    db.close()


def test_read_roundtrip_with_relative_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Production defaults use a relative storage root; records fetched back
    must resolve inside that root once, never double-nested (storage/storage)."""
    monkeypatch.chdir(tmp_path)
    db = Database(tmp_path / "app.db")
    store = FsSqliteImageStore(db, Path("storage"))
    asset = store.write("sess-1", "asset-r", ImageKind.UPLOAD, _jpeg_with_exif())
    reloaded = store.get("asset-r")
    assert reloaded is not None
    assert store.read(reloaded) == asset.path.read_bytes()
    db.close()


def test_write_strips_exif_by_default(tmp_path: Path) -> None:
    store, db, _root = _store(tmp_path)
    asset = store.write("sess-1", "asset-2", ImageKind.UPLOAD, _jpeg_with_exif())
    with Image.open(asset.path) as reloaded:
        exif = reloaded.getexif()
        assert 0x0110 not in exif
    db.close()


def test_write_preserves_exif_when_requested(tmp_path: Path) -> None:
    store, db, _root = _store(tmp_path)
    asset = store.write(
        "sess-1",
        "asset-3",
        ImageKind.UPLOAD,
        _jpeg_with_exif(),
        strip_exif=False,
    )
    with Image.open(asset.path) as reloaded:
        assert reloaded.getexif().get(0x0110) == "CameraModel-X"
    db.close()


def test_rejects_non_image_and_unsupported_format(tmp_path: Path) -> None:
    store, db, _root = _store(tmp_path)
    try:
        store.write("sess-1", "bad-1", ImageKind.UPLOAD, b"not an image")
    except ImageValidationError:
        pass
    else:
        raise AssertionError("expected ImageValidationError for non-image")
    try:
        store.write("sess-1", "bad-2", ImageKind.UPLOAD, b"%PDF-1.4 fake")
    except ImageValidationError:
        pass
    else:
        raise AssertionError("expected ImageValidationError for PDF bytes")
    db.close()


def test_rejects_oversized_image(tmp_path: Path) -> None:
    db = Database(tmp_path / "app.db")
    store = FsSqliteImageStore(db, tmp_path / "media", max_bytes=512)
    big = Image.new("RGB", (256, 256), (30, 100, 200))
    out = io.BytesIO()
    big.save(out, format="JPEG", quality=100)
    data = out.getvalue()
    assert len(data) > 512
    try:
        store.write("sess-1", "big-1", ImageKind.UPLOAD, data)
    except ImageValidationError:
        pass
    else:
        raise AssertionError("expected ImageValidationError for oversized image")
    db.close()


def test_rejects_path_traversal_ids(tmp_path: Path) -> None:
    store, db, _root = _store(tmp_path)
    for bad_id in ("../escape", "a/b", ""):
        try:
            store.write(bad_id, "asset-x", ImageKind.UPLOAD, b"")
        except (ValueError, ImageValidationError):
            continue
        raise AssertionError(f"expected rejection for id {bad_id!r}")
    db.close()


def test_read_guards_session_scope(tmp_path: Path) -> None:
    store, db, _root = _store(tmp_path)
    store.write("sess-1", "asset-4", ImageKind.UPLOAD, _jpeg_with_exif())
    listing = store.list_session("sess-1")
    assert [a.asset_id for a in listing] == ["asset-4"]
    assert store.list_session("other") == []
    db.close()


def test_delete_session_files_removes_only_that_session(tmp_path: Path) -> None:
    store, db, root = _store(tmp_path)
    store.write("sess-1", "a1", ImageKind.UPLOAD, _jpeg_with_exif())
    store.write("sess-2", "a2", ImageKind.UPLOAD, _jpeg_with_exif())
    assert (root / "sess-1").exists()
    store.delete_session_files("sess-1")
    assert not (root / "sess-1").exists()
    assert store.list_session("sess-1") == []
    survivor = store.get("a2")
    assert survivor is not None and store.read(survivor)
    db.close()
