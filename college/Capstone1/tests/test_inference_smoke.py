"""Real-artefact smoke test (Phase D).

Exercises an actual CarDD checkpoint in the active controlled baseline and
hybrid runs, plus an archived legacy checkpoint when present. Each is
skipped (never failed) when its artefact is absent; existence is verified at
runtime, not assumed. This is the ADR 0003 "loud artefact check".
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import torch.nn as nn

from ml.inference import SegmentationEngine, SegmentationResult
from ml.models.cardd_unet import CarddUNet
from ml.models.hybrid_segmentation import HybridSegmentation
from ml.models.resnet34_unet import ResNet34UNet

_EXPERIMENTS = Path(__file__).resolve().parent.parent / "ml" / "experiments"
_ARCHIVE_EXPERIMENTS = Path(__file__).resolve().parent.parent / "archive" / "experiments"


def _resolve_checkpoint(run: str) -> Path | None:
    """Locate a run in the active experiments dir or the archived one."""
    for root in (_EXPERIMENTS, _ARCHIVE_EXPERIMENTS):
        candidate = root / run / "best_checkpoint.pt"
        if candidate.is_file():
            return candidate
    return None


# (experiment dir name, expected class, expected base, expected experiment_id)
_SMOKE_TARGETS = [
    pytest.param(
        "cardd_baseline_ce",
        CarddUNet,
        64,
        "cardd_baseline_ce",
        id="legacy-carddunet",
        marks=pytest.mark.skipif(
            _resolve_checkpoint("cardd_baseline_ce") is None,
            reason="real legacy baseline checkpoint absent (archived experiment)",
        ),
    ),
    pytest.param(
        "final60_baseline_seed42",
        ResNet34UNet,
        0,
        "final60_baseline_seed42",
        id="resnet34-unet-final60",
        marks=pytest.mark.skipif(
            _resolve_checkpoint("final60_baseline_seed42") is None,
            reason="active ResNet34-U-Net checkpoint absent",
        ),
    ),
    pytest.param(
        "final60_hybrid_seed42",
        HybridSegmentation,
        0,
        "final60_hybrid_seed42",
        id="hybrid-final60",
        marks=pytest.mark.skipif(
            _resolve_checkpoint("final60_hybrid_seed42") is None,
            reason="active hybrid checkpoint absent",
        ),
    ),
]


def _plausible_photo() -> np.ndarray:
    rng = np.random.default_rng(7)
    img = rng.integers(30, 200, size=(1080, 1920, 3), dtype=np.uint8)
    img[200:340, 500:700, 1] = 70  # a darker "damage-ish" patch
    return img


@pytest.mark.parametrize("run_dir,model_cls,base,experiment_id", _SMOKE_TARGETS)
def test_real_checkpoint_loads_and_predicts(
    run_dir: str,
    model_cls: type[nn.Module],
    base: int,
    experiment_id: str,
) -> None:
    checkpoint = _resolve_checkpoint(run_dir)
    assert checkpoint is not None
    engine = SegmentationEngine.from_checkpoint(checkpoint, base=base, device="cpu")
    assert isinstance(engine._model, model_cls)
    assert engine.metadata.experiment_id == experiment_id
    assert engine.metadata.base == base
    assert engine.metadata.epoch is not None

    result = engine.predict(_plausible_photo())
    assert isinstance(result, SegmentationResult)
    assert result.mask.shape == (512, 512)
    assert result.mask.dtype == np.uint8
    assert 0.0 <= result.mean_confidence <= 1.0
    assert result.quality.notes  # honest limitation notes always present

    payload = result.to_dict()
    assert payload["width"] == 512 and payload["height"] == 512
    assert payload["mask_png_base64"]
    assert payload["metadata"]["num_classes"] == 7
