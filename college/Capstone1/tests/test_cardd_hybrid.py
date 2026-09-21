"""ADR 0010: CarddHybrid CNN+Transformer net and engine dispatch."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import torch

from ml.inference.engine import SegmentationEngine
from ml.inference.errors import ModelVersionError
from ml.models.cardd_hybrid import CarddHybrid


def _random_rgb(size: tuple[int, int] = (256, 320)) -> np.ndarray:
    return np.random.default_rng(0).integers(0, 256, size=(*size, 3), dtype=np.uint8)


def test_forward_output_shape_and_contract() -> None:
    model = CarddHybrid(num_classes=7, base=32)
    out = model(torch.randn(1, 3, 512, 512))
    assert out.shape == (1, 7, 512, 512)
    assert 1_000_000 < sum(p.numel() for p in model.parameters()) < 6_000_000


def test_backward_runs() -> None:
    model = CarddHybrid(num_classes=7, base=16)
    out = model(torch.randn(2, 3, 64, 64))
    out.pow(2).mean().backward()
    assert model.enc1.block[0].weight.grad is not None


def test_transformer_bottleneck_is_connected() -> None:
    """Gradients must reach the transformer layers, not just the CNN."""
    model = CarddHybrid(num_classes=7, base=16)
    out = model(torch.randn(1, 3, 64, 64))
    out.sum().backward()
    transformer_params = [p for n, p in model.named_parameters() if "transformer" in n]
    assert transformer_params
    assert all(p.grad is not None for p in transformer_params)


def test_engine_dispatch_loads_hybrid_checkpoint(tmp_path: Path) -> None:
    model = CarddHybrid(num_classes=7, base=32)
    ckpt = tmp_path / "hybrid.pt"
    torch.save(
        {"model_state": model.state_dict(), "model_arch": "cardd_hybrid", "base": 32, "epoch": 3},
        ckpt,
    )
    engine = SegmentationEngine.from_checkpoint(ckpt, base=32, device="cpu")
    assert engine.metadata.arch == "CarddHybrid"
    result = engine.predict(_random_rgb())
    assert result.mask.shape == (512, 512)
    assert set(np.unique(result.mask).tolist()) <= set(range(7))
    assert result.prob.shape == (7, 512, 512)


def test_engine_rejects_unknown_arch(tmp_path: Path) -> None:
    model = CarddHybrid(num_classes=7, base=32)
    ckpt = tmp_path / "bad.pt"
    torch.save(
        {"model_state": model.state_dict(), "model_arch": "does_not_exist", "base": 32, "epoch": 0},
        ckpt,
    )
    with pytest.raises(ModelVersionError):
        SegmentationEngine.from_checkpoint(ckpt, base=32, device="cpu")
