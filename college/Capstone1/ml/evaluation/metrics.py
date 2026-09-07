"""Segmentation metric harness for CarDD (Phase 4, extended in Phase 7).

Computes per-class IoU / Dice / precision / recall and macro means from
class-index predictions and targets. Targets are derived from aggregated
per-class binary masks via argmax, so overlapping damage classes collapse to a
single label per pixel (a rare situation in CarDD, recorded as a limitation).

Phase 7 added precision/recall per class and mean precision/recall, and the
small-damage slice is handled by `ml/evaluation/small_damage.py`.
"""

from __future__ import annotations

import torch
from torch import Tensor


def confusion_matrix(pred_classes: Tensor, target_classes: Tensor, num_classes: int) -> Tensor:
    """Return a (C, C) confusion matrix over pixel class indices.

    `conf[i, j]` counts pixels whose target class is `i` and predicted class
    is `j`. Inputs are long tensors of shape (B, H, W) indexing classes.
    """
    flat_pred = pred_classes.reshape(-1).long()
    flat_target = target_classes.reshape(-1).long()
    index = flat_target * num_classes + flat_pred
    counts = torch.bincount(index, minlength=num_classes * num_classes)
    return counts.reshape(num_classes, num_classes).float()


def per_class_iou(confusion: Tensor) -> Tensor:
    """Return (C,) IoU per class; absent classes become 0.0."""
    diag = torch.diagonal(confusion)
    union = confusion.sum(dim=0) + confusion.sum(dim=1) - diag
    present = union > 0
    safe_union = torch.where(present, union, torch.ones_like(union))
    return torch.where(present, diag / safe_union, torch.zeros_like(diag))


def per_class_dice(confusion: Tensor) -> Tensor:
    """Return (C,) Dice per class; absent classes become 0.0."""
    diag = torch.diagonal(confusion)
    denom = confusion.sum(dim=0) + confusion.sum(dim=1)
    present = denom > 0
    safe_denom = torch.where(present, denom, torch.ones_like(denom))
    return torch.where(present, 2 * diag / safe_denom, torch.zeros_like(diag))


def per_class_precision(confusion: Tensor) -> Tensor:
    """Return (C,) precision per class; classes with no prediction become 0.0.

    precision_c = TP_c / (TP_c + FP_c) = diag_c / column_sum_c.
    """
    diag = torch.diagonal(confusion)
    denom = confusion.sum(dim=0)
    present = denom > 0
    safe_denom = torch.where(present, denom, torch.ones_like(denom))
    return torch.where(present, diag / safe_denom, torch.zeros_like(diag))


def per_class_recall(confusion: Tensor) -> Tensor:
    """Return (C,) recall per class; classes with no target become 0.0.

    recall_c = TP_c / (TP_c + FN_c) = diag_c / row_sum_c.
    """
    diag = torch.diagonal(confusion)
    denom = confusion.sum(dim=1)
    present = denom > 0
    safe_denom = torch.where(present, denom, torch.ones_like(denom))
    return torch.where(present, diag / safe_denom, torch.zeros_like(diag))


def mean_iou(confusion: Tensor, exclude_background: bool = True) -> float:
    """Macro mean IoU over classes, excluding background by default."""
    scores = per_class_iou(confusion)
    if exclude_background:
        scores = scores[1:]
    return float(scores.mean().item()) if scores.numel() else 0.0


def mean_dice(confusion: Tensor, exclude_background: bool = True) -> float:
    """Macro mean Dice over classes, excluding background by default."""
    scores = per_class_dice(confusion)
    if exclude_background:
        scores = scores[1:]
    return float(scores.mean().item()) if scores.numel() else 0.0


def mean_precision(confusion: Tensor, exclude_background: bool = True) -> float:
    """Macro mean precision over classes, excluding background by default."""
    scores = per_class_precision(confusion)
    if exclude_background:
        scores = scores[1:]
    return float(scores.mean().item()) if scores.numel() else 0.0


def mean_recall(confusion: Tensor, exclude_background: bool = True) -> float:
    """Macro mean recall over classes, excluding background by default."""
    scores = per_class_recall(confusion)
    if exclude_background:
        scores = scores[1:]
    return float(scores.mean().item()) if scores.numel() else 0.0
