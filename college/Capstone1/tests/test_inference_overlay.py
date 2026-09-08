"""Phase E: overlay rendering + PNG/JPEG encoding."""

from __future__ import annotations

import numpy as np

from ml.inference.overlay import CLASS_COLORS, encode_jpeg, encode_png, render_overlay


def _rgb(w: int = 64, h: int = 64) -> np.ndarray:
    return np.full((h, w, 3), 120, dtype=np.uint8)


def test_render_overlay_blends_class_colors() -> None:
    rgb = _rgb()
    mask = np.zeros((64, 64), dtype=np.uint8)
    mask[10:20, 10:20] = 1
    out = render_overlay(rgb, mask)
    blended = 120 * (1 - 0.45) + CLASS_COLORS[1][0] * 0.45
    assert out[15, 15, 0] == round(blended)
    assert out[0, 0].tolist() == [120, 120, 120]
    assert out.shape == rgb.shape


def test_render_overlay_resizes_mask_to_image() -> None:
    rgb = _rgb(32, 32)
    mask = np.zeros((16, 16), dtype=np.uint8)
    mask[2:4, 2:4] = 2
    out = render_overlay(rgb, mask)
    assert out.shape == (32, 32, 3)


def test_encodes_are_valid_png_jpeg() -> None:
    png = encode_png(_rgb())
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    jpeg = encode_jpeg(_rgb())
    assert jpeg[:2] == b"\xff\xd8"


def test_palette_matches_research_evaluation_colors() -> None:
    assert CLASS_COLORS[0] == (0, 0, 0)
    assert CLASS_COLORS[1] == (0, 200, 255)
    assert CLASS_COLORS[2] == (0, 128, 255)
    assert CLASS_COLORS[3] == (255, 0, 0)
    assert CLASS_COLORS[4] == (255, 255, 0)
    assert CLASS_COLORS[5] == (180, 105, 255)
    assert CLASS_COLORS[6] == (0, 255, 0)
