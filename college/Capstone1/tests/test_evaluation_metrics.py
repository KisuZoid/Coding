"""Unit tests for the Phase 4 segmentation metric harness (mIoU/Dice).

These tests are dataset-independent (pure tensor math), so they always run.
"""

from __future__ import annotations

import pytest
import torch

from ml.evaluation.metrics import (
    confusion_matrix,
    mean_dice,
    mean_iou,
    per_class_dice,
    per_class_iou,
)


def test_confusion_matrix_counts_pairs() -> None:
    pred = torch.tensor([[0, 1], [1, 2]])
    target = torch.tensor([[0, 1], [2, 2]])
    conf = confusion_matrix(pred, target, num_classes=3)
    assert conf.shape == (3, 3)
    assert conf[0, 0] == 1  # both background
    assert conf[1, 1] == 1  # both class 1
    assert conf[2, 2] == 1  # both class 2
    assert conf[2, 1] == 1  # target 2, predicted 1
    assert int(conf.sum()) == 4


def test_per_class_iou_exact() -> None:
    # Perfect prediction for class 1 and 2, nothing else present.
    pred = torch.tensor([[1, 2], [1, 2]])
    target = pred.clone()
    conf = confusion_matrix(pred, target, num_classes=3)
    iou = per_class_iou(conf)
    assert iou[1] == 1.0
    assert iou[2] == 1.0
    assert iou[0] == 0.0  # background absent -> 0.0, not NaN


def test_mean_iou_excludes_background() -> None:
    pred = torch.tensor([[1, 2], [1, 2]])
    target = pred.clone()
    conf = confusion_matrix(pred, target, num_classes=3)
    assert mean_iou(conf) == 1.0  # background excluded
    assert mean_iou(conf, exclude_background=False) == pytest.approx(2.0 / 3.0)


def test_dice_partial_overlap() -> None:
    target = torch.tensor([[1, 1], [2, 2]])
    pred = torch.tensor([[1, 1], [1, 2]])
    conf = confusion_matrix(pred, target, num_classes=3)
    d = per_class_dice(conf)
    # class 1: TP=2, FP=1 (the misclassified class-2 pixel), FN=0 -> 4/5.
    assert d[1] == pytest.approx(4 / 5)
    # class 2: TP=1, FP=0, FN=1 -> 2/3.
    assert d[2] == pytest.approx(2 / 3)
    assert mean_dice(conf) == pytest.approx((4 / 5 + 2 / 3) / 2)


def test_mean_iou_partial() -> None:
    target = torch.tensor([[1, 1], [2, 2]])
    pred = torch.tensor([[1, 1], [1, 2]])
    conf = confusion_matrix(pred, target, num_classes=3)
    # class 1: TP=2, FP=1, FN=0 -> 2/3; class 2: TP=1, FP=0, FN=1 -> 1/2.
    assert mean_iou(conf) == pytest.approx((2 / 3 + 1 / 2) / 2)
