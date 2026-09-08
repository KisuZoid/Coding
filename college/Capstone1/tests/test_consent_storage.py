"""Phase K: consent gating + training-sample persistence + state store."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from apps.api.inspection.consent_service import ConsentService
from apps.api.inspection.context import InspectionContext
from apps.api.storage import (
    ConsentDecision,
    Database,
    FsSqliteImageStore,
    SQLiteConsentStore,
    SQLiteStateStore,
    SQLiteTrainingSampleStore,
)
from apps.api.storage.records import ImageKind
from ml.inference.features import DamageFeatures


def _png() -> bytes:
    ok, buf = cv2.imencode(".png", np.full((4, 4, 3), 200, dtype=np.uint8))
    assert ok
    return buf.tobytes()


def _make(tmp_path: Path) -> tuple[Database, FsSqliteImageStore, Path, ConsentService]:
    db = Database(tmp_path / "app.db")
    images = FsSqliteImageStore(db, tmp_path / "data")
    training_root = tmp_path / "training"
    consent = ConsentService(
        SQLiteConsentStore(db),
        SQLiteTrainingSampleStore(db),
        images,
        training_root,
        "user-consented-v1",
    )
    return db, images, training_root, consent


def _context() -> InspectionContext:
    return InspectionContext(session_id="sess001")


def _features() -> DamageFeatures:
    return DamageFeatures(
        width=8,
        height=8,
        instances=[],
        damage_area_ratio_image=0.05,
        per_class_area_ratio_image={1: 0.05},
        classes_present={1: "dent"},
        num_instances=1,
        low_confidence_instances=0,
        mask=np.zeros((1, 1), dtype=np.uint8),
    )


def test_declined_consent_never_stores_sample(tmp_path: Path) -> None:
    _, images, training_root, service = _make(tmp_path)
    asset = images.write("sess001", "a1", ImageKind.UPLOAD, _png())
    record = service.record_decision("sess001", ConsentDecision.DECLINED)
    result = service.store_training_sample(
        _context(), _features(), consent=record, image_asset_id=asset.asset_id
    )
    assert result["saved"] is False
    assert not (training_root / "user-consented-v1").exists()


def test_granted_consent_stores_png_sample_and_record(tmp_path: Path) -> None:
    db, images, training_root, service = _make(tmp_path)
    asset = images.write("sess001", "a1", ImageKind.UPLOAD, _png())
    record = service.record_decision("sess001", ConsentDecision.GRANTED)
    result = service.store_training_sample(
        _context(), _features(), consent=record, image_asset_id=asset.asset_id
    )
    assert result["saved"] is True
    sample_id = str(result["sample_id"])
    stored = training_root / "user-consented-v1" / f"{sample_id}.png"
    assert stored.is_file()
    assert stored.read_bytes().startswith(b"\x89PNG")
    row = SQLiteTrainingSampleStore(db).get(sample_id)
    assert row is not None
    assert row.provenance == "MODEL_SUGGESTED"
    assert "dent" in row.labels_json


def test_state_store_roundtrip(tmp_path: Path) -> None:
    db = Database(tmp_path / "app.db")
    store = SQLiteStateStore(db)
    store.save("sess001", '{"a": 1}')
    assert store.get("sess001") == '{"a": 1}'
    store.delete("sess001")
    assert store.get("sess001") is None
