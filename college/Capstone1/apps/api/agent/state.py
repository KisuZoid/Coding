"""LangGraph workflow state (photo-first, ADR 0011).

A typed, JSON-serialisable dict persisted into ``session_states`` between chat
turns. The old questionnaire gates (incident / vehicle / repair location /
insurance / waiting_for / halt) are gone: analysis arrives via the /analyze
signpost, chat continues from the stored evidence.
"""

from __future__ import annotations

from typing import Any, TypedDict


class ConversationMessage(TypedDict, total=False):
    role: str
    content: str


class InspectionState(TypedDict, total=False):
    session_id: str
    messages: list[ConversationMessage]

    image_asset_id: str | None
    quality: dict[str, Any] | None
    inspection: dict[str, Any] | None
    explanation: str | None
    consent: str | None

    reply: str | None
