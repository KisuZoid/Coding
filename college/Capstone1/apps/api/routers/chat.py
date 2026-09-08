"""Chat endpoint driving the LangGraph workflow (Phase G wiring)."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any, cast

from fastapi import APIRouter, HTTPException, Request

from apps.api.agent.graph import run_turn
from apps.api.container import Container
from apps.api.shared.schemas import ChatRequest, ChatResponse
from apps.api.storage.records import SessionStatus

router = APIRouter(prefix="/chat", tags=["chat"])


def _container(request: Request) -> Container:
    return cast(Container, request.app.state.container)


def _load_state(c: Container, session_id: str) -> dict[str, Any]:
    raw = c.states.get(session_id)
    if raw:
        loaded = json.loads(raw)
        return {"session_id": session_id, **loaded}
    return {"session_id": session_id, "messages": [], "halt": False}


@router.post("", response_model=ChatResponse)
def chat(request: Request, body: ChatRequest) -> ChatResponse:
    c = _container(request)
    record = c.sessions.get(body.session_id)
    if record is None:
        raise HTTPException(status_code=404, detail="session not found")
    if record.status is not SessionStatus.ACTIVE:
        raise HTTPException(status_code=410, detail="session closed")
    if record.expires_at is not None and record.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=410, detail="session expired")

    state = _load_state(c, body.session_id)
    updated = run_turn(c.workflow, state, body.message)

    reply = updated.get("reply") or ""
    messages = list(updated.get("messages", []))
    if reply:
        messages.append({"role": "assistant", "content": reply})
        updated = {**updated, "messages": messages, "reply": reply}

    c.states.save(body.session_id, json.dumps(updated, default=str))
    if updated.get("finished"):
        c.sessions.close(body.session_id)
    return ChatResponse(
        session_id=body.session_id,
        reply=reply,
        waiting_for=updated.get("waiting_for"),
        finished=bool(updated.get("finished", False)),
        request_id=uuid.uuid4().hex,
    )
