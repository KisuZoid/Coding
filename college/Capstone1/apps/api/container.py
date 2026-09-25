"""Dependency container: wires settings, stores, services, and the workflow.

Built once at app startup (``apps.api.main``); routers receive it through
``request.app.state.container``. The torch model stays lazy so tests that never
hit ``/analyze`` don't pay the CPU load cost.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from apps.api.agent.assistant import AssistantService, build_assistant
from apps.api.agent.graph import Services, build_workflow
from apps.api.inspection.consent_service import ConsentService
from apps.api.model_catalog import (
    DEFAULT_MODEL_ID,
    LEGACY_MODEL_ID,
    ModelSpec,
    UnknownModelError,
    get_model_spec,
    public_model_infos,
)
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
    _engine: SegmentationEngine | None = field(default=None, init=False)
    _engines: dict[str, SegmentationEngine] = field(default_factory=dict, init=False)

    def default_model_id(self) -> str:
        return self.settings.model_id or DEFAULT_MODEL_ID

    def model_id_for_session(self, requested: str | None = None) -> str:
        if requested is not None:
            if requested == LEGACY_MODEL_ID:
                return requested
            get_model_spec(requested)
            return requested
        if self.settings.model_path is not None and self.settings.model_id is None:
            return LEGACY_MODEL_ID
        return self.default_model_id()

    def model_infos(self) -> list[dict[str, Any]]:
        return public_model_infos()

    def resolved_model_path(self, model_id: str | None = None) -> Path:
        selected = model_id or self.model_id_for_session()
        if self.settings.model_path is not None and selected == LEGACY_MODEL_ID:
            return _norm_path(self.settings.model_path)
        if selected == LEGACY_MODEL_ID:
            raise UnknownModelError(selected)
        return get_model_spec(selected).checkpoint

    def _research_notes(
        self,
        label: str,
        iou: float | None,
        description: str,
    ) -> tuple[str, ...]:
        if iou is None:
            metric_note = f"{label}: validation metric is unavailable in the local run record."
        else:
            metric_note = f"{label}: validation foreground mIoU ~{iou:.4f}."
        return (
            f"{metric_note} {description}",
            "Per-pixel predictions are preliminary; not verified damage extent.",
            "Mask-derived severity is 'not currently reliable' for this model.",
        )

    def _engine_metadata(
        self,
        model_id: str,
        checkpoint_path: Path,
        directory: Path | None,
    ) -> tuple[ModelSpec | None, int, str, str | None, float | None, str]:
        if model_id != LEGACY_MODEL_ID:
            spec = get_model_spec(model_id)
            info = spec.public_info()
            equipped = (
                _load_checkpoint(directory) if directory and checkpoint_path.is_file() else None
            )
            base, arch = (0, spec.architecture) if equipped is None else (equipped[1], equipped[2])
            if _canon_arch(arch) != _canon_arch(spec.architecture):
                raise AssertionError(
                    f"model {model_id!r} advertises arch {arch!r}, expected {spec.architecture!r}"
                )
            metric = info.get("best_val_foreground_miou")
            git_revision = info.get("git_revision")
            description = info.get("description")
            return (
                spec,
                base,
                arch,
                git_revision if isinstance(git_revision, str) else None,
                float(metric) if isinstance(metric, int | float) else None,
                description if isinstance(description, str) else "",
            )

        meta = _registry_meta(directory) if directory else (None, None, None)
        git_revision, iou, _ = meta
        equipped = _load_checkpoint(directory) if directory and checkpoint_path.is_file() else None
        base, arch = (64, "cardd_unet") if equipped is None else (equipped[1], equipped[2])
        return (
            None,
            base,
            arch,
            git_revision,
            iou,
            "Configured checkpoint; its run status is not part of the active model catalog.",
        )

    def engine(self, model_id: str | None = None) -> SegmentationEngine:
        selected = model_id or self.model_id_for_session()
        if self._engine is not None:
            metadata = getattr(self._engine, "metadata", None)
            if metadata is None or getattr(metadata, "model_id", None) in {None, selected}:
                return self._engine
        cached = self._engines.get(selected)
        if cached is not None:
            return cached

        checkpoint_path = self.resolved_model_path(selected)
        directory = checkpoint_path.parent if checkpoint_path.is_file() else None
        spec, base, arch, git_revision, iou, description = self._engine_metadata(
            selected,
            checkpoint_path,
            directory,
        )
        label = spec.label if spec is not None else "Configured checkpoint"
        notes = self._research_notes(label, iou, description)

        logger.info(
            "building segmentation engine: model_id=%s checkpoint=%s exists=%s "
            "git_revision=%s registry_miou=%s arch=%s base=%s",
            selected,
            checkpoint_path,
            checkpoint_path.is_file(),
            git_revision,
            f"{iou:.4f}" if iou is not None else None,
            arch,
            base,
        )
        experiment_id = (
            spec.experiment_id if spec is not None else (directory.name if directory else selected)
        )
        engine = SegmentationEngine.from_checkpoint(
            checkpoint_path,
            model_version=self.settings.model_version or None,
            model_id=selected,
            experiment_id=experiment_id,
            git_revision=git_revision,
            base=base,
            baseline_notes=notes,
        )
        if _canon_arch(engine.metadata.arch) != _canon_arch(arch):
            raise AssertionError(
                f"checkpoint advertises arch {arch!r} but engine built {engine.metadata.arch!r}"
            )
        self._engines[selected] = engine
        self._engine = engine
        return engine


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
