from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from fastapi.testclient import TestClient

from apps.api.container import Container
from apps.api.main import create_app
from apps.api.settings import Settings

MODEL_IDS = [
    "final60_baseline_seed42",
    "final60_baseline_seed1337",
    "final60_hybrid_seed42",
    "final60_hybrid_seed1337",
    "final100_hybrid_seed42",
]


def _client(tmp_path: Path) -> TestClient:
    app = create_app(
        Settings(
            environment="test",
            storage_root=tmp_path / "storage",
            training_root=tmp_path / "training",
            model_path=None,
            model_id=None,
            model_version=None,
            groq_api_key="",
            groq_model="unused-in-tests",
        )
    )
    return TestClient(app, raise_server_exceptions=False)


def _container(client: TestClient) -> Container:
    return cast(Container, cast(Any, client.app).state.container)


def test_models_expose_exactly_five_active_entries(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        response = client.get("/models")

    assert response.status_code == 200
    body = response.json()
    assert [model["model_id"] for model in body["models"]] == MODEL_IDS
    assert body["default_model_id"] == "final60_hybrid_seed42"
    assert sum(model["controlled"] for model in body["models"]) == 4
    assert body["models"][-1]["status"] == "EXPLORATORY"
    assert body["models"][-1]["record_status"] == "PARTIAL_RECONSTRUCTED_FROM_CHECKPOINTS"


def test_session_persists_selected_model_and_rejects_unknown_ids(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        created = client.post(
            "/inspection/session",
            json={"model_id": "final100_hybrid_seed42"},
        )
        assert created.status_code == 200
        session = created.json()
        assert session["model_id"] == "final100_hybrid_seed42"

        selected = client.patch(
            f"/inspection/{session['session_id']}/model",
            json={"model_id": "final60_baseline_seed1337"},
        )
        assert selected.status_code == 200
        assert selected.json()["model_id"] == "final60_baseline_seed1337"

        state = client.get(f"/inspection/{session['session_id']}").json()["state"]
        assert state["model_id"] == "final60_baseline_seed1337"

        unknown = client.post(
            "/inspection/session",
            json={"model_id": "not-a-model"},
        )
        assert unknown.status_code == 404
        assert unknown.json()["detail"]["code"] == "MODEL_NOT_FOUND"


def test_model_selection_is_locked_after_analysis_state_exists(tmp_path: Path) -> None:
    with _client(tmp_path) as client:
        created = client.post("/inspection/session")
        session_id = cast(str, created.json()["session_id"])
        container = _container(client)
        container.states.save(
            session_id,
            json.dumps(
                {
                    "session_id": session_id,
                    "messages": [],
                    "model_id": "final60_hybrid_seed42",
                    "inspection": {"damage_fraction": 0.1},
                }
            ),
        )

        response = client.patch(
            f"/inspection/{session_id}/model",
            json={"model_id": "final60_baseline_seed42"},
        )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "MODEL_SELECTION_LOCKED"
