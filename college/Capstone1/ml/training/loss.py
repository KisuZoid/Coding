"""Shared training losses and target aggregation for CarDD segmentation.

`aggregate_targets` and `cross_entropy_loss` are shared by the smoke trainer and
the real training entrypoint so the target/loss semantics cannot diverge
between the two paths.

Run inside the `ai` conda environment.

## Loss correction history

- Phase 4: `bce_loss` over positive pixels only — degenerate (ADR 0007 retracted).
- Phase 8a: BCE with `pos_weight=4` over all pixels — still incompatible with
  argmax decoding (background is a *never-set* channel in `aggregate_targets`,
  so BCE pushes it below every damage channel). See ADR 0008.
- Phase 8b (current): class-weighted softmax cross-entropy over the argmax of
  the aggregated target. Background is a real class; decode = argmax, exactly
  the confusion-metric decode. This is the standard semantic-segmentation
  objective.
"""

from __future__ import annotations

import torch
import torch.nn.functional as F
from torch import Tensor


def aggregate_targets(masks: Tensor, labels: Tensor, num_classes: int) -> Tensor:
    """Aggregate per-instance masks into per-class binary targets (B, C, H, W).

    `masks` is (B, N, H, W) uint8 per-instance; `labels` is (B, N) int64 with
    -1 marking padded instances. Padded instances have all-zero masks, so OR
    aggregation ignores them. Class channels are indexed by the dataset
    category id; channel 0 (background) is never set (its pixels are the
    complement of all damage channels).
    """
    b, _n, h, w = masks.shape
    targets = torch.zeros(b, num_classes, h, w, device=masks.device, dtype=masks.dtype)
    for i in range(_n):
        cls = labels[:, i]
        m = masks[:, i]
        for c in range(1, num_classes):
            sel = cls == c
            if bool(sel.any()):
                targets[sel, c] = torch.maximum(targets[sel, c], m[sel])
    return targets


def class_targets(masks: Tensor, labels: Tensor, num_classes: int) -> Tensor:
    """Return the argmax class-index target (B, H, W) long, background = class 0.

    Built from `aggregate_targets`, so overlapping damage classes collapse to a
    single label per pixel — the same decode the evaluation harness uses.
    """
    return aggregate_targets(masks, labels, num_classes).argmax(dim=1)


def cross_entropy_loss(
    logits: Tensor,
    masks: Tensor,
    labels: Tensor,
    num_classes: int,
) -> Tensor:
    """Softmax cross-entropy between logits and the argmax class target.

    Background is class 0. Uses the same decode as the evaluation harness
    (argmax), so training and metric semantics match. Uniform weighting is the
    default baseline; a weighted variant can be added behind an ADR later.
    """
    targets = class_targets(masks, labels, num_classes)
    return F.cross_entropy(logits, targets)
