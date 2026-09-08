"""Typed storage records and protocol-wide enum constants (Phase C).

These records are the persistence mapping used across every store. They are
deliberately minimal: the richer, API-facing pydantic models (InspectionContext,
TrainingSample, etc.) arrive in later phases and are mapped onto these records
by store implementations.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path


class SessionStatus(StrEnum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"


class ImageKind(StrEnum):
    UPLOAD = "UPLOAD"
    PROCESSED = "PROCESSED"
    OVERLAY = "OVERLAY"
    MASK = "MASK"


class ConsentDecision(StrEnum):
    NO_RESPONSE = "NO_RESPONSE"
    DECLINED = "DECLINED"
    GRANTED = "GRANTED"


class AnnotationStatus(StrEnum):
    UNVERIFIED = "UNVERIFIED"
    USER_PROVIDED = "USER_PROVIDED"
    MODEL_SUGGESTED = "MODEL_SUGGESTED"
    HUMAN_VERIFIED = "HUMAN_VERIFIED"


@dataclass(frozen=True)
class SessionRecord:
    session_id: str
    status: SessionStatus
    created_at: datetime
    expires_at: datetime | None


@dataclass(frozen=True)
class ImageAssetRecord:
    asset_id: str
    session_id: str
    kind: ImageKind
    path: Path
    created_at: datetime


@dataclass(frozen=True)
class ConsentRecord:
    session_id: str
    decision: ConsentDecision
    created_at: datetime
    dataset_version: str | None = None


@dataclass(frozen=True)
class TrainingSampleRecord:
    sample_id: str
    session_id: str
    consent_id: str
    dataset_version: str
    annotation_status: AnnotationStatus
    provenance: str
    image_asset_id: str
    labels_json: str
    created_at: datetime
