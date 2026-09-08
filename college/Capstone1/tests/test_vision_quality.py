"""Phase E: image quality validator guarding /analyze (blur/dark/glare/low-contrast)."""

from __future__ import annotations

import cv2
import numpy as np

from apps.api.vision.quality import (
    ImageQualityValidator,
    QualityStatus,
    QualityThresholds,
)


def _mk(w: int = 256, h: int = 256) -> np.ndarray:
    return np.full((h, w, 3), 128, dtype=np.uint8)


def _sharp() -> np.ndarray:
    img = _mk()
    for i in range(0, 256, 16):
        cv2.line(img, (0, i), (256, i), (220, 40, 40), 2)
        cv2.line(img, (i, 0), (i, 256), (40, 220, 40), 2)
    return img


def test_sharp_bright_image_is_valid() -> None:
    result = ImageQualityValidator(QualityThresholds()).assess(_sharp())
    assert result.status is QualityStatus.VALID
    assert len(result.reasons) == 0


def test_blurred_image_is_too_blurry() -> None:
    img = cv2.GaussianBlur(_sharp(), (41, 41), 0)
    result = ImageQualityValidator(QualityThresholds()).assess(img)
    assert result.status is QualityStatus.TOO_BLURRY
    assert "blur" in result.reasons[0].lower()


def test_dark_image_is_too_dark() -> None:
    img = np.zeros((256, 256, 3), dtype=np.uint8)
    result = ImageQualityValidator(QualityThresholds()).assess(img)
    assert result.status is QualityStatus.TOO_DARK


def test_glare_image_is_excessive_glare() -> None:
    img = _sharp()
    img[0:80, 0:256] = 254
    result = ImageQualityValidator(QualityThresholds()).assess(img)
    assert result.status is QualityStatus.EXCESSIVE_GLARE


def test_low_contrast_is_rejected() -> None:
    img = np.full((256, 256, 3), 128, dtype=np.uint8)
    img[::24, :] = 118
    img[:, ::24] = 140
    result = ImageQualityValidator(QualityThresholds()).assess(img)
    assert result.status is QualityStatus.INSUFFICIENT_CONTEXT


def test_thresholds_are_pins() -> None:
    t = QualityThresholds()
    assert t.min_sharpness_variance == 25.0
    assert t.min_mean_luminance == 45.0
    assert t.max_bright_fraction == 0.30
    assert t.min_contrast_std == 12.0
