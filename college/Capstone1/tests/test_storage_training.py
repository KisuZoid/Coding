"""Consent + training-sample store tests (Phase C)."""

from __future__ import annotations

from pathlib import Path

from apps.api.storage import (
    AnnotationStatus,
    ConsentDecision,
    Database,
    SQLiteConsentStore,
    SQLiteTrainingSampleStore,
)


def _stores(tmp_path: Path) -> tuple[Database, SQLiteConsentStore, SQLiteTrainingSampleStore]:
    db = Database(tmp_path / "app.db")
    return db, SQLiteConsentStore(db), SQLiteTrainingSampleStore(db)


def test_consent_record_and_get(tmp_path: Path) -> None:
    db, consents, _samples = _stores(tmp_path)
    record = consents.record("sess-1", ConsentDecision.GRANTED, dataset_version="v1")
    assert record.decision == ConsentDecision.GRANTED
    assert record.dataset_version == "v1"
    got = consents.get("sess-1")
    assert got is not None and got.decision == ConsentDecision.GRANTED
    db.close()


def test_consent_upsert_updates_decision(tmp_path: Path) -> None:
    db, consents, _samples = _stores(tmp_path)
    consents.record("sess-1", ConsentDecision.DECLINED)
    consents.record("sess-1", ConsentDecision.GRANTED)
    got = consents.get("sess-1")
    assert got is not None and got.decision == ConsentDecision.GRANTED
    db.close()


def test_training_sample_add_get_count_list(tmp_path: Path) -> None:
    db, consents, samples = _stores(tmp_path)
    consent = consents.record("sess-1", ConsentDecision.GRANTED)
    sample = samples.add(
        session_id="sess-1",
        consent=consent,
        image_asset_id="asset-1",
        dataset_version="v1",
        labels={"class_id": "1", "bbox": "[10,10,20,20]"},
        provenance="user",
    )
    assert sample.annotation_status == AnnotationStatus.MODEL_SUGGESTED
    assert samples.count() == 1
    got = samples.get(sample.sample_id)
    assert got is not None and got.image_asset_id == "asset-1"
    recent = samples.list_recent()
    assert [s.sample_id for s in recent] == [sample.sample_id]
    db.close()


def test_training_data_persists_across_reopen(tmp_path: Path) -> None:
    path = tmp_path / "app.db"
    db = Database(path)
    consents = SQLiteConsentStore(db)
    samples = SQLiteTrainingSampleStore(db)
    consent = consents.record("sess-1", ConsentDecision.GRANTED, dataset_version="v1")
    samples.add(
        session_id="sess-1",
        consent=consent,
        image_asset_id="asset-1",
        dataset_version="v1",
        labels={"class_id": "2"},
        provenance="user",
    )
    db.close()

    reopened = Database(path)
    assert SQLiteTrainingSampleStore(reopened).count() == 1
    consent_again = SQLiteConsentStore(reopened).get("sess-1")
    assert consent_again is not None and consent_again.decision == ConsentDecision.GRANTED
    reopened.close()
