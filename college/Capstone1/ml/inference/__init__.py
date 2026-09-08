"""ml/inference (Phase D, ADR 0003): typed, honest baseline segmentation.

The fastapi backend depends on this layer only; it never imports ml/training.
"""

from __future__ import annotations

from ml.inference.classes import (
    BACKGROUND_CLASS,
    CLASS_TO_ID,
    DAMAGE_CLASS_IDS,
    ID_TO_CLASS,
    NUM_CLASSES,
    validate_class_ids,
)
from ml.inference.engine import (
    ModelMetadata,
    QualityAssessment,
    SegmentationEngine,
    SegmentationResult,
)
from ml.inference.errors import InferenceError, ModelLoadError, ModelVersionError
from ml.inference.features import DamageFeatures, DamageInstance, extract_features
from ml.inference.overlay import CLASS_COLORS, encode_jpeg, encode_png, render_overlay
from ml.inference.preprocess import TARGET_SIZE, load_image_rgb, preprocess_image

__all__ = [
    "BACKGROUND_CLASS",
    "CLASS_COLORS",
    "CLASS_TO_ID",
    "DAMAGE_CLASS_IDS",
    "ID_TO_CLASS",
    "NUM_CLASSES",
    "TARGET_SIZE",
    "DamageFeatures",
    "DamageInstance",
    "InferenceError",
    "ModelLoadError",
    "ModelMetadata",
    "ModelVersionError",
    "QualityAssessment",
    "SegmentationEngine",
    "SegmentationResult",
    "encode_jpeg",
    "encode_png",
    "extract_features",
    "load_image_rgb",
    "preprocess_image",
    "render_overlay",
    "validate_class_ids",
]
