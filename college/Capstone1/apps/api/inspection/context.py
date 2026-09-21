"""Typed inspection context (Phase F, photo-first).

One session-scoped context the analysis confirms and the offline consent
bookkeeping derives from: the image asset, the capture-quality outcome, the
model-found damage classes, the damage-area ratio, and provenance. The old
questionnaire fields (incident / vehicle / repair location / insurance) were
removed with the conversation gates. Severity is intentionally absent: the
model provides none, so nothing fabricates it.
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


class VisionInfo(BaseModel):
    image_asset_id: str | None = None
    quality_status: str | None = None
    model_found_classes: dict[str, str] = Field(default_factory=dict)
    damage_area_ratio_image: float | None = None
    provenance: Provenance = Provenance.MODEL


class InspectionContext(BaseModel):
    """Everything known about one inspection session, with provenance."""

    session_id: str
    vision: VisionInfo | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, object]:
        data = self.model_dump(exclude={"updated_at"})
        data["updated_at"] = self.updated_at.isoformat()
        return data
