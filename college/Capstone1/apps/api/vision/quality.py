"""Image-quality validation (Phase E).

Honest, testable heuristics only: luminance, glare (specular/bright
fraction), blur (variance of Laplacian), then contrast. Checks run in an
information-preserving order: a near-black or washed-out frame is reported as
dark/glare rather than a black-and-white blurry frame; a flat-but-sharp frame
is reported as low-contrast, which is semantically closer than "blurry".
``WRONG_ANGLE`` and ``DAMAGE_NOT_VISIBLE`` stay in the contract because the
validation loop needs them, but no heuristic fabricates them here — they are
applied later by the analysis stage when the model finds nothing where damage
was reported.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import cv2
import numpy as np


class QualityStatus(StrEnum):
    VALID = "VALID"
    TOO_BLURRY = "TOO_BLURRY"
    TOO_DARK = "TOO_DARK"
    EXCESSIVE_GLARE = "EXCESSIVE_GLARE"
    WRONG_ANGLE = "WRONG_ANGLE"
    DAMAGE_NOT_VISIBLE = "DAMAGE_NOT_VISIBLE"
    INSUFFICIENT_CONTEXT = "INSUFFICIENT_CONTEXT"


@dataclass(frozen=True)
class QualityThresholds:
    min_sharpness_variance: float = 25.0
    min_mean_luminance: float = 45.0
    max_bright_fraction: float = 0.30
    min_contrast_std: float = 12.0


@dataclass(frozen=True)
class QualityResult:
    status: QualityStatus
    is_valid: bool
    metrics: dict[str, float]
    reasons: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status.value,
            "is_valid": self.is_valid,
            "metrics": self.metrics,
            "reasons": list(self.reasons),
        }


class ImageQualityValidator:
    """Heuristic validator; never inspects model output."""

    def __init__(self, thresholds: QualityThresholds | None = None) -> None:
        self._thresholds = thresholds or QualityThresholds()

    def assess(self, rgb: np.ndarray) -> QualityResult:
        if rgb.ndim != 3 or rgb.shape[2] != 3:
            raise ValueError(f"expected RGB HxWx3, got shape {rgb.shape}")
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        metrics = {
            "sharpness_variance": round(sharpness, 2),
            "mean_luminance": round(float(gray.mean()), 2),
            "bright_fraction": round(float((gray > 250).mean()), 4),
            "contrast_std": round(float(gray.std()), 2),
        }

        status = QualityStatus.VALID
        if metrics["mean_luminance"] < self._thresholds.min_mean_luminance:
            status = QualityStatus.TOO_DARK
        elif metrics["bright_fraction"] > self._thresholds.max_bright_fraction:
            status = QualityStatus.EXCESSIVE_GLARE
        elif sharpness < self._thresholds.min_sharpness_variance:
            status = QualityStatus.TOO_BLURRY
        elif metrics["contrast_std"] < self._thresholds.min_contrast_std:
            status = QualityStatus.INSUFFICIENT_CONTEXT

        reasons: list[str] = []
        if status is not QualityStatus.VALID:
            reasons.append(f"quality check failed ({status.value}): {metrics}")
        return QualityResult(
            status=status,
            is_valid=status is QualityStatus.VALID,
            metrics=metrics,
            reasons=reasons,
        )
