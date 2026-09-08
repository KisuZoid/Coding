"""Overlay rendering for the model mask (Phase E).

Palette values match ``ml/evaluation/evaluate_run.py::CLASS_COLORS`` (the
research artifact) but are redefined here so ``ml/inference`` — and the vision
layer that depends only on it — never imports research/evaluation modules
(ADR 0003).
"""

from __future__ import annotations

import cv2
import numpy as np

CLASS_COLORS: dict[int, tuple[int, int, int]] = {
    0: (0, 0, 0),  # background
    1: (0, 200, 255),  # dent
    2: (0, 128, 255),  # scratch
    3: (255, 0, 0),  # crack
    4: (255, 255, 0),  # glass shatter
    5: (180, 105, 255),  # lamp broken
    6: (0, 255, 0),  # tire flat
}


def _blend(pixels: np.ndarray, color: tuple[int, int, int], alpha: float) -> np.ndarray:
    color_arr = np.asarray(color, dtype=np.float32)
    return pixels * (1.0 - alpha) + color_arr * alpha


def render_overlay(rgb: np.ndarray, mask: np.ndarray, *, alpha: float = 0.45) -> np.ndarray:
    """Overlay the predicted class mask onto the original RGB image."""
    if mask.shape != rgb.shape[:2]:
        mask = cv2.resize(mask, (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_NEAREST)
    output = rgb.astype(np.float32)
    for class_id, color in CLASS_COLORS.items():
        if class_id == 0:
            continue
        selection = mask == class_id
        if not selection.any():
            continue
        output[selection] = _blend(output[selection], color, alpha)
    return np.clip(output, 0, 255).astype(np.uint8)


def encode_png(rgb: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".png", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    if not ok:
        raise ValueError("failed to encode overlay PNG")
    return buf.tobytes()


def encode_jpeg(rgb: np.ndarray, *, quality: int = 90) -> bytes:
    params = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    ok, buf = cv2.imencode(".jpg", cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), params=params)
    if not ok:
        raise ValueError("failed to encode overlay JPEG")
    return buf.tobytes()
