"""Inference preprocessing (Phase D, ADR 0003).

Reproduces exactly the transform used at training time in
``ml/training/cardd_dataset.py`` (:class:`CarddInstanceSegDataset`): resize to
``TARGET_SIZE = 512`` with ``cv2.INTER_LINEAR``, scale by ``1/255``, layout as
``float32 CHW``. Input images are RGB ``uint8`` (the training adapter reads
them as RGB via ``COLOR_BGR2RGB``).

Inference never imports ``ml/training`` (ADR 0003); equivalence is pinned by
``tests/test_inference_preprocess.py``, which recomputes the training ops
independently and asserts bitwise equality.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import torch

TARGET_SIZE = 512


def load_image_rgb(source: Path | bytes) -> np.ndarray:
    """Decode a JPEG/PNG/WebP image as RGB uint8 ``HxWx3``."""
    if isinstance(source, Path):
        raw = np.fromfile(str(source), dtype=np.uint8)
        if raw.size == 0:
            raise ValueError(f"empty or unreadable image file: {source}")
    elif isinstance(source, bytes):
        raw = np.frombuffer(source, dtype=np.uint8)
    else:
        raise TypeError(f"unsupported image source: {type(source).__name__}")
    decoded = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if decoded is None:
        raise ValueError("could not decode image bytes")
    return cv2.cvtColor(decoded, cv2.COLOR_BGR2RGB)


def preprocess_image(rgb: np.ndarray) -> torch.Tensor:
    """Convert RGB uint8 HWC into the training-time float32 CHW tensor."""
    if rgb.dtype != np.uint8:
        raise ValueError(f"preprocess expects uint8 RGB, got dtype {rgb.dtype!r}")
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError(f"preprocess expects HxWx3 RGB, got shape {rgb.shape}")
    resized = cv2.resize(rgb, (TARGET_SIZE, TARGET_SIZE), interpolation=cv2.INTER_LINEAR)
    normalized = resized.astype(np.float32) / 255.0
    return torch.from_numpy(np.transpose(normalized, (2, 0, 1))).contiguous()
