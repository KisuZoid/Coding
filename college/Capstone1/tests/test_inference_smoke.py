"""Real-artefact smoke test (Phase D).

Exercises the actual CarDD baseline checkpoint when it is present locally
(in the git-ignored experiments dir). Skipped otherwise; existence is verified
at runtime, not assumed. This is the ADR 0003 "loud artefact check".
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from ml.inference import SegmentationEngine, SegmentationResult

_CHECKPOINT = (
    Path(__file__).resolve().parent.parent
    / "ml"
    / "experiments"
    / "cardd_baseline_ce"
    / "best_checkpoint.pt"
)

pytestmark = pytest.mark.skipif(
    not _CHECKPOINT.is_file(),
    reason="real baseline checkpoint absent (git-ignored experiments dir)",
)


def _plausible_photo() -> np.ndarray:
    rng = np.random.default_rng(7)
    img = rng.integers(30, 200, size=(1080, 1920, 3), dtype=np.uint8)
    img[200:340, 500:700, 1] = 70  # a darker "damage-ish" patch
    return img


def test_real_checkpoint_loads_and_predicts() -> None:
    engine = SegmentationEngine.from_checkpoint(_CHECKPOINT, device="cpu")
    assert engine.metadata.experiment_id == "cardd_baseline_ce"
    assert engine.metadata.base == 64
    assert engine.metadata.epoch is not None
    assert engine.metadata.git_revision is None  # no fabricated revision

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
