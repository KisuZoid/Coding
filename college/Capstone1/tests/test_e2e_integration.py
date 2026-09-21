"""Phase P + ADR 0011: end-to-end integration over the FastAPI stack.

Drives the real HTTP contract the browser uses — session, upload, analyze,
follow-up chat, state, consent, delete — through one persisted application per
test (tmp storage roots, offline stub assistant, deterministic stub engine for
scenario control). One test exercises the committed hybrid checkpoint
end-to-end; it is skipped (never failed) when the artifact is absent. No cost
or repair fields exist anywhere in the contracts (asserted per test).
"""

from __future__ import annotations

import base64
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from apps.api.container import Container
from apps.api.main import create_app
from apps.api.settings import Settings
from ml.inference.engine import (
    ModelMetadata,
    QualityAssessment,
    SegmentationEngine,
    SegmentationResult,
)

_CHECKPOINT = Path("ml/experiments/cardd_hybrid_ce/best_checkpoint.pt")

# Fields that must never appear in a response or persisted state after the
# cost/repair removal.
_FORBIDDEN = {"cost", "repair", "quote", "price", "estimate", "money", "amount_paid"}


# --------------------------------------------------------------------------- #
# Image fixtures
# --------------------------------------------------------------------------- #


def _valid_rgb() -> np.ndarray:
    rng = np.random.default_rng(0)
    checker = np.indices((256, 256)).sum(axis=0) // 16 % 2
    blocks = np.where(checker, 156, 100).astype(np.int16)
    noisy = np.clip(blocks + rng.integers(-8, 9, (256, 256)).astype(np.int16), 0, 255).astype(
        np.uint8
    )
    noisy[96:160, 96:160] = 40
    return np.stack([noisy] * 3, axis=-1)


def _blurry_rgb() -> np.ndarray:
    return np.stack([cv2.GaussianBlur(_valid_rgb()[:, :, 0], (21, 21), 0)] * 3, axis=-1)


def _too_dark_rgb() -> np.ndarray:
    return np.full((256, 256, 3), 28, np.uint8)


def _glare_rgb() -> np.ndarray:
    gray = np.full((256, 256), 200, np.uint8)
    gray[:120, :] = 255
    return np.stack([gray] * 3, axis=-1)


def _low_contrast_rgb() -> np.ndarray:
    gray = np.full((256, 256), 120, np.uint8)
    gray[::24, :] = 118
    gray[:, ::24] = 140
    return np.stack([gray] * 3, axis=-1)


def _png_bytes(rgb: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".png", rgb)
    assert ok
    return buf.tobytes()


# --------------------------------------------------------------------------- #
# Deterministic stub engine (real SegmentationResult objects, no model)
# --------------------------------------------------------------------------- #


def _stub_result(mask: np.ndarray, *, low_confidence: bool) -> SegmentationResult:
    h, w = mask.shape
    prob = np.zeros((7, h, w), np.float32)
    prob[0] = 0.5
    for cid in np.unique(mask):
        if cid > 0:
            prob[int(cid)] = np.where(mask == int(cid), 0.95, prob[int(cid)])
    return SegmentationResult(
        mask=mask.astype(np.uint8),
        prob=prob,
        pixel_confidence=prob.max(axis=0),
        mean_confidence=0.55,
        damage_fraction=float((mask > 0).mean()),
        class_fractions={int(cid): float((mask == cid).mean()) for cid in range(7)},
        quality=QualityAssessment(low_confidence=low_confidence, notes=["e2e stub"]),
        metadata=ModelMetadata(
            model_version=None,
            experiment_id="e2e-stub",
            base=64,
            num_classes=7,
            checkpoint_path="e2e-stub",
            git_revision=None,
        ),
    )


def _scratch_mask() -> np.ndarray:
    mask = np.zeros((256, 256), np.uint8)
    mask[96:160, 96:160] = 2  # class 2 == scratch
    return mask


def _as_dict(value: object) -> dict[str, Any]:
    return cast(dict[str, Any], value)


def _container(client: TestClient) -> Container:
    app = cast(Any, client.app)
    return cast(Container, app.state.container)


class _StubEngine:
    def __init__(self, result: SegmentationResult) -> None:
        self._result = result

    def predict_bytes(self, data: bytes) -> SegmentationResult:  # noqa: ARG002
        return self._result


def _install_stub(client: TestClient, factory: Callable[[], SegmentationResult]) -> None:
    _container(client)._engine = cast(SegmentationEngine, _StubEngine(factory()))


# --------------------------------------------------------------------------- #
# Session choreography helpers
# --------------------------------------------------------------------------- #


def _make_client(tmp_path: Path) -> TestClient:
    app = create_app(
        Settings(
            environment="test",
            storage_root=tmp_path / "storage",
            training_root=tmp_path / "training",
            model_path=None,
            model_version=None,
            groq_api_key="",
            groq_model="unused-in-tests",
        )
    )
    return TestClient(app, raise_server_exceptions=False)


def _new_session(client: TestClient) -> str:
    body = client.post("/inspection/session")
    assert body.status_code == 200
    return cast(str, _as_dict(body.json())["session_id"])


def _chat(client: TestClient, session_id: str, message: str) -> dict[str, Any]:
    resp = client.post("/chat", json={"session_id": session_id, "message": message})
    assert resp.status_code == 200, resp.text
    return _as_dict(resp.json())


def _upload(client: TestClient, session_id: str, rgb: np.ndarray) -> None:
    resp = client.post(
        f"/inspection/{session_id}/upload",
        files={"file": ("photo.png", _png_bytes(rgb), "image/png")},
    )
    assert resp.status_code == 200, resp.text


def _state(client: TestClient, session_id: str) -> dict[str, Any]:
    resp = client.get(f"/inspection/{session_id}")
    assert resp.status_code == 200
    return cast(dict[str, Any], _as_dict(resp.json())["state"])


def _assert_no_forbidden_fields(obj: dict[str, Any]) -> None:
    for key, value in obj.items():
        assert key.lower() not in _FORBIDDEN, f"forbidden field present: {key}"
        if isinstance(value, dict):
            _assert_no_forbidden_fields(value)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


@pytest.mark.skipif(not _CHECKPOINT.is_file(), reason="hybrid checkpoint not present")
def test_full_journey_happy_path_with_real_engine(tmp_path: Path) -> None:
    """Browser journey against the hybrid engine: photo-first, no cost."""
    client = _make_client(tmp_path)
    session_id = _new_session(client)
    _upload(client, session_id, _valid_rgb())

    analysis = client.post(f"/inspection/{session_id}/analyze")
    assert analysis.status_code == 200, analysis.text
    body = _as_dict(analysis.json())
    assert body["status"] == "OK"
    assert body["assistant_message"]
    assert body["quality_status"] == "VALID"

    overlay = base64.b64decode(body["overlay_png_base64"])
    assert overlay[:8] == b"\x89PNG\r\n\x1a\n"

    follow_up = _chat(client, session_id, "What did you find?")
    assert follow_up["reply"]
    # ChatResponse contract: no waiting_for / finished gates.
    assert set(follow_up) == {"session_id", "reply", "request_id"}

    state = _state(client, session_id)
    inspection = state["inspection"]
    assert inspection["quality"]["status"] == "VALID"
    assert "low_confidence" in inspection
    _assert_no_forbidden_fields(body)
    _assert_no_forbidden_fields(inspection)

    resp = client.post(f"/inspection/{session_id}/consent", json={"decision": "GRANTED"})
    assert resp.status_code == 200, resp.text
    assert (tmp_path / "training" / "user-consented-v1").is_dir()

    assert client.delete(f"/inspection/{session_id}").status_code == 200
    assert client.get(f"/inspection/{session_id}").status_code == 410
    assert client.post("/chat", json={"session_id": session_id, "message": "hi"}).status_code == 410


def test_poor_quality_photo_returns_guidance_then_retake_succeeds(tmp_path: Path) -> None:
    client = _make_client(tmp_path)
    _install_stub(client, lambda: _stub_result(_scratch_mask(), low_confidence=False))
    session_id = _new_session(client)

    for rgb, expected in (
        (_blurry_rgb(), "TOO_BLURRY"),
        (_too_dark_rgb(), "TOO_DARK"),
        (_glare_rgb(), "EXCESSIVE_GLARE"),
        (_low_contrast_rgb(), "INSUFFICIENT_CONTEXT"),
    ):
        _upload(client, session_id, rgb)
        resp = client.post(f"/inspection/{session_id}/analyze")
        assert resp.status_code == 200, resp.text
        body = _as_dict(resp.json())
        assert body["status"] == "QUALITY_FAILED"
        assert body["quality_status"] == expected
        assert body["quality_reasons"]
        assert "retake" in body["assistant_message"].lower()
        # No segmentation output for a rejected photo.
        assert body["inspection"] is None
        assert body["overlay_png_base64"] is None
        state = _state(client, session_id)
        assert state["inspection"] is None
        assert "retake" in (state.get("explanation") or "").lower()

    _upload(client, session_id, _valid_rgb())
    resp = client.post(f"/inspection/{session_id}/analyze")
    assert resp.status_code == 200, resp.text
    assert _as_dict(resp.json())["status"] == "OK"


def test_low_confidence_proceeds_and_is_flagged_in_state(tmp_path: Path) -> None:
    client = _make_client(tmp_path)
    _install_stub(client, lambda: _stub_result(_scratch_mask(), low_confidence=True))
    session_id = _new_session(client)
    _upload(client, session_id, _valid_rgb())
    resp = client.post(f"/inspection/{session_id}/analyze")
    assert resp.status_code == 200, resp.text
    body = _as_dict(resp.json())
    assert body["low_confidence"] is True

    reply = _chat(client, session_id, "Is that reliable?")
    assert reply["reply"]
    assert _state(client, session_id)["inspection"]["low_confidence"] is True


def test_no_cost_or_repair_fields_in_any_contract(tmp_path: Path) -> None:
    client = _make_client(tmp_path)
    _install_stub(client, lambda: _stub_result(_scratch_mask(), low_confidence=False))
    session_id = _new_session(client)
    _upload(client, session_id, _valid_rgb())
    resp = client.post(f"/inspection/{session_id}/analyze")
    assert resp.status_code == 200, resp.text
    body = _as_dict(resp.json())
    _assert_no_forbidden_fields(body)

    reply = _chat(client, session_id, "What should I do next?")
    assert reply["reply"]
    assert "quote" not in reply["reply"].lower()

    state = _state(client, session_id)
    _assert_no_forbidden_fields(state)


def test_engine_failure_surfaces_500_and_session_survives(tmp_path: Path) -> None:
    class _Boom:
        def predict_bytes(self, data: bytes) -> SegmentationResult:  # noqa: ARG002
            raise RuntimeError("simulated inference failure")

    client = _make_client(tmp_path)
    _container(client)._engine = cast(SegmentationEngine, _Boom())
    session_id = _new_session(client)
    _upload(client, session_id, _valid_rgb())
    assert client.post(f"/inspection/{session_id}/analyze").status_code == 500

    # the session is still usable afterwards
    resp = _chat(client, session_id, "still here")
    assert resp["reply"]
    assert "photo" in resp["reply"].lower()


@pytest.mark.parametrize(
    "decision,expect_saved",
    [("GRANTED", True), ("DECLINED", False)],
)
def test_consent_endpoint(tmp_path: Path, decision: str, expect_saved: bool) -> None:
    client = _make_client(tmp_path)
    _install_stub(client, lambda: _stub_result(_scratch_mask(), low_confidence=False))
    session_id = _new_session(client)
    _upload(client, session_id, _valid_rgb())
    assert client.post(f"/inspection/{session_id}/analyze").status_code == 200

    resp = client.post(f"/inspection/{session_id}/consent", json={"decision": decision})
    assert resp.status_code == 200, resp.text
    body = _as_dict(resp.json())
    assert body["saved"] is expect_saved
    assert body["dataset_version"] == "user-consented-v1"
    if expect_saved:
        assert body["sample_id"]
        assert (tmp_path / "training" / "user-consented-v1").is_dir()


def test_validation_contract_on_edge_inputs(tmp_path: Path) -> None:
    client = _make_client(tmp_path)
    session_id = _new_session(client)

    resp = client.post("/chat", json={"session_id": session_id, "message": ""})
    assert resp.status_code == 422
    resp = client.post("/chat", json={"session_id": session_id, "message": "x" * 1001})
    assert resp.status_code == 422
    assert client.post("/chat", json={"session_id": "nope", "message": "hi"}).status_code == 404

    assert client.post(f"/inspection/{session_id}/analyze").status_code == 404

    resp = client.post(
        f"/inspection/{session_id}/upload",
        files={"file": ("notes.txt", b"definitely not an image", "text/plain")},
    )
    assert resp.status_code == 400
