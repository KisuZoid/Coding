"""Phase P: full end-to-end integration over the FastAPI + LangGraph stack.

Drives the real HTTP contract the browser uses — session, chat, upload,
analyze, state, consent, finish, delete — through one persisted application
per test (tmp storage roots, rule-based Groq, deterministic stub engine for
scenario control). One test exercises the committed checkpoint end-to-end;
it is skipped (never failed) when the artifact is absent.
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

_CHECKPOINT = Path("ml/experiments/cardd_baseline_ce/best_checkpoint.pt")

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


def _no_damage_mask() -> np.ndarray:
    return np.zeros((256, 256), np.uint8)


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


def _to_photo(client: TestClient, session_id: str, first_message: str) -> None:
    resp = _chat(client, session_id, first_message)
    assert resp["waiting_for"] == "REPAIR_LOCATION"
    resp = _chat(client, session_id, "not sure yet")
    assert resp["waiting_for"] == "INSURANCE"
    resp = _chat(client, session_id, "no insurance claim")
    assert resp["waiting_for"] == "PHOTO"


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


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


@pytest.mark.skipif(not _CHECKPOINT.is_file(), reason="committed demo checkpoint not present")
def test_full_journey_happy_path_with_real_engine(tmp_path: Path) -> None:
    """The browser journey against the committed engine: no fabricated cost,
    honest low-confidence flag, agreement computed, consent stored, finish."""
    client = _make_client(tmp_path)
    session_id = _new_session(client)
    _to_photo(client, session_id, "I hit a pothole and scraped the front bumper")
    _upload(client, session_id, _valid_rgb())

    analysis = client.post(f"/inspection/{session_id}/analyze")
    assert analysis.status_code == 200, analysis.text
    body = _as_dict(analysis.json())
    assert "overlay_png_base64" in body
    assert isinstance(body["low_confidence"], bool)

    overlay = base64.b64decode(body["overlay_png_base64"])
    assert overlay[:8] == b"\x89PNG\r\n\x1a\n"

    resp = _chat(client, session_id, "Photo uploaded - what do you think?")
    assert resp["waiting_for"] == "CONSENT"

    state = _state(client, session_id)
    assert state["analysis"]["quality_reasons"] == []
    assert "low_confidence" in state["analysis"]
    assert state["cost"]["status"] == "DATA_UNAVAILABLE"
    assert state["repair"]["action"]  # honest demonstration rule label
    allowed = {"AGREEMENT", "PARTIAL_AGREEMENT", "DISAGREEMENT", "NOT_APPLICABLE"}
    assert state["comparison"] in allowed
    assert "quote" in (resp["reply"] or "").lower()

    resp = _chat(client, session_id, "yes")
    assert resp["waiting_for"] == "FINISH" and resp["finished"] is False
    training_files = list((tmp_path / "training").rglob("*.png"))
    assert training_files  # consented sample was persisted

    resp = _chat(client, session_id, "I am done, please wrap up.")
    assert resp["finished"] is True

    assert client.get(f"/inspection/{session_id}").status_code == 410
    assert client.post("/chat", json={"session_id": session_id, "message": "hi"}).status_code == 410
    assert client.delete(f"/inspection/{session_id}").status_code == 200
    # Closed sessions keep an audit row but are gone to the domain (410 Gone);
    # a second delete is idempotent.
    assert client.get(f"/inspection/{session_id}").status_code == 410
    assert client.delete(f"/inspection/{session_id}").status_code == 200


def test_poor_quality_photo_rejected_with_reasons_then_retake_succeeds(tmp_path: Path) -> None:
    client = _make_client(tmp_path)
    session_id = _new_session(client)
    _to_photo(client, session_id, "I hit a pothole and scraped the front bumper")

    for rgb, expected in (
        (_blurry_rgb(), "TOO_BLURRY"),
        (_too_dark_rgb(), "TOO_DARK"),
        (_glare_rgb(), "EXCESSIVE_GLARE"),
        (_low_contrast_rgb(), "INSUFFICIENT_CONTEXT"),
    ):
        _upload(client, session_id, rgb)
        resp = client.post(f"/inspection/{session_id}/analyze")
        assert resp.status_code == 422, resp.text
        detail = _as_dict(resp.json())["detail"]
        assert detail["status"] == expected
        assert detail["reasons"]

    _upload(client, session_id, _valid_rgb())
    resp = client.post(f"/inspection/{session_id}/analyze")
    assert resp.status_code == 200, resp.text
    assert isinstance(_as_dict(resp.json())["low_confidence"], bool)


def test_low_confidence_proceeds_and_is_flaged_in_state(tmp_path: Path) -> None:
    client = _make_client(tmp_path)
    _install_stub(client, lambda: _stub_result(_scratch_mask(), low_confidence=True))
    session_id = _new_session(client)
    _to_photo(client, session_id, "I hit a pothole and scraped the front bumper")
    _upload(client, session_id, _valid_rgb())
    assert client.post(f"/inspection/{session_id}/analyze").status_code == 200

    resp = _chat(client, session_id, "Photo uploaded - what do you think?")
    assert resp["waiting_for"] == "CONSENT"
    state = _state(client, session_id)
    assert state["analysis"]["low_confidence"] is True


def test_disagreement_flagged_when_model_finds_what_user_did_not_say(tmp_path: Path) -> None:
    client = _make_client(tmp_path)
    _install_stub(client, lambda: _stub_result(_scratch_mask(), low_confidence=False))
    session_id = _new_session(client)
    _to_photo(client, session_id, "I scraped the bonnet of the car by a lamppost")
    state = _state(client, session_id)
    assert state["damage_location"] == "bonnet"

    _upload(client, session_id, _valid_rgb())
    assert client.post(f"/inspection/{session_id}/analyze").status_code == 200
    resp = _chat(client, session_id, "Photo uploaded - what do you think?")
    assert resp["waiting_for"] == "CONSENT"
    assert _state(client, session_id)["comparison"] == "DISAGREEMENT"


def test_one_sided_report_is_partial_agreement(tmp_path: Path) -> None:
    client = _make_client(tmp_path)
    _install_stub(client, lambda: _stub_result(_no_damage_mask(), low_confidence=False))
    session_id = _new_session(client)
    _to_photo(client, session_id, "I hit a pothole and scraped the front bumper")
    state = _state(client, session_id)
    assert state["damage_location"] == "bumper"

    _upload(client, session_id, _valid_rgb())
    assert client.post(f"/inspection/{session_id}/analyze").status_code == 200
    resp = _chat(client, session_id, "Photo uploaded - what do you think?")
    assert resp["waiting_for"] == "CONSENT"
    assert _state(client, session_id)["comparison"] == "PARTIAL_AGREEMENT"


def test_engine_failure_surfaces_500_and_session_survives(tmp_path: Path) -> None:
    class _Boom:
        def predict_bytes(self, data: bytes) -> SegmentationResult:  # noqa: ARG002
            raise RuntimeError("simulated inference failure")

    client = _make_client(tmp_path)
    _container(client)._engine = cast(SegmentationEngine, _Boom())
    session_id = _new_session(client)
    _to_photo(client, session_id, "I hit a pothole and scraped the front bumper")
    _upload(client, session_id, _valid_rgb())
    assert client.post(f"/inspection/{session_id}/analyze").status_code == 500

    # the session is still usable afterwards
    resp = _chat(client, session_id, "still here")
    assert resp["waiting_for"] in ("PHOTO", "CONSENT")


def test_consent_endpoint_granted_persists_sample(tmp_path: Path) -> None:
    client = _make_client(tmp_path)
    _install_stub(client, lambda: _stub_result(_scratch_mask(), low_confidence=False))
    session_id = _new_session(client)
    _to_photo(client, session_id, "I hit a pothole and scraped the front bumper")
    _upload(client, session_id, _valid_rgb())
    assert client.post(f"/inspection/{session_id}/analyze").status_code == 200
    reply = _chat(client, session_id, "Photo uploaded - what do you think?")
    assert reply["waiting_for"] == "CONSENT"

    resp = client.post(f"/inspection/{session_id}/consent", json={"decision": "GRANTED"})
    assert resp.status_code == 200, resp.text
    body = _as_dict(resp.json())
    assert body["saved"] is True and body["sample_id"]
    assert body["dataset_version"] == "user-consented-v1"
    assert (tmp_path / "training" / "user-consented-v1").is_dir()

    declined = client.post(f"/inspection/{session_id}/consent", json={"decision": "DECLINED"})
    assert declined.status_code == 200
    assert _as_dict(declined.json())["saved"] is False


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
