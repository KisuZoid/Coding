"""Damage instance and feature extraction (Phase E).

Connected components over the per-pixel ``argmax`` damage classes of a
:class:`SegmentationResult`. Areas are strictly **image-denominator**
(ADR 0005): ``area_ratio_image`` = component pixels divided by the total
inference-resolution pixels (512x512). Never cm^2, never part-normalised.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

import cv2
import numpy as np

from ml.inference.classes import ID_TO_CLASS
from ml.inference.engine import SegmentationResult

_LOW_CONFIDENCE = 0.5


@dataclass(frozen=True)
class DamageInstance:
    """One connected damage region discovered in the predicted mask."""

    instance_id: int
    class_id: int
    class_name: str
    area_pixels: int
    area_ratio_image: float
    bbox: tuple[int, int, int, int]
    centroid: tuple[float, float]
    mean_confidence: float
    max_confidence: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "instance_id": self.instance_id,
            "class_id": self.class_id,
            "class_name": self.class_name,
            "area_pixels": self.area_pixels,
            "area_ratio_image": self.area_ratio_image,
            "bbox": {"x": self.bbox[0], "y": self.bbox[1], "w": self.bbox[2], "h": self.bbox[3]},
            "centroid": {"x": round(self.centroid[0], 2), "y": round(self.centroid[1], 2)},
            "mean_confidence": self.mean_confidence,
            "max_confidence": self.max_confidence,
        }


@dataclass(frozen=True)
class DamageFeatures:
    """The honest, serialisable feature set for one analysed image."""

    width: int
    height: int
    instances: list[DamageInstance]
    damage_area_ratio_image: float
    per_class_area_ratio_image: dict[int, float]
    classes_present: dict[int, str]
    num_instances: int
    low_confidence_instances: int
    mask: np.ndarray

    def to_dict(self) -> dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "num_instances": self.num_instances,
            "damage_area_ratio_image": round(self.damage_area_ratio_image, 6),
            "per_class_area_ratio_image": {
                str(cid): round(v, 6) for cid, v in self.per_class_area_ratio_image.items()
            },
            "classes_present": {str(cid): name for cid, name in self.classes_present.items()},
            "instances": [inst.to_dict() for inst in self.instances],
            "low_confidence_instances": self.low_confidence_instances,
        }


def extract_features(
    result: SegmentationResult,
    *,
    min_component_pixels: int = 8,
) -> DamageFeatures:
    """Turn a segmentation result into connected damage regions and features."""
    mask = result.mask
    pixel_confidence = result.pixel_confidence
    h, w = mask.shape
    image_pixels = float(h * w)

    instances: list[DamageInstance] = []
    per_class_area: dict[int, int] = {}

    for class_id in range(1, int(result.prob.shape[0])):
        class_mask = (mask == class_id).astype(np.uint8)
        _, labels, stats, _centroids = cv2.connectedComponentsWithStats(class_mask, connectivity=8)
        labels = cast(np.ndarray, labels)
        stats = cast(np.ndarray, stats)
        for label in range(1, int(stats.shape[0])):
            x, y, box_w, box_h, area = (int(v) for v in stats[label][:5])
            if area < min_component_pixels:
                continue
            comp = labels == label
            weights = pixel_confidence[comp]
            ys, xs = np.nonzero(comp)
            centroid = (float(xs.mean()), float(ys.mean()))
            per_class_area[class_id] = per_class_area.get(class_id, 0) + area
            instances.append(
                DamageInstance(
                    instance_id=len(instances),
                    class_id=class_id,
                    class_name=ID_TO_CLASS[class_id],
                    area_pixels=area,
                    area_ratio_image=round(area / image_pixels, 6),
                    bbox=(x, y, box_w, box_h),
                    centroid=centroid,
                    mean_confidence=round(float(weights.mean()), 4),
                    max_confidence=round(float(weights.max()), 4),
                )
            )

    damage_pixels = sum(per_class_area.values())
    per_class_ratio = {cid: area / image_pixels for cid, area in per_class_area.items()}
    classes_present = {cid: ID_TO_CLASS[cid] for cid in per_class_area}
    low_confidence = sum(1 for inst in instances if inst.mean_confidence < _LOW_CONFIDENCE)

    return DamageFeatures(
        width=w,
        height=h,
        instances=instances,
        damage_area_ratio_image=damage_pixels / image_pixels,
        per_class_area_ratio_image=per_class_ratio,
        classes_present=classes_present,
        num_instances=len(instances),
        low_confidence_instances=low_confidence,
        mask=mask.copy(),
    )
