"""Segmentation engine (Phase D, ADR 0003).

Loads a checkpoint through the artefact contract — a state dict with
``model_state`` plus ``base`` and ``model_arch`` keys — and exposes a typed
prediction API for the product. The architecture is dispatched from the
checkpoint's ``model_arch`` key:

- ``resnet34_unet`` / ``baseline``  -> ``ResNet34UNet`` (research baseline,
  architecture spec v3 §9.1)
- ``hybrid`` / ``hybrid_segmentation`` -> ``HybridSegmentation`` (research
  model, spec v3 §4/§5/§18)
- ``cardd_hybrid`` / ``CarddHybrid`` -> ``CarddHybrid`` (legacy hybrid, ADR 0010)
- ``cardd_unet`` / ``CarddUNet`` / missing key -> ``CarddUNet`` (legacy U-Net)

A missing or mismatched artefact fails loudly at construction; there is no
silent fallback (ADR 0003). Every result carries a ``QualityAssessment`` with
honest, model-card-grounded limitations and a ``low_confidence`` flag, so
downstream stages (Phase E features and the API) can never present an underfit
or intermediate model as reliable ground truth.

The research models return ``(main, aux1, aux2)`` from ``forward`` (deep
supervision); this module normalizes to the main head before decoding, exactly
as ``ml/evaluation/evaluate_run.py::forward_main_logits`` does.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import cv2
import numpy as np
import torch

from ml.inference.classes import (
    DAMAGE_CLASS_IDS,
    ID_TO_CLASS,
    NUM_CLASSES,
)
from ml.inference.errors import ModelLoadError, ModelVersionError
from ml.inference.preprocess import load_image_rgb, preprocess_image
from ml.models.cardd_hybrid import CarddHybrid
from ml.models.cardd_unet import CarddUNet
from ml.models.hybrid_segmentation import HybridSegmentation
from ml.models.resnet34_unet import ResNet34UNet

# Honest limits for the current research model (carried for deployments that
# omit registry metadata). The 15-epoch pilots (seed 0, full CarDD splits)
# reached a foreground mIoU of ~0.613 (baseline) / ~0.596 (hybrid) — intermediate,
# not a final research conclusion. Several minority classes are not reliably
# separated at this stage.
_BASELINE_LIMITATIONS = (
    "Current research segmentation model (CarDD, 15-epoch pilot, intermediate): "
    "foreground mIoU ~0.596 to 0.613 measured; not a final research conclusion.",
    "Per-pixel predictions are preliminary; not verified damage extent.",
    "Mask-derived severity is 'not currently reliable' for this model.",
)


def _main_logits(model: torch.nn.Module, tensor: torch.Tensor) -> torch.Tensor:
    """Forward pass normalized to the main segmentation head.

    Research models (``ResNet34UNet``, ``HybridSegmentation``) return
    ``(main, aux1, aux2)`` under deep supervision; legacy models return a single
    logits tensor. Return the main head in both cases.
    """
    out = model(tensor)
    if isinstance(out, tuple | list):
        return cast(torch.Tensor, out[0])
    return cast(torch.Tensor, out)


def _build_model(arch: str, *, base: int, num_classes: int) -> torch.nn.Module:
    """Instantiate the checkpoint's architecture from its ``model_arch`` key.

    Legacy baselines predate the key (or store ``cardd_unet``) and map to
    CarddUNet; hybrid runs store ``cardd_hybrid``; the current research
    baseline/hybrid store ``resnet34_unet`` / ``hybrid`` (architecture spec v3).
    The pretrained encoder is deliberately not downloaded here — the checkpoint
    ``model_state`` is authoritative and replaced immediately after. Unknown
    keys fail loudly so an artefact is never silently run with the wrong
    architecture.
    """
    arch_l = "".join(arch.lower().split("_"))
    if arch_l in {"resnet34unet", "baseline"}:
        return ResNet34UNet(num_classes=num_classes, pretrained=False)
    if arch_l in {"hybrid", "hybridsegmentation"}:
        return HybridSegmentation(num_classes=num_classes, pretrained=False)
    if arch_l in {"carddhybrid"}:
        return CarddHybrid(base=base, num_classes=num_classes)
    if not arch or arch_l in {"carddunet"}:
        return CarddUNet(base=base, num_classes=num_classes)
    raise ModelVersionError(f"unknown model_arch in checkpoint: {arch!r}")


def _resolve_device(device: str | torch.device | None) -> torch.device:
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    return torch.device(device)


@dataclass(frozen=True)
class ModelMetadata:
    """Provenance of the artefact that produced a result (ADR 0003)."""

    model_version: str | None
    experiment_id: str
    base: int
    num_classes: int
    checkpoint_path: str
    epoch: int | None = None
    git_revision: str | None = None
    arch: str = "cardd_unet"

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_version": self.model_version,
            "experiment_id": self.experiment_id,
            "base": self.base,
            "num_classes": self.num_classes,
            "checkpoint_path": self.checkpoint_path,
            "epoch": self.epoch,
            "git_revision": self.git_revision,
            "arch": self.arch,
        }


@dataclass(frozen=True)
class QualityAssessment:
    """Confidence decision plus human-readable honest limitations."""

    low_confidence: bool
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"low_confidence": self.low_confidence, "notes": list(self.notes)}


@dataclass(frozen=True)
class SegmentationResult:
    """Model output for one image, before any damage features are computed."""

    mask: np.ndarray  # HxW uint8 argmax class index
    prob: np.ndarray  # CxHxW float32 softmax
    pixel_confidence: np.ndarray  # HxW float32 = max softmax per pixel
    mean_confidence: float
    damage_fraction: float
    class_fractions: dict[int, float]
    quality: QualityAssessment
    metadata: ModelMetadata

    def to_dict(self) -> dict[str, Any]:
        """Compact JSON-ready payload (full arrays stay on the dataclass)."""
        encode_ok, encoded = cv2.imencode(".png", self.mask)
        if not encode_ok:
            raise ModelLoadError("failed to encode result mask as PNG")
        mask_b64 = base64.b64encode(encoded.tobytes()).decode("ascii")
        per_class = {
            str(cid): {
                "mean_prob": round(float(self.prob[cid].mean()), 4),
                "max_prob": round(float(self.prob[cid].max()), 4),
            }
            for cid in range(int(self.prob.shape[0]))
        }
        return {
            "mask_png_base64": mask_b64,
            "width": int(self.mask.shape[1]),
            "height": int(self.mask.shape[0]),
            "mean_confidence": round(self.mean_confidence, 4),
            "damage_fraction": round(self.damage_fraction, 6),
            "class_fractions": {str(cid): round(v, 6) for cid, v in self.class_fractions.items()},
            "per_class_prob": per_class,
            "quality": self.quality.to_dict(),
            "metadata": self.metadata.to_dict(),
        }


class SegmentationEngine:
    """Typed, stateless-when-idle wrapper around a segmentation checkpoint."""

    def __init__(
        self,
        model: torch.nn.Module,
        metadata: ModelMetadata,
        device: str | torch.device | None = None,
        *,
        min_mean_confidence: float = 0.5,
        min_damage_fraction: float = 0.001,
        baseline_notes: tuple[str, ...] | None = None,
    ) -> None:
        if metadata.num_classes != NUM_CLASSES:
            raise ModelVersionError(
                f"engine supports the {NUM_CLASSES}-channel CarDD contract, "
                f"got num_classes={metadata.num_classes}"
            )
        if metadata.num_classes != len(ID_TO_CLASS):
            raise ModelVersionError("num_classes disagrees with the CarDD class map")
        self._model = model.to(_resolve_device(device))
        self._model.eval()
        self._device = _resolve_device(device)
        self._metadata = metadata
        self._min_mean_confidence = min_mean_confidence
        self._min_damage_fraction = min_damage_fraction
        self._baseline_notes = baseline_notes or _BASELINE_LIMITATIONS

    @classmethod
    def from_checkpoint(
        cls,
        checkpoint_path: Path | str,
        *,
        model_version: str | None = None,
        experiment_id: str | None = None,
        git_revision: str | None = None,
        base: int = 64,
        num_classes: int = NUM_CLASSES,
        device: str | torch.device | None = None,
        baseline_notes: tuple[str, ...] | None = None,
    ) -> SegmentationEngine:
        """Build an engine from a git-ignored, locally present checkpoint.

        ``experiment_id`` defaults to the checkpoint's parent directory name
        (e.g. ``pilot15_hybrid``) so the metadata never mislabels which run an
        artefact came from.
        """
        path = Path(checkpoint_path)
        if not path.is_file():
            raise ModelLoadError(f"model checkpoint not found: {path}")
        try:
            checkpoint = torch.load(str(path), map_location="cpu", weights_only=False)
        except Exception as exc:  # any load failure is a loud artefact error
            raise ModelLoadError(f"could not read checkpoint {path}: {exc}") from exc
        if not isinstance(checkpoint, dict) or "model_state" not in checkpoint:
            raise ModelLoadError(f"checkpoint lacks the model_state contract: {path}")
        arch = checkpoint.get("model_arch")
        arch_name = arch if isinstance(arch, str) else ""
        # `base` is a legacy (Cardd*) channel multiplier; the research
        # checkpoint files (resnet34_unet / hybrid) store base=0 as a contract
        # fill-in, so the consistency check applies to legacy architectures only.
        if arch_name.lower().startswith("cardd"):
            ckpt_base = checkpoint.get("base")
            if isinstance(ckpt_base, int) and ckpt_base != base:
                raise ModelVersionError(
                    f"checkpoint built with base={ckpt_base}, engine configured for base={base}"
                )
        model = _build_model(arch_name, base=base, num_classes=num_classes)
        try:
            model.load_state_dict(cast(dict[str, Any], checkpoint["model_state"]))
        except RuntimeError as exc:
            raise ModelVersionError(f"checkpoint weights disagree with the engine: {exc}") from exc
        epoch = checkpoint.get("epoch")
        metadata = ModelMetadata(
            model_version=model_version,
            experiment_id=experiment_id or path.parent.name,
            base=base,
            num_classes=num_classes,
            checkpoint_path=str(path.resolve()),
            epoch=epoch if isinstance(epoch, int) else None,
            git_revision=git_revision,
            arch=model.__class__.__name__,
        )
        return cls(model, metadata, device=device, baseline_notes=baseline_notes)

    @property
    def metadata(self) -> ModelMetadata:
        return self._metadata

    @torch.inference_mode()
    def predict(self, rgb: np.ndarray) -> SegmentationResult:
        """Segment one RGB uint8 image and return typed, honest output."""
        tensor = preprocess_image(rgb).unsqueeze(0).to(self._device)
        logits = _main_logits(self._model, tensor).squeeze(0).cpu()  # 7x512x512
        prob = torch.softmax(logits, dim=0).float()
        mask = torch.argmax(logits, dim=0).to(torch.uint8)
        confidence = prob.max(dim=0).values
        mean_confidence = float(confidence.mean().item())
        fractions = {
            cid: float((mask == cid).float().mean().item()) for cid in range(int(prob.shape[0]))
        }
        damage_fraction = sum(fractions[cid] for cid in DAMAGE_CLASS_IDS)

        notes = list(self._baseline_notes)
        if mean_confidence < self._min_mean_confidence:
            notes.append("Low mean per-pixel confidence.")
        if damage_fraction < self._min_damage_fraction:
            notes.append("No damage regions detected above the configured threshold.")
        low_confidence = (
            mean_confidence < self._min_mean_confidence
            or damage_fraction < self._min_damage_fraction
        )

        return SegmentationResult(
            mask=mask.numpy(),
            prob=prob.numpy(),
            pixel_confidence=confidence.numpy(),
            mean_confidence=mean_confidence,
            damage_fraction=damage_fraction,
            class_fractions=fractions,
            quality=QualityAssessment(low_confidence=low_confidence, notes=notes),
            metadata=self._metadata,
        )

    @torch.inference_mode()
    def predict_bytes(self, data: bytes) -> SegmentationResult:
        """Decode raw image bytes (JPEG/PNG/WebP) and predict."""
        return self.predict(load_image_rgb(data))
