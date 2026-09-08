"""Phase I/J: repair rule (labelled demo) + honest cost estimator."""

from __future__ import annotations

import json

import numpy as np

from apps.api.cost.cost_estimator import (
    SYNTHETIC_LABEL,
    CostStatus,
    UnavailableCostEstimator,
)
from apps.api.inspection.context import DamageLocation, InspectionContext
from apps.api.repair.repair_estimator import (
    RULE_LABEL,
    DemoRepairEstimator,
    RepairAction,
)
from ml.inference.features import DamageFeatures


def _context(damage: str | None = None) -> InspectionContext:
    return InspectionContext(
        session_id="s1",
        incident=None,
        damage_location=DamageLocation(panel=damage) if damage else None,
    )


def _features(classes: dict[int, str], ratio: float = 0.01, instances: int = 2) -> DamageFeatures:
    return DamageFeatures(
        width=512,
        height=512,
        instances=[],
        damage_area_ratio_image=ratio,
        per_class_area_ratio_image={int(k): ratio / max(len(classes), 1) for k in classes},
        classes_present=classes,
        num_instances=instances,
        low_confidence_instances=0,
        mask=np.zeros((1, 1), dtype=np.uint8),
    )


def test_repair_rule_is_labelled_demo() -> None:
    est = DemoRepairEstimator().estimate(_context(), _features({2: "scratch"}))
    assert est.rule == RULE_LABEL
    assert est.is_p_reliminary is True
    assert est.action is RepairAction.REPAIR


def test_repair_replace_for_safety_classes() -> None:
    est = DemoRepairEstimator().estimate(
        _context(), _features({4: "glass shatter", 6: "tire flat"})
    )
    assert est.action is RepairAction.REPLACE


def test_repair_manual_review_when_user_reports_but_model_finds_nothing() -> None:
    est = DemoRepairEstimator().estimate(_context("bumper"), _features({}))
    assert est.action is RepairAction.MANUAL_REVIEW


def test_repair_manual_review_for_widespread_damage() -> None:
    est = DemoRepairEstimator().estimate(_context(), _features({1: "dent"}, ratio=0.9))
    assert est.action is RepairAction.MANUAL_REVIEW


def test_cost_default_is_data_unavailable_and_never_fabricated() -> None:
    est = UnavailableCostEstimator().estimate(
        _context(), _features({1: "dent"}), allow_synthetic=False
    )
    assert est.status is CostStatus.DATA_UNAVAILABLE
    assert est.p50 is None
    assert est.is_synthetic_demo is False


def test_synthetic_cost_is_labeled_and_flag_guarded() -> None:
    est = UnavailableCostEstimator().estimate(
        _context(), _features({1: "dent"}), allow_synthetic=True
    )
    assert est.status is CostStatus.SYNTHETIC_ESTIMATE
    assert est.is_synthetic_demo is True
    assert est.synthetic_label == SYNTHETIC_LABEL
    assert "NOT A REAL QUOTE" in est.synthetic_label
    assert est.p10 and est.p50 and est.p90


def test_synthetic_structure_plays_nicely_with_json() -> None:
    est = UnavailableCostEstimator().estimate(
        _context(), _features({1: "dent"}), allow_synthetic=True
    )
    json.loads(json.dumps(est.to_dict()))
