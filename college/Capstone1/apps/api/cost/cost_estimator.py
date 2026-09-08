"""Cost estimation (Phase J).

The honest default is ``DATA_UNAVAILABLE``: the research track has **no
repair-cost ground truth**, so a real quote can never be produced. The P10/P50/
P90 structure is preserved for a future quantile model. Synthetic demo values
exist only behind an explicit ``ALLOW_SYNTHETIC_ESTIMATE`` flag and are always
labelled "DEMO / SYNTHETIC ESTIMATE — NOT A REAL QUOTE".
"""

from __future__ import annotations

from enum import StrEnum
from typing import Protocol

from pydantic import BaseModel

from apps.api.inspection.context import InspectionContext
from ml.inference.features import DamageFeatures

SYNTHETIC_LABEL = "DEMO / SYNTHETIC ESTIMATE — NOT A REAL QUOTE"


class CostStatus(StrEnum):
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    SYNTHETIC_ESTIMATE = "SYNTHETIC_ESTIMATE"


class Money(BaseModel):
    amount: float
    currency: str = "INR"


class CostEstimate(BaseModel):
    status: CostStatus
    p10: Money | None = None
    p50: Money | None = None
    p90: Money | None = None
    explanation: str
    is_synthetic_demo: bool = False
    synthetic_label: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status.value,
            "p10": self.p10.model_dump() if self.p10 else None,
            "p50": self.p50.model_dump() if self.p50 else None,
            "p90": self.p90.model_dump() if self.p90 else None,
            "explanation": self.explanation,
            "is_synthetic_demo": self.is_synthetic_demo,
            "synthetic_label": self.synthetic_label,
        }


class CostEstimator(Protocol):
    def estimate(
        self,
        context: InspectionContext,
        features: DamageFeatures,
        *,
        allow_synthetic: bool,
    ) -> CostEstimate:
        """Return a cost estimate that is always honestly labelled."""
        ...


class UnavailableCostEstimator:
    """Safest real path: no cost data exists, so no real quote is produced."""

    def estimate(
        self,
        _context: InspectionContext,
        features: DamageFeatures,
        *,
        allow_synthetic: bool,
    ) -> CostEstimate:
        if allow_synthetic:
            base = 4000.0 + 3500.0 * min(features.damage_area_ratio_image, 1.0)
            return CostEstimate(
                status=CostStatus.SYNTHETIC_ESTIMATE,
                p10=Money(amount=round(base * 0.7, 2)),
                p50=Money(amount=round(base, 2)),
                p90=Money(amount=round(base * 1.6, 2)),
                explanation=(
                    "This is a synthetic, rule-based illustration generated for "
                    "the demo. AutoInspect-X has no real repair-cost ground truth, "
                    "so this is NOT a real quote and must not be used for decisions."
                ),
                is_synthetic_demo=True,
                synthetic_label=SYNTHETIC_LABEL,
            )
        return CostEstimate(
            status=CostStatus.DATA_UNAVAILABLE,
            explanation=(
                "Repair cost is not available. The model cannot estimate a real "
                "quote: no validated cost data exists for this vehicle damage. "
                "Please contact a certified workshop for an actual estimate."
            ),
            is_synthetic_demo=False,
            synthetic_label=None,
        )
