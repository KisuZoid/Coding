"""Dependency container: wires settings, stores, services, and the workflow.

Built once at app startup (``apps.api.main``); routers receive it through
``request.app.state.container``. The torch model stays lazy so tests that never
hit ``/analyze`` don't pay the CPU load cost.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from apps.api.agent.assistant import AssistantService, build_assistant
from apps.api.agent.graph import Services, build_workflow
from apps.api.inspection.consent_service import ConsentService
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

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_REGISTRY = Path("ml/experiments/registry.json")
_DEFAULT_CHECKPOINT = Path("ml/experiments/pilot15_hybrid/best_checkpoint.pt")


def _norm_path(candidate: Path) -> Path:
    """Resolve a possibly-relative artefact path regardless of the process CWD.

    Absolute paths are returned unchanged. Relative paths resolve against the
    current working directory when the file is found there, and otherwise
    against the repository root — so the backend fails loudly with a concrete
    path instead of silently pointing at a different directory (e.g. when
    uvicorn is launched from ``apps/api``).
    """
    if candidate.is_absolute():
        return candidate
    if candidate.is_file():
        return candidate.resolve()
    rooted = (_REPO_ROOT / candidate).resolve()
    return rooted if rooted.is_file() else (_REPO_ROOT / candidate)


def _canon_arch(value: str) -> str:
    """Canonical arch token, alias-aware across class names and token names.

    ``HybridSegmentation`` (the class actually built) and ``hybrid`` (the
    checkpoint key) must compare equal; the same holds for ResNet34UNet /
    ``resnet34_unet`` / ``baseline`` and the legacy Cardd* family.
    """
    compact = "".join(value.lower().split("_"))
    return {
        "baseline": "resnet34unet",
        "resnet34unet": "resnet34unet",
        "hybridsegmentation": "hybrid",
        "hybrid": "hybrid",
        "carddhybrid": "carddhybrid",
        "carddunet": "carddunet",
        "unet": "carddunet",
    }.get(compact, compact)


def _load_checkpoint(directory: Path) -> tuple[str, int, str]:
    """Read base + model_arch straight from the artefact (never guessed)."""
    ckpt = Path(directory) / "best_checkpoint.pt"
    if not ckpt.is_file():
        raise FileNotFoundError(f"checkpoint not found: {ckpt}")
    import torch

    data = torch.load(str(ckpt), map_location="cpu", weights_only=False)
    base = data.get("base", 64)
    arch = data.get("model_arch") or "cardd_unet"
    return str(ckpt), int(base), str(arch)


def _registry_meta(directory: Path) -> tuple[str | None, float | None, str | None]:
    """Look up the committed run's git revision + validation metric from registry.

    Prefers ``best_val_foreground_miou`` (the metric recorded by the research
    smoke/pilot runs); falls back to the legacy ``best_val_mean_iou``. The third
    element names which key supplied the value.
    """
    if not _norm_path(_REGISTRY).is_file():
        return None, None, None
    try:
        runs = json.loads(_norm_path(_REGISTRY).read_text())
    except json.JSONDecodeError:
        return None, None, None
    prefix = f"{directory.name}-"
    for run in runs:
        if run.get("experiment_id", "").startswith(prefix):
            metric = run.get("best_val_foreground_miou")
            if isinstance(metric, int | float):
                return run.get("git_revision"), float(metric), "best_val_foreground_miou"
            metric = run.get("best_val_mean_iou")
            if isinstance(metric, int | float):
                return run.get("git_revision"), float(metric), "best_val_mean_iou"
            return run.get("git_revision"), None, None
    return None, None, None


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
    assistant: AssistantService
    workflow: object
    _engine: SegmentationEngine | None = None

    def resolved_model_path(self) -> Path:
        """Configured checkpoint path, resolved CWD- and repo-root-independently."""
        return _norm_path(Path(self.settings.model_path or _DEFAULT_CHECKPOINT))

    def engine(self) -> SegmentationEngine:
        if self._engine is None:
            checkpoint_path = self.resolved_model_path()
            directory = checkpoint_path.parent if checkpoint_path.is_file() else None
            meta = _registry_meta(directory) if directory else (None, None, None)
            git_revision, iou, iou_key = meta

            equipped = _load_checkpoint(directory) if directory else None
            base, arch = (64, "cardd_unet") if equipped is None else (equipped[1], equipped[2])

            notes: tuple[str, ...] | None = None
            if iou is not None:
                if iou_key == "best_val_foreground_miou":
                    model_note = (
                        "Current research segmentation model (CarDD, 15-epoch pilot, "
                        f"intermediate): foreground mIoU ~{iou:.4f} — not a final "
                        "research conclusion."
                    )
                else:
                    model_note = (
                        f"Current research segmentation model (CarDD): validation mIoU ~{iou:.4f}."
                    )
                notes = (
                    model_note,
                    "Per-pixel predictions are preliminary; not verified damage extent.",
                    "Mask-derived severity is 'not currently reliable' for this model.",
                )

            logger.info(
                "building segmentation engine: checkpoint=%s exists=%s "
                "git_revision=%s registry_miou=%s arch=%s base=%s",
                checkpoint_path,
                checkpoint_path.is_file(),
                git_revision,
                f"{iou:.4f}" if iou is not None else None,
                arch,
                base,
            )
            self._engine = SegmentationEngine.from_checkpoint(
                checkpoint_path,
                model_version=self.settings.model_version or None,
                experiment_id=directory.name if directory else "unknown",
                git_revision=git_revision,
                base=base,
                baseline_notes=notes,
            )
            if _canon_arch(self._engine.metadata.arch) != _canon_arch(arch):
                raise AssertionError(
                    "checkpoint advertises arch "
                    f"{arch!r} but engine built {self._engine.metadata.arch!r}"
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
    assistant = build_assistant(settings)
    workflow = build_workflow(Services(assistant=assistant))

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
        assistant=assistant,
        workflow=workflow,
    )
