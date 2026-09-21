"""API request/response contracts (Phases B, K, L wiring; photo-first)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Liveness payload exposed by ``GET /health``."""

    status: Literal["ok"]
    service: str
    environment: str
    version: str


class SessionCreated(BaseModel):
    session_id: str
    status: str
    created_at: str
    expires_at: str


class UploadResponse(BaseModel):
    session_id: str
    asset_id: str
    kind: str
    note: str


class AnalyzeResponse(BaseModel):
    """Result of one photo analysis (quality gate + segmentation + assistant).

    ``status`` distinguishes a finished segmentation run (``OK``) from a
    capture-quality rejection (``QUALITY_FAILED``). On quality failure the
    endpoint returns no segmentation output and the assistant gives the user
    retake guidance. On success, ``inspection`` carries the structured evidence
    and ``assistant_message`` the first explanation in the conversation. No
    cost or repair fields exist by design.
    """

    session_id: str
    status: Literal["OK", "QUALITY_FAILED"]
    assistant_message: str
    # True when the live LangChain assistant was unavailable and a clearly
    # offline, deterministic evidence summary/retake guidance was used instead.
    assistant_fallback: bool = False
    asset_id: str | None = None
    quality_status: str | None = None
    quality_reasons: list[str] = Field(default_factory=list)
    inspection: dict[str, Any] | None = None
    classes_present: dict[str, str] = Field(default_factory=dict)
    low_confidence: bool = False
    damage_fraction: float = 0.0
    mean_confidence: float = 0.0
    overlay_png_base64: str | None = None


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    request_id: str


class ConsentRequest(BaseModel):
    decision: Literal["GRANTED", "DECLINED"]


class ConsentResponse(BaseModel):
    session_id: str
    decision: str
    dataset_version: str
    sample_id: str | None = None
    saved: bool
    note: str


class InspectionStateResponse(BaseModel):
    session_id: str
    status: str
    state: dict[str, Any]
