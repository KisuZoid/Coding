"""Phase F: inspection context + provenance + user-vs-model comparison."""

from __future__ import annotations

import json

from apps.api.inspection.context import (
    ComparisonResult,
    InspectionContext,
    Provenance,
    VisionInfo,
)


def test_context_default_provenance_is_user() -> None:
    ctx = InspectionContext(session_id="abc123", incident=None)
    assert ctx.incident is None
    assert ctx.updated_at is not None


def test_vision_carries_model_provenance() -> None:
    assert VisionInfo(image_asset_id="a1").provenance is Provenance.MODEL


def test_compare_agreement() -> None:
    assert (
        InspectionContext.compare_user_vs_model({"dent", "scratch"}, {"dent", "scratch"})
        is ComparisonResult.AGREEMENT
    )


def test_compare_partial_on_missing_class() -> None:
    assert (
        InspectionContext.compare_user_vs_model({"dent", "scratch"}, {"dent"})
        is ComparisonResult.PARTIAL_AGREEMENT
    )


def test_compare_disagreement_no_shared_classes() -> None:
    assert (
        InspectionContext.compare_user_vs_model({"tire flat"}, {"dent"})
        is ComparisonResult.DISAGREEMENT
    )


def test_compare_not_applicable_when_both_empty() -> None:
    assert InspectionContext.compare_user_vs_model(set(), set()) is ComparisonResult.NOT_APPLICABLE


def test_to_dict_is_serialisable() -> None:
    ctx = InspectionContext(session_id="s2", incident=None)
    json.dumps(ctx.to_dict())
