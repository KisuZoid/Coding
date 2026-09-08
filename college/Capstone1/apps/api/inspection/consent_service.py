"""Training-data consent + sample storage (Phase K).

Optional, always explicit. When a user grants consent, the uploaded image is
copied under ``<training_root>/<dataset_version>/`` and a minimal
``TrainingSample`` row is written (image + labels + provenance + consent +
dataset version). Full chat history and personal identifiers are never stored.
"""

from __future__ import annotations

from pathlib import Path

from apps.api.inspection.context import InspectionContext
from apps.api.storage import (
    ConsentDecision,
    ConsentRecord,
    SQLiteConsentStore,
    SQLiteTrainingSampleStore,
)
from apps.api.storage.image_store import FsSqliteImageStore
from ml.inference.features import DamageFeatures

_CLASS_NAMES_TO_IDS = {
    "dent": 1,
    "scratch": 2,
    "crack": 3,
    "glass shatter": 4,
    "lamp broken": 5,
    "tire flat": 6,
}


class ConsentService:
    """Records a decision and, on GRANTED, persists one training sample."""

    def __init__(
        self,
        consents: SQLiteConsentStore,
        samples: SQLiteTrainingSampleStore,
        images: FsSqliteImageStore,
        training_root: Path,
        dataset_version: str,
    ) -> None:
        self._consents = consents
        self._samples = samples
        self._images = images
        self._training_root = training_root
        self._dataset_version = dataset_version

    def record_decision(
        self,
        session_id: str,
        decision: ConsentDecision,
        dataset_version: str | None = None,
    ) -> ConsentRecord:
        return self._consents.record(
            session_id, decision, dataset_version=dataset_version or self._dataset_version
        )

    def store_training_sample(
        self,
        context: InspectionContext,
        features: DamageFeatures,
        *,
        consent: ConsentRecord,
        image_asset_id: str,
        provenance: str = "MODEL_SUGGESTED",
    ) -> dict[str, object]:
        """Persist the image + labels for a granted consent; None result means skipped."""
        if consent.decision is not ConsentDecision.GRANTED:
            return {"saved": False, "reason": "consent not granted"}
        asset = self._images.get(image_asset_id)
        if asset is None:
            return {"saved": False, "reason": "image asset no longer available"}
        image_bytes = self._images.read(asset)

        sample = self._samples.add(
            session_id=context.session_id,
            consent=consent,
            image_asset_id=image_asset_id,
            dataset_version=self._dataset_version,
            labels=self._build_labels(features),
            provenance=provenance,
        )

        version_dir = self._training_root / self._dataset_version
        version_dir.mkdir(parents=True, exist_ok=True)
        ext = asset.path.suffix or ".png"
        target = version_dir / f"{sample.sample_id}{ext}"
        target.write_bytes(image_bytes)
        return {"saved": True, "sample_id": sample.sample_id, "path": str(target)}

    @staticmethod
    def _build_labels(features: DamageFeatures) -> dict[str, object]:
        classes = {name: _CLASS_NAMES_TO_IDS[name] for name in features.classes_present.values()}
        return {
            "class_ids": classes,
            "num_instances": features.num_instances,
            "damage_area_ratio_image": features.damage_area_ratio_image,
        }
