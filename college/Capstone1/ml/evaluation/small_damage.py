"""Small-damage evaluation slice (Phase 7).

Criterion (dataset-derived, documented in
`docs/research/segmentation-experiment-config.md` §9):

  An instance is "small damage" when its resized-512 mask area is below the
  25th percentile of the *train split* per-instance mask-area distribution.

  Measured on CarDD-COCO train2017 (2026-09-08):
  p25 area at 512x512 ~= 3014 px, n = 6211 instances.
  This sits below the dent/scratch medians but above the crack median, so it
  captures exactly the "easy to miss" small tail (crack, small scratches, small
  dents) rather than labelling whole classes as small.

The slice aggregates per-class confusion only from the masks of small instances;
everything the model predicts everywhere else is counted against this target,
so the metrics reflect ability to land on the small regions specifically.
"""

from __future__ import annotations

from collections.abc import Iterable

import cv2
import numpy as np
import torch
from torch import Tensor

from ml.training.cardd_dataset import TARGET_SIZE


def quantile_area(q: float, data_root: str, split: str = "train2017") -> float:
    """Return the q-th percentile of per-instance mask area at 512x512 resize."""
    from ml.datasets.cardd_adapter import CarddAdapter

    adapter = CarddAdapter(data_root, split)
    areas: list[float] = []
    for image in adapter.images():
        masks = adapter.rasterize(image)
        if masks.shape[0] == 0:
            continue
        target = (TARGET_SIZE, TARGET_SIZE)
        areas.extend(
            int(cv2.resize(m, target, interpolation=cv2.INTER_NEAREST).sum()) for m in masks
        )
    return float(np.percentile(areas, 100.0 * q))


class SmallDamageSlice:
    """Filters per-instance masks to those below a given area threshold."""

    def __init__(self, threshold: float) -> None:
        self.threshold = threshold

    def small_mask(self, masks: np.ndarray, areas: Iterable[float]) -> np.ndarray:
        """Return a copy of `masks` (N, H, W) with large instances zeroed."""
        kept = np.zeros_like(masks)
        for i, area in enumerate(areas):
            if float(area) < self.threshold:
                kept[i] = masks[i]
        return kept

    def target_classes(self, small_masks: np.ndarray, labels: np.ndarray) -> Tensor:
        """Aggregate small-instance masks into a (H, W) class-index target."""
        h, w = small_masks.shape[1:]
        target = np.zeros((h, w), dtype=np.int64)
        for mask, label in zip(small_masks, labels, strict=True):
            if int(mask.sum()) > 0:
                target[mask > 0] = int(label)
        return torch.as_tensor(target, dtype=torch.long)


def small_damage_summary(confusion: Tensor) -> dict[str, float]:
    """Compact summary values for the small-damage slice."""
    from ml.evaluation.metrics import mean_dice, mean_iou, mean_precision, mean_recall

    return {
        "small_mean_iou": mean_iou(confusion),
        "small_mean_dice": mean_dice(confusion),
        "small_mean_precision": mean_precision(confusion),
        "small_mean_recall": mean_recall(confusion),
    }
