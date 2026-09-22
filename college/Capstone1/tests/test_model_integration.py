"""Model-integration regression tests for the MODEL_UNAVAILABLE fix.

Covers the concrete failure chains reported by the demo UI ("model
unavailable" while upload/quality/chat still worked):

- checkpoint path resolution that is independent of the process CWD;
- engine loading of both the primary ``model_state`` key and the ``model``
  alias (legacy artefacts);
- CPU-safe loading and a multiclass ``[1, 7, 512, 512]`` output (never a
  binary foreground/background collapse);
- inference on one real CarDD photo through the engine and through the HTTP
  ``/analyze`` contract;
- a missing checkpoint surfacing as ``MODEL_UNAVAILABLE`` with the real
  reason logged server-side.

Tests that need the git-ignored pilot checkpoint or a CarDD dataset image use
a runtime presence guard and are skipped (never failed) when missing, matching
``tests/test_inference_smoke.py``.
"""

from __future__ import annotations

import logging
from pathlib import Path

import cv2
import numpy as np
import pytest
import torch
from fastapi.testclient import TestClient

from apps.api.container import _norm_path
from apps.api.main import create_app
from apps.api.settings import Settings
from ml.inference.engine import SegmentationEngine

_REPO_ROOT = Path(__file__).resolve().parent.parent
_CHECKPOINT = _REPO_ROOT / "ml" / "experiments" / "pilot15_hybrid" / "best_checkpoint.pt"
_SAMPLE_PHOTO = _REPO_ROOT / "datasets" / "CarDD_COCO" / "test2017" / "000950.jpg"

_skip_no_checkpoint = pytest.mark.skipif(
    not _CHECKPOINT.is_file(), reason="pilot hybrid checkpoint absent"
)
_skip_no_photo = pytest.mark.skipif(not _SAMPLE_PHOTO.is_file(), reason="CarDD test photo absent")


# --------------------------------------------------------------------------- #
# Checkpoint path resolution (CWD independence)
# --------------------------------------------------------------------------- #


def test_norm_path_absolute_passthrough(tmp_path: Path) -> None:
    assert _norm_path(tmp_path / "x.pt") == tmp_path / "x.pt"


def test_norm_path_resolves_against_repo_root_when_cwd_has_no_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    relative = Path("ml/experiments/pilot15_hybrid/best_checkpoint.pt")
    assert _norm_path(relative) == _CHECKPOINT


def test_norm_path_missing_relative_points_at_repo_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    missing = Path("ml/experiments/does-not-exist.pt")
    assert _norm_path(missing) == _REPO_ROOT / "ml/experiments/does-not-exist.pt"


# --------------------------------------------------------------------------- #
# Checkpoint loading: primary key, alias key, CPU
# --------------------------------------------------------------------------- #


def test_from_checkpoint_accepts_model_alias(tmp_path: Path) -> None:
    from ml.models.resnet34_unet import ResNet34UNet

    model = ResNet34UNet(num_classes=7, pretrained=False)
    ckpt = tmp_path / "alias.pt"
    torch.save(
        {"model": model.state_dict(), "base": 0, "epoch": 3, "model_arch": "resnet34_unet"},
        ckpt,
    )
    engine = SegmentationEngine.from_checkpoint(ckpt, base=0, device="cpu")
    assert isinstance(engine._model, ResNet34UNet)
    assert engine.metadata.epoch == 3


@_skip_no_checkpoint
def test_engine_loads_hybrid_checkpoint_on_cpu() -> None:
    engine = SegmentationEngine.from_checkpoint(_CHECKPOINT, base=0, device="cpu")
    assert engine.metadata.arch == "HybridSegmentation"
    assert engine.metadata.base == 0
    assert engine.metadata.epoch == 14


# --------------------------------------------------------------------------- #
# Inference: multiclass output + one real photo
# --------------------------------------------------------------------------- #


@_skip_no_checkpoint
def test_real_checkpoint_output_is_multiclass_not_binary() -> None:
    engine = SegmentationEngine.from_checkpoint(_CHECKPOINT, base=0, device="cpu")
    rng = np.random.default_rng(7)
    img = rng.integers(30, 200, size=(1080, 1920, 3), dtype=np.uint8)

    result = engine.predict(img)

    assert result.mask.shape == (512, 512)
    assert result.prob.shape == (7, 512, 512)
    assert 0 <= int(result.mask.min()) <= int(result.mask.max()) <= 6
    assert all(0.0 <= float(result.prob[cid].max()) <= 1.0 for cid in range(7))


@_skip_no_checkpoint
@_skip_no_photo
def test_real_photo_produces_damage_regions() -> None:
    engine = SegmentationEngine.from_checkpoint(_CHECKPOINT, base=0, device="cpu")
    data = _SAMPLE_PHOTO.read_bytes()

    result = engine.predict_bytes(data)

    assert result.mask.shape == (512, 512)

    assert result.damage_fraction > 0.0
    assert result.mask.max() >= 1


# --------------------------------------------------------------------------- #
# HTTP contract
# --------------------------------------------------------------------------- #


def _make_client(tmp_path: Path, *, model_path: Path | None) -> TestClient:
    app = create_app(
        Settings(
            environment="test",
            storage_root=tmp_path / "storage",
            training_root=tmp_path / "training",
            model_path=model_path,
            model_version=None,
            groq_api_key="",
            groq_model="unused-in-tests",
        )
    )
    return TestClient(app, raise_server_exceptions=False)


def _new_session(client: TestClient) -> str:
    resp = client.post("/inspection/session")
    assert resp.status_code == 200
    return str(resp.json()["session_id"])


@_skip_no_checkpoint
@_skip_no_photo
def test_api_analyze_with_real_engine_returns_structured_json(tmp_path: Path) -> None:
    client = _make_client(tmp_path, model_path=_CHECKPOINT)
    with client:
        session_id = _new_session(client)
        data = _SAMPLE_PHOTO.read_bytes()
        up = client.post(
            f"/inspection/{session_id}/upload",
            files={"file": ("photo.jpg", data, "image/jpeg")},
        )
        assert up.status_code == 200, up.text

        resp = client.post(f"/inspection/{session_id}/analyze")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["status"] == "OK"
        assert body["classes_present"]
        assert body["low_confidence"] is False
        assert body["damage_fraction"] > 0.0
        assert body["mean_confidence"] > 0.0
        assert body["overlay_png_base64"]
        meta = body["inspection"]["model_metadata"]
        assert meta["arch"] == "HybridSegmentation"
        assert meta["num_classes"] == 7
        assert meta["experiment_id"] == "pilot15_hybrid"


def test_api_missing_checkpoint_is_model_unavailable_and_reason_is_logged(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    bogus = tmp_path / "empty" / "checkpoint.pt"
    client = _make_client(tmp_path, model_path=bogus)
    with client:
        session_id = _new_session(client)
        rng = np.random.default_rng(0)
        img = rng.integers(30, 200, size=(256, 256, 3), dtype=np.uint8)
        ok, buf = cv2.imencode(".png", img)
        assert ok
        up = client.post(
            f"/inspection/{session_id}/upload",
            files={"file": ("photo.png", buf.tobytes(), "image/png")},
        )
        assert up.status_code == 200

        with caplog.at_level(logging.ERROR, logger="apps.api.routers.inspection"):
            resp = client.post(f"/inspection/{session_id}/analyze")

    assert resp.status_code == 500
    assert resp.json()["detail"]["code"] == "MODEL_UNAVAILABLE"
    assert any("model checkpoint not found" in rec.message for rec in caplog.records)
