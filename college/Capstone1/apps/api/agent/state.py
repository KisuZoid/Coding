"""LangGraph workflow state (Phase G).

A typed, JSON-serialisable dict persisted into ``session_states`` between chat
turns. Kept deliberately shallow: nested facts are stored as plain dicts so the
state round-trips through the state store without pydantic plumbing.
"""

from __future__ import annotations

from typing import Any, TypedDict


class ConversationMessage(TypedDict, total=False):
    role: str
    content: str


class InspectionState(TypedDict, total=False):
    session_id: str
    messages: list[ConversationMessage]

    waiting_for: str | None
    optional_cursor: int

    incident: str | None
    damage_location: str | None
    vehicle_make: str | None
    vehicle_model: str | None
    vehicle_year: int | None
    repair_city: str | None
    insurance_claim: bool | None

    image_asset_id: str | None
    analysis: dict[str, Any] | None
    feature_summary: dict[str, Any] | None
    comparison: str | None

    repair: dict[str, Any] | None
    cost: dict[str, Any] | None
    explanation: str | None
    consent: str | None

    reply: str | None
    halt: bool
    finished: bool
