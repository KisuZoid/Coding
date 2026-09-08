"""Preprocessing tests (Phase D, ADR 0003).

Pins the inference transform to the exact training-time operations in
ml/training/cardd_dataset.py by recomputing them independently and asserting
equality, without importing ml/training.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest
import torch

from ml.inference.preprocess import TARGET_SIZE, load_image_rgb, preprocess_image


def test_preprocess_matches_training_transform() -> None:
    rng = np.random.default_rng(0)
    img = rng.integers(0, 256, size=(533, 800, 3), dtype=np.uint8)

    got = preprocess_image(img)

    assert TARGET_SIZE == 512
    assert got.shape == (3, 512, 512)
    assert got.dtype == torch.float32
    resized = cv2.resize(img, (512, 512), interpolation=cv2.INTER_LINEAR)
    expected = torch.from_numpy(
        np.transpose(resized.astype(np.float32) / 255.0, (2, 0, 1))
    ).contiguous()
    assert torch.equal(got, expected)
    assert float(got.min()) >= 0.0 and float(got.max()) <= 1.0


def test_preprocess_rejects_float_and_wrong_shape() -> None:
    with pytest.raises(ValueError):
        preprocess_image(np.zeros((64, 64, 3), dtype=np.float32))
    with pytest.raises(ValueError):
        preprocess_image(np.zeros((64, 64, 4), dtype=np.uint8))
    with pytest.raises(ValueError):
        preprocess_image(np.zeros((64, 64), dtype=np.uint8))


def test_load_image_rgb_from_bytes_and_file(tmp_path: Path) -> None:
    import cv2

    bgr = np.zeros((40, 60, 3), dtype=np.uint8)
    bgr[:, :, 0] = 255  # blue channel in BGR -> red in RGB
    ok, buf = cv2.imencode(".png", bgr)
    assert ok
    data = buf.tobytes()

    got = load_image_rgb(data)
    assert got.shape == (40, 60, 3)
    assert tuple(got[0, 0]) == (0, 0, 255)  # BGR blue -> RGB blue confirmed

    path = tmp_path / "img.png"
    path.write_bytes(data)
    assert np.array_equal(load_image_rgb(path), got)

    with pytest.raises(ValueError):
        load_image_rgb(b"not an image")
    with pytest.raises(TypeError):
        load_image_rgb(123)  # type: ignore[arg-type]  # deliberate API guard
