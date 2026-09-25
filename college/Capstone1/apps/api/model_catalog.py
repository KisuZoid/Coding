from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_ID = "final60_hybrid_seed42"
LEGACY_MODEL_ID = "legacy_configured"

ModelStatus = Literal["CONTROLLED", "EXPLORATORY"]
ModelFamily = Literal["baseline", "hybrid"]


class UnknownModelError(ValueError):
    def __init__(self, model_id: str) -> None:
        super().__init__(f"unknown model id: {model_id}")


@dataclass(frozen=True, slots=True)
class ModelSpec:
    model_id: str
    label: str
    family: ModelFamily
    architecture: str
    seed: int
    configured_epochs: int
    status: ModelStatus
    experiment_id: str
    checkpoint: Path
    run_record: Path
    description: str

    @property
    def relative_checkpoint(self) -> str:
        return self.checkpoint.relative_to(REPOSITORY_ROOT).as_posix()

    def public_info(self) -> dict[str, Any]:
        record = self._read_record()
        best_metric = record.get("best_val_foreground_miou")
        best_epoch = record.get("best_epoch")
        git_revision = record.get("git_revision")
        record_status = record.get("record_status")
        return {
            "model_id": self.model_id,
            "label": self.label,
            "family": self.family,
            "architecture": self.architecture,
            "seed": self.seed,
            "configured_epochs": self.configured_epochs,
            "status": self.status,
            "controlled": self.status == "CONTROLLED",
            "available": self.checkpoint.is_file(),
            "checkpoint": self.relative_checkpoint,
            "experiment_id": self.experiment_id,
            "best_val_foreground_miou": (
                float(best_metric) if isinstance(best_metric, int | float) else None
            ),
            "best_epoch": best_epoch if isinstance(best_epoch, int) else None,
            "git_revision": git_revision if isinstance(git_revision, str) else None,
            "record_status": (
                record_status
                if isinstance(record_status, str)
                else ("recorded" if record else "checkpoint_metadata_only")
            ),
            "description": self.description,
        }

    def _read_record(self) -> dict[str, Any]:
        if not self.run_record.is_file():
            return {}
        try:
            value = json.loads(self.run_record.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return value if isinstance(value, dict) else {}


def _spec(
    model_id: str,
    label: str,
    family: ModelFamily,
    architecture: str,
    seed: int,
    configured_epochs: int,
    status: ModelStatus,
    experiment_id: str,
    description: str,
) -> ModelSpec:
    experiment_dir = REPOSITORY_ROOT / "ml" / "experiments" / model_id
    return ModelSpec(
        model_id=model_id,
        label=label,
        family=family,
        architecture=architecture,
        seed=seed,
        configured_epochs=configured_epochs,
        status=status,
        experiment_id=experiment_id,
        checkpoint=experiment_dir / "best_checkpoint.pt",
        run_record=experiment_dir / "run_record.json",
        description=description,
    )


MODEL_SPECS: tuple[ModelSpec, ...] = (
    _spec(
        "final60_baseline_seed42",
        "Final 60 · ResNet34 U-Net · seed 42",
        "baseline",
        "resnet34_unet",
        42,
        60,
        "CONTROLLED",
        "final60_baseline_seed42",
        "Controlled 60-epoch baseline run; its validation result is model-specific.",
    ),
    _spec(
        "final60_baseline_seed1337",
        "Final 60 · ResNet34 U-Net · seed 1337",
        "baseline",
        "resnet34_unet",
        1337,
        60,
        "CONTROLLED",
        "final60_baseline_seed1337",
        "Controlled 60-epoch baseline run; its validation result is model-specific.",
    ),
    _spec(
        "final60_hybrid_seed42",
        "Final 60 · Hybrid · seed 42",
        "hybrid",
        "hybrid_segmentation",
        42,
        60,
        "CONTROLLED",
        "final60_hybrid_seed42",
        "Controlled 60-epoch hybrid run; its validation result is model-specific.",
    ),
    _spec(
        "final60_hybrid_seed1337",
        "Final 60 · Hybrid · seed 1337",
        "hybrid",
        "hybrid_segmentation",
        1337,
        60,
        "CONTROLLED",
        "final60_hybrid_seed1337",
        "Controlled 60-epoch hybrid run; its validation result is model-specific.",
    ),
    _spec(
        "final100_hybrid_seed42",
        "Final 100 · Hybrid · seed 42 · exploratory",
        "hybrid",
        "hybrid_segmentation",
        42,
        100,
        "EXPLORATORY",
        "final100_hybrid_seed42",
        "Exploratory continuation resumed from final60_hybrid_seed42; not a matched comparison.",
    ),
)

MODEL_BY_ID = {spec.model_id: spec for spec in MODEL_SPECS}
MODEL_IDS = tuple(MODEL_BY_ID)


def get_model_spec(model_id: str) -> ModelSpec:
    try:
        return MODEL_BY_ID[model_id]
    except KeyError as exc:
        raise UnknownModelError(model_id) from exc


def public_model_infos() -> list[dict[str, Any]]:
    return [spec.public_info() for spec in MODEL_SPECS]
