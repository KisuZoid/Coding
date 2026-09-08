"""Session-scoped filesystem image store (Phase C).

Owns the ephemeral image lifecycle: upload bytes are validated, normalised
re-encoded so location/EXIF metadata is stripped by default, stored under
``<root>/<session_id>/``, and ledgered in SQLite for auditability. Deleting a
session removes its files and asset rows only — the training side (consent,
samples) lives in separate tables and is never touched here.
"""

from __future__ import annotations

import io
import shutil
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from apps.api.storage.database import Database, is_valid_id
from apps.api.storage.records import ImageAssetRecord, ImageKind

_ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
_EXTENSIONS = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp"}

_DEFAULT_MAX_BYTES = 15 * 1024 * 1024


class ImageValidationError(ValueError):
    """Raised when stored bytes are not a valid, allowed image."""


def normalize_image(
    data: bytes,
    *,
    max_bytes: int = _DEFAULT_MAX_BYTES,
    strip_exif: bool = True,
) -> tuple[bytes, str]:
    """Validate and re-encode image bytes, removing metadata by default."""
    if len(data) > max_bytes:
        raise ImageValidationError(f"image too large: {len(data)} bytes > {max_bytes} bytes")
    try:
        with Image.open(io.BytesIO(data)) as probe:
            probe.verify()
            fmt = probe.format
    except (UnidentifiedImageError, OSError) as exc:
        raise ImageValidationError("invalid image data") from exc
    if fmt not in _ALLOWED_FORMATS:
        raise ImageValidationError(f"unsupported image format: {fmt!r}")

    with Image.open(io.BytesIO(data)) as opened:
        img: Image.Image = opened
        if img.mode != "RGB":
            img = img.convert("RGB")
        out = io.BytesIO()
        if strip_exif or fmt == "PNG":
            img.save(out, format=fmt)
            return out.getvalue(), fmt or "JPEG"
        exif = img.getexif().tobytes()
        if fmt == "WEBP":
            img.save(out, format="WEBP", exif=exif)
        else:
            img.save(out, format=fmt, exif=exif)
        return out.getvalue(), fmt or "JPEG"


def _from_row(row: sqlite3.Row, root: Path) -> ImageAssetRecord:
    return ImageAssetRecord(
        asset_id=row["id"],
        session_id=row["session_id"],
        kind=ImageKind(row["kind"]),
        path=root / row["relative_path"],
        created_at=datetime.fromisoformat(row["created_at"]),
    )


class FsSqliteImageStore:
    """Filesystem-backed ImageStore with a SQLite asset ledger."""

    def __init__(
        self,
        db: Database,
        root: Path,
        max_bytes: int = _DEFAULT_MAX_BYTES,
    ) -> None:
        self._db = db
        self._root = root
        self.max_bytes = max_bytes

    def _resolve(self, rel: Path) -> Path:
        target = (self._root / rel).resolve()
        if not target.is_relative_to(self._root.resolve()):
            raise ValueError("asset path escapes storage root")
        return target

    def session_root(self, session_id: str) -> Path:
        if not is_valid_id(session_id):
            raise ValueError(f"invalid session id: {session_id!r}")
        path = self._root / session_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write(
        self,
        session_id: str,
        asset_id: str,
        kind: ImageKind,
        data: bytes,
        *,
        strip_exif: bool = True,
    ) -> ImageAssetRecord:
        if not is_valid_id(session_id):
            raise ValueError(f"invalid session id: {session_id!r}")
        if not is_valid_id(asset_id):
            raise ValueError(f"invalid asset id: {asset_id!r}")
        normalized, fmt = normalize_image(data, max_bytes=self.max_bytes, strip_exif=strip_exif)
        rel = Path(session_id) / f"{asset_id}{_EXTENSIONS[fmt]}"
        target = self._resolve(rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(normalized)
        now = datetime.now(UTC)
        self._db.execute(
            "INSERT OR REPLACE INTO image_assets "
            "(id, session_id, kind, relative_path, created_at) VALUES (?, ?, ?, ?, ?)",
            (asset_id, session_id, kind.value, rel.as_posix(), now.isoformat()),
        )
        return ImageAssetRecord(
            asset_id=asset_id,
            session_id=session_id,
            kind=kind,
            path=target,
            created_at=now,
        )

    def get(self, asset_id: str) -> ImageAssetRecord | None:
        row = self._db.query_one(
            "SELECT id, session_id, kind, relative_path, created_at FROM image_assets WHERE id = ?",
            (asset_id,),
        )
        if row is None:
            return None
        return _from_row(row, self._root)

    def read(self, asset: ImageAssetRecord) -> bytes:
        rel = asset.path.relative_to(self._root)
        target = self._resolve(rel)
        if not target.is_file():
            raise FileNotFoundError(f"asset file missing: {target}")
        return target.read_bytes()

    def list_session(self, session_id: str) -> list[ImageAssetRecord]:
        rows = self._db.query_all(
            "SELECT id, session_id, kind, relative_path, created_at "
            "FROM image_assets WHERE session_id = ? ORDER BY created_at",
            (session_id,),
        )
        return [_from_row(row, self._root) for row in rows]

    def delete_session_files(self, session_id: str) -> None:
        if not is_valid_id(session_id):
            raise ValueError(f"invalid session id: {session_id!r}")
        shutil.rmtree(self._root / session_id, ignore_errors=True)
        self._db.execute("DELETE FROM image_assets WHERE session_id = ?", (session_id,))
