"""API request/response contracts (Phases B, K, L wiring)."""

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
    session_id: str
    asset_id: str
    low_confidence: bool
    damage_fraction: float
    mean_confidence: float
    classes_present: dict[str, str]
    analysis: dict[str, Any]
    overlay_png_base64: str


class ChatRequest(BaseModel):
    session_id: str
    message: str = Field(..., min_length=1, max_length=1000)


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    waiting_for: str | None = None
    finished: bool = False
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
