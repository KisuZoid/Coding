"""Typed inspection context (Phase F).

One session-scoped context the agent conversation builds and the analysis
confirms — incident, vehicle, repair location (city-level only, never street),
vision evidence, and per-field provenance. Severity is intentionally absent:
the underfit baseline cannot provide it, so nothing fabricates it.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Provenance(StrEnum):
    USER = "USER"
    MODEL = "MODEL"
    DERIVED = "DERIVED"
    INFERRED = "INFERRED"
    SYSTEM = "SYSTEM"


class ComparisonResult(StrEnum):
    AGREEMENT = "AGREEMENT"
    PARTIAL_AGREEMENT = "PARTIAL_AGREEMENT"
    DISAGREEMENT = "DISAGREEMENT"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class IncidentInfo(BaseModel):
    summary: str | None = None
    provenance: Provenance = Provenance.USER


class VehicleInfo(BaseModel):
    make: str | None = None
    model: str | None = None
    year: int | None = None
    provenance: Provenance = Provenance.USER


class DamageLocation(BaseModel):
    panel: str | None = None
    details: str | None = None
    provenance: Provenance = Provenance.USER


class RepairLocation(BaseModel):
    city: str | None = None
    proximity_preference: str | None = None
    provenance: Provenance = Provenance.USER


class VisionInfo(BaseModel):
    image_asset_id: str | None = None
    quality_status: str | None = None
    model_found_classes: dict[str, str] = Field(default_factory=dict)
    damage_area_ratio_image: float | None = None
    provenance: Provenance = Provenance.MODEL


class InspectionContext(BaseModel):
    """Everything known about one inspection session, with provenance."""

    session_id: str
    incident: IncidentInfo | None = None
    damage_location: DamageLocation | None = None
    vehicle: VehicleInfo | None = None
    repair_location: RepairLocation | None = None
    insurance_claim: bool | None = None
    vision: VisionInfo | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, object]:
        data = self.model_dump(exclude={"updated_at"})
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def compare_user_vs_model(
        cls,
        user_damage: set[str],
        model_classes: set[str],
    ) -> ComparisonResult:
        """Agreement between what the user reported and what the model found.

        Class-name level: dent/scratch/crack/glass shatter/lamp broken/
        tire flat. Exact match is AGREEMENT; a partial overlap or a one-sided
        report is PARTIAL_AGREEMENT; a non-empty conflict with zero shared
        classes is DISAGREEMENT.
        """
        if not user_damage and not model_classes:
            return ComparisonResult.NOT_APPLICABLE
        if not user_damage or not model_classes:
            return ComparisonResult.PARTIAL_AGREEMENT
        if user_damage == model_classes:
            return ComparisonResult.AGREEMENT
        if user_damage & model_classes:
            return ComparisonResult.PARTIAL_AGREEMENT
        return ComparisonResult.DISAGREEMENT
