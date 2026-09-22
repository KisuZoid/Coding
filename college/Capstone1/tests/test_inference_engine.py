"""Engine tests (Phase D, ADR 0003) against a synthetic checkpoint."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
import torch

from ml.inference import (
    ModelLoadError,
    ModelMetadata,
    ModelVersionError,
    SegmentationEngine,
)
from ml.models.cardd_unet import CarddUNet
from ml.models.hybrid_segmentation import HybridSegmentation
from ml.models.resnet34_unet import ResNet34UNet


def _solid_rgb(size: tuple[int, int] = (64, 80)) -> np.ndarray:
    img = np.zeros((*size, 3), dtype=np.uint8)
    img[:, :, 2] = 200  # mostly blue-ish region
    return img


def _random_rgb(size: tuple[int, int] = (533, 800), seed: int = 0) -> np.ndarray:
    return np.random.default_rng(seed).integers(0, 256, size=(*size, 3), dtype=np.uint8)


def _write_checkpoint(path: Path, *, base: int = 64, epoch: int = 99) -> None:
    model = CarddUNet(base=base, num_classes=7)
    torch.save(
        {"model_state": model.state_dict(), "base": base, "epoch": epoch},
        path,
    )


def _write_research_checkpoint(path: Path, *, arch: str, base: int = 0, epoch: int = 14) -> None:
    model = (
        ResNet34UNet(num_classes=7, pretrained=False)
        if arch in {"resnet34_unet", "baseline"}
        else HybridSegmentation(num_classes=7, pretrained=False)
    )
    torch.save(
        {"model_state": model.state_dict(), "base": base, "epoch": epoch, "model_arch": arch},
        path,
    )


def test_research_archs_dispatch_and_predict(
    tmp_path: Path,
) -> None:
    import torch.nn as nn

    cases = [
        ("resnet34_unet", ResNet34UNet),
        ("baseline", ResNet34UNet),
        ("hybrid", HybridSegmentation),
        ("hybrid_segmentation", HybridSegmentation),
    ]
    for arch, model_cls in cases:
        ckpt = tmp_path / f"{arch}.pt"
        _write_research_checkpoint(ckpt, arch=arch)
        engine = SegmentationEngine.from_checkpoint(ckpt, base=0, device="cpu")
        assert isinstance(engine._model, nn.Module)
        assert isinstance(engine._model, model_cls)
        assert engine.metadata.experiment_id == ckpt.parent.name
        assert engine.metadata.base == 0
        assert engine.metadata.epoch == 14
        result = engine.predict(_random_rgb())
        assert result.mask.shape == (512, 512)
        assert result.prob.shape == (7, 512, 512)


def test_research_archs_skip_legacy_base_check(tmp_path: Path) -> None:
    ckpt = tmp_path / "pilot.pt"
    _write_research_checkpoint(ckpt, arch="hybrid", base=0)
    engine = SegmentationEngine.from_checkpoint(ckpt, base=64, device="cpu")
    assert isinstance(engine._model, HybridSegmentation)
    result = engine.predict(_random_rgb())
    assert result.mask.shape == (512, 512)


def test_unknown_arch_raises_loudly(tmp_path: Path) -> None:
    ckpt = tmp_path / "unknown.pt"
    _write_research_checkpoint(ckpt, arch="hybrid")
    data = torch.load(str(ckpt), map_location="cpu", weights_only=False)
    data["model_arch"] = "something_else"
    torch.save(data, ckpt)
    with pytest.raises(ModelVersionError):
        SegmentationEngine.from_checkpoint(ckpt, base=0, device="cpu")


def test_from_checkpoint_loads_and_predicts(tmp_path: Path) -> None:
    ckpt = tmp_path / "model.pt"
    _write_checkpoint(ckpt, epoch=12)
    engine = SegmentationEngine.from_checkpoint(
        ckpt, model_version="1.0.0", git_revision="deadbeef", device="cpu"
    )

    result = engine.predict(_random_rgb())

    assert result.mask.shape == (512, 512)
    assert result.mask.dtype == np.uint8
    assert result.prob.shape == (7, 512, 512)
    assert result.pixel_confidence.shape == (512, 512)
    np.testing.assert_allclose(result.prob.sum(axis=0), 1.0, atol=1e-5)
    assert set(np.unique(result.mask).tolist()) <= set(range(7))
    assert 0.0 <= result.damage_fraction <= 1.0
    assert set(result.class_fractions) == set(range(7))
    assert result.quality.notes
    assert result.metadata.model_version == "1.0.0"
    assert result.metadata.git_revision == "deadbeef"
    assert result.metadata.epoch == 12
    assert result.metadata.base == 64


def test_from_checkpoint_fails_loudly_when_artefact_unusable(tmp_path: Path) -> None:
    with pytest.raises(ModelLoadError):
        SegmentationEngine.from_checkpoint(tmp_path / "missing.pt", device="cpu")

    garbage = tmp_path / "garbage.pt"
    garbage.write_bytes(b"not a torch artefact")
    with pytest.raises(ModelLoadError):
        SegmentationEngine.from_checkpoint(garbage, device="cpu")

    truncated = tmp_path / "truncated.pt"
    torch.save({"base": 64}, truncated)  # missing model_state -> contract violation
    with pytest.raises(ModelLoadError):
        SegmentationEngine.from_checkpoint(truncated, device="cpu")


def test_from_checkpoint_rejects_base_mismatch(tmp_path: Path) -> None:
    ckpt = tmp_path / "base32.pt"
    _write_checkpoint(ckpt, base=32)
    with pytest.raises(ModelVersionError):
        SegmentationEngine.from_checkpoint(ckpt, base=64, device="cpu")


def test_low_confidence_flag_respects_thresholds() -> None:
    model = CarddUNet(base=64, num_classes=7)
    metadata = ModelMetadata(
        model_version=None,
        experiment_id="test",
        base=64,
        num_classes=7,
        checkpoint_path="fakepath",
    )
    strict = SegmentationEngine(model, metadata, device="cpu")
    permissive = SegmentationEngine(
        model,
        metadata,
        device="cpu",
        min_mean_confidence=0.0,
        min_damage_fraction=0.0,
    )

    result = strict.predict(_solid_rgb())
    assert result.quality.low_confidence is True
    assert result.mean_confidence < 0.5  # near-uniform softmax from random init

    relaxed = permissive.predict(_solid_rgb())
    assert relaxed.quality.low_confidence is False
    assert relaxed.quality.notes  # baseline limitations still present


def test_predict_bytes_decode_and_reject(tmp_path: Path) -> None:
    import cv2

    ckpt = tmp_path / "model.pt"
    _write_checkpoint(ckpt)
    engine = SegmentationEngine.from_checkpoint(ckpt, device="cpu")

    ok, buf = cv2.imencode(".png", _solid_rgb())
    assert ok
    result = engine.predict_bytes(buf.tobytes())
    assert result.mask.shape == (512, 512)

    with pytest.raises(ValueError):
        engine.predict_bytes(b"not an image at all")


def test_result_to_dict_is_compact_json(tmp_path: Path) -> None:
    ckpt = tmp_path / "model.pt"
    _write_checkpoint(ckpt)
    engine = SegmentationEngine.from_checkpoint(ckpt, device="cpu")
    payload = engine.predict(_random_rgb()).to_dict()

    assert set(payload) == {
        "mask_png_base64",
        "width",
        "height",
        "mean_confidence",
        "damage_fraction",
        "class_fractions",
        "per_class_prob",
        "quality",
        "metadata",
    }
    assert payload["width"] == payload["height"] == 512
    assert payload["mask_png_base64"]
    assert set(payload["per_class_prob"]) == {"0", "1", "2", "3", "4", "5", "6"}
    assert payload["quality"]["low_confidence"] is True
    assert payload["metadata"]["num_classes"] == 7
