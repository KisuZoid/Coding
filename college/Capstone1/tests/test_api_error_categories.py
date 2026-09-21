"""API error-category + LLM-fallback contracts (ADR 0011 photo-first).

Verifies the typed failure surface (``detail.code`` ∈ SESSION_NOT_FOUND /
NO_UPLOADED_PHOTO / MODEL_UNAVAILABLE / INFERENCE_FAILED / LLM_UNAVAILABLE)
and that ``/analyze`` still returns the structured segmentation result when the
live LangChain assistant is down (``assistant_fallback``), while ``/chat`` is
purely LLM-bound.

No live network: every assistant path is a raising double; the model path uses
a deterministic stub engine or a deliberately missing checkpoint.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from apps.api.agent.assistant import AssistantUnavailableError
from apps.api.container import Container
from apps.api.main import create_app
from apps.api.settings import Settings
from ml.inference.engine import (
    ModelMetadata,
    QualityAssessment,
    SegmentationEngine,
    SegmentationResult,
)


def _valid_rgb() -> np.ndarray:
    rng = np.random.default_rng(0)
    checker = np.indices((256, 256)).sum(axis=0) // 16 % 2
    blocks = np.where(checker, 156, 100).astype(np.int16)
    noisy = np.clip(blocks + rng.integers(-8, 9, (256, 256)).astype(np.int16), 0, 255).astype(
        np.uint8
    )
    noisy[96:160, 96:160] = 40
    return np.stack([noisy] * 3, axis=-1)


def _png_bytes(rgb: np.ndarray) -> bytes:
    ok, buf = cv2.imencode(".png", rgb)
    assert ok
    return buf.tobytes()


def _as_dict(value: object) -> dict[str, Any]:
    return cast(dict[str, Any], value)


def _container(client: TestClient) -> Container:
    return cast(Container, cast(Any, client.app).state.container)


def _new_session(client: TestClient) -> str:
    body = client.post("/inspection/session")
    assert body.status_code == 200
    return cast(str, _as_dict(body.json())["session_id"])


def _upload(client: TestClient, session_id: str) -> None:
    resp = client.post(
        f"/inspection/{session_id}/upload",
        files={"file": ("photo.png", _png_bytes(_valid_rgb()), "image/png")},
    )
    assert resp.status_code == 200, resp.text


class _BoomAssistant:
    """Every production LLM call raises -> exercises the typed LLM_UNAVAILABLE."""

    provider = "boom"

    def damages_explanation(self, evidence: dict[str, Any]) -> str:  # noqa: ARG002
        raise AssistantUnavailableError("llm down")

    def retake_guidance(self, reasons: list[str]) -> str:  # noqa: ARG002
        raise AssistantUnavailableError("llm down")

    def chat_reply(
        self,
        history: list[dict[str, str]],  # noqa: ARG002
        evidence: dict[str, Any] | None,  # noqa: ARG002
    ) -> str:
        raise AssistantUnavailableError("llm down")


class _StubEngine:
    def __init__(self, result: SegmentationResult) -> None:
        self._result = result

    def predict_bytes(self, data: bytes) -> SegmentationResult:  # noqa: ARG002
        return self._result


def _scratch_result() -> SegmentationResult:
    mask = np.zeros((256, 256), np.uint8)
    mask[96:160, 96:160] = 2
    prob = np.zeros((7, 256, 256), np.float32)
    prob[0] = 0.5
    prob[2] = np.where(mask == 2, 0.95, 0.5)
    return SegmentationResult(
        mask=mask,
        prob=prob,
        pixel_confidence=prob.max(axis=0),
        mean_confidence=0.55,
        damage_fraction=float((mask > 0).mean()),
        class_fractions={int(cid): float((mask == cid).mean()) for cid in range(7)},
        quality=QualityAssessment(low_confidence=False, notes=["test"]),
        metadata=ModelMetadata(
            model_version=None,
            experiment_id="test",
            base=32,
            num_classes=7,
            checkpoint_path="test",
        ),
    )


def _make_client(
    tmp_path: Path,
    *,
    assistant: object | None = None,
    model_path: Path | None = None,
    monkeypatch: pytest.MonkeyPatch | None = None,
) -> TestClient:
    settings = Settings(
        environment="test",
        storage_root=tmp_path / "storage",
        training_root=tmp_path / "training",
        model_path=model_path,
        model_version=None,
        groq_api_key="sk-test",  # non-empty so the container wants a LangChain assistant
        groq_model="unused-in-tests",
    )
    if assistant is not None:
        assert monkeypatch is not None
        monkeypatch.setattr("apps.api.container.build_assistant", lambda _settings: assistant)
    return TestClient(create_app(settings), raise_server_exceptions=False)


def _detail(resp: Any) -> dict[str, Any]:
    body = _as_dict(resp.json())
    return _as_dict(body["detail"])


def test_analyze_ok_without_groq_when_llm_down(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Structured segmentation result must survive a dead LLM (req: analyze).

    The engine runs independently of Groq; the unavailable LLM is replaced by
    a clearly flagged offline evidence summary, never a 503.
    """
    client = _make_client(tmp_path, assistant=_BoomAssistant(), monkeypatch=monkeypatch)
    _container(client)._engine = cast(SegmentationEngine, _StubEngine(_scratch_result()))
    session_id = _new_session(client)
    _upload(client, session_id)

    resp = client.post(f"/inspection/{session_id}/analyze")
    assert resp.status_code == 200, resp.text
    body = _as_dict(resp.json())
    assert body["status"] == "OK"
    assert body["assistant_fallback"] is True
    assert body["assistant_message"]
    assert body["inspection"] is not None
    assert body["classes_present"] == {"2": "scratch"}
    assert body["overlay_png_base64"]
    assert "scratch" in body["assistant_message"].lower()


def test_quality_failed_keeps_retake_guidance_when_llm_down(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A rejected photo still yields retake guidance (offline) instead of 503."""
    client = _make_client(tmp_path, assistant=_BoomAssistant(), monkeypatch=monkeypatch)
    session_id = _new_session(client)
    gray = np.full((256, 256, 3), 28, np.uint8)  # TOO_DARK
    resp = client.post(
        f"/inspection/{session_id}/upload",
        files={"file": ("photo.png", _png_bytes(gray), "image/png")},
    )
    assert resp.status_code == 200

    resp = client.post(f"/inspection/{session_id}/analyze")
    assert resp.status_code == 200, resp.text
    body = _as_dict(resp.json())
    assert body["status"] == "QUALITY_FAILED"
    assert body["assistant_fallback"] is True
    assert body["quality_status"] == "TOO_DARK"
    assert "retake" in body["assistant_message"].lower()


def test_chat_llm_unavailable_code(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Chat is LLM-bound: a dead LLM is a typed 503, not a vague message."""
    client = _make_client(tmp_path, assistant=_BoomAssistant(), monkeypatch=monkeypatch)
    session_id = _new_session(client)
    resp = client.post("/chat", json={"session_id": session_id, "message": "hi"})
    assert resp.status_code == 503
    assert _detail(resp)["code"] == "LLM_UNAVAILABLE"
    assert "Traceback" not in resp.text and "gsk-" not in resp.text


def test_model_unavailable_code(tmp_path: Path) -> None:
    """Missing checkpoint artefact surfaces as MODEL_UNAVAILABLE (loud, no fallback)."""
    bogus = tmp_path / "empty" / "checkpoint.pt"
    client = _make_client(tmp_path, model_path=bogus)
    session_id = _new_session(client)
    _upload(client, session_id)
    resp = client.post(f"/inspection/{session_id}/analyze")
    assert resp.status_code == 500
    assert _detail(resp)["code"] == "MODEL_UNAVAILABLE"


def test_inference_failed_code(tmp_path: Path) -> None:
    """A forward-pass failure is INFERENCE_FAILED, distinct from MODEL_UNAVAILABLE."""
    client = _make_client(tmp_path)

    class _Boom:
        def predict_bytes(self, data: bytes) -> SegmentationResult:  # noqa: ARG002
            raise RuntimeError("simulated forward failure")

    _container(client)._engine = cast(SegmentationEngine, _Boom())
    session_id = _new_session(client)
    _upload(client, session_id)
    resp = client.post(f"/inspection/{session_id}/analyze")
    assert resp.status_code == 500
    assert _detail(resp)["code"] == "INFERENCE_FAILED"


def test_session_and_photo_error_codes(tmp_path: Path) -> None:
    client = _make_client(tmp_path)
    resp = client.post("/inspection/does-not-exist/analyze")
    assert resp.status_code == 404
    assert _detail(resp)["code"] == "SESSION_NOT_FOUND"

    resp = client.post("/chat", json={"session_id": "does-not-exist", "message": "hi"})
    assert resp.status_code == 404
    assert _detail(resp)["code"] == "SESSION_NOT_FOUND"

    session_id = _new_session(client)
    resp = client.post(f"/inspection/{session_id}/analyze")
    assert resp.status_code == 404
    assert _detail(resp)["code"] == "NO_UPLOADED_PHOTO"
