"""Train-split-derived pixel class statistics (architecture spec 10 / 19A).

Computes, from the **training split only**, the per-class pixel frequencies
used to build:

- the inverse-square-root foreground loss weights (mean foreground weight 1.0),
- the fixed reduced background weight,
- per-image sampling weights for class-aware training batches.

Everything here is a DERIVED FEATURE (rasterized annotation counts at 512x512),
never ground-truth damage evidence and never a validation/test statistic.
The result is cached as JSON under ``ml/datasets/reports/`` so the three repeat
runs (multi-seed) do not re-rasterize the training set each time.

Run inside the `ai` conda environment.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import cv2
import numpy as np

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TARGET_512 = (512, 512)
DEFAULT_CACHE = _REPO_ROOT / "ml" / "datasets" / "reports" / "train2017_class_stats.json"
BACKGROUND_PIXEL_WEIGHT = 0.1  # fixed reduced background weight (spec 19A)


@dataclass(frozen=True)
class TrainClassStats:
    """Class statistics derived from a single (train) split."""

    split: str
    class_pixel_counts: dict[int, int]
    foreground_weights: dict[int, float]
    background_weight: float
    image_ids: list[int]
    sampling_weights: list[float]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _inverse_sqrt_weights(class_pixel_counts: dict[int, int]) -> dict[int, float]:
    """Return inverse-square-root frequency weights with foreground mean 1.0."""
    foreground = {cid: float(n) for cid, n in class_pixel_counts.items() if cid != 0 and n > 0}
    inv_sqrt = {cid: 1.0 / math.sqrt(n) for cid, n in foreground.items()}
    mean = sum(inv_sqrt.values()) / max(len(inv_sqrt), 1)
    return {cid: value / mean for cid, value in inv_sqrt.items()}


def _image_sampling_weight(
    classes_present: list[int], foreground_weights: dict[int, float]
) -> float:
    """Per-image weight favouring images that contain rare classes.

    Assumption (recorded, not measured): an image gets a bonus proportional to
    its rarest present class, capped at 3x the plain weight.
    """
    if not classes_present:
        return 1.0
    w_max = max(foreground_weights.get(cid, 1.0) for cid in classes_present)
    return max(1.0, min(3.0, 1.0 + 2.0 * (w_max - 1.0)))


def compute_train_class_stats(data_root: Path | str, split: str = "train2017") -> TrainClassStats:
    """Rasterize the split's annotations and derive all class statistics."""
    from ml.datasets.cardd_adapter import CarddAdapter

    adapter = CarddAdapter(data_root, split)
    class_pixel_counts: dict[int, int] = {}
    image_ids: list[int] = []
    per_image_classes: list[list[int]] = []
    for image in adapter.images():
        if not image.annotations:
            continue
        image_ids.append(image.image_id)
        classes_present: set[int] = set()
        masks = adapter.rasterize(image)
        for mask, annotation in zip(masks, image.annotations, strict=True):
            class_id = int(annotation.category_id)
            classes_present.add(class_id)
            resized = cv2.resize(mask, _TARGET_512, interpolation=cv2.INTER_NEAREST)
            class_pixel_counts[class_id] = class_pixel_counts.get(class_id, 0) + int(
                np.count_nonzero(resized)
            )
        per_image_classes.append(sorted(classes_present))

    foreground_weights = _inverse_sqrt_weights(class_pixel_counts)
    sampling_weights = [
        _image_sampling_weight(classes, foreground_weights) for classes in per_image_classes
    ]
    return TrainClassStats(
        split=split,
        class_pixel_counts=class_pixel_counts,
        foreground_weights=foreground_weights,
        background_weight=BACKGROUND_PIXEL_WEIGHT,
        image_ids=image_ids,
        sampling_weights=sampling_weights,
    )


def get_train_class_stats(
    data_root: Path | str,
    split: str = "train2017",
    cache_path: Path | None = None,
) -> TrainClassStats:
    """Return cached (preferred) or freshly computed train-split statistics.

    The cache carries the split name and is regenerated on a mismatch, so a
    different split can never silently reuse another split's statistics.
    """
    path = cache_path or DEFAULT_CACHE
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("split") == split:
            return TrainClassStats(
                split=str(data["split"]),
                class_pixel_counts={int(k): int(v) for k, v in data["class_pixel_counts"].items()},
                foreground_weights={
                    int(k): float(v) for k, v in data["foreground_weights"].items()
                },
                background_weight=float(data["background_weight"]),
                image_ids=[int(v) for v in data["image_ids"]],
                sampling_weights=[float(v) for v in data["sampling_weights"]],
            )
    stats = compute_train_class_stats(data_root, split)
    payload = stats.to_dict()
    payload.update(
        {
            "kind": "DERIVED FEATURE",
            "note": (
                "Rasterized CarDD-COCO annotation pixel counts at 512x512 from the "
                f"{split} split only. Not validation/test statistics; not ground-truth "
                "damage evidence."
            ),
            "generated": datetime.now(UTC).isoformat(),
        }
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return stats
