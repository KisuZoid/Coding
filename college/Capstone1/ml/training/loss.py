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

from dataclasses import dataclass
from typing import cast

import torch
import torch.nn.functional as F
from torch import Tensor

DICE_SMOOTH = 1e-6  # soft Dice smoothing (architecture spec 19A)
FOCAL_GAMMA = 2.0  # Focal loss gamma (architecture spec 19A)
DEEP_SUPERVISION_WEIGHTS = (0.75, 0.15, 0.10)  # main, aux1, aux2
BACKGROUND_PIXEL_WEIGHT = 0.1  # fixed reduced background weight (spec 19A)


@dataclass(frozen=True)
class ClassWeights:
    """Pixel-class weights for the Focal term, derived from the train split.

    ``foreground`` maps CarDD category id (1..6) to its weight; ``background``
    is the fixed reduced weight applied to class 0.
    """

    foreground: dict[int, float]
    background: float = BACKGROUND_PIXEL_WEIGHT

    def as_tensor(self, num_classes: int, device: torch.device) -> Tensor:
        weights = torch.full((num_classes,), 1.0, device=device)
        weights[0] = self.background
        for class_id, value in self.foreground.items():
            if 1 <= class_id < num_classes:
                weights[class_id] = value
        return weights


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


def resize_targets_nearest(targets: Tensor, size: tuple[int, int]) -> Tensor:
    """Nearest-neighbour resize of per-class target channels to `size`.

    Used to bring full-resolution targets to the auxiliary-head resolutions
    (architecture spec 8 / 19A). Returns the input unchanged when already at
    the right resolution.
    """
    if targets.shape[-2:] == size:
        return targets
    return cast(Tensor, F.interpolate(targets, size=size, mode="nearest"))


def _soft_dice_loss(logits: Tensor, targets: Tensor, smooth: float = DICE_SMOOTH) -> Tensor:
    """Soft multi-class Dice loss over the six foreground classes only.

    Background channel 0 is excluded from the mean (architecture spec 19A).
    """
    probs = torch.softmax(logits, dim=1)
    num_classes = int(logits.shape[1])
    losses: list[Tensor] = []
    for class_id in range(1, num_classes):
        pred = probs[:, class_id]
        target = targets[:, class_id]
        numerator = 2.0 * (pred * target).sum() + smooth
        denominator = pred.sum() + target.sum() + smooth
        losses.append(1.0 - numerator / denominator)
    if not losses:
        return torch.zeros((), device=logits.device, dtype=logits.dtype)
    return torch.stack(losses).mean()


def _focal_loss(
    logits: Tensor,
    targets_idx: Tensor,
    weights: Tensor,
    gamma: float = FOCAL_GAMMA,
) -> Tensor:
    """Multi-class Focal loss (architecture spec 19A), averaged over pixels."""
    num_classes = int(logits.shape[1])
    probs = torch.softmax(logits, dim=1)
    log_probs = torch.log_softmax(logits, dim=1)
    cls_idx = targets_idx.clamp(min=0, max=num_classes - 1)
    one_hot = F.one_hot(cls_idx, num_classes).permute(0, 3, 1, 2).to(dtype=probs.dtype)
    pt = (probs * one_hot).sum(dim=1)
    log_pt = (log_probs * one_hot).sum(dim=1)
    class_weight = weights[cls_idx]
    focal = -(class_weight * (1.0 - pt).pow(gamma) * log_pt)
    return cast(Tensor, focal.mean())


def level_loss(
    logits: Tensor,
    targets: Tensor,
    weights: Tensor,
    smooth: float = DICE_SMOOTH,
    gamma: float = FOCAL_GAMMA,
) -> Tensor:
    """0.5 Dice + 0.5 Focal for one prediction scale (architecture spec 19A)."""
    targets_idx = targets.argmax(dim=1)
    dice = _soft_dice_loss(logits, targets, smooth=smooth)
    focal = _focal_loss(logits, targets_idx, weights, gamma=gamma)
    return 0.5 * dice + 0.5 * focal


def dice_focal_loss(
    main_logits: Tensor,
    aux1_logits: Tensor | None,
    aux2_logits: Tensor | None,
    masks: Tensor,
    labels: Tensor,
    num_classes: int,
    weights: ClassWeights,
    smooth: float = DICE_SMOOTH,
    gamma: float = FOCAL_GAMMA,
) -> tuple[Tensor, dict[str, float]]:
    """Deep-supervised Dice + Focal training objective.

    Sums the per-level objective with the locked weights 0.75 / 0.15 / 0.10.
    Auxiliary targets are nearest-neighbour resized to the head resolution.
    `aux1_logits` / `aux2_logits` may be ``None`` (legacy single-output
    models, in which case only the main objective is used).

    Returns the total loss plus a per-level breakdown for logging.
    """
    targets = aggregate_targets(masks, labels, num_classes).float().to(main_logits.device)
    weight_tensor = weights.as_tensor(num_classes, main_logits.device)
    main_scale = level_loss(main_logits, targets, weight_tensor, smooth=smooth, gamma=gamma)
    total = DEEP_SUPERVISION_WEIGHTS[0] * main_scale
    parts: dict[str, float] = {"main": float(main_scale.item())}

    if aux1_logits is not None:
        t1 = resize_targets_nearest(targets, (int(aux1_logits.shape[2]), int(aux1_logits.shape[3])))
        a1 = level_loss(aux1_logits, t1, weight_tensor, smooth=smooth, gamma=gamma)
        total = total + DEEP_SUPERVISION_WEIGHTS[1] * a1
        parts["aux1"] = float(a1.item())
    if aux2_logits is not None:
        t2 = resize_targets_nearest(targets, (int(aux2_logits.shape[2]), int(aux2_logits.shape[3])))
        a2 = level_loss(aux2_logits, t2, weight_tensor, smooth=smooth, gamma=gamma)
        total = total + DEEP_SUPERVISION_WEIGHTS[2] * a2
        parts["aux2"] = float(a2.item())
    return total, parts
