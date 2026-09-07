"""Unit tests for the Phase 7 additions: precision/recall and small-damage slice."""

import numpy as np
import pytest
import torch

from ml.evaluation.metrics import (
    confusion_matrix,
    mean_precision,
    mean_recall,
    per_class_precision,
    per_class_recall,
)
from ml.evaluation.small_damage import SmallDamageSlice


def _conf(pred: torch.Tensor, tgt: torch.Tensor, c: int) -> torch.Tensor:
    return confusion_matrix(pred, tgt, c)


def test_per_class_precision_recall_perfect() -> None:
    pred = torch.tensor([[1, 1], [0, 2]])
    tgt = pred.clone()
    conf = _conf(pred, tgt, 3)
    assert torch.allclose(per_class_precision(conf), torch.tensor([1.0, 1.0, 1.0]))
    assert torch.allclose(per_class_recall(conf), torch.tensor([1.0, 1.0, 1.0]))


def test_per_class_precision_recall_known_values() -> None:
    # class 1 predicted 3px, 2 correct -> precision 2/3, recall 2/5
    pred = torch.tensor([[1, 1, 1], [0, 0, 0], [0, 0, 0]])
    tgt = torch.tensor([[1, 1, 0], [0, 1, 1], [1, 0, 0]])  # 5 ones in class 1
    conf = _conf(pred, tgt, 2)
    p = per_class_precision(conf)[1].item()
    r = per_class_recall(conf)[1].item()
    assert p == pytest.approx(2 / 3, rel=1e-4)
    assert r == pytest.approx(2 / 5, rel=1e-4)


def test_absent_classes_zero_precision_recall() -> None:
    pred = torch.tensor([[0, 0], [0, 0]])
    tgt = torch.tensor([[0, 0], [0, 0]])
    conf = _conf(pred, tgt, 3)
    assert per_class_precision(conf)[1].item() == 0.0
    assert per_class_recall(conf)[1].item() == 0.0


def test_mean_precision_recall_excludes_background() -> None:
    # background always perfect; one foreground class imperfect
    pred = torch.tensor([[0, 0, 1], [0, 0, 1], [0, 1, 0]])  # 3 predicted, 2 correct
    tgt = torch.tensor([[0, 0, 1], [0, 0, 1], [0, 0, 0]])  # 2 targets, both found
    conf = _conf(pred, tgt, 2)
    assert mean_precision(conf) == pytest.approx(2 / 3)
    assert mean_recall(conf) == pytest.approx(1.0)


def test_small_damage_keeps_only_small_instances() -> None:
    slice_ = SmallDamageSlice(threshold=100)
    masks = np.zeros((3, 8, 8), dtype=np.uint8)
    masks[0, 0:2, 0:4] = 1  # 8 px  -> small
    masks[1, 0:6, 0:6] = 1  # 36 px -> small
    masks[2, 0:8, 0:8] = 1  # 64 px -> small
    areas = [8.0, 36.0, 64.0]
    kept = slice_.small_mask(masks, areas)
    assert kept.sum() == (8 + 36 + 64)
    areas2 = [8.0, 250.0, 64.0]
    kept2 = slice_.small_mask(masks, areas2)
    assert kept2.sum() == (8 + 64)
    assert kept2[1].sum() == 0


def test_small_damage_target_classes() -> None:
    slice_ = SmallDamageSlice(threshold=100)
    masks = np.zeros((2, 8, 8), dtype=np.uint8)
    masks[0, :2, :2] = 1  # small, label 2
    masks[1, 2:2] = 0
    masks[1, 3:5, 3:5] = 1  # small, label 5
    labels = np.array([2, 5])
    target = slice_.target_classes(masks, labels)
    assert target[0, 0] == 2 and target[1, 1] == 2
    assert target[3, 3] == 5 and target[4, 4] == 5
    assert target[6, 6] == 0
