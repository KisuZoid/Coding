"""Phase E: damage features (connected components + image-denominator areas)."""

from __future__ import annotations

import json

import numpy as np
import pytest

from ml.inference.classes import ID_TO_CLASS
from ml.inference.engine import ModelMetadata, QualityAssessment, SegmentationResult
from ml.inference.features import extract_features


def _result(mask: np.ndarray, confidence: float = 0.95) -> SegmentationResult:
    c = int(mask.max() + 1)
    prob = np.zeros((c, *mask.shape), dtype=np.float32)
    for cls in np.unique(mask):
        prob[cls] = np.where(mask == cls, confidence, 0.05 / max(c - 1, 1))
    pixel_conf = prob.max(axis=0)
    return SegmentationResult(
        mask=mask,
        prob=prob,
        pixel_confidence=pixel_conf,
        mean_confidence=float(pixel_conf.mean()),
        damage_fraction=float((mask > 0).mean()),
        class_fractions={int(i): float((mask == i).mean()) for i in np.unique(mask)},
        quality=QualityAssessment(low_confidence=False, notes=["test"]),
        metadata=ModelMetadata(
            model_version=None,
            experiment_id="test",
            checkpoint_path="n/a",
            base=8,
            num_classes=c,
        ),
    )


def test_two_instances_same_class_are_separate_components() -> None:
    mask = np.zeros((32, 32), dtype=np.uint8)
    mask[2:6, 2:6] = 1
    mask[10:14, 10:14] = 1
    features = extract_features(_result(mask))
    assert features.num_instances == 2
    assert [i.class_name for i in features.instances] == ["dent", "dent"]


def test_area_is_image_denominator() -> None:
    mask = np.zeros((32, 32), dtype=np.uint8)
    mask[4:8, 4:8] = 3
    features = extract_features(_result(mask))
    assert features.damage_area_ratio_image == pytest.approx(16 / (32 * 32))
    assert features.per_class_area_ratio_image[3] == pytest.approx(16 / (32 * 32))


def test_components_smaller_than_minimum_are_ignored() -> None:
    mask = np.zeros((32, 32), dtype=np.uint8)
    mask[5, 5] = 2
    features = extract_features(_result(mask), min_component_pixels=8)
    assert features.num_instances == 0


def test_classes_present_maps_ids_to_names() -> None:
    mask = np.zeros((16, 16), dtype=np.uint8)
    mask[1:5, 1:5] = 1
    mask[8:12, 8:12] = 6
    features = extract_features(_result(mask))
    assert features.classes_present == {1: ID_TO_CLASS[1], 6: ID_TO_CLASS[6]}


def test_low_confidence_instances_counted() -> None:
    mask = np.zeros((32, 32), dtype=np.uint8)
    mask[2:6, 2:6] = 1
    features = extract_features(_result(mask, confidence=0.3), min_component_pixels=4)
    assert features.num_instances == 1
    assert features.low_confidence_instances == 1
    assert features.instances[0].mean_confidence < 0.5


def test_feature_dict_is_json_serialisable() -> None:
    mask = np.zeros((16, 16), dtype=np.uint8)
    mask[2:5, 2:5] = 2
    features = extract_features(_result(mask))
    payload = json.loads(json.dumps(features.to_dict()))
    assert payload["num_instances"] == 1
    assert payload["damage_area_ratio_image"] > 0


def test_clean_background_produces_empty_features() -> None:
    mask = np.zeros((16, 16), dtype=np.uint8)
    features = extract_features(_result(mask))
    assert features.num_instances == 0
    assert features.damage_area_ratio_image == 0.0
