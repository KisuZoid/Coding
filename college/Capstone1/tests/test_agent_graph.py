"""Phase G: end-to-end LangGraph turn flow (stub services, no network/engine)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from apps.api.agent.graph import Services, build_workflow, run_turn
from apps.api.agent.groq_service import RuleBasedGroqService
from apps.api.cost.cost_estimator import UnavailableCostEstimator
from apps.api.inspection.consent_service import ConsentService
from apps.api.repair.repair_estimator import DemoRepairEstimator
from apps.api.storage import (
    Database,
    FsSqliteImageStore,
    SQLiteConsentStore,
    SQLiteTrainingSampleStore,
)


def _services(tmp_path: Path) -> Services:
    db = Database(tmp_path / "app.db")
    training_root = tmp_path / "training"
    consent = ConsentService(
        SQLiteConsentStore(db),
        SQLiteTrainingSampleStore(db),
        FsSqliteImageStore(db, tmp_path / "data"),
        training_root,
        "user-consented-v1",
    )
    return Services(
        groq=RuleBasedGroqService(),
        repair_estimator=DemoRepairEstimator(),
        cost_estimator=UnavailableCostEstimator(),
        consent=consent,
        allow_synthetic=False,
    )


def _base_state(session_id: str = "s1") -> dict[str, Any]:
    return {"session_id": session_id, "messages": [], "halt": False}


def test_flow_asks_incident_then_optional_fields_then_photo(tmp_path: Path) -> None:
    wf = build_workflow(_services(tmp_path))
    state = run_turn(wf, _base_state(), "Hi there!")
    assert state["waiting_for"] == "INCIDENT"

    state = run_turn(wf, state, "I rear-ended another car at a light.")
    assert state["incident"]
    assert state["waiting_for"] == "DAMAGE_LOCATION"

    state = run_turn(wf, state, "the rear bumper took the hit")
    assert state["damage_location"] == "bumper"
    assert state["waiting_for"] == "REPAIR_LOCATION"

    state = run_turn(wf, state, "skip")
    assert state["waiting_for"] == "INSURANCE"

    state = run_turn(wf, state, "no insurance")
    assert "photo" in (state["reply"] or "").lower()


def test_full_pipeline_reaches_consent_without_fabricated_quote(tmp_path: Path) -> None:
    wf = build_workflow(_services(tmp_path))
    state = run_turn(wf, _base_state(), "I hit a pothole and scraped the front bumper")
    assert state["damage_location"] == "bumper"
    state = run_turn(wf, state, "skip")
    state = run_turn(wf, state, "no insurance claim")
    assert "photo" in (state["reply"] or "").lower()

    analysis = {
        "features": {
            "width": 8,
            "height": 8,
            "num_instances": 1,
            "damage_area_ratio_image": 0.05,
            "per_class_area_ratio_image": {"2": 0.05},
            "classes_present": {"2": "scratch"},
            "low_confidence_instances": 0,
        },
        "low_confidence": False,
        "model_classes": {2: "scratch"},
    }
    state = {**state, "image_asset_id": "a1", "analysis": analysis}
    state = run_turn(wf, state, "I uploaded it")
    assert state.get("waiting_for") == "CONSENT"
    assert state["feature_summary"]["classes_present"] == {"2": "scratch"}
    assert (state.get("repair") or {}).get("action")
    cost = state.get("cost") or {}
    assert cost["status"] == "DATA_UNAVAILABLE"
    assert "quote" in (state["reply"] or "").lower()


def test_hard_quality_failure_requests_retake(tmp_path: Path) -> None:
    wf = build_workflow(_services(tmp_path))
    state = dict(_base_state(), incident="hit a curb")
    state = {
        **state,
        "image_asset_id": "a1",
        "analysis": {"quality_reasons": ["quality check failed (TOO_BLURRY)"], "features": {}},
    }
    state = run_turn(wf, state, "photo is attached")
    assert "retake" in (state["reply"] or "").lower()


def test_low_confidence_proceeds_past_pipeline(tmp_path: Path) -> None:
    """Low model confidence (soft) must not force a retake-loop; it is surfaced
    as an honest flag and the pipeline still reaches consent."""
    wf = build_workflow(_services(tmp_path))
    state = dict(_base_state(), incident="hit a curb")
    analysis = {
        "features": {
            "width": 8,
            "height": 8,
            "num_instances": 1,
            "damage_area_ratio_image": 0.05,
            "per_class_area_ratio_image": {"2": 0.05},
            "classes_present": {"2": "scratch"},
            "low_confidence_instances": 0,
        },
        "low_confidence": True,
        "quality_reasons": [],
        "model_classes": {2: "scratch"},
    }
    state = {**state, "image_asset_id": "a1", "analysis": analysis}
    state = run_turn(wf, state, "I uploaded it")
    assert state.get("waiting_for") == "CONSENT"
    assert state["analysis"]["low_confidence"] is True
