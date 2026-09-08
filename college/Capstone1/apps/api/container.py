"""Dependency container: wires settings, stores, services, and the workflow.

Built once at app startup (``apps.api.main``); routers receive it through
``request.app.state.container``. The torch model remains lazy so tests that never
hit ``/analyze`` don't pay the CPU load cost.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from apps.api.agent.graph import Services, build_workflow
from apps.api.agent.groq_service import GroqService, build_groq_service
from apps.api.cost.cost_estimator import UnavailableCostEstimator
from apps.api.inspection.consent_service import ConsentService
from apps.api.repair.repair_estimator import DemoRepairEstimator
from apps.api.settings import Settings, get_settings
from apps.api.storage import (
    Database,
    FsSqliteImageStore,
    SessionCleanup,
    SQLiteConsentStore,
    SQLiteSessionStore,
    SQLiteStateStore,
    SQLiteTrainingSampleStore,
    resolve_database_path,
)
from ml.inference.engine import SegmentationEngine

_REGISTRY = Path("ml/experiments/registry.json")
_DEFAULT_CHECKPOINT = Path("ml/experiments/cardd_baseline_ce/best_checkpoint.pt")


def _load_checkpoint(directory: Path) -> tuple[str, int]:
    """Read base + epoch straight from the artefact (never guessed)."""
    ckpt = Path(directory) / "best_checkpoint.pt"
    if not ckpt.is_file():
        raise FileNotFoundError(f"checkpoint not found: {ckpt}")
    import torch

    data = torch.load(str(ckpt), map_location="cpu", weights_only=False)
    base = data.get("base", 64)
    return str(ckpt), int(base)


def _registry_meta(directory: Path) -> tuple[str | None, float | None]:
    """Look up the committed run's git revision + val mIoU from registry.json."""
    if not _REGISTRY.is_file():
        return None, None
    try:
        runs = json.loads(_REGISTRY.read_text())
    except json.JSONDecodeError:
        return None, None
    prefix = f"{directory.name}-"
    for run in runs:
        if run.get("experiment_id", "").startswith(prefix):
            return run.get("git_revision"), run.get("best_val_mean_iou")
    return None, None


@dataclass
class Container:
    settings: Settings
    db: Database
    sessions: SQLiteSessionStore
    images: FsSqliteImageStore
    consents: SQLiteConsentStore
    training_samples: SQLiteTrainingSampleStore
    states: SQLiteStateStore
    cleanup: SessionCleanup
    consent: ConsentService
    repair: DemoRepairEstimator
    cost: UnavailableCostEstimator
    groq: GroqService
    workflow: object
    _engine: SegmentationEngine | None = None

    def engine(self) -> SegmentationEngine:
        if self._engine is None:
            checkpoint_path = Path(self.settings.model_path or _DEFAULT_CHECKPOINT)
            directory = checkpoint_path.parent if checkpoint_path.is_file() else None
            git_revision, iou = _registry_meta(directory) if directory else (None, None)

            base = 64
            if checkpoint_path.is_file():
                import torch

                data = torch.load(str(checkpoint_path), map_location="cpu", weights_only=False)
                if isinstance(data.get("base"), int):
                    base = data["base"]

            notes: tuple[str, ...] | None = None
            if iou is not None:
                notes = (
                    f"Demo-grade baseline (CarDD, underfit): validation mIoU ~{iou:.4f}.",
                    "Per-pixel predictions are preliminary; not verified damage extent.",
                    "Mask-derived severity is 'not currently reliable' for this model.",
                )
            self._engine = SegmentationEngine.from_checkpoint(
                checkpoint_path,
                model_version=self.settings.model_version or None,
                experiment_id=directory.name if directory else "unknown",
                git_revision=git_revision,
                base=base,
                baseline_notes=notes,
            )
        return self._engine


def build_container(settings: Settings | None = None) -> Container:
    settings = settings or get_settings()
    storage_root = settings.storage_root
    db_path = resolve_database_path(settings.database_url, storage_root)
    db = Database(db_path)

    sessions = SQLiteSessionStore(db)
    images = FsSqliteImageStore(db, storage_root)
    consents = SQLiteConsentStore(db)
    training_samples = SQLiteTrainingSampleStore(db)
    states = SQLiteStateStore(db)

    consent = ConsentService(
        consents,
        training_samples,
        images,
        settings.training_root,
        settings.training_dataset_version,
    )
    repair = DemoRepairEstimator()
    cost = UnavailableCostEstimator()
    groq = build_groq_service(settings)
    workflow = build_workflow(
        Services(
            groq=groq,
            repair_estimator=repair,
            cost_estimator=cost,
            consent=consent,
            allow_synthetic=settings.allow_synthetic_estimate,
        )
    )

    return Container(
        settings=settings,
        db=db,
        sessions=sessions,
        images=images,
        consents=consents,
        training_samples=training_samples,
        states=states,
        cleanup=SessionCleanup(sessions, images),
        consent=consent,
        repair=repair,
        cost=cost,
        groq=groq,
        workflow=workflow,
    )
