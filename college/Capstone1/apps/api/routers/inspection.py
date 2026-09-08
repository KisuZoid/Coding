"""Inspection lifecycle + vision endpoints (Phases K-P wiring).

Keeps the honesty contract at the API boundary: the overlay is only ever the
model's *predicted* mask, area is image-denominator, and consent/training writes
flow exclusively through ``ConsentService``.
"""

from __future__ import annotations

import base64
import json
import uuid
from datetime import UTC, datetime
from typing import Annotated, Any, cast

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from apps.api.agent.graph import context_from_state, features_from_summary
from apps.api.container import Container
from apps.api.shared.schemas import (
    AnalyzeResponse,
    ConsentRequest,
    ConsentResponse,
    InspectionStateResponse,
    SessionCreated,
    UploadResponse,
)
from apps.api.storage.records import ConsentDecision, ImageKind, SessionStatus
from apps.api.vision.quality import ImageQualityValidator
from ml.inference.features import extract_features
from ml.inference.overlay import encode_png, render_overlay
from ml.inference.preprocess import load_image_rgb

router = APIRouter(prefix="/inspection", tags=["inspection"])


def _container(request: Request) -> Container:
    return cast(Container, request.app.state.container)


def _valid_session(request: Request, session_id: str) -> Container:
    c = _container(request)
    record = c.sessions.get(session_id)
    if record is None:
        raise HTTPException(status_code=404, detail="session not found")
    if record.status is not SessionStatus.ACTIVE:
        raise HTTPException(status_code=410, detail="session closed")
    if record.expires_at is not None and record.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=410, detail="session expired")
    return c


def _load_state(c: Container, session_id: str) -> dict[str, Any]:
    raw = c.states.get(session_id)
    if raw:
        loaded = json.loads(raw)
        return {"session_id": session_id, **loaded}
    return {"session_id": session_id, "messages": [], "halt": False}


def _save_state(c: Container, session_id: str, state: dict[str, Any]) -> None:
    c.states.save(session_id, json.dumps(state, default=str))


@router.post("/session", response_model=SessionCreated)
def create_session(request: Request) -> SessionCreated:
    c = _container(request)
    session_id = uuid.uuid4().hex
    record = c.sessions.create(session_id)
    _save_state(c, session_id, {"session_id": session_id, "messages": [], "halt": False})
    return SessionCreated(
        session_id=record.session_id,
        status=record.status.value,
        created_at=record.created_at.isoformat(),
        expires_at=record.expires_at.isoformat() if record.expires_at else "",
    )


@router.post("/{session_id}/upload", response_model=UploadResponse)
def upload_photo(
    session_id: str, request: Request, file: Annotated[UploadFile, File()]
) -> UploadResponse:
    c = _valid_session(request, session_id)
    data = file.file.read()
    asset_id = uuid.uuid4().hex
    try:
        asset = c.images.write(session_id, asset_id, ImageKind.UPLOAD, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    state = _load_state(c, session_id)
    state["image_asset_id"] = asset.asset_id  # a new photo supersedes the previous one
    _save_state(c, session_id, state)
    return UploadResponse(
        session_id=session_id,
        asset_id=asset.asset_id,
        kind=asset.kind.value,
        note="Photo stored for this session only; analysis will follow in /analyze.",
    )


@router.post("/{session_id}/analyze", response_model=AnalyzeResponse)
def analyze_photo(session_id: str, request: Request) -> AnalyzeResponse:
    c = _valid_session(request, session_id)
    state = _load_state(c, session_id)
    asset_id = state.get("image_asset_id")
    asset = c.images.get(asset_id) if asset_id else None
    if asset is None:
        raise HTTPException(status_code=404, detail="no uploaded photo for this session")
    data = c.images.read(asset)

    # Hard capture-quality gate (Phase E contract): reject before any model
    # inference when the photo is dark, glare-struck, blurry, or flat. These are
    # capture problems the user can fix by retaking; they are not model output.
    rgb = load_image_rgb(data)
    quality = ImageQualityValidator().assess(rgb)
    if not quality.is_valid:
        raise HTTPException(
            status_code=422,
            detail={"status": quality.status.value, "reasons": quality.reasons},
        )

    engine = c.engine()
    result = engine.predict_bytes(data)
    features = extract_features(result)

    overlay_png = encode_png(render_overlay(rgb, result.mask))
    overlay_b64 = base64.b64encode(overlay_png).decode("ascii")
    c.images.write(session_id, uuid.uuid4().hex, ImageKind.OVERLAY, overlay_png)

    analysis = {
        **result.to_dict(),
        **features.to_dict(),
        "model_classes": features.classes_present,
        "classes_present": features.classes_present,
        "mean_confidence": result.mean_confidence,
        "damage_fraction": result.damage_fraction,
        # Honest flags persisted for the workflow: the engine's confidence as
        # reported, plus the capture-quality outcome (empty because a rejected
        # photo never reaches this point). Low model confidence is a soft
        # signal — surfaced, never silently retaken; hard capture failures are
        # rejected above.
        "low_confidence": result.quality.low_confidence,
        "quality_reasons": quality.reasons,
        "quality": quality.to_dict(),
        "overlay_png_base64": overlay_b64,
    }
    state["analysis"] = analysis
    _save_state(c, session_id, state)
    return AnalyzeResponse(
        session_id=session_id,
        asset_id=asset.asset_id,
        low_confidence=result.quality.low_confidence,
        damage_fraction=result.damage_fraction,
        mean_confidence=result.mean_confidence,
        classes_present={str(k): v for k, v in features.classes_present.items()},
        analysis=analysis,
        overlay_png_base64=overlay_b64,
    )


@router.get("/{session_id}", response_model=InspectionStateResponse)
def get_inspection(session_id: str, request: Request) -> InspectionStateResponse:
    c = _valid_session(request, session_id)
    state = _load_state(c, session_id)
    return InspectionStateResponse(
        session_id=session_id,
        status="ACTIVE",
        state=state,
    )


@router.post("/{session_id}/consent", response_model=ConsentResponse)
def consent(session_id: str, request: Request, body: ConsentRequest) -> ConsentResponse:
    c = _valid_session(request, session_id)
    record = c.consent.record_decision(session_id, ConsentDecision(body.decision))
    sample_id: str | None = None
    saved = False
    note = "Decision recorded. The photos are not used for training."

    if record.decision is ConsentDecision.GRANTED:
        state = _load_state(c, session_id)
        summary = (state.get("analysis") or {}).get("features", {})
        if not summary:
            summary = state.get("analysis") or {}
        try:
            stored = c.consent.store_training_sample(
                context_from_state(state),
                features_from_summary(summary),
                consent=record,
                image_asset_id=state.get("image_asset_id") or "",
            )
            if stored.get("saved"):
                saved = True
                sample_id = str(stored.get("sample_id"))
                note = (
                    "Anonymised sample stored for the consent dataset (MODEL_SUGGESTED provenance)."
                )
            else:
                note = "Consent granted, but no training sample could be stored."
        except Exception as exc:  # never leak internals to the client
            note = f"Consent granted, but sample storage failed: {exc}"

    return ConsentResponse(
        session_id=session_id,
        decision=record.decision.value,
        dataset_version=record.dataset_version or "",
        sample_id=sample_id,
        saved=saved,
        note=note,
    )


@router.delete("/{session_id}")
def delete_inspection(session_id: str, request: Request) -> dict[str, str]:
    c = _container(request)
    if not c.cleanup.cleanup(session_id):
        raise HTTPException(status_code=404, detail="session not found")
    return {"session_id": session_id, "status": "deleted"}
