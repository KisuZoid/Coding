"""Phase F: inspection context + provenance (photo-first)."""

from __future__ import annotations

import json

from apps.api.inspection.context import InspectionContext, Provenance, VisionInfo


def test_context_minimal_roundtrip() -> None:
    ctx = InspectionContext(session_id="abc123")
    assert ctx.session_id == "abc123"
    assert ctx.updated_at is not None
    json.dumps(ctx.to_dict())


def test_vision_carries_model_provenance() -> None:
    assert VisionInfo(image_asset_id="a1").provenance is Provenance.MODEL


def test_vision_populated_from_analysis() -> None:
    vision = VisionInfo(
        image_asset_id="a1",
        quality_status="VALID",
        model_found_classes={"1": "dent"},
        damage_area_ratio_image=0.05,
    )
    data = vision.model_dump()
    assert data["quality_status"] == "VALID"
    assert data["model_found_classes"] == {"1": "dent"}
    assert data["damage_area_ratio_image"] == 0.05


def test_to_dict_is_serialisable() -> None:
    ctx = InspectionContext(
        session_id="s2",
        vision=VisionInfo(image_asset_id="a1", quality_status="TOO_BLURRY"),
    )
    json.dumps(ctx.to_dict())
