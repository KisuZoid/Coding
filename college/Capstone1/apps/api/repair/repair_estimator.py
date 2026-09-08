"""Repair-action estimation (Phase I).

A tiny, clearly-labelled **demonstration rule**, explicitly not a production
decision. The interface exists so a learned model can replace the rule later
without touching callers. Every output announces its own status.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel

from apps.api.inspection.context import InspectionContext
from ml.inference.features import DamageFeatures

RULE_LABEL = "Preliminary demonstration rule"


class RepairAction(StrEnum):
    REPAIR = "REPAIR"
    REPLACE = "REPLACE"
    MANUAL_REVIEW = "MANUAL_REVIEW"


class RepairEstimate(BaseModel):
    action: RepairAction
    rule: str = RULE_LABEL
    is_p_reliminary: bool = True
    reason: str


class RepairEstimator(Protocol):
    def estimate(
        self,
        context: InspectionContext,
        features: DamageFeatures,
    ) -> RepairEstimate:
        """Produce a labelled repair recommendation."""
        ...


class DemoRepairEstimator:
    """Deterministic, transparent rule for the teacher showcase."""

    def estimate(
        self,
        context: InspectionContext,
        features: DamageFeatures,
    ) -> RepairEstimate:
        classes = set(features.classes_present.values())
        if "tire flat" in classes or "glass shatter" in classes or "lamp broken" in classes:
            reason = (
                f"{RULE_LABEL}: detected {sorted(classes)} typically requires part replacement."
            )
            return RepairEstimate(action=RepairAction.REPLACE, reason=reason)
        if context.damage_location and not classes:
            reason = (
                f"{RULE_LABEL}: user reported damage at "
                f"{context.damage_location.panel or 'the vehicle'}, but the model "
                "found no damage regions — manual review required."
            )
            return RepairEstimate(action=RepairAction.MANUAL_REVIEW, reason=reason)
        if features.damage_area_ratio_image >= 0.02:
            reason = (
                f"{RULE_LABEL}: widespread damage "
                f"(area ratio {features.damage_area_ratio_image:.3f}) — manual "
                "review recommended before repair pricing."
            )
            return RepairEstimate(action=RepairAction.MANUAL_REVIEW, reason=reason)
        reason = f"{RULE_LABEL}: detected damage is localised and repairable."
        return RepairEstimate(action=RepairAction.REPAIR, reason=reason)
